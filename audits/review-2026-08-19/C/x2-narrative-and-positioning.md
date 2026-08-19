# AiLibi — Narrative & Positioning review (portfolio-perception track, X2)

Reviewer stance: an outsider who did not build this, reading it the way a hiring manager,
a senior engineer, a researcher, a recruiter, and another AI-native builder would.
Read-only. Everything tagged [VERIFIED] I read or ran on this checkout (main @ b809b19c,
2026-08-18); [JUDGMENT] is my inference.

Inputs read [VERIFIED]: `README.md` (248 lines / 3,833 words), `docs/reading-guide.md`
(378 lines / 3,239 words), `docs/architecture.md`, `AGENTS.md`, `CONTRIBUTING.md`, top of
`DESIGN.md`, `tasks/post-phase-14-plan.md`, headers of `audits/audit-phase-18-close.md`,
`audits/audit-phase-19-close.md`, `audits/audit-phase-19-triage.md`, `docs/media/README.md`,
`docs/deployment.md` (top), `training/README.md` (top), `AGENT_IMPLEMENTATION.md` (top),
`git log` (80 most recent + full author tally), `gh repo view` metadata.

Things I ran [VERIFIED]:
- The README's determinism demo (`run_game.py --seed 42` twice → `diff -q`) prints IDENTICAL,
  in well under a minute, offline. The claim a reader can check fastest is real.
- Author tally over 877 commits (2026-05-01 → 2026-08-18): `dkdan10` 355, `Claude` 310,
  `Daniel Keinan` 211, `ci repro` 1. Co-Authored-By trailers on ~790 commits name the model
  lineage (`Claude Fable 5` 324, `Claude Opus 4.8` 302 incl. 1M-context variants, `Opus 5` 43,
  `Opus 4.7` 3, bare `Claude` 116). Latest merged PR is #350.
- Size for context: ~104k lines non-test Python, ~134k lines Python tests, ~22k lines TS/TSX,
  ~157k lines under `audits/ tasks/ agent_prompts/`; 321 task contracts ↔ 321 generated prompts;
  80 files under `audits/`; 100 committed replays.
- GitHub metadata: description `""`, topics `null`, homepage `""`, `has_pages: false`,
  0 stars / 0 forks. No CI badge in the README (0 shield/badge references).
- Two media assets exist and are recent (2026-08-16): `docs/media/spectator-journey.gif` (1.5 MB),
  `spectator-meeting.png` (190 KB). No hosted demo URL anywhere in the tree.

---

## 0. Executive summary

[JUDGMENT] This repo has an unusually strong story and tells it in the wrong voice. The
strongest, most differentiated 2026 story — *one person directed AI coding agents through
19 phases / 350 PRs / 321 byte-mirrored contracts and kept a deterministic, firewall-enforced
system coherent the whole way* — is present in the README's second paragraph, and then buried
under an internal phase ledger written in the project's own audit idiom ("ladder tip",
"baseline 6", "NO-FLIP", "adopting record", "canary denominator", "conviction-economy referee").
The first 60 seconds are good (GIF, screenshot, three runnable commands); minute two is a
506-word single paragraph about phases 15–19 that no outsider can parse. Meanwhile the
things a portfolio reader looks for first — who built it, a hosted demo, a results table, a
GitHub description/topics — are absent, even though the static demo bundle the project built
specifically for public sharing exists and is documented as "the only sanctioned public
artifact" (`README.md` §"Watch a replay"; `docs/deployment.md`).

The honesty is real and it is the asset. But honesty is currently delivered as apology
("here is the honest caveat", "designed for, not yet confirmed", "NOT demonstrated") without
the positive frame that makes it read as rigor rather than as a project confessing.

---

## 1. What the repo tells by default, in the first 60 seconds [VERIFIED reading of the fold]

Above the fold, in order (`README.md:1–39`):

1. `# AiLibi` — no byline, no one-liner about the *name* (the alibi pun goes unexplained).
2. Blockquote tagline: *"An Among-Us-style social-deduction simulator being built almost
   entirely by AI coding agents under a strict review protocol — and a working example of how
   to keep architecture coherent across many agent-authored pull requests."*
   → Two stories fused in one sentence; present-continuous "being built" says "unfinished";
   the second clause is the actual pitch but is subordinate.
3. GIF + long caption, PNG + long caption. Strong. Captions are specific and confident.
4. `### Reproduce the three claims above` — three commands (determinism, replay integrity,
   spectator). Excellent instinct — but "the three claims above" are not enumerated as claims
   anywhere above; the reader has to reverse-engineer which three sentences count.
5. Then `## What this is` — *"AiLibi is two things at once."* Paragraph 1: the testbed;
   paragraph 2: the workflow experiment with "300+ merged agent-authored PRs … zero
   observation-firewall violations". This is the best 120 words in the file.

So the default story is: **"agent-built simulator, rigorously gated"** — the right story —
told for about 40 seconds. Then `## Project status` (line 84: a 135-word single sentence
with nested parentheses; line 107: a 506-word paragraph) converts the impression from
"disciplined system" to "intensely documented internal research log I am not the audience
for". [JUDGMENT] A recruiter bounces here; a senior engineer skims to `## Setup`; a researcher
is intrigued by the vocabulary but has no glossary yet (it lives in `docs/reading-guide.md` §4).

Net first-60-seconds verdict: the repo tells story A (below) by *declaration*, and story
"C — an internal ML research ledger" by *volume*.

---

## 2. The candidate stories, who each is for, and the evidence for each

### A. "I can direct AI coding agents to build a rigorous, architecturally coherent system at scale"
- Audience: hiring managers and eng leads staffing AI-native teams; other builders; anyone
  evaluating "can this person run agents responsibly". [JUDGMENT] The most valuable and most
  differentiated story in 2026, and the one where the evidence is overwhelming *and* uniquely
  legible in git.
- Evidence [VERIFIED]: `tasks/phase-0..19.md` (321 contracts) ↔ `agent_prompts/` (321
  generated prompts, `generate_prompts.py --check` byte-mirror gate, cited in the 19-close audit
  as "All 321 prompts are in sync"); `AGENTS.md` (the standing rules an agent reads); the
  contract → prompt → PR chain in the log ("task 19.13: proof above the fold + the static demo
  artifact (#343)"); `.github/pull_request_template.md` (Summary / DoD / Decisions /
  Questions); four `import-linter` contracts + `mypy --strict` + leak property test +
  determinism test (`docs/architecture.md` §"Enforced boundaries"); the "coordination:" commits
  between task merges showing the human re-anchoring contracts after each batch; the
  Claude-vs-Codex reconciled audits (`audits/audit-2026-05-15-0225-reconciled.md`,
  `audits/audit-phase-19-triage.md`); `CONTRIBUTING.md`'s "issues are welcome, pull requests
  are not the workflow"; the co-author trailers naming model versions.
- What is missing for it: the human is never named or described at the front door (see §5).

### B. "A deterministic multi-agent reasoning testbed with a real observation firewall"
- Audience: senior engineers, researchers, other builders wanting a substrate.
- Evidence [VERIFIED]: `engine/` pure tick + full-RNG-state hash; `observation/` firewall;
  the run-twice demo (I ran it: IDENTICAL); `scripts/verify_samples.sh`; 100 replays with
  `MANIFEST.md` provenance; `eval/` typed analyzers + the prompt-regression close gate;
  `docs/architecture.md` (146 lines, as-built, with an ASCII layering diagram — the best
  single technical page in the repo); the "Three reproducibility scopes" section that refuses
  to overclaim.
- This is the story that makes A *credible*: the system is not a toy, so directing agents to
  build it is a real feat.

### C. "Honest, pre-registered, negative-result ML research"
- Audience: researchers; ML engineers who care about evaluation discipline. [JUDGMENT] Also
  the story most likely to *misfire* with recruiters ("four phases, nothing shipped").
- Evidence [VERIFIED]: `training/README.md` tier map (keep/freeze/retire, reopening
  checklist), `audits/audit-phase-17-close.md` and `-18-close.md` NO-FLIP titles,
  `audit-phase-18-emergence-preregistration.md`, errata discipline in reports,
  `docs/reading-guide.md` §6 "The honest ML story" (excellent), the N1/N2 findings.
- Right framing: "the gate held under a result nobody wanted" (the reading guide already
  says this at §5 item 3 — that sentence should be at the front door, not the phase ledger).

### D. "A polished spectator product"
- Audience: recruiters, general readers, the "show me" crowd.
- Evidence [VERIFIED]: GIF/PNG, the "Playful" React+PixiJS viewer, guided tour, featured
  strip, meeting pause, finale card, static demo bundle (`scripts/build_demo_bundle.py`),
  Playwright journey (`frontend/e2e/bundle.spec.ts` per `docs/media/README.md`).
- Weakness: not hosted; the frontend had zero tests until Task 19.12 (2026-08-16) per the
  triage; the reading guide itself says "the median game is formulaic; roughly one game in
  eight holds something a human would rewind" (§3, labeled JUDGMENT). D is the *hook*, not
  the story.

Recommended composition: **lead with A, prove it with B, hook with D, and present C as a
section titled by its result** ("What the measurements said: four learned arms beat the
baseline on wins, none was adopted, and here is why the gate is right").

---

## 3. Where the front door dilutes or undercuts its best story (quoted)

MUST-level dilutions:

1. **The phase ledger in `## Project status`.** `README.md:84` (135 words, one sentence) and
   `README.md:107` (506 words, one paragraph) — e.g. *"…closed 2026-07-18: co-adaptation — the ML
   corpus re-recorded at baseline 5 (restoring it as the canonical canary denominator), the
   ballot surrogate re-fit (first GO verdict, training-time-runner tier), and the full
   impostor/crew slate re-run and re-selected under the baseline-5 referee — with the
   evidence-gated default flip ruled FAIL (`utility-es` keeps a +0.16 win edge over the scripted
   FSM but fails the conversion-economy floors; `policy-es` passes the referee at a 0.02 win
   rate)…"* This is audit prose pasted into the README. The table above it stops at Phase 14
   with the note *"The table covers the arc through Phase 14; the paragraph below it carries
   phases 15–19"* — the author knows the paragraph is a table that was never extended.
   [JUDGMENT] This one block does more damage to first impressions than anything else in the
   repo.

2. **Provenance prose inside "Watch a replay".** `README.md:149` (234 words): *"They are the
   Task-18.12 adopting record for baseline 6: the meeting layer graduated **CREW-ONLY** — the
   roll-call round, the endpoint-band whereabouts exemption, the vent-placement contradiction
   variant (flag-minting plus the absent-set widening), and the absence prior all made
   unconditional beside the nine levers already retired, while the impostor-answer arm
   (`impostor_roll_call`) did not ship, so the record was made in a bare environment with that
   toggle OFF"* — a reader who wants to *watch a replay* is handed lever-graduation history.
   The two useful facts (100 replays, two 50-game tournaments, 34%/30% impostor win rate,
   Qwen3.6-27B) are in there and should be the whole paragraph.

3. **Apologising for the clone.** `README.md:220–222` (~150 words) and repeated nearly
   verbatim in `docs/reading-guide.md` §2: *"`--filter=blob:none` is the fast path, and here is
   the honest caveat."* … *"a `filter-repo` pass and a force-push that invalidates every
   existing clone and every commit sha cited in the audits. That is not scheduled."* The
   caveat is correct and one line of it is warranted; three paragraphs of it, in Setup and again
   in the reading guide, foregrounds a housekeeping wart. (Also: `gh api` reports repo size
   ~94 MB; the README says "roughly the 256 MiB the working tree needs" — the two numbers measure
   different things, but a reader sees "256 MiB" and winces.)

4. **Meta-commentary leaking into the pitch.** *"So far: 300+ merged agent-authored PRs — the
   live count is on GitHub, deliberately not re-pinned here"* (`README.md:47`). The
   parenthetical is a note-to-self about a doc-drift fix (triage row 2). Say "350 merged PRs
   (as of 2026-08-18)" or use a badge; do not explain your pinning policy in the headline
   sentence.

5. **The word "owner".** README uses it 3×, the reading guide 5×, the audits constantly
   ("routed to the owner", "the owner's merge is the ratification"), and it is never introduced
   as *the human, Daniel*. An outsider cannot tell whether "owner" is a person, a role, or a
   bot. It is the single most important word for story A and it is undefined.

GOOD-level dilutions:

6. **Jargon before the glossary.** "ladder tip", "adopting record", "graduated lever",
   "canary denominator", "NO-FLIP", "the §1.3 bar", "conviction-economy referee",
   "supply/conversion gauges", "starved-economy shape" all appear in `README.md` before any
   definition; the glossary is `docs/reading-guide.md` §4, one link away, itself 700 words. The
   reading guide even diagnoses this: *"§3.2 item 5 is also the diagnosis that produced this
   guide: the corpus is case law with no glossary."* True — but the fix landed one hop *below*
   the README rather than by removing the idiom from the README.

7. **"The outsider's five minutes"** (`docs/reading-guide.md:1`) is 3,239 words with an
   11-term glossary and a 7-row featured table — a 15-minute read. The title over-promises,
   which is exactly the failure mode the project otherwise polices. Its §1 numbers table,
   however, is the best portfolio asset in the repo and is *not* in the README.

8. **Hedges without the positive frame.** *"General social deduction: NOT demonstrated. This
   is the qualification the project's credibility rests on volunteering."* (reading guide §3);
   *"designed for, not yet confirmed"* (README, twice); *"nothing recorded"* / *"with nothing
   recorded (the ladder tip stands at baseline 6)"* (README status, twice). Each is right. Each
   lands as a confession because the sentence that should precede it — what *was*
   demonstrated, and why the refusal to overclaim is the point — is missing or comes later.

9. **"being built"** in the tagline and *"Everything since has pushed agent-reasoning quality
   on the same substrate"* — the READMe never says what state the project is in for a reader
   (finished? paused? active?). The audits say Phase 19 closed 2026-08-18 and a decision is
   "routed to the owner". Say so in one line: "Active; 19 phases closed; next phase under
   decision."

10. **Small confusions:** *"the default game is 4 players / 1 impostor"* (README §What this
    is) vs the reading guide's *"The served default is the 9-player / 2-impostor set"* — both
    true (CLI default vs spectator default) but adjacent-reading readers see a contradiction.
    `### Reproduce the three claims above` with no enumerated claims. "MVP (phases 0–5) is
    complete" is said three times across README.

What HELPS (keep, and move up):
- The GIF/PNG pair and their captions — specific, no marketing gloss, recorded from the
  shippable artifact (and `docs/media/README.md` explains why; that discipline is itself a
  portfolio point).
- `README.md:41–52` "What this is" — two crisp paragraphs.
- `## Three load-bearing decisions` — crisp, verifiable, linked to ADR-0001.
- `## Architecture notes` — the one-line-per-package list is exactly right.
- `docs/architecture.md` — as-built, short, honest ("`agents/runtime.py` is a TEST-ONLY
  Phase-2 harness — the production agent is …").
- `docs/reading-guide.md` §1 table ("The numbers worth knowing", each with a committed source)
  and §3's 2×2 cross-tab — the single most convincing "we measured ourselves" exhibit.
- `CONTRIBUTING.md` — the clearest statement of the workflow in the repo; also the honest
  "PRs are not the workflow" line reads as confidence, not hostility.
- The `[VERIFIED]`/`[JUDGMENT]` labelling convention, and errata-not-rewrite for records.
- Co-author trailers naming model versions — a free provenance graph in `git log`.

---

## 4. What is missing that portfolio readers expect

| Expected item | Present? [VERIFIED] | Note |
|---|---|---|
| Hosted demo link | **No** (`has_pages: false`, no URL in tree) | The static bundle exists *for this purpose*; `docs/deployment.md`: "exactly one sanctioned way to put AiLibi in front of someone… build the static demo bundle and serve that." Not hosting it is the largest single gap. |
| Author / "built by" line | **No** in README; LICENSE says "Daniel Keinan"; git shows `dkdan10` | See §5. |
| GitHub description / topics / homepage | **No** — all empty | Free, five minutes, first thing a recruiter reads. |
| CI badge | **No** | `ci.yml` exists; the "every PR merged green" claim has no visible badge. |
| 60-second video | Partial — a 15 s GIF (good) | Fine as-is; a 90 s narrated walkthrough would serve recruiters. NICE. |
| Architecture diagram (image) | ASCII only (`docs/architecture.md`; `DESIGN.md` §1.1 diagram is the *target* arch, annotated as not built) | An SVG of the as-built layering + the firewall arrow belongs above the fold. |
| One-page results table | Exists in `docs/reading-guide.md` §1, **not** in README | Lift it. |
| "What I learned" / retrospective | **No** single write-up | The material exists across `training/README.md` §3, reading-guide §1 "honesty culture", triage §1, close audits — nobody will assemble it. |
| Blog post / thread | No | NICE. |
| Contributions-graph story | Implicit; 3 git identities + "Claude" as author (see §5) | A `.mailmap` + one README sentence would fix legibility. |
| Audit index | **No** — 80 files under `audits/`, no `audits/README.md` | The reading guide names three; the other 77 are unnavigable. |
| Project state / roadmap one-liner | Buried in the 506-word paragraph | One line + link to `tasks/post-phase-14-plan.md`. |
| Explanation of the name | No | One clause: "AiLibi — *alibi*, with AI." NICE. |

---

## 5. Authorship legibility — can a reader tell what the human did vs the agents?

[VERIFIED facts]
- Commit authors: `dkdan10` (2 emails) 355, `Daniel Keinan` 211, `Claude` 310. Three
  identities for one human plus "Claude" as first-class author on 35% of commits.
- Co-Authored-By trailers on ~90% of commits name the model *version*.
- README says every *coding* PR was agent-authored against a human-authored contract, and
  the human reviews; `CONTRIBUTING.md` says the same more clearly. The `tasks/` → `agent_prompts/`
  → PR chain is inspectable. "coordination:" commits and "(owner)" tasks show human
  ratification steps.
- Nowhere at the front door: the human's name, or a plain-language sentence of what the
  human personally did (wrote 321 contracts? authored the audits? or were the audits also
  agent-written — `audit-phase-19-input-claude.md` and `-codex.md` clearly are; the triage
  says "Produced by the Phase-18 coordination session" — is that a person or a session?).

[JUDGMENT] Verdict: the *mechanics* of authorship are more legible here than in almost any
agent-built repo I can imagine — but the *narrative* of authorship is absent, and absence
gets read uncharitably ("did the human write anything?", or the opposite, "is this
vibe-coded?"). Currently it reads as **ambiguous**. With one paragraph it becomes an
unambiguous **strength**, because the interesting claim is not "agents wrote the code" but
"a human specified, gated, audited and ruled on 350 PRs and the architecture never broke".
That paragraph must also say what the human did *not* do (write production code by hand),
because that is what makes the rest impressive rather than suspicious.

Also decide the voice. The docs are written in a third-person institutional register ("the
owner", "the operator", "the designer ruling") that suits agents reading a contract and
alienates humans reading a README. The README and reading guide can say "I".

---

## 6. Concrete proposals

### 6a. Proposed one-paragraph repo description (for the README top and, trimmed, the GitHub "About")

> **AiLibi** is a deterministic Among-Us-style social-deduction simulator where LLM agents
> witness, remember, accuse and vote under an enforced observation firewall — and it was built
> almost entirely by AI coding agents. I (Daniel Keinan) wrote every task contract, review
> gate and audit ruling; Claude Code and Codex agents wrote the code: 350 merged PRs across 19
> phases, every one merged green through the same gate (`import-linter` firewall, `mypy
> --strict`, a recursive leak test, byte-identical replay determinism), zero firewall
> violations, and a four-phase ML program that was pre-registered, measured, and — when its
> learned movers beat the baseline on wins but failed the referee — honestly *not* shipped.
> Watch a curated 9-player game in the hosted spectator, or reproduce the determinism claim
> offline in under a minute.

GitHub "About" (≤ 350 chars): *Deterministic social-deduction sim (Among-Us-style) with LLM
agents behind an enforced observation firewall — built by directing AI coding agents against
written contracts: 350 PRs, 19 phases, byte-identical replays, honest negative ML results.*
Topics: `multi-agent`, `llm-agents`, `social-deduction`, `deterministic-simulation`,
`agentic-coding`, `claude-code`, `evaluation`, `python`, `react`.

### 6b. Proposed README above-the-fold outline (headings only, ~1 screen + a scroll)

```
# AiLibi — LLM social deduction behind a firewall, built by directing AI agents
  (one-line byline: by Daniel Keinan · code by Claude Code / Codex agents · MIT · CI badge)
  ▶ Live demo (static bundle on Pages)  ·  15-s GIF  ·  screenshot
## Sixty seconds: what you are looking at            (3 sentences + the GIF caption)
## By the numbers                                    (one table: PRs, contracts, phases, tests,
                                                      firewall violations, replays, win rates,
                                                      citation compliance — each with its source)
## Verify it yourself in one minute                  (the three commands, each labelled with
                                                      the claim it proves)
## How it was built — the human/agent split          (the 5-step loop; who did what; link to
                                                      AGENTS.md, a sample contract + prompt)
## What it is (the testbed)                          (three load-bearing decisions, one
                                                      as-built diagram, link to architecture.md)
## What the measurements said                        (evidence-processing: yes; deception: yes;
                                                      general deduction: not yet — the 2×2;
                                                      the ML program: 4 arms beat baseline, none
                                                      adopted, why the gate is right)
## What I learned                                    (6–10 bullets; link to a longer write-up)
## Status & roadmap                                  (2 lines + link to post-phase-14-plan.md)
## Run it                                            (setup / spectator / tournament / providers)
## Architecture notes · Docs · Reading guide · History (phase table 0–19, one row each)
```

The phase-15–19 paragraphs, the lever-graduation provenance, and the clone-history caveat move
to `docs/history.md` (or extend the phase table) and `docs/artifacts.md` respectively.

---

## 7. MUST / GOOD / NICE

### MUST (blocks the project from landing with its audience)
1. **Rewrite the fold** per §6b: byline + thesis + numbers table + demo link in the first
   screen; move `README.md:84`, `:107`, `:149` (the phase ledger and lever provenance) out of
   the README. [JUDGMENT, high confidence]
2. **Host the static demo bundle** (GitHub Pages or any static host) and link it from line 1.
   The artifact and its trust-boundary doc already exist; `has_pages` is false. [VERIFIED gap]
3. **State authorship in plain language**: name, what the human did (contracts, gates,
   reviews, audit rulings, product direction), what the agents did (all production code, most
   audits), which agents (Claude Code / Codex, per `AGENT_IMPLEMENTATION.md` and the trailers).
   Define "owner" = you at first use, or drop the word in outsider-facing docs.
4. **Fill GitHub metadata**: description, topics, homepage → the demo. [VERIFIED empty]
5. **Reframe the honesty as rigor, not apology**: for each hedge ("NOT demonstrated",
   "designed for, not yet confirmed", "nothing recorded"), lead with what *was* shown and why
   the refusal to overclaim is the discipline. Reduce the clone-size caveat to one line + link.

### GOOD (would materially strengthen)
6. Lift `docs/reading-guide.md` §1 "numbers worth knowing" into the README as the results
   table; add the §3 2×2 cross-tab beside it.
7. An as-built architecture SVG (layering + the firewall arrow), replacing/augmenting the
   ASCII in `docs/architecture.md`; retire or clearly caption `DESIGN.md` §1.1's target diagram.
8. A "What I learned" page (2–3 screens): directing agents at scale (contract byte-mirroring,
   the coordination re-anchoring commits, why PRs from outsiders are refused), what CI could
   and could not catch, the ML negative result and pre-registration, doc-drift as a first-class
   bug (Phase 19). The material exists; it needs assembling once.
9. CI badge; a `## Status` one-liner ("Active. 19 phases closed 2026-08-18; next phase under
   decision — see …").
10. Retitle/trim the reading guide (it is not five minutes) or split: `docs/reading-guide.md`
    (5 real minutes) + `docs/glossary.md` + `docs/audits-index.md`.
11. `audits/README.md` index (80 files; three named as "read first", 77 orphaned).
12. Extend the phase table to 19 with one row each and delete the paragraph form.
13. Consistency nits: `### Reproduce the three claims above` → name the claims; reconcile
    "default game is 4p1i" vs "served default is 9p2i" in one sentence; say "MVP complete"
    once.

### NICE
14. `.mailmap` consolidating `dkdan10` / `Daniel Keinan`; note in the README that "Claude" as
    commit author on ~35% of commits is the dispatch pattern, not a second maintainer.
15. A 90-second narrated video or Loom of the featured seed-2 game + one contract → PR walk.
16. A blog post / thread: "350 PRs, zero hand-written production code, one firewall".
17. Explain the name (AI + alibi) in one clause.
18. A dated phase timeline (`docs/history.md`) with one paragraph per phase and its close audit
    linked — the phase-history content currently in the README belongs there.
19. First-person voice in README and reading guide; keep the institutional register for
    `AGENTS.md`, contracts, and audits where it belongs.

---

Report path:
/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/reports/C/x2-narrative-and-positioning.md
