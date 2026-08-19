# X1 — Front-door reproduction & perception audit (AiLibi as a portfolio project)

Reviewer role: careful outsider who has never seen the repo, testing every claim the README makes above the fold, then auditing README.md, docs/reading-guide.md, docs/architecture.md, CONTRIBUTING.md, SECURITY.md, docs/deployment.md for perception: clarity, credibility, signal-to-noise, staleness, and what is missing for a portfolio audience.
Repo HEAD at review: `b809b19c` (main, clean). Date: 2026-08-18. Read-only; all runs went to scratch dirs. Machine: macOS arm64, uv 0.11.7, node 26, .venv + node_modules already present (so timings below exclude `setup_env.sh`, which was read, not run).

Labels: **[VERIFIED]** = I ran it or read the bytes. **[JUDGMENT]** = my inference/opinion.

---

## 1. Front-door reproduction — every command, timed

| # | README claim / command | Ran | Wall time | Result | Verdict |
|---|---|---|---|---|---|
| 1 | Determinism: `run_game.py --seed 42` twice into a fresh dir, `diff -q` | yes | 0.3 s + 0.2 s + 0.0 s | Two 50,337-byte JSONL files, `diff -q` exit 0, byte-identical. Each run also emitted an unmentioned `r1.audit.jsonl` sidecar (38,881 B). | **[VERIFIED] TRUE**. Trivially fast, works exactly as written. |
| 2 | `bash scripts/verify_samples.sh` — "every committed sample still reconstructs" | yes | 3.6 s | `All 50 samples verified clean.` for `4p1i/` and again for `9p2i/`. Exit 0. | **[VERIFIED] TRUE**. 100/100. |
| 3 | `uv run python scripts/build_demo_bundle.py` — "a static directory with no API process in it" | yes, with `--out <scratch>` (default `frontend/dist/demo-bundle` is gitignored via `frontend/.gitignore`, so the default would NOT dirty the tree; I used a scratch dir only because other reviewers share this checkout and Vite `--emptyOutDir` would clobber `frontend/dist`) | 4.3 s (incl. `tsc --noEmit` + `vite build`) | 8.8 MB dir: `index.html`, `assets/`, `data/{4p1i,9p2i}/…` (204 JSON files, 7.2 MB), a generated `README.md`. Served with `python -m http.server`, opened in a browser: viewer loads, guided tour appears, seed 2 (9p) plays, no console errors. | **[VERIFIED] TRUE**. The GIF in the README is genuinely reproducible in one command. |
| 4 | `uv run python scripts/check_doc_facts.py` | yes | 0.2 s | `Doc facts verified: README.md and .env.example agree with 2 sample manifests, audits/audit-phase-18-close.md, and the 14-lever substrate registry.` | **[VERIFIED] TRUE**. Checks: sample provenance date + win rates + counts, "ladder tip" sentences, lever registry vs .env.example. |
| 5 | 5-game fake-provider tournament (`run_tournament.py --num-games 5 --output-dir <scratch>`) | yes | 0.4 s | 5 replays + 199 KB `tournament-eval-report.json` (keys: report, vote_correctness, accusation_calibration, alibi_fabrication, cost_dashboard, meeting_rate, conversion, gate_metrics, deduction). Content: 5/5 IMPOSTOR wins, 0 ejections, 4 meetings all SKIP, `vote_correctness_rate: null`, `survival_rate: null`, `ejection_accuracy: null`, cost $0. | **[VERIFIED] runs**; **[JUDGMENT]** the report an outsider gets is a degenerate all-null document — see MUST-3. |
| 6 | `bash scripts/setup_env.sh` | read only | n/a (audit-cited cold gate is ~10 min for `check.sh`; `npm ci` + `uv sync` typically 1–3 min) | Script is sound: requires `uv`, `uv sync --locked --group dev`, prints toolchain versions, `npm ci` with 3 retries, `AILIBI_SKIP_FRONTEND` validated. No `.python-version` file; relies on uv resolving `requires-python = ">=3.11,<3.12"` (uv will auto-download 3.11 — fine, but undocumented). Fails loud without npm. | **[VERIFIED by reading]** reasonable. |
| 7 | Markdown links in README.md + docs/*.md (+CONTRIBUTING, SECURITY, AGENTS) | yes (script) | — | 49 relative links, **0 broken**. | **[VERIFIED]** clean. |
| 8 | Test count | `pytest --collect-only` | 3.1 s | 4,961 collected, 4,644 selected by default (317 `campaign`-marked deselected). | Reading guide's "4,531 passed" is labelled "at the Phase-19 chartering commit" — historically honest, but a reader who runs today gets a different denominator. |

Bottom line for the front door: **every reproducible claim above the fold reproduces, in under 10 seconds total on a warm machine.** [VERIFIED] That is unusually strong for a portfolio repo and is the single best thing this project has going for it. The problems are all in the prose around it.

**Noise observed on every run [VERIFIED]:** each of commands 1, 2, 3, 5 prints (twice per game, on stderr):
`agents.strategic.prompts.loader: AILIBI_PROMPT_SET is unset — falling back to the frozen reference set 'qwen3_5_9b', two generations behind the operational baseline 'qwen3_6_27b'; export AILIBI_PROMPT_SET=qwen3_6_27b to run the baseline set.`
`AILIBI_PROMPT_SET` is mentioned **nowhere** in README.md, .env.example, AGENTS.md or docs/architecture.md (grep count 0 in each). So the outsider's very first command tells them they are running something "two generations behind", pointing at a knob no front-door document names. The 5-game tournament prints it 6 times before the summary.

Minor front-door observations [VERIFIED]:
- The generated bundle `README.md` bakes the builder's absolute path (`baked from /Users/danielkeinan/projects/AiLibi/replays/samples`) into a file the docs describe as "the only sanctioned public artifact".
- `run_game.py` writes an `*.audit.jsonl` sidecar beside the replay; README never mentions it, so the diff demo leaves an unexplained extra file.
- The 4-player fake tournament yields 100% impostor wins with the FSM alone; the README does warn "set a real provider … for metric values that reflect real model behavior", but does not point to the committed real-provider reports (`replays/samples/{4p1i,9p2i}/tournament-eval-report.json` exist).

---

## 2. GitHub front door (outside the README) [VERIFIED via `gh`]

- Repository **description: empty. Topics: none. Homepage: none.** 0 stars, 0 forks, no releases. The About panel — the first thing a recruiter sees — is blank.
- 346 merged PRs (`search/issues is:pr is:merged`), highest PR #350; README's "300+ merged agent-authored PRs — the live count is on GitHub" is accurate and not stale. All 346 PRs are authored by the owner account `dkdan10`; the "agent-authored" claim is visible only via `claude/…` branch names and commit authors (`git shortlog`: Claude 310, dkdan10 355, Daniel Keinan 211 commits) — not falsifiable from GitHub UI, and unstated in the README.
- CI: `ci.yml` + `campaign-tier.yml`; latest main runs green. **No CI badge in the README.**
- README does not name the license (MIT is only in LICENSE/CONTRIBUTING), has no author line, no contact, no "live demo" link. `docs/media/README.md` shows the GIF is a capture of the static bundle — yet the bundle is not hosted anywhere (no Pages workflow), so the reader must clone to see it move.

---

## 3. Documentation audit

### 3.1 README.md — shape and length [VERIFIED]
- 249 lines, **3,833 words**; ~15–19 min at 200–250 wpm (my read, with the jargon: >20 min).
- Section weights: hero 10%, What this is 6%, How built 4%, Three decisions 6%, **Project status 22% (846 words)**, Reproduce 9%, Watch a replay 15%, Tournament 12%, Setup 8%, Architecture notes 7%.
- Longest paragraph: **506 words** (README:107, the phases 15–19 paragraph), containing a **172-word sentence**. 137 parentheticals and 81 em-dashes in the file.
- Narrative-of-process/history vs description-of-product: ≈ **41% process/history** (How-built + Project status + the "What this is" second half + the baseline-6/lever provenance paragraph in Watch a replay + the clone-history caveat) vs ≈ 59% product. The process share is concentrated in the least readable text.

### 3.2 Claims: verifiable / unverifiable / stale [VERIFIED unless marked]
Verifiable from the repo and true: determinism; 100 samples reconstruct; 34%/30% win rates (`check_doc_facts`); "300+ PRs" (346); "13 graduated levers + 1 live toggle" (`orchestrator/replay.py`; the `game_over` record I generated stamps exactly 14 flags, `impostor_roll_call: false`); phase status "Phase 19 closed 2026-08-18" (`tasks/phase-19.md:3 STATUS: CLOSED 2026-08-18`, `audits/audit-phase-19-close.md` present); tracked working tree ≈ 260 MiB (README "roughly 256 MiB"); ADR-0001 exists; Task 3.19 contract (~480 lines) and its prompt (340 lines) exist.
Not verifiable from the repo (stated as fact): "every one of them merged green through the same full gate" (branch-protection history is not in the repo); "zero observation-firewall violations" across all phases (only provable as "CI would have failed" — fine, but say so). [JUDGMENT] Both are believable; both should be phrased as what the reader *can* check.
Numbers with no in-README source: "+0.12 to +0.30", "0.938 — 90/96", "83/96 = 0.8646", "0.625", "citation compliance 1.000", "0.02 win rate", "+0.16" — all in the Project-status paragraph, each attributed only to a 1,000+-line audit link. They are traceable (I spot-checked `audits/audit-phase-18-close.md:104-105`, `:719`, `training/reports/report-finalist-eval.md:268-271` — all present) but a reader cannot tell what they mean without §4 of the reading guide.
Stale/drifted anchors in docs/reading-guide.md (24 `file:line` citations; I checked 30 anchors incl. ranges): 27 hit; drifted: `eval/watchability.py:548` → symbol is at :538; `tasks/phase-19.md:22` (range :22-23 still covers it); `audits/audit-phase-18-close.md:39` (range :38-39 fine); `report-finalist-eval.md:268` (range fine). Line-number citations are inherently brittle — the guide's own convention will rot with every edit.
ADR-0001 vs README: README says the three decisions are "recorded verbatim in ADR-0001"; the ADR text differs (ADR: "ticks at a fixed rate (target 2 Hz)", "≤ 100 LLM calls", author "Codex"; README omits both figures). Minor, but "verbatim" is false as written. Reading guide says "Enforcement is four import-linter contracts"; README says "import-linter" only — consistent enough.
docs/deployment.md cites "audit C-C-1, C-C-2, C-C-4" with no file — an outsider cannot resolve them (they resolve to `audits/audit-2026-05-30-0059-mvp-close.md` et al. only via grep).
Terminology: consistent on impostor/imposter (0 misspellings), 9p2i, fake/anthropic/ollama/featherless. Mild drift: "spectator UI" / "the spectator" / "replay viewer" / "spectator surface" all used for one thing; "GM view" vs "game-master view"; "conviction engine" (meetings/) vs "engine" (engine/) — the reading guide has to explicitly disambiguate.

### 3.3 Jargon [VERIFIED counts]
docs/reading-guide.md §4 defines **11** terms (baseline N, adopting record, ladder tip, graduated lever, the §1.3 bar, NO-FLIP, canary denominator, findings-not-failures, the 15.18 convention, the two-owner gate, errata discipline). **6 of the 11 appear in README.md undefined**: "baseline" (19×), "adopting record" (3×), "ladder tip" (4×), "graduated" (5×), "NO-FLIP"/"no mover flip" (2×), "canary denominator" (2×). README additionally uses ≥15 terms defined in neither place: referee (4×), slate (4×), arm, mover, champion, conviction-economy, supply/conversion floors, absence prior, roll-call round, endpoint-band whereabouts exemption, flag-minting, starved-economy shape, screening-tier shortlist, two-axis owner ruling, training-time-runner tier, evidence-gated default flip. The README's "New here?" pointer sends readers to a guide that is itself **3,239 words** while titled "the outsider's five minutes" (≈13–16 min).

### 3.4 Per-document verdicts [JUDGMENT unless marked]
- **README.md** — hero (GIF + PNG + "Reproduce the three claims") is excellent and honest; commands are correct [VERIFIED]. From "Project status" onward it turns into an internal changelog written for the owner: the phases 15–19 paragraph is unreadable to any of the target audiences. "Watch a replay" buries the product under a provenance paragraph ("the meeting layer graduated CREW-ONLY … the endpoint-band whereabouts exemption, the vent-placement contradiction variant (flag-minting plus the absent-set widening) …"). Setup's clone caveat is honest but ~150 words about `filter-repo` is more than a newcomer needs.
- **docs/reading-guide.md** — the best-written document in the set; §1 numbers table with owning paths, §3's cross-tab (68/2 vs 10/21) and the "General social deduction: NOT demonstrated" admission are exactly what a researcher wants. But it is 3× its advertised length, its §4 glossary is needed to read the README (wrong direction: the README should not depend on it), and it leans on `file:line` anchors that already drift.
- **docs/architecture.md** — 1,089 words, current, ASCII layering diagram, names the four contracts and their backing tests. Good for senior engineers. It is not linked from the README's first screen (only in "What this is" and the footer).
- **CONTRIBUTING.md** — clear, candid ("issues are welcome, pull requests are not the workflow"). Refreshingly honest; may alienate open-source-minded readers but is coherent with the thesis.
- **SECURITY.md** — well-scoped, explains the deliberate unauthenticated GM view. Good.
- **docs/deployment.md** — accurate about the bundle; the "audit C-C-1" anchors are unresolvable; ~1,235 words for what is essentially "loopback only; ship the static bundle".

---

## 4. Audience read [JUDGMENT]
- **Recruiter (60 s):** blank GitHub About, no badge, no one-line pitch under the title other than the italic tagline, no live link, 0 stars. GIF helps. Likely bounce before "What this is".
- **Hiring manager (5 min):** the hero + "How this is being built" lands the thesis (contracts → generated prompts → agent PR → gate). Then hits "Project status" and cannot tell what was achieved. Missing: a results/"what I learned" block, a "my role vs the agents' role" line, and any tests/CI signal.
- **Senior engineer (15 min):** will love reproduce-in-10-seconds, `check_doc_facts.py`, the firewall (import-linter + planted-leak tests), the honesty about the three reproducibility scopes. Will be irritated by the 172-word sentence and by having to learn "adopting record" to parse the README.
- **Researcher:** the reading guide §3 cross-tab and "NOT demonstrated" are the hook; NO-FLIP twice + pre-registration + errata is a real methodological story. But the story is scattered across README §Project status, reading-guide §1/§3/§6, `training/README.md` and 80 audit files (24,527 lines). No single 1-page results summary with the 3–4 headline findings.
- **Other builders (agentic workflow):** the strongest audience fit — but the workflow artifacts (task contract → prompt) are linked once and never shown; no diagram, no excerpt, no "here is one contract and the PR it produced".

---

## 5. Findings

### MUST address (blocks the project from landing)
1. **README "Project status" is unreadable to every target audience.** [VERIFIED metrics] 846 words / 22% of the file; a 506-word paragraph with a 172-word sentence; ≥20 undefined terms. Replace with a 6–8 row table (phase, dates, one-line outcome, link) and move the phase narratives to `docs/history.md` or the audits they already link. The reader must be able to answer "what did this project find?" in 30 seconds.
2. **The README depends on a glossary that lives elsewhere.** [VERIFIED] 6 of the 11 §4 terms + ≥15 others are used undefined in README.md. Either the README stops using them above the fold, or a 5-line "vocabulary" box precedes their first use. Rule of thumb: nothing in README.md should require docs/reading-guide.md §4.
3. **First-run noise contradicts the reproducibility pitch.** [VERIFIED] Every front-door command emits "AILIBI_PROMPT_SET is unset — … two generations behind the operational baseline" and points at an env var documented nowhere at the front door. Either default the prompt set to the operational baseline for the CLI surfaces, silence the notice under the fake provider, or document `AILIBI_PROMPT_SET` in README/.env.example next to `AILIBI_LLM_PROVIDER` and say the notice is expected.
4. **Empty GitHub About panel + no badge, no license line, no author, no hosted demo.** [VERIFIED] Set description + topics (multi-agent, social-deduction, llm-agents, deterministic-simulation, agentic-workflow…), add a CI badge, an MIT line, and — since `build_demo_bundle.py` produces a static, publishable artifact in 4 s — deploy it to GitHub Pages and link it in the first 3 lines. The GIF proves the artifact exists; a link would let people click it.
5. **The fake-provider tournament the README hands out produces an all-null report.** [VERIFIED] 5/5 impostor wins, 0 ejections, every rate `null`. Either point the README example at `replays/samples/9p2i/tournament-eval-report.json` ("here is a real one") or make the runbook say up front what the fake output will look like and why.

### GOOD to address (materially strengthens)
6. **State the headline results once, in one place, near the top.** [JUDGMENT] E.g.: 100/100 replays byte-reconstruct; 520/520 ballots cite valid evidence; 87% of correct 9p ejections ride a vent sighting vs ~30–39% otherwise (i.e. general deduction NOT demonstrated); learned movers beat the FSM on wins (+0.12–0.30) but were not adopted (NO-FLIP ×2). These are all in the reading guide already; the README never states them.
7. **Show the workflow, don't just link it.** [JUDGMENT] One 15-line excerpt of a task contract + the matching prompt header + the PR it produced (branch `claude/…`, gate green) would make "300+ agent-authored PRs" concrete. Also say how a reader can verify agent authorship (branch names / commit authors), since GitHub shows one human author on all 346 PRs.
8. **Trim the reading guide to its title or retitle it.** [VERIFIED 3,239 words] Either a real 5-minute version (§1 numbers table + §2 demo + §3 cross-tab + the 3 audits ≈ 800 words) with the rest as "reading guide, long form", or call it what it is.
9. **Replace `file:line` citations with symbol/heading anchors** in the reading guide (already 1 drifted of ~30 checked; the convention guarantees rot).
10. **README "Watch a replay"**: lead with what the viewer shows and the 7 featured seeds (the reading guide's table is much better than the README's provenance paragraph); move the baseline-6 lever provenance to `replays/samples/*/MANIFEST.md`, which the README already calls canonical.
11. **Make the unverifiable claims verifiable-shaped**: "every PR merged green through the same gate" → "CI is required on `main`; see .github/workflows/ci.yml; check.sh runs the same gate locally"; "zero firewall violations" → "the firewall has never been breached in CI: import-linter contract + tests/test_firewall.py planted-leak test + recursive leak sweep".
12. **Fix small truth wobbles**: "recorded verbatim in ADR-0001" (ADR text differs: 2 Hz, ≤100 calls, author Codex); deployment.md's unresolvable "audit C-C-1/2/4"; the bundle README baking an absolute local path; explain the `*.audit.jsonl` sidecar in one clause.
13. **Add a Python 3.11 note or `.python-version`** so `setup_env.sh` behaviour on a machine without 3.11 is stated (uv will download it — say so).

### NICE
14. A one-screen architecture diagram in the README (the ASCII block in docs/architecture.md is fine — inline it).
15. Mention `docker-compose.yml` in README (currently only deployment/SECURITY know it exists) or delete it if unsupported.
16. Consolidate the four top-level meta docs (AGENTS.md, DESIGN.md 9,730 words, AGENT_IMPLEMENTATION.md, DESIGN.md's "historical" status) into a `docs/` index; a newcomer sees 5 markdown files at root plus 24 in tasks/ and 80 in audits/ with no map besides the README footer.
17. Reduce em-dash/parenthetical density (81 / 137 in README) — the house style reads as one voice thinking aloud rather than documentation.
18. Consider a `results/` or `docs/findings.md` page for researchers that carries the cross-tab, N1/N2, and the McNemar note with a plain-language sentence each.

---

## 6. Raw numbers (for the record)
- Timings (warm env): run_game 0.3 s / 0.2 s; diff 0.0 s; verify_samples 3.6 s; check_doc_facts 0.2 s; tournament×5 0.4 s; build_demo_bundle 4.3 s; pytest collect 3.1 s.
- README: 249 lines, 3,833 words; longest para 506 words; longest sentence 172 words; 137 "(" ; 81 "—".
- Docs word counts: reading-guide 3,239; architecture 1,089; CONTRIBUTING 633; SECURITY 627; deployment 1,235; AGENTS 1,299; DESIGN 9,730.
- Links: 49 relative, 0 broken. Audits: 80 files, 24,527 lines. tasks/: 24 files, 29,807 lines. agent_prompts/: 321 files.
- Git: 877 commits; 182 merge commits + 170 squash "(#N)" subjects; 346 merged PRs on GitHub, max #350; tracked tree ≈ 260 MiB; .git 190 MB locally.
- Tests: 4,961 collected / 4,644 default-selected (317 `campaign`).
- Scratch outputs: `/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/work/x1/` (det/, tourn/, bundle/, *.log, timings.txt).

Note: at the end of this review `git status` showed one untracked `.coverage` file (21:40) — pytest-cov is not installed in the project venv and my only in-repo command was `pytest --collect-only`; concurrent reviewer pytest processes were running at that time, so it is theirs, and I left it in place. Nothing in the repo was created, edited, staged or committed by this review.
