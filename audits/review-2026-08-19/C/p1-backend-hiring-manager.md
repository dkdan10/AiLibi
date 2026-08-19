# AiLibi — portfolio read as a Senior Backend / Platform Hiring Manager

Persona: 15–20 minutes before a phone screen. Read README, docs/reading-guide.md,
docs/architecture.md, skimmed the tree, opened engine/tick.py, observation/service.py,
llm/client.py, meetings/manager.py (head), CI + scripts/check.sh + .importlinter, one test
file, and ran the README's determinism demo. Read-only. Everything tagged [VERIFIED] I ran
or read; [JUDGMENT] is my inference as this persona.

Actual time spent by the persona (honest budget): ~22 minutes; I would have wanted to stop
at minute ~9 (README "Project status") and only continued because the demo block at the top
had already bought goodwill.

---

## 1. What I think this project IS (two sentences)

A deterministic, replayable Among-Us-style multi-agent simulation (pure tick engine +
observation firewall + LLM-driven meetings + React/PixiJS spectator) that doubles as an
eval harness for agent reasoning under hidden information. Simultaneously — and this is the
part the author is actually selling — a documented, ~300-PR case study in running AI coding
agents against written task contracts with the architecture enforced by tooling
(import-linter, mypy --strict, leak tests, byte-identical replays) rather than by trust.

## 2. First impressions, minute by minute

- **0:00–1:30 — README top.** [VERIFIED] The tagline is one clear sentence. The GIF +
  screenshot with captions are strong: I can see there is a real product with a real UI
  before I read a word of prose. The "Reproduce the three claims above" block immediately
  under it is exactly what I want — three commands, one of them a `diff -q`. Goodwill: high.
- **1:30–3:00 — "What this is" / "How this is being built".** [VERIFIED] Clean, two-part
  framing, five-step loop, two linked artifacts (contract + generated prompt). Reads like a
  competent staff-level engineer wrote it. The claim "zero observation-firewall violations"
  registers as bold — I'll want to see how it's enforced.
- **3:00–4:30 — "Three load-bearing decisions".** [VERIFIED] The best section for my
  audience. Determinism, firewall, two-tier reasoning, structured memory — each with the
  enforcement mechanism named. This is where I decided the author has architectural taste.
- **4:30–9:00 — "Project status".** [VERIFIED] This is where I got lost. Line 84 is one
  ~110-word sentence; line 107 is a single ~600-word paragraph carrying phases 15–19,
  written entirely in an in-house dialect ("baseline 6 (the 18.12 meeting-layer adopting
  record) stands as the ladder tip", "restoring the canonical canary denominator",
  "NO-FLIP", "conversion-economy referee", "the evidence-gated default flip ruled FAIL").
  As an outsider I do not know what a baseline is, what a lever is, what a referee is, or
  why I should care whether something flipped. I skimmed for numbers, found "no mover
  flip" and "nothing recorded", and my honest reaction was: four phases of ML work with
  a null result, described at a level of detail only the author can parse. **This is
  where the persona stops reading the README.** I scrolled to "Architecture notes"
  (good, tight, package-per-bullet) and left.
- **9:00–12:00 — docs/reading-guide.md.** [VERIFIED] The intent is right ("the outsider's
  five minutes") and §1's numbers table with a committed path per number is genuinely
  impressive — I've rarely seen a side project cite its own evidence like this. §3 ("what
  the corpus demonstrates — and what it does not", "General social deduction: NOT
  demonstrated") is the single most credibility-building passage in the repo. But it's
  378 lines, and §4 is an eleven-term glossary of the project's private vocabulary. A
  glossary existing is a tell that the vocabulary is the problem. I read §1–§3, skimmed
  §4, skipped §5–§6.
- **12:00–14:00 — docs/architecture.md.** [VERIFIED] 146 lines, ASCII layering diagram,
  one paragraph per package, an "Enforced boundaries" section naming the four
  import-linter contracts and the tests that back them. This is the document I wanted
  first. Excellent for my audience — I would put a link to it in the first screen of the
  README.
- **14:00–17:00 — tree + CI + source.** [VERIFIED] `.importlinter` has the four contracts;
  `scripts/check.sh` is the one-command gate and CI runs exactly that (actions SHA-pinned,
  `permissions: contents: read` — nice hygiene). engine/tick.py: `advance_tick(state,
  actions, *, game_map, ...) -> tuple[WorldState, list[EngineEvent]]`, frozen dataclasses,
  a clear seven-step loop — this is a real pure engine. llm/client.py: a Protocol with a
  worked "how to add an adapter" sketch — good API taste. observation/service.py: a
  ~50-line comment block before the first function citing "Task 10.14, DESIGN.md §3.4,
  §4.5; audit-2026-06-13-1816 D-D-1", "Codex review, PR #155" — thorough, but this is
  provenance-as-comments and it slows a reader down badly. meetings/manager.py is 3,989
  lines and orchestrator/game.py is 3,193 — big files for a code base this size.
- **17:00–19:00 — try one thing.** [VERIFIED] Ran the run-twice determinism demo: both
  runs 0.24s, `diff -q` silent, replay is 21 JSONL lines with a `state_hash` per tick. Also
  ran `uv run lint-imports` (4 kept, 0 broken) and `tests/test_firewall.py` (9 passed,
  0.66s). It works exactly as advertised. One rough edge: the first thing the script prints
  is a warning — "AILIBI_PROMPT_SET is unset — falling back to the frozen reference set
  'qwen3_5_9b', two generations behind the operational baseline" — which is meaningless to
  a first-time runner and reads like a misconfiguration.
- **19:00–22:00 — over budget.** Glanced at pyproject (pinned deps, mypy strict, a
  provable runtime/dev partition), the PR template (Summary / DoD / Decisions / Questions —
  a good template), tests/ (184 files, ~4,300 test functions, property tests present).

## 3. Strongest three / weakest three, for a backend/platform hiring manager

**Strongest**
1. **Architecture enforced by tooling, and it's real.** [VERIFIED] The firewall claim is
   backed by an import-linter contract, a test that plants a bad import and asserts the
   linter rejects it, a Hypothesis-driven recursive leak scan, and a determinism test that
   diffs whole replays. `check.sh` == CI. This is exactly the "make the invariant
   un-violatable" instinct I hire for.
2. **The reproducibility demo is 30 seconds and it works.** [VERIFIED] Two commands, a
   diff, done. Plus a `verify_samples.sh` that reconstructs 100 committed replays through
   state hashes offline. Most portfolio repos give me a screenshot; this one gives me a
   proof I can run.
3. **Intellectual honesty about results.** [VERIFIED] "General social deduction: NOT
   demonstrated"; the three reproducibility scopes with the third explicitly "designed for,
   not yet confirmed"; a four-phase ML program that "did not ship a default policy change,
   and that is the result, not a footnote". For a senior role, willingness to publish a
   well-measured negative is a strong signal about how this person will report status to
   me.

**Weakest**
1. **The README loses the outsider at "Project status".** [VERIFIED lines 84, 107] Two
   paragraphs of dense in-house vocabulary, hundreds of words each, with no payoff a
   stranger can extract. This is where a busy reader forms the impression "smart but
   can't summarize for an audience" — which is the opposite of what the rest of the repo
   demonstrates. [JUDGMENT] It also unintentionally foregrounds the null ML result over
   the shipped, working system.
2. **Private vocabulary everywhere, including code comments.** [VERIFIED] "ladder tip",
   "adopting record", "graduated lever", "canary denominator", "the 15.18 convention",
   "the two-owner gate", "NO-FLIP", "the §1.3 bar", "conviction economy referee". The
   glossary in reading-guide.md §4 is well done, but the fact that eleven terms need
   defining before an outsider can read the status section is itself the finding.
   Source comments cite task IDs and audit filenames rather than explaining intent in
   plain terms; a new engineer on my team would find that hard to onboard to.
3. **Signal-to-noise / scale of the meta-artifacts.** [VERIFIED] 80 audit files (5.1 MB),
   321 generated prompts (3.3 MB), 24 task files (2.1 MB), 221 MB of replays, some
   4k-line modules. Everything is there for a reason the author can defend, but for a
   15-minute reader it reads as volume, and the README does not tell me which 5% to look
   at (reading-guide.md tries, but it too is long). [JUDGMENT] It also raises the
   question a hiring manager will ask on the call: how much of the *judgment* here is the
   author's vs the agents' — and the repo doesn't yet make that legible (see §7 MUST-3).

## 4. Specific lines that helped and hurt

**Helped**
- README:3 — "An Among-Us-style social-deduction simulator being built almost entirely by
  AI coding agents under a strict review protocol — and a working example of how to keep
  architecture coherent across many agent-authored pull requests." Clear thesis in one line.
- README:13–32 — "Reproduce the three claims above" block. Best thing in the repo for me.
- README:74 — the firewall paragraph: "`agents/` cannot import `engine/`, directly or
  transitively (import-linter enforced, tested with direct- and transitive-leak fixtures)".
  Concrete, checkable, and I checked it.
- README:129 — "'Reproducible' is three different claims here, and the repo keeps them
  apart rather than trading on the strongest one." Exactly the sentence I want a senior
  engineer to write.
- reading-guide.md:39–50 — the numbers table with a committed source per row.
- reading-guide.md:170–171 — "**General social deduction: NOT demonstrated.** This is the
  qualification the project's credibility rests on volunteering."
- architecture.md:11–21 — the ASCII layering diagram; :104–118 "Enforced boundaries".
- llm/client.py docstring — the "Minimum surface a second-provider adapter must implement"
  section. Small thing, shows API design taste.
- .github/workflows/ci.yml — SHA-pinned actions with the tag in a comment, least-privilege
  token, and the comment explaining why the campaign tier is a separate workflow file
  (skipped jobs satisfying required checks). That is a platform engineer's comment.

**Hurt**
- README:84 — "…every learned arm keeps a real win edge over the same-seed scripted FSM
  (+0.12 to +0.30) yet fails the baseline-6 conviction-economy referee, so the scripted FSM
  stays the default mover, the learned champion stays opt-in, and baseline 6 (the 18.12
  meeting-layer adopting record) stands as the ladder tip". Six undefined terms in one
  clause; nested parentheticals; the reader has no anchor.
- README:107 — the ~600-word single paragraph. Sample: "…the meeting-layer package
  graduated CREW-ONLY at the baseline-6 adopting record with the ML corpus re-recorded on
  it (restoring the canonical canary denominator at the new substrate), the
  conviction-economy model landed GO (conversion-label accuracy 0.938 — 90/96 on its own
  conversion labels, never a property of the composed runner)…". I stopped here.
- README:149 — the "Watch a replay" paragraph spends its first ~120 words on provenance
  ("the Task-16.2 locked model, non-thinking — on the `qwen3_6_27b` `v3` prompt set, model
  and prompt registry both unmoved at this record… the roll-call round, the endpoint-band
  whereabouts exemption, the vent-placement contradiction variant (flag-minting plus the
  absent-set widening)…") before telling me what I'll see when the UI opens.
- README:47 — "So far: 300+ merged agent-authored PRs — the live count is on GitHub,
  deliberately not re-pinned here". The hedge is honest but the parenthetical draws
  attention to a bookkeeping worry rather than the achievement.
- README:230 — the clone caveat is a full paragraph on `--filter=blob:none` and an
  unscheduled `filter-repo` pass. Correct, but this is a footnote, not front-page material.
- reading-guide.md §4 — "the 15.18 convention", "the two-owner gate", "the §1.3 bar":
  naming conventions after task numbers and section numbers is fine internally and
  actively hostile to outsiders.
- observation/service.py:31–83 — a 50-line comment before the first function, citing
  "audit-2026-06-13-1816 D-D-1" and "Codex review, PR #155". The intent is good
  (rationale preserved), the effect is that the file's actual API is buried.
- First-run stderr from `run_game.py`: "AILIBI_PROMPT_SET is unset — falling back to the
  frozen reference set 'qwen3_5_9b', two generations behind the operational baseline". A
  newcomer's first output is a warning about something they can't be expected to know.

## 5. What I could verify vs. took on faith

**Verified in my budget**
- Determinism run-twice: byte-identical (`diff -q` silent), sub-second per game.
- Import-linter: 4 contracts kept, 0 broken; tests/test_firewall.py 9 passed.
- CI == `scripts/check.sh` (ruff, ruff format, lint-imports, task-doc validation,
  prompt-generation check, mypy strict, pytest, frontend lint/tsc/vitest/build); actions
  SHA-pinned; least-privilege permissions.
- engine/tick.py is a pure function over frozen dataclasses with a per-tick state hash.
- ~4,300 test functions across 184 files; property tests exist (`test_tick_properties.py`,
  `test_leak_property.py`).
- The GIF/PNG in docs/media exist and match the README captions.
- git history: 877 commits; authorship split dkdan10 / Claude / Daniel Keinan — consistent
  with the "agents author PRs, human merges" story.

**Taken on faith (couldn't or wouldn't in 20 min)**
- "300+ merged agent-authored PRs, every one merged green" — plausible from the history,
  not counted.
- The 4,531-passed gate figure and `verify_samples.sh` on 100 replays — did not run the
  full suite (other reviewers share the machine; it's minutes, not seconds).
- Every number in reading-guide.md §1 and §3 (34%/30% win rates, 520/520 citations,
  68/78 vent cross-tab) — cited to files, not re-derived.
- Any claim about real-LLM behavior — the default is a fake provider, and I would not
  set up Ollama/Featherless before a phone screen.
- The quality of the agent reasoning itself (out of scope for me; other reviewers own it).

## 6. Verdict

- **Advance to phone screen:** yes. **Take the meeting:** yes — the enforced-architecture
  story and the run-twice demo are enough. **Star the repo:** yes, on the strength of the
  first 80 README lines and docs/architecture.md.
- What I'll probe on the call: how much of the design judgment is the author's vs the
  agents'; why meetings/manager.py is 4k lines; how they'd onboard a human engineer given
  the private vocabulary; and whether they can explain Phase 15–18 in three sentences a
  VP would understand.
- **The single change that would most raise the verdict:** rewrite README "Project
  status" (lines 82–107) as a ~10-line, plain-English section — what shipped, what was
  tried, what the honest result was — and move the phase-by-phase ledger and its
  vocabulary into a linked `docs/history.md`. The current status section is the one place
  the repo undercuts its own best trait (clarity under enforcement).

## 7. MUST / GOOD / NICE for this audience

**MUST address (blocks landing with a hiring manager)**
1. **README "Project status" (lines 82–107).** [VERIFIED] Replace the two dense paragraphs
   with a plain-language status a stranger can read in 60 seconds. Keep the phase table;
   move the phase 15–19 ledger and every "baseline/lever/ladder/referee/NO-FLIP" sentence
   into a linked history page. Right now this is where the reader stops.
2. **Define or eliminate the private vocabulary on the front door.** [VERIFIED] No README
   or first-screen sentence should require reading-guide.md §4 to parse. Either say
   "the current reference recording (baseline 6)" once and stop, or don't mention baselines
   in the README at all.
3. **Make the human's contribution legible.** [JUDGMENT] For a hiring read, the open
   question is "what did *you* do?" The repo says agents wrote every coding PR; it should
   say, in one short section, what the human owned: architecture, task contracts, review,
   the decisions in the ADR, the audit judgments. A pointer to 2–3 contracts and 1 review
   that show the human's judgment would answer the question the interviewer will ask.

**GOOD to address (materially strengthens)**
4. **Put docs/architecture.md one click from the top of the README** (it's linked at line
   45 mid-paragraph and at line 248). For engineers it's the best document in the repo.
5. **Trim "Watch a replay" (line 149)** to what the user sees; move provenance to
   `replays/samples/*/MANIFEST.md` where it already lives.
6. **First-run experience:** silence or reword the `AILIBI_PROMPT_SET is unset` warning
   for the default fake-provider path, or default the variable so a newcomer's first output
   is clean.
7. **A hosted static demo link.** [VERIFIED docs/deployment.md has no URL] The static
   bundle exists and needs no API; a GitHub Pages link in the README top would let a
   recruiter *see* it without cloning 256 MiB.
8. **CI status badge + a one-line "stack" line** (Python 3.11 / FastAPI / Pydantic /
   React + Vite + PixiJS / uv) near the top — cheap orientation for skimmers.
9. **Comment style in source:** keep the rationale, but lead with plain intent and push
   task/audit citations to the end of the comment (observation/service.py:31–83 is the
   exemplar of the current style).
10. **File size:** meetings/manager.py (3,989 lines) and orchestrator/game.py (3,193) will
    be asked about; a sentence in architecture.md acknowledging why, or a split, helps.

**NICE**
11. Fold reading-guide.md §1–§3 down to a true five-minute read; move §4–§6 to separate
    pages (glossary, ML story).
12. Shorten the clone caveat (line 230) to one sentence + link.
13. Rename convention-labels that are task numbers ("the 15.18 convention", "the §1.3 bar")
    to descriptive names in the glossary ("merge-as-ratification convention",
    "the flip bar").
14. A short CONTRIBUTING pointer for humans (CONTRIBUTING.md is 86 lines and exists;
    surface it).
