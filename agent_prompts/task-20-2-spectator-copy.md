# Agent Prompt — 20.2 Product copy: the audit dialect leaves the spectator surface

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-20.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 20.2 — Product copy: the audit dialect leaves the spectator surface, anchored to G-41 and G-37 (`audits/review-2026-08-19/A/collated-findings.md` §D — "Spectator UI: internal jargon and layout on the product surface" and "Agent tick stamps are +1 vs the replay timeline"); `audits/review-2026-08-19/A/ux-visual-pass-lead.md` (the picker-legend line, the CORRECT-badge spoiler line, the Tournament-tab dialect line); `audits/review-2026-08-19/C/p3-frontend-product-engineer.md` §3 weakest-3 item 3, §4 "Hurt", §7 GOOD 6 and GOOD 9; `audits/review-2026-08-19/C/collated-portfolio.md` B6; `audits/review-2026-08-19/D/FINAL-synthesis.md` §4 wave-0 row 0.3, §2 row 12 (C-113 [D-VERIFIED]), §4 wave-2 row 2.14 (the clock re-stamp — NOT scheduled in Phase 20); `audits/audit-phase-20-planning.md` §3 (wave 0); AGENTS.md:95-98 (craft rule 4, no internal dialect on user-facing surfaces) and :99-102 (rule 5, verifiable-shaped claims). Anchors re-verified at HEAD `b809b19c` (with the planning PR in the working tree): `frontend/src/components/TournamentDashboard.tsx`:188, :241, :251-253, :299, :320, :324-326, :338, :366, :518, :703, :838, :935; `MeetingView.tsx`:224, :233, :524-549, :672-682; `BallotCard.tsx`:30-35, :100-105, :131, :145-150, :166-178; `ReplayPicker.tsx`:373-387, :421-427, :456, :457, :509-542; `HighlightCard.tsx`:54-59, :102-104, :119, :175-197; `ReplayControls.tsx`:603-614; `MetricCaveat.tsx`:1-12. Also in scope, and the boundary this measures: `TurnCard.tsx`:291 is the ONLY user-facing dialect string in `frontend/src` outside this task's seven core files. The clock seam is `orchestrator/game.py`:1778 (packets built), :1785-1786 (`input_tick` then `advance_tick`), :1794 (`record_tick(input_tick, …)`) — the review's ":1778-1793" is one line short at HEAD. The metric truth is `eval/vote_correctness.py`:11-25 ("structurally pinned to 1.0") against `replays/samples/9p2i/tournament-eval-report.json` → `vote_correctness.vote_correctness_rate` = 0.9230769230769231 (72 evidence-backed of 78 impostor ejections). Test-runner facts: `frontend/vitest.config.ts` (`environment: "node"`, `include: src/**/*.test.ts(x)`) and `frontend/src/components/CostChips.test.ts`:12-14 (an existing node-env `.test.ts` importing a `.tsx` — the precedent this task reuses).. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-20.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-20-spectator-copy`
**Depends on:** none (root)
**Section refs:** G-41 and G-37 (`audits/review-2026-08-19/A/collated-findings.md` §D — "Spectator UI: internal jargon and layout on the product surface" and "Agent tick stamps are +1 vs the replay timeline"); `audits/review-2026-08-19/A/ux-visual-pass-lead.md` (the picker-legend line, the CORRECT-badge spoiler line, the Tournament-tab dialect line); `audits/review-2026-08-19/C/p3-frontend-product-engineer.md` §3 weakest-3 item 3, §4 "Hurt", §7 GOOD 6 and GOOD 9; `audits/review-2026-08-19/C/collated-portfolio.md` B6; `audits/review-2026-08-19/D/FINAL-synthesis.md` §4 wave-0 row 0.3, §2 row 12 (C-113 [D-VERIFIED]), §4 wave-2 row 2.14 (the clock re-stamp — NOT scheduled in Phase 20); `audits/audit-phase-20-planning.md` §3 (wave 0); AGENTS.md:95-98 (craft rule 4, no internal dialect on user-facing surfaces) and :99-102 (rule 5, verifiable-shaped claims). Anchors re-verified at HEAD `b809b19c` (with the planning PR in the working tree): `frontend/src/components/TournamentDashboard.tsx`:188, :241, :251-253, :299, :320, :324-326, :338, :366, :518, :703, :838, :935; `MeetingView.tsx`:224, :233, :524-549, :672-682; `BallotCard.tsx`:30-35, :100-105, :131, :145-150, :166-178; `ReplayPicker.tsx`:373-387, :421-427, :456, :457, :509-542; `HighlightCard.tsx`:54-59, :102-104, :119, :175-197; `ReplayControls.tsx`:603-614; `MetricCaveat.tsx`:1-12. Also in scope, and the boundary this measures: `TurnCard.tsx`:291 is the ONLY user-facing dialect string in `frontend/src` outside this task's seven core files. The clock seam is `orchestrator/game.py`:1778 (packets built), :1785-1786 (`input_tick` then `advance_tick`), :1794 (`record_tick(input_tick, …)`) — the review's ":1778-1793" is one line short at HEAD. The metric truth is `eval/vote_correctness.py`:11-25 ("structurally pinned to 1.0") against `replays/samples/9p2i/tournament-eval-report.json` → `vote_correctness.vote_correctness_rate` = 0.9230769230769231 (72 evidence-backed of 78 impostor ejections). Test-runner facts: `frontend/vitest.config.ts` (`environment: "node"`, `include: src/**/*.test.ts(x)`) and `frontend/src/components/CostChips.test.ts`:12-14 (an existing node-env `.test.ts` importing a `.tsx` — the precedent this task reuses).
**Complexity:** Small
**Record impact:** none — display copy and one display gate only; no engine, prompt-template, DTO or detector byte moves, so nothing here waits on the Phase-20 adopting record.
**Measurement:** `cd frontend && npm run test && npm run lint && npm run tsc:check` green (including the new `src/lib/copy.test.ts`, whose perturbation leg proves the dialect matcher bites); `grep -rnE 'DESIGN\.md §|Task [0-9]+\.[0-9]+|audits/|sentinel|KPI' frontend/src` returns hits only on source-comment lines, never on a rendered string.

The spectator is the project's best asset and its copy is written in a private
dialect. Every reviewer who opened the Tournament tab hit it: card subtitles carrying
"(DESIGN.md §11.3)" (TournamentDashboard.tsx:188, :935), "(Task 9.6 / 10.x; typed on
the wire by 12.2.)" (:299), "(Task 19.14; audits/audit-phase-19-triage.md §7 item 15)"
(:518), "(Task 10.4), re-anchored by 19.5 … the Task-17.6 successor" (:366), and
caveat chips reading "sentinel — not a KPI" (:253) and "sentinel — read the split"
(:326) over hint strings like `imp-voter 91 · invalid 1 · inversion 87` (:320). The
meeting dialog's Resolution card labels its verdict "§4.6" twice (MeetingView.tsx:224,
:233). The reviewer's summary of the whole viewer was that its two real problems are
the corpse bug and the internal jargon in copy (`A/ux-visual-pass-lead.md`), and the
portfolio track independently made "strip audit/task citations from user-facing text"
its B6. AGENTS.md's craft rule 4 now makes this binding for every PR from Phase 20 on;
this contract is that rule executed on the surface the rule was written for.

Three of the strings are not merely opaque — they are false or spoiling. The
vote-correctness section (TournamentDashboard.tsx:241, :251) tells a visitor the rate
is "pinned to 1.0 by construction" and that "Below 1.0 means a detector/recording bug
to chase", while the committed report the tile renders reads 0.9230769230769231 — 72
evidence-backed of 78 impostor ejections in
`replays/samples/9p2i/tournament-eval-report.json`. The dashboard therefore
contradicts its own number on screen, in the one place a sceptical reader is looking
for honesty ([D-VERIFIED], `D/FINAL-synthesis.md` §2 row 12; the README leg of that
finding is refuted and no README edit belongs here). Separately, the ballot
CORRECT/INCORRECT badge (BallotCard.tsx:166-178) renders on role ground truth whenever
the perspective is Omniscient, including while the spectator has outcomes hidden — a
viewer who deliberately chose the unspoiled mode is told, per ballot, who the
impostors were.

That badge is a deliberate decision being revisited, not an oversight, and the
contract records the reversal rather than silently flipping it: BallotCard.tsx:30-35
states that the gating is "on PERSPECTIVE alone, deliberately never on
`revealOutcome`", on the reasoning that reveal governs outcome information and
perspective governs what the current frame may know. The ruling here: a per-ballot
correctness mark is outcome information for a first-time viewer — it names the
impostors before the game names them — so it is gated on Omniscient AND the reveal,
and the module comment is rewritten to say that, with the superseded reasoning kept as
one history line. The narrower firewall rule the same file enforces (role-disclosing
rewrite chips and the coerced-rationale body suppressed under fog,
`visibleRewriteReasons` / `visibleRationale` at :68-98) is untouched: reveal must
never WIDEN what fog hides, and it does not here.

Two smaller truths ride along. The rubric bars R1/R2/R3/R7 (HighlightCard.tsx:54-59,
:175-197) render as bare keys with their words available only in a hover title, and
the header legend that spells them out exists only on the Highlights tab
(ReplayPicker.tsx:456) — so the Replays tab, which is where the picker opens, shows
four unlabelled bars. And the set names "9p2i" / "4p1i" are never expanded anywhere on
the surface, including in the set selector (ReplayPicker.tsx:509-542) that is the
first control a visitor touches. Finally the two-clock seam (G-37): agent-facing
observation stamps are one ahead of the replay timeline the transport scrubs —
111,283/111,283 memory sighting lines match world truth at Δ=−1 and only 51.8% at Δ=0
(`A/s3-meeting-decisions.md`), while the meeting header's "It is tick N" matches the
replay tick exactly in 771/771 calls (`A/s2-movement-positions.md`) — because the
packet is built at `orchestrator/game.py`:1778 before `advance_tick` at :1786 and
recorded against the pre-advance `input_tick` at :1794. Every one of the review's
eight watchers opened by hand-deriving that convention. The engine-side resolution
(re-stamp or assert) is `D/FINAL-synthesis.md` §4 row 2.14 and is NOT scheduled in
Phase 20, so this task ships the honest label only: a one-line note beside the tick
readout that states the convention truthfully, and that a later re-stamp would delete.

**Files in scope:**
- frontend/src/components/TournamentDashboard.tsx; (copy + tooltips only — every tile value, ordering and layout byte-identical)
- frontend/src/components/MeetingView.tsx; (the §-citation copy on the Resolution card; threading the reveal state to the ballots panel)
- frontend/src/components/BallotCard.tsx; (the CORRECT/INCORRECT badge gated on the outcome-reveal state; the module comment records the reversed ruling)
- frontend/src/components/ReplayPicker.tsx; (the rubric legend on both tabs + set-name expansion in the selector and the empty states)
- frontend/src/components/HighlightCard.tsx; (the sub-score bars carry their words, not only a hover title)
- frontend/src/components/MetricCaveat.tsx; (the caveat component's own "sentinel notes" doc wording; no rendered string lives here — if the file needs no change after the call sites are rewritten, the PR says so)
- frontend/src/components/ReplayControls.tsx; (the agent-clock note beside the tick readout)
- frontend/src/lib/copy.ts; (new: the user-facing copy tables + the pure expandSetName / dialectHits / badge-gate helpers)
- frontend/src/lib/copy.test.ts; (new: the dialect gate with its perturbation leg, the legend/set-expansion pins, the badge-gate combinations)
- frontend/src/components/TurnCard.tsx; (the one dialect string at :291 — copy only)

**Files NOT in scope:**
- frontend/src/components/MapView.tsx and BodyMarker.tsx (the body-layer task owns the map this wave)
- frontend/src/hooks/useFocusTrap.ts, frontend/src/components/GuidedTour.tsx, frontend/src/App.tsx (the dock-and-focus task owns layout and the overlay stack; it lands after this one)
- everything in frontend/src/components/TurnCard.tsx except the :291 tooltip string (the structured-turn-markers task owns this file's chips and markers in wave 2; this task rewrites that one tooltip's wording and nothing else, and lands well ahead of it — 20.28 depends on 20.16, which depends on this task, so the shared file is dep-ordered)
- api/, api/schemas.py and the generated `frontend/src/types/` (no data, DTO or view-model-version change; the action-fidelity task owns the DTO)
- eval/vote_correctness.py (the vote-correctness-truth task owns the docstring and the doc-fact pin; coordinate the WORDING of what the metric measures, never the file)
- agents/strategic/prompts/ and every prompt template (no task in this phase edits a game prompt except the single prompt-set bump)
- replays/ and any recorded byte (nothing re-records)
- frontend/src/stories/ (the stories already drive `revealOutcome` through the store at MeetingView.stories.tsx:421-447 and :484-524, so they need no edit; if one breaks, fix the component, not the story)

**Definition of done:**
- [ ] Every user-facing string on the eight surfaces lives as a value in one new `frontend/src/lib/copy.ts` module (plain `.ts`, no JSX, importable by the node-env vitest project) and NONE of those values matches the dialect matcher: a `DESIGN.md §…` citation, a bare `§N.N` section reference, a `Task N.M` reference, an `audits/…` path, or the words "sentinel" / "KPI". Every rendered string named in Section refs (the fourteen on the dashboard, including the §5.4 alibi-survival description at :703, and the two on the Resolution card) is rewritten in plain English that keeps the substance (what the number counts, what its denominator is, what a caveat warns about) and drops the pointer.
- [ ] `frontend/src/lib/copy.test.ts` pins it two ways and can fail: it asserts the matcher flags a deliberately dialect-bearing fixture string (the perturbation leg, craft rule 2), then asserts every exported copy value is clean, then reads the eight in-scope `.tsx` files off disk with `//`, `/* */` and `{/* */}` comments stripped and asserts zero dialect hits in what remains. The disk leg ships with an EMPTY allow-list — `TurnCard.tsx` included, every in-scope surface must come back clean — and the test states that in one line, so any future allow-list entry is a deliberate act.
- [ ] The rubric bars carry their words wherever they render: `HighlightCard.tsx`'s `SubScoreBar` labels each spoke with its meaning (not only in the hover `title` at :183), and the Replays tab header carries the same R1/R2/R3/R7 legend the Highlights header carries at `ReplayPicker.tsx`:456 — pinned by a vitest assertion over the exported legend table. The other half of that same ternary, the Replays-tab sentence at :457 ("Every recorded replay in the served set."), stops asserting a completeness this build cannot honour — the static demo bundle serves a subset (the reviewer measured 4 of 50 in bundle mode, `C/p3-frontend-product-engineer.md` §4 "Hurt" and §7 GOOD 9) — and becomes a sentence that is true in BOTH live and bundle mode without reading a build flag (`STATIC_DATA_MODE` is module-private to `frontend/src/api/client.ts`, which this task does not edit); the new value is pinned in `copy.test.ts`.
- [ ] Set ids are expanded once per surface: a pure `expandSetName` helper in `frontend/src/lib/copy.ts` maps `9p2i` → "9 players, 2 impostors" and `4p1i` → "4 players, 1 impostor", falls back to the raw id for any unrecognised set (the selector's options come from `/sets` and grow), and is used by the `SetSelector` options (`ReplayPicker.tsx`:509-542) and by the first mention in the picker's empty states (:373-387, :421-427). The three cases — both known ids and one unknown id — are pinned in `copy.test.ts`.
- [ ] The ballot CORRECT/INCORRECT badge renders only when the perspective is Omniscient AND the store's `revealOutcome` is true: `MeetingView` reads `revealOutcome` from `useReplayStore` and threads it through `BallotsPanel` (:524-549, :672-682) to `BallotCard`; the badge's gate is an exported pure predicate so `copy.test.ts` pins all four (omniscient × revealed) combinations with no DOM. `BallotCard.tsx`:30-35's comment is rewritten to state the new rule with one history line for the superseded one, and the fog-side rules (`visibleRewriteReasons`, `visibleRationale`) are unchanged and still pinned.
- [ ] The vote-correctness copy (`TournamentDashboard.tsx`:241, :251-253) states what the metric counts — the share of impostor ejections that carry a naming contradiction or a kill-witness chain on the record — says that it is a bug detector rather than a quality score in plain English (the words "sentinel" and "KPI" do not appear), and makes NO structural-1.0 claim; instead it says what a value below 1 means (an impostor ejection with no such evidence recorded against them) without asserting which cause applies. The tile keeps rendering the live value; no number is hard-coded into copy.
- [ ] A one-line agent-clock note sits beside the tick readout (`ReplayControls.tsx`:603-614): this timeline is the replay/engine clock, and an agent's own observation stamps read one ahead of it, with a tooltip saying that a memory line stamped tick N describes the map shown at N−1 while the meeting header's tick matches this readout. The note carries no measurement figures and no task or audit id; the corroborating counts live in the code comment and the test, not on screen.
- [ ] No layout, tile, value, ordering or aria-label semantic changes beyond the copy and the one badge gate; the PR quotes `git diff --stat` and the reviewer can see the dashboard's numbers are untouched.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.
- Re-verify every file:line anchor the contract cites at HEAD before editing; if an anchor has moved, record the true location under `## Decisions` — never edit from a stale line number.
- Grep every consumer of each symbol, path, or constant you will change (the blast radius); if a hit lies outside the files in scope, stop and ask rather than widening scope silently.

## Craft rules (AGENTS.md "Craft rules" — non-negotiable for every file you touch)
- Lead with intent: a docstring or comment states what the code does and why, now; provenance (task ids, audit paths) is at most one trailing line. Do not narrate history in source.
- A gate must be able to fail: every new test or check that guards an invariant ships with a planted or perturbed case proving it bites, and checks the semantics it claims, not only the shape.
- Retire means delete: when a lever graduates or a branch dies, delete the resolver, the parameter, the branch and the tests that pin them; keep only the stamp key and one history line.
- No internal dialect on user-facing surfaces: UI copy, rendered game prompts, spoken text and README carry no task or audit ids, no threshold arithmetic, and no undefined jargon.
- Claims are verifiable-shaped: a doc claim names the mechanism that enforces it; a number is recomputed from committed bytes and its command goes in the PR.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-20-spectator-copy` with a title like `task 20.2: product copy: the audit dialect leaves the spectator surface`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing G-41 and G-37 (`audits/review-2026-08-19/A/collated-findings.md` §D — "Spectator UI: internal jargon and layout on the product surface" and "Agent tick stamps are +1 vs the replay timeline"); `audits/review-2026-08-19/A/ux-visual-pass-lead.md` (the picker-legend line, the CORRECT-badge spoiler line, the Tournament-tab dialect line); `audits/review-2026-08-19/C/p3-frontend-product-engineer.md` §3 weakest-3 item 3, §4 "Hurt", §7 GOOD 6 and GOOD 9; `audits/review-2026-08-19/C/collated-portfolio.md` B6; `audits/review-2026-08-19/D/FINAL-synthesis.md` §4 wave-0 row 0.3, §2 row 12 (C-113 [D-VERIFIED]), §4 wave-2 row 2.14 (the clock re-stamp — NOT scheduled in Phase 20); `audits/audit-phase-20-planning.md` §3 (wave 0); AGENTS.md:95-98 (craft rule 4, no internal dialect on user-facing surfaces) and :99-102 (rule 5, verifiable-shaped claims). Anchors re-verified at HEAD `b809b19c` (with the planning PR in the working tree): `frontend/src/components/TournamentDashboard.tsx`:188, :241, :251-253, :299, :320, :324-326, :338, :366, :518, :703, :838, :935; `MeetingView.tsx`:224, :233, :524-549, :672-682; `BallotCard.tsx`:30-35, :100-105, :131, :145-150, :166-178; `ReplayPicker.tsx`:373-387, :421-427, :456, :457, :509-542; `HighlightCard.tsx`:54-59, :102-104, :119, :175-197; `ReplayControls.tsx`:603-614; `MetricCaveat.tsx`:1-12. Also in scope, and the boundary this measures: `TurnCard.tsx`:291 is the ONLY user-facing dialect string in `frontend/src` outside this task's seven core files. The clock seam is `orchestrator/game.py`:1778 (packets built), :1785-1786 (`input_tick` then `advance_tick`), :1794 (`record_tick(input_tick, …)`) — the review's ":1778-1793" is one line short at HEAD. The metric truth is `eval/vote_correctness.py`:11-25 ("structurally pinned to 1.0") against `replays/samples/9p2i/tournament-eval-report.json` → `vote_correctness.vote_correctness_rate` = 0.9230769230769231 (72 evidence-backed of 78 impostor ejections). Test-runner facts: `frontend/vitest.config.ts` (`environment: "node"`, `include: src/**/*.test.ts(x)`) and `frontend/src/components/CostChips.test.ts`:12-14 (an existing node-env `.test.ts` importing a `.tsx` — the precedent this task reuses).), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
