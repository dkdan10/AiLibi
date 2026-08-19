# AiLibi — collated portfolio-perception ledger (Track C merge)

Merged from six independent reads of `main @ b809b19c` (2026-08-18):
`p1-backend-hiring-manager.md`, `p2-ml-research-lead.md`, `p3-frontend-product-engineer.md`,
`p4-recruiter-skimmer.md`, `x1-front-door-reproduction.md`, `x2-narrative-and-positioning.md`.
Read-only throughout; nothing in the repo was touched by any track.

Merger's own spot-check [VERIFIED]: README.md = 3,833 words; line 84 = 135 words, line 107 =
506 words, line 149 = 234 words; docs/reading-guide.md = 3,239 words. These match every
persona's numbers, so the line-anchored findings below are current at HEAD.

Labels carried through from the source reports: **[VERIFIED]** = a persona ran/read/measured
it; **[JUDGMENT]** = inference. Where I add my own ruling it is marked **[MERGER]**.

---

## 0. Consensus at a glance

Every persona independently reached the same headline verdicts:

- **Take the meeting / advance:** 6/6 yes (P2 "conditional — communication is the blocker").
- **Star:** 5/6 yes; P3 "not on the current front door" (no hosted demo).
- **Single change that most raises the verdict:** 5/6 named the README "Project status"
  block (lines 82–107) plus its neighbours; P3 named hosting the demo + re-recording the GIF.
- **What impressed everyone:** the three offline commands work in seconds; the enforced
  architecture; the meeting view / Mind inspector; the honesty about what was NOT shown.
- **What lost everyone:** the same ~850 words of internal ledger prose between minute 4 and
  minute 6 of the README, written in an undefined private vocabulary.

Item × persona matrix (M = raised as MUST, G = GOOD, N = NICE, · = not raised):

| # | Item | P1 HM | P2 ML | P3 FE | P4 Rec | X1 Repro | X2 Narr |
|---|---|---|---|---|---|---|---|
| A1 | Rewrite README status (84/107) + "Watch a replay" (149) | M | M | M | M | M | M |
| A2 | No undefined private vocabulary on the front door | M | M | M | M | M | G |
| A3 | Host the static demo; fix the hero GIF | G | · | M | · | M | M |
| A4 | GitHub About/topics/homepage; badge; license/author line | G | · | M | M | M | M |
| A5 | Authorship statement — human vs agents (incl. AI auditors) | M | M* | N | M | G | M |
| A6 | State the results once, plainly (README table + ML page) | · | M | · | G | G | G |
| B1 | First-run `AILIBI_PROMPT_SET` warning | G | · | · | · | M | · |
| B2 | Fake-provider tournament yields an all-null report | · | · | · | · | M | · |
| B3 | Reading guide: not "five minutes"; retitle/split | N | · | G | · | G | G |
| B4 | Architecture doc/diagram one click from the top | G | G | · | G | N | G |
| B5 | Show the workflow (contract → prompt → PR), not just link | · | · | N | · | G | G |
| B6 | UI jargon / bundle empty-state / picker copy | · | · | G | · | · | · |
| B8 | Prose pass (em-dashes, hedges, defensive parentheticals, clone caveat) | N | · | · | G | N | M** |
| B12 | Extend phase table to 19; `docs/history.md`; `audits/README.md` | M*** | · | · | M*** | M*** | G |

\* P2's MUST-3 ("two independent external audits" = two AI models; single model, n=50) is folded
into A5. \*\* X2's MUST-5 (reframe honesty as rigor) is folded into A1/A6. \*\*\* implied by
their A1 fix ("move the ledger to a linked history page").

---

## (A) Consensus MUST-address items

Ordered by how many audiences each blocks and how cheap the fix is.

### A1. Rewrite README "Project status" (lines 82–107) and "Watch a replay" (line 149) for outsiders — 6/6

- **Audience blocked:** every persona stopped reading linearly here — recruiter (P4, minute
  3:15), hiring manager (P1, minute 4:30–9:00), frontend/product (P3, 4:30–6:00), research
  lead (P2, 3:00–5:00), X1, X2. This is the point on the page where the skimmer decides.
- **Evidence [VERIFIED by all six]:** line 84 is a 135-word single sentence with nested
  parentheticals; line 107 is a 506-word single paragraph (35 opening parentheses, a 172-word
  sentence) covering phases 15–19; the status section is 846 words = 22% of the README; line
  149 spends 234 words on lever provenance ("the roll-call round, the endpoint-band whereabouts
  exemption, the vent-placement contradiction variant (flag-minting plus the absent-set
  widening)…") inside a section headed "Watch a replay". The phase table stops at 14 with the
  note "the paragraph below it carries phases 15–19" — the author knows the paragraph is a
  table that was never extended (X2).
- **Second-order damage:** on a literal read the status is a run of negatives — "closed …
  with no mover flip", "closed 2026-08-18 with nothing recorded", "zero of the fourteen
  pre-registered emergence rulings demonstrated" — which P3, P4 and X2 all report reading as
  "the last two phases produced nothing" until they reached reading-guide §1 "The honesty
  culture". P1 [JUDGMENT]: it "unintentionally foregrounds the null ML result over the
  shipped, working system." X2: honesty "delivered as apology … without the positive frame."
- **Concrete fix (synthesised):**
  1. Replace lines 82–107 with ≤150 words of plain English + a phase table extended to 19
     (one row each: phase, dates, one-line outcome, link to its close audit). P4's draft is
     usable nearly verbatim: *"Started May 2026. MVP done in phases 0–5. Phases 6–19 pushed
     how well the agents reason and added a machine-learned tactical policy; the learned
     policies beat the scripted one on wins but I kept the scripted one as default because
     they failed my pre-registered evidence-quality bar — I record misses as findings rather
     than moving the bar. Details: audits/…"*
  2. Say in one sentence what "no flip / nothing recorded" MEANS (a bar was pre-registered;
     the honest answer was "not yet") — lead with what WAS shown, then the refusal to overclaim.
  3. Add a one-line project state: "Active. 19 phases closed 2026-08-18; next phase under
     decision — see tasks/post-phase-14-plan.md" (X2 GOOD-9).
  4. Cut line 149 to: what the viewer shows, the 7 featured seeds (the reading guide §2 table
     is better than the README's paragraph), "100 replays, two 50-game tournaments,
     Qwen3.6-27B, 34%/30% impostor wins, provenance in `replays/samples/*/MANIFEST.md`."
  5. Move the phase-15–19 narrative and the lever-graduation provenance to `docs/history.md`
     and the sample MANIFESTs (which the README already calls canonical).

### A2. No undefined private vocabulary anywhere on the front door — 6/6

- **Audience blocked:** all; P1 frames it as the interview risk ("smart but can't summarize
  for an audience"); P2 as "a legibility cliff between the numbers and the reader."
- **Evidence [VERIFIED X1 counts]:** 6 of the 11 glossary terms in reading-guide §4 appear
  undefined in README.md ("baseline" 19×, "adopting record" 3×, "ladder tip" 4×, "graduated"
  5×, "NO-FLIP"/"no mover flip" 2×, "canary denominator" 2×) plus ≥15 terms defined nowhere
  (referee, slate, arm, mover, champion, conviction-economy, supply/conversion floors, absence
  prior, roll-call round, endpoint-band whereabouts exemption, flag-minting, starved-economy
  shape, screening-tier shortlist, two-axis owner ruling, training-time-runner tier,
  evidence-gated default flip). The idiom also leaks into the hero captions ("featured strip",
  "the shippable static bundle" — P4), the reproduce block ("re-using one silently doubled
  per-seed files in Phase 4" — P4), the reading guide's own opener ("baseline-6 adopting
  record" — P4, P2), and UI tooltips (P3, see B6). Conventions named after task numbers ("the
  15.18 convention", "the §1.3 bar", "the two-owner gate") are, per P1/P2/X1, the clearest
  tell of a private dialect. The reading guide diagnoses this itself ("the corpus is case law
  with no glossary") but the fix landed one hop BELOW the README (X2).
- **Rule to adopt (X1):** nothing in README.md may require docs/reading-guide.md §4 to parse.
- **Concrete fix:** (a) A1 removes most instances; (b) where a term must survive, say it once
  in plain words ("the current reference recording — internally 'baseline 6'") and stop
  (P1); (c) rename task-number conventions to descriptive names in the glossary
  ("merge-as-ratification", "the flip bar", "reference recording", "held-out monitoring
  corpus" — P1 NICE-13, P2 NICE); (d) define "owner" = the human at first use, or drop it in
  outsider-facing docs (X2 MUST-5 item 5: "the single most important word for story A and it
  is undefined"); (e) shorten both image captions to one sentence each (P4).

### A3. Host the static demo bundle and re-record the hero GIF — P3 M, X1 M, X2 M, P1 G

- **Audience blocked:** recruiters and demo-first engineers ("for this audience the URL *is*
  the project" — P3); P3 would not star without it, would star and forward with it.
- **Evidence [VERIFIED P3, X1, X2]:** `scripts/build_demo_bundle.py` produces an 8.8 MB
  static directory with a relative asset base in ~4–5 s, plays with no API (P3 drove it in a
  browser; X1 served it), and is e2e-tested against the built artifact with `/api` blocked at
  the network layer (`frontend/e2e/bundle.spec.ts`). `docs/deployment.md` calls it "exactly one
  sanctioned way to put AiLibi in front of someone who is not the local operator." Yet
  `has_pages: false`, homepage `null`, no URL anywhere in the tree. Every reader must clone
  ~256 MiB and install uv + node to see anything move.
- **GIF [VERIFIED P3 by extracting 20 frames + `getBoundingClientRect` at three viewports]:**
  the only asset "most readers will ever see" (docs/media/README.md's words) never shows the
  map or a token moving — at the 1000×640 recording viewport the fixed bottom dock covers the
  PixiJS canvas entirely (canvas top 311 px vs dock top 308 px). The caption promises "the map,
  an autoplay that stops itself" — the autoplay is there, the map isn't. (See D1 for the
  X2/P4 partial dissent.)
- **Concrete fix:** a ~15-line GitHub Pages workflow deploying `frontend/dist/demo-bundle`;
  put the URL in README line 1 and the GitHub homepage field. Re-record the GIF at ≥1440×900
  (or scroll the map into frame) showing at least one token moving, one kill, one meeting
  pause; optionally add an MP4/WebM (GitHub renders video; 640 px GIF is palette-crushed —
  P3, P4). Keep the meeting PNG as the hero still — every persona called it the money shot.
  Fix the two bundle warts before hosting: the Tournament tab dumping raw http.server 404 HTML
  in-app, and the generated bundle README baking `/Users/danielkeinan/…` (P3, X1).

### A4. Fill the GitHub About panel; add a CI badge, a license line, a byline — P3 M, P4 M, X1 M, X2 M

- **Audience blocked:** recruiters first ("on the repo card there is literally nothing but
  the name" — P4); everyone else loses the 1-second health check.
- **Evidence [VERIFIED via `gh` by P3, P4, X1, X2]:** description `""`, topics none,
  homepage none, `has_pages: false`, 0 stars, 0 forks, no releases; README has zero badges,
  zero author name, no license mention (MIT only in LICENSE/CONTRIBUTING).
- **Concrete fix (five minutes):** description ≈ X2 §6a short form (≤350 chars): *"Deterministic
  social-deduction sim (Among-Us-style) with LLM agents behind an enforced observation
  firewall — built by directing AI coding agents against written contracts: 350 PRs, 19
  phases, byte-identical replays, honest negative ML results."* Topics (union of P3/P4/X1/X2):
  `multi-agent`, `llm-agents`, `social-deduction`, `deterministic-simulation`,
  `agentic-coding`, `claude-code`, `evaluation`, `among-us`, `python`, `fastapi`, `react`,
  `pixijs`. Homepage = the Pages URL from A3. README: CI badge + MIT badge + Python 3.11
  badge, and a byline line under the title.

### A5. State authorship in plain language: who the human is, what the human did, what the agents did — P1 M, P4 M, X2 M, P2 M (auditor identity), X1 G, P3 N

- **Audience blocked:** hiring managers ("the open question is 'what did *you* do?'" — P1;
  P4: "did a person actually drive this?" is the reflex the prose style triggers); researchers
  (P2: "two independent external audits" turns out to mean two AI models, disclosed only in
  reading-guide §5.2).
- **Evidence [VERIFIED X2, P4, X1]:** README names no person — LICENSE says "Daniel Keinan",
  git shows three human identities (`dkdan10` 355, `Daniel Keinan` 211) plus "Claude" as
  first-class author on 310 commits (35%), the latest commit on `main` is authored "Claude",
  all 346 merged PRs show one human author on GitHub; the docs say "the owner"/"the human"/"the
  operator" and never introduce them. Co-Authored-By trailers name model versions on ~90% of
  commits (Fable 5 ×324, Opus 4.8 ×302, …) — a free provenance graph nobody points at.
  X2's verdict: "the *mechanics* of authorship are more legible here than in almost any
  agent-built repo … but the *narrative* of authorship is absent, and absence gets read
  uncharitably."
- **Concrete fix:** one short README section (X2 §6a is a usable draft): name; what the human
  owned (321 task contracts, review gates, audit rulings, product/design direction, the ADR
  decisions); what the agents did (all production code; most audits — Claude Code and Codex,
  per `AGENT_IMPLEMENTATION.md` and the trailers); what the human did NOT do (write production
  code by hand — "that is what makes the rest impressive rather than suspicious"); how a reader
  can verify it (`claude/…` branch names, commit authors, trailers); 3 links: one contract,
  its generated prompt, and the merged PR it produced (P1 MUST-3, P3 NICE-12, X1 GOOD-7). Say
  "AI auditors (Claude and Codex), commissioned by the owner" at first mention of the audits,
  and "all gameplay/ML numbers are on one model + prompt set at n=50" (P2). Optional
  `.mailmap` + one sentence explaining "Claude" as commit author (X2 NICE-14, P4 NICE).
  Switch README/reading-guide to first person; keep the institutional register for
  AGENTS.md, contracts and audits (X2 NICE-19).

### A6. State the results once, in one place, plainly — P2 M, X1 G, X2 G, P4 G

- **Audience blocked:** researchers ("no single 1-page results summary" — X1; "no artifact
  tells the ML story in the standard research shape" — P2) and hiring managers ("cannot tell
  what was achieved" — X1 §4). Also the enabling move for A1: the ledger content must land
  somewhere before it can leave the README.
- **Evidence [VERIFIED P2, X1, X2]:** the numbers exist and reproduce (P2 re-derived the
  McNemar table and the vent-sighting cross-tab from committed files with stdlib) but are
  scattered across README §status, reading-guide §1/§3/§6, `training/README.md` (whose title
  is a tier map — "the entry point to the ML program is a disposition ledger") and 80 audit
  files (24,527 lines). The README never states the headline findings.
- **Concrete fix:** (a) lift reading-guide §1 "numbers worth knowing" into the README as a
  results table with sources (100/100 replays byte-reconstruct; 520/520 ballots cite valid
  evidence; 87% of correct 9p ejections ride an engine-certified vent sighting vs ~chance
  without — i.e. general social deduction NOT demonstrated; learned movers beat the FSM on
  wins +0.12–0.30 but were not adopted, NO-FLIP ×2); (b) write a ≤2-page `docs/ml-program.md`
  (or rewrite the top of `training/README.md`) in research shape — problem, environment
  (obs/actions/reward, one figure), method (ES over a 19-weight utility scorer; the referee as
  selection gate, not reward), one results table (arm, win vs same-seed FSM, McNemar p,
  referee verdict), N1/N2 framed as referee-exploitation / specification gaming (P2: "the most
  interesting *research* result in the repo … under-sold"), limitations (one model, n=50, bar
  construction, raw finalist slate off-repo), related work. Everything needed already exists
  in reading-guide §6, `audit-phase-19-input-claude.md` §6 and `training/README.md` §3.

---

## (B) GOOD-to-address items

B1. **First-run noise contradicts the reproducibility pitch** (X1 MUST-3, P1 GOOD-6; ruled
GOOD-top, see D3). [VERIFIED X1, P1] Every front-door command prints, twice per game on
stderr, "`AILIBI_PROMPT_SET` is unset — falling back to the frozen reference set 'qwen3_5_9b',
two generations behind the operational baseline…"; the variable is documented in none of
README, .env.example, AGENTS.md or docs/architecture.md; the 5-game tournament prints it 6×.
Fix: default the CLI surfaces to the operational set, silence under the fake provider, or
document the variable next to `AILIBI_LLM_PROVIDER` and say the notice is expected.

B2. **The fake-provider tournament the README hands out produces an all-null report** (X1
MUST-5). [VERIFIED] 5/5 impostor wins, 0 ejections, `vote_correctness_rate: null`,
`ejection_accuracy: null`. Fix: point the README example at
`replays/samples/9p2i/tournament-eval-report.json` ("here is a real one") and say up front
what fake output looks like and why.

B3. **The reading guide is 3× its advertised length** (P1 N, P3 G, X1 G, X2 G). [VERIFIED
3,239 words, 378 lines, 11-term glossary, `file:line` anchors already drifting — 1 of ~30
checked by X1]. Fix: a real 5-minute page (§1 table + §2 demo + §3 cross-tab + three audits ≈
800 words) with the rest split into `docs/glossary.md`, `docs/audits-index.md` /
`audits/README.md`; replace `file:line` citations with heading anchors (X1 GOOD-9).

B4. **Put `docs/architecture.md` (and a diagram) one click from the top** (P1 G, P2 G, P4 G,
X2 G, X1 N). It is "the document I wanted first" (P1) and "the best single technical page in
the repo" (X2); today linked mid-paragraph at line 45 and in the footer. Inline the ASCII
layering block or an SVG (layering + the firewall arrow) in the README; retire or caption
`DESIGN.md` §1.1's target diagram as target-not-as-built. P2 also wants a one-page environment
spec (rooms, ticks, actions, observation packet fields, meeting protocol) and a related-work
paragraph (Werewolf/Avalon/Among-Us LLM benchmarks; hidden-role RL) so a researcher can place
the environment.

B5. **Show the workflow, don't just link it** (X1 G, X2 fold, P3 N, P1 M-3 fold). A 15-line
excerpt of a task contract + the matching prompt header + the PR it produced (branch
`claude/…`, gate green) makes "300+ agent-authored PRs" concrete; today the contract and prompt
are linked once and never shown, and the PR is not linked.

B6. **UI copy: strip audit/task citations from user-facing text and fix the bundle's empty
states** (P3 GOOD 5, 6, 9, 10). [VERIFIED P3] TournamentDashboard tooltips read "(Task 19.14;
audits/audit-phase-19-triage.md §7 item 15)", "Since Task 13.13 the vote gate is
non-directive", "DESIGN.md §11.3"; MeetingView Resolution card shows "§4.6"; the bundle
Tournament tab dumps raw 404 HTML; the picker header says "Every recorded replay in the served
set" while the bundle ships 4 of 50; "4p1i / 9p2i" never expanded; the map is clipped at
1280×800 and hidden at 1000×640 behind the fixed dock — collapse the timeline by default or
un-fix the dock below ~800 px tall.

B7. **Source-comment style and file size** (P1 GOOD 9, 10). `observation/service.py:31–83` is
a 50-line provenance comment ("audit-2026-06-13-1816 D-D-1", "Codex review, PR #155") before
the first function — lead with plain intent, push citations to the end. `meetings/manager.py`
(3,989 lines) and `orchestrator/game.py` (3,193) will be asked about; one sentence in
architecture.md acknowledging why, or a split.

B8. **Prose pass** (P4 G, X2 M-3/4 folded, P1 N-12, X1 N-17). [VERIFIED] 81 em-dashes and
137 parentheticals in the README; repeated "deliberately / honest / fails loud / load-bearing";
the defensive "300+ … the live count is on GitHub, deliberately not re-pinned here" (say "350
merged PRs as of 2026-08-18" or badge it); the ~150-word `--filter=blob:none` / `filter-repo`
clone caveat in Setup, repeated in the reading guide (one line + link to `docs/artifacts.md`);
the Darwin-arm64 portability paragraph at line 133; "MVP complete" said three times; "default
game is 4p1i" vs "served default is 9p2i" reconciled in one sentence; "### Reproduce the three
claims above" should name the three claims. P4: "the cadence undercuts" credible content and
"lands the strongest AI-generated-prose smell on the page."

B9. **Make unverifiable claims verifiable-shaped and fix small truth wobbles** (X1 GOOD 11,
12; P3 N-11). "every one merged green through the same gate" → "CI is required on `main`; see
ci.yml; check.sh runs the same gate locally"; "zero firewall violations" → "never breached in
CI: import-linter contract + `tests/test_firewall.py` planted-leak test + recursive leak
sweep". Fix: "recorded verbatim in ADR-0001" (ADR text differs: 2 Hz, ≤100 calls, author
Codex); `docs/deployment.md`'s unresolvable "audit C-C-1/2/4"; the bundle README's absolute
local path; explain the `*.audit.jsonl` sidecar `run_game.py` writes beside the replay.

B10. **ML-program hygiene items a research reader will spot** (P2 GOOD). Commit or explicitly
de-scope the 449-game finalist raw slate (`training/reports/_finalist_eval_raw` is empty; rows
point at `/Users/…`) — today the central ML ruling rests on measurements *of* evidence not in
the repo; add uncertainty to the referee floors (a Wilson helper exists) or say why not;
restructure `training/README.md` program-summary-first, tier map second, reopening checklist
last.

B11. **A "What I learned" page** (X2 GOOD-8, P4 NICE, P1 interview probe). 2–3 screens on
directing agents at scale (contract byte-mirroring, coordination re-anchoring commits, why
outside PRs are refused), what CI could and could not catch, the ML negative result and
pre-registration, doc-drift as a first-class bug (Phase 19), and — owning P2's critique — when
to stop building measurement. Material exists across `training/README.md` §3, reading-guide
§1, triage §1, close audits; nobody will assemble it but the author.

B12. **Navigation of the meta-corpus** (X2 GOOD 11–12, X1 NICE-16, P4 NICE, P1 MUST-1
implied). `audits/README.md` index (80 files, three named "read first", 77 orphaned);
`docs/history.md` with the extended phase table and one paragraph per phase; consider folding
AGENTS.md / AGENT_IMPLEMENTATION.md / DESIGN.md (9,730 words, partly "historical") under a
`docs/` index — a newcomer sees 5 root markdown files + 24 tasks + 80 audits with no map.

B13. **"At a glance" block under the tagline** (P4 G, P1 G-8): stack (Python 3.11 · FastAPI ·
Pydantic · React/Vite/PixiJS · uv · mypy --strict · Hypothesis), timeline (May–Aug 2026, solo),
scale (877 commits / 350 PRs / 321 contracts / 100 committed replays / ~4.6k tests), status.
(Absorbed into F.)

---

## (C) NICE

- Explain the name in one clause — "AiLibi: *alibi*, with AI" (P4, X2).
- `.mailmap` consolidating `dkdan10` / `Daniel Keinan`; note that "Claude" as commit author is
  the dispatch pattern, not a second maintainer (X2, P4).
- A 20–90 s MP4/WebM or narrated Loom of the featured seed-2 game + one contract → PR walk
  (P3, P4, X2).
- One cross-model spot-check (10 seeds on a second open model) to bound how model-specific
  the "87% vent" finding is (P2).
- A blog post / thread: "350 PRs, zero hand-written production code, one firewall" or "N1/N2
  as specification gaming of a social-deduction referee" (P2, X2).
- Trim close-audit headers to a real one-line verdict + table (P2).
- Mention `docker-compose.yml` in the README or delete it; add `.python-version` or a note
  that uv downloads 3.11 (X1).
- Component-level render tests for MeetingView/MindInspector (today the vitest suite is
  pure-logic) (P3).
- Bake the 9p2i tournament report into a second "full corpus" bundle so the hosted Dashboard
  has something to show (P3).
- Surface CONTRIBUTING.md from the README (P1); it reads as confidence ("issues are welcome,
  pull requests are not the workflow") — keep it (X2, P4; see D8).
- Rename glossary items toward standard vocabulary where one exists (P1, P2).
- First-person voice in README and reading guide (X2).

---

## (D) Disagreements between personas, and rulings

**D1. Is the hero GIF good enough?** P4: "looks *designed*, not like a Gradio demo. Caught my
eye." X2: "Fine as-is; a 90 s narrated walkthrough would serve recruiters" (NICE). P3
[VERIFIED frame sheet + layout math]: the map is never in frame; the caption over-promises.
**Ruling [MERGER]:** both are right about different things — the GIF establishes "real
product" in a second, and it fails to show the product's central surface. P3's evidence is
measured, not impressionistic; re-record (A3). Keep the caption idea, keep the meeting PNG as
the hero still.

**D2. Where does the "Reproduce the three claims" block belong?** P1, P4, X1, X2 praise it at
the top ("best thing in the repo for me" — P1). P3 [JUDGMENT] would put a two-sentence pitch
and the demo link first, commands after ("three bash blocks before I've been told what the
thing is"). X2 notes the "three claims" are never enumerated. **Ruling:** keep it on the first
screen, but after a 3-sentence pitch + demo link + byline, and label each command with the
claim it proves (see F).

**D3. Severity of the first-run warning.** X1: MUST ("contradicts the reproducibility
pitch"). P1: GOOD ("reads like a misconfiguration"). **Ruling:** GOOD-top (B1). It does not
stop anyone from advancing, but it is a one-line fix and it is the first output every
verifier sees — do it in the same PR as A1.

**D4. How to lead the ML story.** P2 wants N1/N2 as the headline research finding and a
research-shape summary. X2 warns story C ("negative-result ML research") "is the story most
likely to *misfire* with recruiters ('four phases, nothing shipped')" and should be "presented
as a section titled by its result." P4 read the negatives as failure. **Ruling:** not a
conflict once split by audience — the README gets one paragraph titled by its result ("four
learned arms beat the baseline on wins; none was adopted; here is why the gate is right"),
and `docs/ml-program.md` carries N1/N2 as the headline for researchers (A6).

**D5. The tagline.** P4: "the best sentence in the repo." P3: it leads with *how it was
built*, hook buried one clause deep. X2: "being built" says unfinished; the second clause is
the pitch but subordinate. **Ruling:** keep both ideas; reorder product-first, process-second;
drop "being built"; give it a byline. F carries a proposal.

**D6. The reading guide.** P2: "the project's best front door and should be closer to the
top." X1/X2/P3: 3× its advertised length; the README should not depend on its glossary; the
title "over-promises, which is exactly the failure mode the project otherwise polices."
**Ruling:** both — its §1 numbers table and §3 cross-tab move UP into the README (A6); the
document itself is retitled/split (B3).

**D7. Process ceremony: asset or theatre?** P2 [JUDGMENT] reads owner ratification-by-merge,
locked decisions, ledgers L1–L10, "the two-owner gate" as "process theatre for a one-person
project" and the flip bar as "close to unpassable by construction" (quoting the project's own
input audit). P1, P4, X2 read the same protocol as the differentiated 2026 story ("Directed
300+ AI-agent PRs against written contracts with CI-enforced architecture … is a story I can
sell"). **Ruling:** the protocol is the asset when explained as an agent-direction discipline
(A5, B5) and a liability when it leaks unexplained into outsider docs (A2). The fix is
framing, not removing the process. P2's sharper point — "strong on measurement, weak on
knowing when to stop building measurement" — is unrebutted by anyone and belongs in the "what
I learned" page (B11) as an owned lesson, not hidden.

**D8. CONTRIBUTING's "pull requests are not the workflow."** X1: "may alienate
open-source-minded readers." P4/X2: reads as confidence, coherent with the thesis. **Ruling:**
keep; it is one of the clearest statements of the workflow in the repo.

**D9. Volume of meta-artifacts.** P1/P4: reads as volume, the README never says which 5% to
read. P2: "apparatus-to-result ratio" — ~29k LOC training + 26k tests + 17k experiments around
a 19-weight champion. X2: the repo "tells story C by *volume*." **Ruling:** consensus, not a
disagreement — the answer is navigation (B12, B3), a results page (A6), and owning the ratio
in B11; nobody recommends deleting the record.

---

## (E) The project's genuine strengths as a portfolio piece

All six reads converge on these; every one is [VERIFIED] by at least one persona.

1. **The front-door claims reproduce, offline, in seconds.** Determinism run-twice
   `diff -q` silent (~0.5 s total; P1, P2, X1, X2 all ran it); `verify_samples.sh` 100/100
   in ~3.5 s (P2, X1); the demo bundle builds in ~4–5 s and plays with no API (P3, X1);
   `check_doc_facts.py` cross-checks README numbers against manifests and the lever registry
   (X1). X1: "unusually strong for a portfolio repo and is the single best thing this project
   has going for it."
2. **Architecture enforced by tooling, and it is real.** Four import-linter contracts (4
   kept, 0 broken — P1 ran it), `mypy --strict`, a planted-leak test that asserts the linter
   rejects a bad import, a Hypothesis recursive leak scan, whole-replay determinism tests;
   `scripts/check.sh` == CI; SHA-pinned actions with least-privilege token and a comment
   explaining the campaign-tier split ("that is a platform engineer's comment" — P1).
   `engine/tick.py` is a pure function over frozen dataclasses with a per-tick state hash.
3. **The meeting view + Mind inspector.** Reactive accusation chain, per-turn typed
   observations, ballots with confidence and rationale, and the literal prompt/response with
   token counts and model id one click away. P3: "a better LLM-agent debugging surface than
   most commercial agent tools ship"; firewall-safe visual grammar (identity ≠ guilt) is "a
   design decision I'd hire for." Design intentionality is documented (frontend/CLAUDE.md,
   tokens.ts with a test, Storybook, code-split Pixi) — the UI does not read as templated.
4. **Eval hygiene above most published LLM-agent evals.** P2 verified that pre-registration
   (PR #298, 07-19) precedes measurement (#317, 07-31) precedes ruling (#318, 08-01) in git;
   `paired_stats.py` (stdlib exact McNemar + Wilson) reproduces the guide's cells exactly; the
   vent-sighting 2×2 (68/2 vs 10/21) reproduces from a committed JSON in 20 lines; same-seed
   comparators; "UNRESOLVABLE" as an outcome class; additive errata; `eval/watchability.py`
   states "SELECTION-ONLY … NEVER a training reward" with Goodhart citations.
5. **Intellectual honesty that no persona doubted.** "General social deduction: NOT
   demonstrated. This is the qualification the project's credibility rests on volunteering."
   (reading-guide §3); the three reproducibility scopes kept apart, the third "designed for,
   not yet confirmed"; NO-FLIP ×2 with the losing evidence committed; "It did not ship a
   default policy change, and that is the result, not a footnote." P1: for a senior role this
   is "a strong signal about how this person will report status to me."
6. **The workflow story with receipts.** 321 contracts ↔ 321 byte-mirrored generated prompts;
   AGENTS.md; the PR template; "coordination:" re-anchoring commits; co-author trailers naming
   model versions on ~90% of commits; Claude-vs-Codex reconciled audits; a CONTRIBUTING that
   says the quiet part. P4: "a differentiated, 2026-relevant, hiring-manager-friendly story —
   it's the thing that would make me take the meeting."
7. **The substrate is a usable research environment** (P2): deterministic replays with
   per-tick SHA-256, an enforced firewall, meeting records with typed claims/observations/
   `reply_to` chains/contradiction flags, every LLM call logged, 100 committed games with
   MANIFEST provenance. "A better research artifact than most 'LLM Werewolf' repos."
8. **The best-written passages already exist** — README:3 tagline, README:41–52 "What this
   is", "Three load-bearing decisions", "Three reproducibility scopes", the Architecture-notes
   bullet map, docs/architecture.md, reading-guide §1 table and §3, the tour copy and picker
   blurbs ("The emergency button, pressed with no body ever found: the table has to argue from
   absence alone." — P3: "this is how the whole README should sound"). The fix is editing and
   reordering, not writing from scratch.

---

## (F) Proposed front door plan

### F1. README above the fold (one screen + one scroll)

```
# AiLibi — LLM social deduction behind an observation firewall, built by directing AI coding agents
  by Daniel Keinan · code by Claude Code / Codex agents · MIT · [CI badge] [Python 3.11] · May–Aug 2026, solo
  ▶ Live demo (static bundle on GitHub Pages)   ·   [meeting PNG as hero still]   ·   [re-recorded GIF or MP4]

## Sixty seconds: what you are looking at
  3 sentences: nine LLM agents move, get killed, meet, accuse and vote; the two impostors
  know each other, the seven crewmates reason in the dark; the spectator lets you open any
  agent's mind (prompt, response, memory, beliefs). Name pun in one clause.

## At a glance
  Stack · 877 commits / 350 merged PRs / 321 contracts / 19 phases · 100 committed replays ·
  ~4.6k tests · zero firewall violations · status: active, phase 19 closed 2026-08-18, next
  phase under decision.

## Verify it yourself in one minute       (the existing three commands, each labelled with the
                                           claim it proves: byte-identical replay / 100 samples
                                           reconstruct / the demo is a static directory)

## How it was built — who did what         (the 5-step loop; the human/agent split in ~120
                                           words; 3 links: one contract → its prompt → the PR;
                                           how to verify agent authorship in git)

## What it is                              (three load-bearing decisions; the as-built layering
                                           diagram; link to docs/architecture.md)

## What the measurements said              (results table lifted from reading-guide §1, each
                                           row with its committed source; the 2×2 cross-tab;
                                           one paragraph titled by its result on the ML program)

## What I learned                          (6–10 bullets; link to docs/lessons.md)

## Status & history                        (2 lines + phase table 0–19, one row each, each row
                                           linking its close audit; narrative in docs/history.md)

## Run it                                  (setup / spectator / tournament / providers; clone
                                           caveat = one line + link)

## Architecture notes · Docs index · Reading guide · Glossary
```

Everything currently at README lines 84, 107, 149, 133 and the ~150-word clone caveat leaves
the README: phase narrative → `docs/history.md`; lever provenance → `replays/samples/*/
MANIFEST.md`; portability and clone notes → `docs/artifacts.md`; ML detail →
`docs/ml-program.md`; vocabulary → `docs/glossary.md`; audit navigation → `audits/README.md`.

### F2. Repo description paragraph (README top; trimmed for GitHub About)

X2 §6a, adopted: *"**AiLibi** is a deterministic Among-Us-style social-deduction simulator
where LLM agents witness, remember, accuse and vote under an enforced observation firewall —
and it was built almost entirely by AI coding agents. I (Daniel Keinan) wrote every task
contract, review gate and audit ruling; Claude Code and Codex agents wrote the code: 350
merged PRs across 19 phases, every one merged green through the same gate (import-linter
firewall, mypy --strict, a recursive leak test, byte-identical replay determinism), zero
firewall violations, and a four-phase ML program that was pre-registered, measured, and —
when its learned movers beat the baseline on wins but failed the referee — honestly *not*
shipped. Watch a curated 9-player game in the hosted spectator, or reproduce the determinism
claim offline in under a minute."*

GitHub About (≤350 chars) and topics: as in A4.

### F3. Demo hosting

- Add `.github/workflows/pages.yml` (~15 lines): on push to `main`, run
  `uv run python scripts/build_demo_bundle.py`, upload `frontend/dist/demo-bundle`, deploy to
  Pages. The artifact already has a relative asset base and an e2e spec that runs against it
  with `/api` blocked (`frontend/e2e/bundle.spec.ts`), so the trust boundary in
  `docs/deployment.md` is already argued.
- Before the first deploy: fix the Tournament-tab 404 dump (static-mode empty state: "The demo
  bundle ships the featured games only; the eval dashboard needs a tournament report — see the
  repo"), make the picker header truthful in bundle mode, expand "4p1i / 9p2i" once, print a
  repo-relative path in the bundle README, and consider baking the 9p2i tournament report so
  the Dashboard is populated (P3).
- Set the Pages URL as the GitHub homepage and README line 1.

### F4. Media

- Keep `docs/media/spectator-meeting.png` as the hero still (unanimous "money shot").
- Re-record `spectator-journey.gif` at ≥1440×900 so the map with moving tokens, one kill and
  the meeting auto-pause are all in frame; keep the "transport stops itself" beat; captions
  cut to one sentence each. Optionally ship an MP4/WebM beside it (GitHub renders video; no
  palette crush at 640 px).
- Add one as-built architecture image (layering + the firewall arrow) — SVG from the ASCII in
  `docs/architecture.md`; caption `DESIGN.md` §1.1 as the *target* diagram.
- NICE: a 90-second narrated walkthrough (seed 2 game + one contract → PR).

### F5. Authorship statement (template, ~120 words, first person)

> I'm Daniel Keinan. I built AiLibi solo between May and August 2026 by directing AI coding
> agents (Claude Code, and Codex for review/audit) against written task contracts. I wrote
> the 321 contracts in `tasks/`, the standing rules in `AGENTS.md`, the review gates and the
> audit rulings; I did not write production code by hand. The agents wrote every coding PR
> (350 merged) and most of the audits; agent commits are authored "Claude" with a
> Co-Authored-By trailer naming the model version, and every PR was opened from a
> `claude/…` branch and merged only after `scripts/check.sh` — the same gate CI runs — was
> green. Here is one contract → its generated prompt → the PR it produced: [links]. The
> "external audits" cited in the docs are AI auditors I commissioned, not third parties.

### F6. Sequencing (all cheap; one afternoon for A1–A5, a day for A6)

1. A4 (GitHub About/topics/badge/byline) — five minutes, no code.
2. A3 (Pages workflow + bundle empty-state fixes + GIF re-record).
3. A1 + A2 + A5 in one README PR, creating `docs/history.md`, `docs/glossary.md`,
   `docs/artifacts.md`, `audits/README.md`; B1 (prompt-set warning) and B8 (prose pass) ride
   along.
4. A6 (`docs/ml-program.md` + README results table), then B3 (reading-guide split), B4
   (architecture link/diagram), B5, B6, B9.
5. B11 "what I learned" — the one thing only the human can write, and the thing every
   hiring-manager persona said they would ask about on the call.
