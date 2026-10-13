# AiLibi as a portfolio project — the technical-recruiter / generalist skim (3–5 min, laptop)

Persona: technical recruiter / generalist. Budget: ~4 minutes on the GitHub landing page.
Read: README.md (all of it, at skim speed), docs/reading-guide.md §1–2, CONTRIBUTING.md,
LICENSE, the top-level tree, git log stats, GitHub About metadata (`gh repo view`).
Everything below is [VERIFIED] unless marked [JUDGMENT]. I did not open code.

Repo snapshot at read time (2026-08-18) [VERIFIED]:
- 877 commits, 84 active days, May 1 → Aug 18 2026 (~3.5 months). PRs numbered up to #350.
- Commit authorship: `dkdan10` 355, `Daniel Keinan` 211 (same person, two identities),
  `Claude <noreply@anthropic.com>` 310, `ci repro` 1. The most recent commit on `main` is
  authored "Claude".
- 1,687 tracked files: 510 .md, 383 .py, 376 .jsonl, 145 .json, 62 .j2, 48 .tsx, 25 .ts.
  Markdown outnumbers Python. `replays/` is 221 MB.
- Top level: 26 entries incl. AGENTS.md, AGENT_IMPLEMENTATION.md (779 lines), DESIGN.md
  (1,054 lines), 80 files in `audits/`, 24 in `tasks/`, 321 in `agent_prompts/`.
- **GitHub About box: description = "" (empty), topics = none, homepage = none, 0 stars,
  0 forks.** (`gh repo view dkdan10/AiLibi --json description,repositoryTopics,...`)
- README: 248 lines / 3,833 words / 81 em-dashes / zero badges / zero author name.
- All 24 relative links in README, all in reading-guide §1–2 and CONTRIBUTING resolve.
  Both media files exist (GIF 640×410, 114 frames, 1.4 MB; PNG 192 KB). No dead links.

---

## (1) What I think this project IS, in two sentences

A solo developer built an Among-Us-style social-deduction simulator where AI agents move
around a map, get murdered, hold meetings, and vote — deterministic engine, LLM-driven
meeting reasoning, a polished replay viewer — and used it as a testbed for agent reasoning
under hidden information. The bigger story is *how* it was built: ~300+ pull requests were
each written by an AI coding agent from a written task contract the human authored, with
architecture enforced by CI (import boundaries, strict typing, a "no-cheating" leak test,
byte-identical replays) instead of trust.

That is the pitch I could give a hiring manager. Note that I got the second sentence from
the tagline + "What this is" — I did NOT get it from the Project status section, which
actively fought it.

---

## (2) First impressions, minute by minute

**0:00–0:45 — Title, tagline, GIF, screenshot.**
- "AiLibi" — cute name (alibi + AI); no subtitle explaining the pun, and the About box is
  empty, so on the repo card there is literally nothing but the name.
- Tagline blockquote: *"An Among-Us-style social-deduction simulator being built almost
  entirely by AI coding agents under a strict review protocol — and a working example of
  how to keep architecture coherent across many agent-authored pull requests."* — Strong.
  Two ideas, both legible to a non-specialist. This is the best sentence in the repo. [JUDGMENT]
- The GIF: cream/ink UI, a replay list with editorial blurbs, a meeting screen, a timeline.
  It looks *designed*, not like a Gradio demo. Caught my eye. It is small (640 px) and
  dithered, so at laptop zoom I could not read the text inside it — but I could tell it is a
  real product UI. [VERIFIED by frame extraction]
- The PNG screenshot is the winner: "Accusation chain & transcript", "Ballots (8)" with
  confidence bars and a "✓ CORRECT" pill, a "Mind inspector" rail, an event timeline with
  K/M/V markers. A recruiter instantly gets "these are AI players accusing each other and
  voting, and I can inspect their minds." That single image carries more than the next
  2,000 words.
- The two italic captions are long (58 and 87 words), full of insider nouns ("featured
  strip", "seed 2, tick 7", "p-1 accuses p-4", "the shippable static bundle"). I skimmed
  them; they read like alt-text for someone who already knows the product.

**0:45–1:30 — "Reproduce the three claims above" code block.**
- Positive: it signals "you can check this yourself in three commands." Even without
  running it, "the same seed twice, byte-identical replay JSONL" and "Free, offline, no API
  key" are recruiter-legible proof points.
- Negative: the comment *"re-using one silently doubled per-seed files in Phase 4"* is an
  insider war story that means nothing to me and takes up two lines above the fold.
- Then a paragraph about building a "static directory with no API process in it" — I skipped.

**1:30–2:30 — "What this is" + "How this is being built".**
- "AiLibi is two things at once." — good framing. Bold lead-ins, short paragraphs. The
  numbers land: *"300+ merged agent-authored PRs … every one of them merged green through
  the same full gate, and zero observation-firewall violations."*
- Small hedge that reads oddly: *"the live count is on GitHub, deliberately not re-pinned
  here"* — I don't know why you're telling me that; it sounds defensive.
- The five-step loop (author contract → generate prompt → dispatch agent → review → checkpoint)
  is the clearest thing in the README and the thing I'd repeat to a hiring manager. Linking a
  real 300-line contract and its generated prompt is a nice "here's the receipt" move.
- "New here? docs/reading-guide.md is the outsider's five minutes" — noticed, appreciated,
  but I'd never leave the README on a first skim.

**2:30–3:15 — "Three load-bearing decisions".**
- Skimmed the bold sentences: tick-based deterministic engine + observation firewall;
  two-tier reasoning; structured memory. I understand "agents can't peek at hidden state
  because the import graph physically forbids it" — that's a nice line to repeat.
- Type names (`ObservationPacket`, `PublicMapView`, `ActionIntent`) are fine in a code
  section; the paragraph is dense but I could see it's for engineers, not me.

**3:15–4:00 — "Project status". This is where I stopped reading.**
- The first paragraph is one 135-word sentence with nested parentheses. The paragraph
  under the table is **506 words, one paragraph, 35 opening parentheses**. Sample:
  *"…closed 2026-08-01 with no mover flip: every learned arm keeps a real win edge over
  the same-seed scripted FSM (+0.12 to +0.30) yet fails the baseline-6 conviction-economy
  referee, so the scripted FSM stays the default mover, the learned champion stays opt-in,
  and baseline 6 (the 18.12 meeting-layer adopting record) stands as the ladder tip"*
- I do not know what a "mover", a "conviction-economy referee", a "ladder tip", an
  "adopting record", a "canary denominator", "graduated CREW-ONLY", "NO-FLIP", or "routed to
  the owner" are. Nothing on the page defines them. The reading guide's glossary (§4) is
  where they live, but I'm on the README.
- Worse for the audience: on a literal read, the status reads as a run of negatives —
  *"closed … with no mover flip"*, *"closed 2026-08-18 with nothing recorded"*, *"zero of the
  fourteen pre-registered emergence rulings demonstrated"*, *"no crew adoption"*. Insiders
  read that as scientific honesty; a recruiter reads "the last two phases didn't work."
  [JUDGMENT — but that is how I read it on first pass, and I had to go to reading-guide
  §1 "The honesty culture" to learn it's meant as a feature.]
- The phase table (0–14) is fine and skimmable; it stops at 14 and hands off to the wall.

**4:00–4:30 — scrolled the rest by headings.**
- "Reproduce a game", "Watch a replay", "Run a tournament & read the metrics", "Setup",
  "Architecture notes" — clear headings, good sectioning. The Architecture-notes bullet
  list (`engine/`, `observation/`, `agents/` …) is exactly the "tell me the shape" thing
  a generalist wants; I would move a two-line version of it up.
- The "Watch a replay" body paragraph is 234 words about "the Task-18.12 adopting record
  for baseline 6 … the roll-call round, the endpoint-band whereabouts exemption, the
  vent-placement contradiction variant (flag-minting plus the absent-set widening)…" — I
  bounced off it inside a section whose heading promised "watch a replay".
- Never found: the author's name, a contact/LinkedIn/site, a stack line, a start date, a
  CI badge, a "what I learned" or "why". LICENSE says "Daniel Keinan"; README says "the
  human", "the owner". [VERIFIED: README contains no author name.]

**CONTRIBUTING.md (30 seconds):** clear and unusually candid — *"issues are welcome, pull
requests are not the workflow."* Explains why in plain English. Good signal of someone who
thinks about process. Would not put off a recruiter. LICENSE: MIT, 2026, Daniel Keinan — fine.

**reading-guide §1–2 (60 seconds, over budget):** §1 is what the README's status section
should have been: a numbers table with "Committed source" column, and a short "honesty
culture" paragraph that explains NO-FLIP as a virtue. §2's featured-replay table with
spoiler-free blurbs ("the most Among-Us moment in the corpus") is charming and legible.
But its opener still uses the idiom without defining it ("baseline-6 adopting record"),
and it cites `audits/...:719`-style line refs a generalist will never follow.

---

## (3) Strongest three / weakest three — FOR THIS AUDIENCE

Strongest:
1. **The tagline + the meeting screenshot.** Together they answer "what is it" and "does it
   look real" in under 20 seconds. The UI looks like a shipped product, not a notebook.
2. **The workflow story with receipts.** "300+ agent-authored PRs, each from a written
   contract, CI-enforced architecture, zero firewall violations, here's a contract and its
   generated prompt." That is a differentiated, 2026-relevant, hiring-manager-friendly story
   — it's the thing that would make me take the meeting.
3. **Verifiability posture.** Three offline commands to reproduce three claims; every number
   in reading-guide §1 points at a committed file; a CONTRIBUTING that says the quiet part.
   Even without running anything, the *shape* of it reads as credible.

Weakest:
1. **The "Project status" wall (README lines 84 and 107).** One 135-word sentence and one
   506-word paragraph in an undefined private vocabulary, whose surface reading is "the last
   two phases produced nothing." It sits at exactly the point in the page where a skimmer
   decides whether to keep going, and it is the section a recruiter would most naturally
   read ("what state is it in?"). It also lands the strongest AI-generated-prose smell on
   the page: chained em-dashes, "deliberately", "the honest caveat", "fails loud", "load-
   bearing", 81 em-dashes total.
2. **No human, no About.** Empty GitHub description, no topics, no author name or link in
   the README, "the owner"/"the human" as the only references to a person, and the latest
   commit on main authored "Claude". For a recruiter trying to attach a project to a
   candidate this is a real gap — and combined with the prose style it invites the "did a
   person actually drive this?" question the project's whole thesis is supposed to answer.
3. **Signal-to-noise for a generalist.** Insider idiom leaks everywhere, including into the
   hero captions and the "Watch a replay" body ("adopting record", "graduated CREW-ONLY",
   "13 graduated levers", "ladder tip"), and there is no one-line stack, no timeline, no
   "why I built this". Markdown files outnumber Python files (510 vs 383) and `audits/`
   has 80 files — impressive discipline, but the landing page never tells me which 3 to
   care about, so it reads as volume rather than signal.

---

## (4) Specific lines that helped / hurt

Helped:
- README:3 tagline (quoted above). Best line in the repo.
- README:47 *"The product is a research environment for studying agent reasoning under
  hidden information — not a game with AI players bolted on."*
- README:49 *"Every coding PR was opened by an AI coding agent against a task contract
  authored by a human. Architecture is enforced by tooling — import-linter, `mypy --strict`,
  a recursive observation leak test, byte-identical replay determinism."*
- README:53–63 the five-step loop; README:65–68 the linked contract + generated prompt.
- README:74 *"an agent physically cannot read the hidden state it is supposed to deduce"*
  (reading-guide §1 phrasing) / README's *"`agents/` cannot import `engine/`, directly or
  transitively (import-linter enforced…)"*.
- README:234–246 the `engine/ observation/ agents/ …` bullet map.
- CONTRIBUTING:3–4 *"issues are welcome, pull requests are not the workflow."*
- reading-guide:29–41 the numbers table with a "Committed source" column.
- reading-guide:44–52 "The honesty culture — the strongest single asset" — this paragraph
  is what turns "nothing recorded" from a red flag into a selling point; it belongs (short
  form) in the README.
- reading-guide §2 featured table blurbs — human, spoiler-free, fun.

Hurt:
- README:84 (135-word sentence) and README:107 (506 words, 35 parentheticals): "no mover
  flip", "conviction-economy referee", "ladder tip", "adopting record", "canary
  denominator", "graduated CREW-ONLY", "starved-economy shape", "screening-tier shortlist",
  "two-axis owner ruling: NO-FLIP", "routed to the owner", "N1/N2".
- README:84 / 107 *"closed 2026-08-18 with nothing recorded"* — reads as failure to an
  outsider.
- README:148 (234 words) *"…the roll-call round, the endpoint-band whereabouts exemption,
  the vent-placement contradiction variant (flag-minting plus the absent-set widening), and
  the absence prior all made unconditional beside the nine levers already retired, while the
  impostor-answer arm (`impostor_roll_call`) did not ship…"* — inside "Watch a replay".
- README:19–20 comment *"re-using one silently doubled per-seed files in Phase 4"* — insider
  anecdote above the fold.
- README:49 *"the live count is on GitHub, deliberately not re-pinned here"* — defensive hedge.
- README:133 *"until an owner-assisted Darwin-arm64 run (the recorded failure host)
  reproduces the pinned digest … (Task 19.3)"* — fine for engineers, noise for me.
- README:230 the clone-size caveat paragraph — 200 words about `--filter=blob:none` and
  `filter-repo` in the Setup section; a generalist just wants "clone, run, done".
- Captions under both images: too long, insider nouns.
- Repeated idiom words: "baseline" ×19, "substrate" ×9, "canonical" ×5, "graduated" ×5,
  "referee" ×4, "ladder tip" ×4, "honest" ×4, "adopting record" ×3, "deliberately" ×3.
- No badges (CI / license / Python) — minor, but every recruiter uses them as a 1-second
  health check.
- Empty GitHub description + no topics [VERIFIED via gh]. On search results / profile
  pinned cards the project shows as just "AiLibi".

---

## (5) What I could verify vs. what I took on faith

Verified myself in the budget:
- All README/guide/CONTRIBUTING links resolve; both images exist and are real UI captures.
- The scale claims are consistent with the git log: 877 commits, PRs to #350, 3.5-month
  arc, 80 audits, 24 phase docs, 321 generated prompts, 100 sample replays under
  `replays/samples/{4p1i,9p2i}`.
- The "built by AI agents" story is visible in authorship: 310 commits by "Claude", PR
  merges by dkdan10, "task 19.28: the phase close (owner) (#350)"-style titles.
- MIT license, 2026, Daniel Keinan.
- The persona would NOT run `scripts/setup_env.sh` etc. — but the fact that the three
  commands are offline and need no API key is stated clearly, which is the part a
  recruiter can relay.

Taken on faith:
- "300+ merged agent-authored PRs … every one merged green", "zero observation-firewall
  violations", the 34%/30% impostor win rates, the 4,531-test gate — I can see where they
  say the numbers live but I would not check.
- Everything in the Project-status wall (I couldn't parse it, so I couldn't judge it).
- That the "honesty culture" is real rather than rhetorical — reading-guide §1 makes a
  persuasive case, but only if you get there.

---

## (6) Would I advance / take the meeting / star?

- **Take the meeting: yes** — on the strength of the tagline, the screenshot, and the
  workflow story. "Directed 300+ AI-agent PRs against written contracts with CI-enforced
  architecture, in 3.5 months, solo" is a story I can sell to a hiring manager for any
  agentic-engineering / AI-tooling / platform role. [JUDGMENT]
- **Advance the candidate: yes, with a note** — "strong builder + process thinker; README
  needs an editor; ask them to explain Phase 18 in plain English in the screen."
- **Star the repo: probably yes** on the screenshot; would not have if I'd landed on the
  status section first.

**The single change that would most raise it:** replace README "Project status" (lines
82–107) with a ~120-word plain-English paragraph — *"Started May 2026. MVP done in phases
0–5. Phases 6–19 pushed how well the agents reason and added a machine-learned tactical
policy; the learned policies beat the scripted one on wins but I kept the scripted one as
default because they failed my pre-registered evidence-quality bar — I record misses as
findings rather than moving the bar. Details: audits/…"* — and move the 500-word history
into `docs/` or the reading guide. Second-closest: fill in the GitHub About/description +
topics and put a name + link at the top of the README.

---

## (7) MUST / GOOD / NICE — for the recruiter / generalist audience

MUST (blocks landing with this audience):
- **Rewrite README "Project status" (lines 82–107) in plain English, ≤150 words, no
  undefined idiom.** Say what "no flip / nothing recorded" *means* (a bar was pre-registered
  and the honest answer was "not yet") in one sentence, or a recruiter reads it as failure.
  Move the phase-by-phase 15–19 history to a `docs/history.md` or the reading guide.
- **Fill in the GitHub About box** (description ≈ the tagline; topics like `multi-agent`,
  `llm`, `simulation`, `among-us`, `agentic-workflow`, `python`, `react`) and add a
  homepage if the static demo bundle is ever hosted. [VERIFIED empty today.]
- **Put a person on the page.** Author name + one link (GitHub profile / site / LinkedIn)
  near the top; "the owner"/"the human" → "I / Daniel". This also defuses the
  "AI-generated repo, who actually did this?" reflex that the prose style otherwise triggers.

GOOD (materially strengthens):
- A 3–4 line **"At a glance" block** right under the tagline: stack (Python 3.11 · FastAPI ·
  React/Vite/PixiJS · Hypothesis · mypy --strict), timeline (May–Aug 2026, solo), scale
  (877 commits / 350 PRs / 100 committed replays), status (v0.1, MVP complete, active).
- **Shorten the two image captions** to one sentence each; keep the "the transport stops
  itself at a meeting" idea, drop "featured strip / shippable static bundle / seed 2 tick 7".
- **Cut the "Watch a replay" body** (line 148) to two sentences + a link; the
  graduated-levers inventory belongs in the sample-set MANIFEST it already cites.
- **Move the clone-size caveat** (line 230) and the Darwin-arm64 portability paragraph
  (line 133) out of the main flow into `docs/` with a one-line pointer.
- **Add badges** (CI, license, Python 3.11) — a one-second health check recruiters actually use.
- **Bring the reading-guide §1 "honesty culture" paragraph (short form) into the README** —
  it is the best framing of the project's distinctive value and it currently lives one click
  away, below where the skimmer stopped.
- **Prose pass for AI-smell**: fewer em-dashes (81), fewer "deliberately/honest/fails
  loud/load-bearing", shorter sentences. The content is credible; the cadence undercuts it.

NICE:
- A higher-resolution / less-dithered hero GIF (640 px is soft on a laptop; the PNG is
  fine) or an MP4/WebP.
- One line under the title explaining the name ("alibi + AI").
- A "why I built this / what I learned about directing agents" 5-line section — recruiters
  and hiring managers love it, and it's the one thing here only the human can write.
- Consider whether the top level needs AGENTS.md *and* AGENT_IMPLEMENTATION.md *and*
  DESIGN.md as siblings of README — a generalist can't tell which is current; a `docs/`
  fold with README pointers would read cleaner.
- Optional: set the "Claude" commit author to a clearly labelled bot identity or mention
  in README that agent commits are attributed to "Claude" on purpose — currently it's
  unexplained.
