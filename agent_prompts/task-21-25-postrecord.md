# Agent Prompt — 21.25 After the record: the graduation sweep, the results on the phase's own bytes, the F-class checks re-run

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-21.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 21.25 — After the record: the graduation sweep, the results on the phase's own bytes, the F-class checks re-run, anchored to `AGENTS.md`:62-89 (the Graduation-sweeps rule as amended by its own precedent — *delete the mechanism, keep the stamp key and one history line*; the prose sweep named as the smaller half; `orchestrator/replay.py`'s two registries named as the source of truth for what is still live) and `AGENTS.md`:106-108 (craft rule 3, "Retire means delete", which cross-references rather than restates it), with craft rules 2 and 5 at :102-105 and :112-116 binding every gate and every number this task writes; `audits/audit-phase-20-close.md`:115-123 (F2 — two stale narrations whose own committed pins already disagree with them, routed as a prose-sweep item), :125-152 (F3 — three front-door word budgets, un-gated and exceeded at close HEAD, with the finding's own two halves: each budget was already over at the merge of the contract that set it, and four later contracts widened all three; *a budget nothing can fail is prose*), :154-177 (F4 — the audits index stated the wrong ladder tip and no gate could catch it there; the gate-coverage half routed, not fixed); the precedents this contract fuses, `tasks/phase-20.md` Task 20.37 (the post-record graduation sweep — seventeen resolvers, 332 source lines, 227 test env-lines, and the structural gate that stops them regenerating), Task 20.38 (the before/after column and the two-part verdict shape) and Task 20.41 (the tail-truth pass); the phase's own records — the maintenance re-record audit `audits/audit-phase-21-rerecord.md`, the pre-registration and its decision rule, the offline counterfactual, and the adopting record audit written by 21.24, whose path is read off `scripts/check_doc_facts.py`'s `_LADDER_TIP_AUDIT` after that PR rather than guessed here. Anchors re-verified at HEAD `4002f19b`: `orchestrator/replay.py`:524-546 (`_RETIRED_ALWAYS_ON_LEVERS`, TWENTY-ONE keys in graduation order, the comment at :519-523 naming the adopting records and stating the eight Phase-20 keys were adopted *by owner override of a FINDING verdict*), :568-570 (`_TOGGLEABLE_LEVER_RESOLVERS`, ONE live entry — `impostor_roll_call`, bound to the local mirror at :117), :578-588 (`TOGGLEABLE_SUBSTRATE_FLAG_KEYS`, `SUBSTRATE_FLAG_KEYS`), :591-615 (`substrate_flag_snapshot`, retired keys stamped unconditionally `True`), :617 (`env_var_for_lever`, a pure `f"AILIBI_{key.upper()}"` derivation that depends on no `ENV_*` constant), :623-647 (`retired_levers_stamped_off`, the loader's refusal of a legacy stamp); `grep -rnE 'def [a-z_]+_enabled\(' agents meetings orchestrator` returns exactly TWO hits at HEAD — `agents/strategic/prompts/loader.py`:329 and `orchestrator/replay.py`:117, both the live 18.10 pair — so the tree this task inherits is swept clean and the only residue it can create is its own; `tests/meetings/test_lever_registry.py`:1-31 (the module docstring stating the rule), :46 (`_SWEPT_PACKAGES` = `agents`, `meetings`, `orchestrator`), :51-60 (`_PHASE20_ADOPTED`, the eight keys whose absence makes a stamp legacy), :154-163 (`test_no_accept_and_ignore_resolver_survives`, the AST walk over all three packages), :166-185 and :188-211 (its two planted counter-cases), :254 (the legacy-stamp refusal), :290-298 (the pin that a live resolver survives, so the gate is not a ban on the name); `.env.example`:88-121 (the graduated-always-ON note, "Twenty-one" spelled out, the rule that a graduated name carries no `AILIBI_*=` line, and the closing sentence naming the one live toggle) against `scripts/check_doc_facts.py`:1194 (`check_lever_registry`) and its default-OFF wording guard at :1265-1270; `scripts/check_doc_facts.py`:201-208 (`_README`, `_LADDER_TIP_AUDIT` = `audits/audit-phase-20-baseline-7.md`, `_GLOSSARY`, `_HISTORY`, `_READING_GUIDE`, `_AUDITS_INDEX`), :213-223 (`_LINKED_DOCUMENTS`, `_LESSONS`), :233-234 (`_ML_PAGE`, `_CLAIM_DOCUMENTS`), :237-242 (`_LADDER_TIP_DOCUMENTS` — README, glossary, history and the reading guide; `audits/README.md` is still ABSENT at HEAD, which is F4's routed half), :279 (`_AUDIT_LADDER_TIP`), :291-293 (`_REGENERATED_DATE`, `_WIN_RATE_CLAIM`), :444-457 (the results-table locators) and :450 (`_BEFORE_COLUMN_HEADER = "At baseline 6"` — the hard-coded name of the history column), :459-479 (`_DERIVED_BEFORE_CLAIMS`' member claims and the citation pin), :523-533 (`_PICKER`, `_GUIDE_EXHIBIT`, `_MIN_EXHIBIT_SEEDS` = 2), :538 (`_PROOF_PARTITION_AUDIT` = `audits/audit-phase-19-close.md`), :590-603 (`_DERIVED_BEFORE_CLAIMS` / `_QUOTED_BEFORE_CLAIMS`, the registry that keeps the unchecked set from growing), :609-611 (`_INJUSTICE_SENTENCE`), :712-736 (`check_facts`, the whole check order), :1119 (`check_ladder_tip`), :1835-1878 (`check_before_columns`), :1881-1920 (`check_unowned_history`), :2455-2470 (`results_before_column`), :2525-2537 (`phase_19_partition`), :2587-2599 (`record_partition`), :2650-2662 (`audit_partition`), :2743 (`check_volatile_stamps`), :2799-2843 (`check_guide_narrative`, the guide's PROSE bound to the instrument pins), :3006-3074 (`check_verdict_figures`, reading BOTH `_LADDER_TIP_AUDIT` and `_PROOF_PARTITION_AUDIT`), :3077-3117 (`check_featured_exhibits`); `grep -n word scripts/check_doc_facts.py` finds NO budget check at HEAD, so F3 stands until the prose-truth contract lands its ruling; `wc -w README.md docs/reading-guide.md docs/ml-program.md docs/lessons.md` reads 3,425 / 1,303 / 1,838 / 1,491 at HEAD; README.md:132-152 (the results section — :134 the "current recording, with the one it replaced beside it" sentence, :136 the header row carrying the `At baseline 6` column, :138-144 the seven rows, :146 the *valid* gloss, :148 the vent headline, :150 the verdict passage stating FINDING then the dated owner override), :171 (the status paragraph, already recording the phase-20 close), :217 (the sample-provenance paragraph); `docs/reading-guide.md`:11-26 (the numbers table with its own `At baseline 6` column), :49 (§2, the exhibit paragraph), :77-97 (§3 and the vent cross-tab, 69/83 meetings and the 69/0, 16/14 cells), :108 (§4); `docs/history.md`:160-172 (still headed "## In progress: phase 20" and closing "the phase stays open behind it", which README.md:171 and the close audit already contradict at HEAD) and :176-201 ("Where the sample sets came from", twenty-one graduated settings, and the §6.1 warning paragraph); `docs/ml-program.md`:140-149 (the comparator erratum) and :151-176 (the "What the next recording changed under all of this" section — the ONLY section of that page this task may edit); `frontend/src/components/ReplayPicker.tsx`:103-146 (`FEATURED_GAMES`, seven curated games: `9p2i` seeds 2, 23, 13, 46 and `4p1i` seeds 29, 2, 11).. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-21.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-21-postrecord`
**Depends on:** 21.11, 21.17, 21.24
**Section refs:** `AGENTS.md`:62-89 (the Graduation-sweeps rule as amended by its own precedent — *delete the mechanism, keep the stamp key and one history line*; the prose sweep named as the smaller half; `orchestrator/replay.py`'s two registries named as the source of truth for what is still live) and `AGENTS.md`:106-108 (craft rule 3, "Retire means delete", which cross-references rather than restates it), with craft rules 2 and 5 at :102-105 and :112-116 binding every gate and every number this task writes; `audits/audit-phase-20-close.md`:115-123 (F2 — two stale narrations whose own committed pins already disagree with them, routed as a prose-sweep item), :125-152 (F3 — three front-door word budgets, un-gated and exceeded at close HEAD, with the finding's own two halves: each budget was already over at the merge of the contract that set it, and four later contracts widened all three; *a budget nothing can fail is prose*), :154-177 (F4 — the audits index stated the wrong ladder tip and no gate could catch it there; the gate-coverage half routed, not fixed); the precedents this contract fuses, `tasks/phase-20.md` Task 20.37 (the post-record graduation sweep — seventeen resolvers, 332 source lines, 227 test env-lines, and the structural gate that stops them regenerating), Task 20.38 (the before/after column and the two-part verdict shape) and Task 20.41 (the tail-truth pass); the phase's own records — the maintenance re-record audit `audits/audit-phase-21-rerecord.md`, the pre-registration and its decision rule, the offline counterfactual, and the adopting record audit written by 21.24, whose path is read off `scripts/check_doc_facts.py`'s `_LADDER_TIP_AUDIT` after that PR rather than guessed here. Anchors re-verified at HEAD `4002f19b`: `orchestrator/replay.py`:524-546 (`_RETIRED_ALWAYS_ON_LEVERS`, TWENTY-ONE keys in graduation order, the comment at :519-523 naming the adopting records and stating the eight Phase-20 keys were adopted *by owner override of a FINDING verdict*), :568-570 (`_TOGGLEABLE_LEVER_RESOLVERS`, ONE live entry — `impostor_roll_call`, bound to the local mirror at :117), :578-588 (`TOGGLEABLE_SUBSTRATE_FLAG_KEYS`, `SUBSTRATE_FLAG_KEYS`), :591-615 (`substrate_flag_snapshot`, retired keys stamped unconditionally `True`), :617 (`env_var_for_lever`, a pure `f"AILIBI_{key.upper()}"` derivation that depends on no `ENV_*` constant), :623-647 (`retired_levers_stamped_off`, the loader's refusal of a legacy stamp); `grep -rnE 'def [a-z_]+_enabled\(' agents meetings orchestrator` returns exactly TWO hits at HEAD — `agents/strategic/prompts/loader.py`:329 and `orchestrator/replay.py`:117, both the live 18.10 pair — so the tree this task inherits is swept clean and the only residue it can create is its own; `tests/meetings/test_lever_registry.py`:1-31 (the module docstring stating the rule), :46 (`_SWEPT_PACKAGES` = `agents`, `meetings`, `orchestrator`), :51-60 (`_PHASE20_ADOPTED`, the eight keys whose absence makes a stamp legacy), :154-163 (`test_no_accept_and_ignore_resolver_survives`, the AST walk over all three packages), :166-185 and :188-211 (its two planted counter-cases), :254 (the legacy-stamp refusal), :290-298 (the pin that a live resolver survives, so the gate is not a ban on the name); `.env.example`:88-121 (the graduated-always-ON note, "Twenty-one" spelled out, the rule that a graduated name carries no `AILIBI_*=` line, and the closing sentence naming the one live toggle) against `scripts/check_doc_facts.py`:1194 (`check_lever_registry`) and its default-OFF wording guard at :1265-1270; `scripts/check_doc_facts.py`:201-208 (`_README`, `_LADDER_TIP_AUDIT` = `audits/audit-phase-20-baseline-7.md`, `_GLOSSARY`, `_HISTORY`, `_READING_GUIDE`, `_AUDITS_INDEX`), :213-223 (`_LINKED_DOCUMENTS`, `_LESSONS`), :233-234 (`_ML_PAGE`, `_CLAIM_DOCUMENTS`), :237-242 (`_LADDER_TIP_DOCUMENTS` — README, glossary, history and the reading guide; `audits/README.md` is still ABSENT at HEAD, which is F4's routed half), :279 (`_AUDIT_LADDER_TIP`), :291-293 (`_REGENERATED_DATE`, `_WIN_RATE_CLAIM`), :444-457 (the results-table locators) and :450 (`_BEFORE_COLUMN_HEADER = "At baseline 6"` — the hard-coded name of the history column), :459-479 (`_DERIVED_BEFORE_CLAIMS`' member claims and the citation pin), :523-533 (`_PICKER`, `_GUIDE_EXHIBIT`, `_MIN_EXHIBIT_SEEDS` = 2), :538 (`_PROOF_PARTITION_AUDIT` = `audits/audit-phase-19-close.md`), :590-603 (`_DERIVED_BEFORE_CLAIMS` / `_QUOTED_BEFORE_CLAIMS`, the registry that keeps the unchecked set from growing), :609-611 (`_INJUSTICE_SENTENCE`), :712-736 (`check_facts`, the whole check order), :1119 (`check_ladder_tip`), :1835-1878 (`check_before_columns`), :1881-1920 (`check_unowned_history`), :2455-2470 (`results_before_column`), :2525-2537 (`phase_19_partition`), :2587-2599 (`record_partition`), :2650-2662 (`audit_partition`), :2743 (`check_volatile_stamps`), :2799-2843 (`check_guide_narrative`, the guide's PROSE bound to the instrument pins), :3006-3074 (`check_verdict_figures`, reading BOTH `_LADDER_TIP_AUDIT` and `_PROOF_PARTITION_AUDIT`), :3077-3117 (`check_featured_exhibits`); `grep -n word scripts/check_doc_facts.py` finds NO budget check at HEAD, so F3 stands until the prose-truth contract lands its ruling; `wc -w README.md docs/reading-guide.md docs/ml-program.md docs/lessons.md` reads 3,425 / 1,303 / 1,838 / 1,491 at HEAD; README.md:132-152 (the results section — :134 the "current recording, with the one it replaced beside it" sentence, :136 the header row carrying the `At baseline 6` column, :138-144 the seven rows, :146 the *valid* gloss, :148 the vent headline, :150 the verdict passage stating FINDING then the dated owner override), :171 (the status paragraph, already recording the phase-20 close), :217 (the sample-provenance paragraph); `docs/reading-guide.md`:11-26 (the numbers table with its own `At baseline 6` column), :49 (§2, the exhibit paragraph), :77-97 (§3 and the vent cross-tab, 69/83 meetings and the 69/0, 16/14 cells), :108 (§4); `docs/history.md`:160-172 (still headed "## In progress: phase 20" and closing "the phase stays open behind it", which README.md:171 and the close audit already contradict at HEAD) and :176-201 ("Where the sample sets came from", twenty-one graduated settings, and the §6.1 warning paragraph); `docs/ml-program.md`:140-149 (the comparator erratum) and :151-176 (the "What the next recording changed under all of this" section — the ONLY section of that page this task may edit); `frontend/src/components/ReplayPicker.tsx`:103-146 (`FEATURED_GAMES`, seven curated games: `9p2i` seeds 2, 23, 13, 46 and `4p1i` seeds 29, 2, 11).
**Complexity:** Medium
**Record impact:** post-record — no recorded byte moves in this PR; every figure is quoted from a record already committed, and every deletion is of a branch production already takes.
**Measurement:** `grep -rnE 'def [a-z_]+_enabled\(' agents meetings orchestrator | wc -l` reads 2 — the live 18.10 pair and nothing else — with the PR quoting the same grep run before the sweep so the deleted count is visible; `uv run pytest tests/meetings/test_lever_registry.py -q` green including both planted counter-cases; `uv run python scripts/check_doc_facts.py` green; `uv run pytest tests/scripts/test_check_doc_facts.py tests/api/test_sets.py -q` green including the new perturbation cases — a history cell naming a recording that is no longer the one this record replaced, and a narrative figure drifted from the pin that owns it, each fail the check; `bash scripts/verify_samples.sh` reports 100/100 and `bash scripts/check.sh` is green.

This is the payoff task, and it is three jobs that share one precondition: the record has spoken. The
levers built default-OFF in wave 2 either graduated or did not, the figures the front door states
either moved or did not, and the prose classes the phase-20 close routed forward are either still
true on the new bytes or were re-opened by the act of recording. All three answers exist only after
the adopting record commits, and none of them may be guessed here.

**The sweep half is smaller than its precedent and must stay that way.** Task 20.37 deleted seventeen
accept-and-ignore resolvers, 332 source lines and 227 test env-lines because five graduations had
accumulated the residue; it left behind the structural gate that stops them regenerating, and at HEAD
that gate holds — `grep -rnE 'def [a-z_]+_enabled\(' agents meetings orchestrator` returns exactly
two hits, `agents/strategic/prompts/loader.py`:329 and `orchestrator/replay.py`:117, both halves of
the one live 18.10 toggle. So the only residue this task can face is the residue this phase created:
the wave-2 levers' own resolvers, their `ENV_*` constants and `__all__` entries, the `env` parameters
threaded to reach them, the `if <lever>_enabled():` guards, and the tests that pin the parameter
rather than the behaviour. The rule is unchanged and already written down (`AGENTS.md`:62-89): delete
the mechanism, keep the snake_case key in `_RETIRED_ALWAYS_ON_LEVERS` and one trailing history line
naming the adopting record, then sweep the prose so nothing tells a reader the behaviour can be
switched off.

There is a sequencing consequence the previous generation did not have, and this contract states it
rather than discovering it in CI. `tests/meetings/test_lever_registry.py`:154-163 walks every module
under `agents/`, `meetings/` and `orchestrator/` with `ast` and fails on any `*_enabled` function that
neither reads its `env` argument nor returns anything but a bare `True`. That is precisely the shape a
graduation flip took in the previous phase, so the record's own PR cannot graduate a lever by flipping
its resolver body and leave the deletion to this task — the default tier goes red the moment it does.
Whatever the record's PR had to delete to keep its own gate green is therefore already gone when this
task starts; what is left is the residue a record's re-pin sweep does not reach: parameters and their
call sites, dead branches collapsed to their always-taken side, parameter-pinning tests, the
`.env.example` note, the legacy-stamp roster, and the prose. This task re-verifies the record's
deletions, deletes what remains, and quotes the census both ways in the PR.

**The results half reports a record whose verdict this contract may not assume.** Two branches exist
and the DoD is written for both. If the rule adopted the wave-2 slate, the levers graduate and the
front door states the adoption the way the record states it. If the rule returned a FINDING and no
override followed, nothing graduates, the three levers stay live env-gated toggles with their
resolvers, parameters, tests and `.env.example` entries intact, and the sweep half is a recorded
no-op — the PR quotes `_TOGGLEABLE_LEVER_RESOLVERS` to prove it rather than passing the bullets in
silence. The precedent for this discipline is the previous phase's own results task, which was
written for two branches and got a third: the pre-registered rule returned **FINDING** — bars 1 and 2
missed, conviction accuracy without engine-certified proof at 61/103 = 0.5922 against a bar of 0.60
and 42 innocent ejections against fewer than 35 — and baseline 7 is canon *by explicit owner override
of that FINDING verdict*, recorded at `audits/audit-phase-20-baseline-7.md` §6.1 (2026-08-26). That
sentence is a standing constraint on every byte written here: no document, table cell, docstring,
comment or commit message may state or imply that those bars passed, that the verdict was ADOPTED
under the rule, or that the substrate was adopted on the arithmetic. Whatever this phase's record
returns is reported in the same two-part shape — the verdict per the rule first, any owner action
second, dated and attributed — and the first half is never softened by the second.

The mechanical work on the front door is small because the machinery was built for it, and the
discipline around it is the whole task: **quote, do not compute.** Every figure comes from the record
audit or from the test pin that owns it, and a figure with no pin does not enter the front door. Two
gate constants are the exception that needs real thought rather than a re-quote.
`scripts/check_doc_facts.py`:450 hard-codes the history column's name as `At baseline 6`, and :538
hard-codes `_PROOF_PARTITION_AUDIT` as the phase-19 close, parsed by `phase_19_partition` (:2525) —
together those decide *which* recording the front door's before column is history of. This phase
commits bytes twice: once as maintenance of the record on the corrected substrate, whose audit
publishes every instrument cell before and after, and once as the adopting record. The column can
only be history of one of them, and the honest answer is the recording the current one replaced. Move
the constants with the prose or the column silently becomes a claim about a recording two generations
back while `check_before_columns` (:1835) keeps passing, because agreement between two tables cannot
see a header that means something else than it did.

**The F-class half is a re-run, not a re-fix, and the distinction is the point.** F2 is a class, not
two lines: a narration whose own committed pin already disagrees with it. The prose-truth contract
closes both known instances at HEAD — `orchestrator/game.py`:387-391 still describing an archived v3
prompt set that no longer exists, and `frontend/src/lib/bodies.test.ts`:9 still quoting a
baseline-6 phantom-frame census above two assertions that pin the current bytes — but a record
re-opens the class by construction, because a re-record moves exactly the censuses those sentences
quote. So this task re-runs the sweep on the bytes the phase committed rather than trusting the
earlier fix, fixes what falls inside its own files, and routes the rest with file, line and the
disagreeing pin instead of widening scope. F3 is the reason the reporting has a budget at all: three
front-door word budgets were exceeded at the merge of the contract that set each one, and four later
contracts — a results table, a before/after column, a media block and a tail-truth pass — widened all
three on pages already over. This task is the same shape of contract and must not repeat it: if the
reporting will not fit the gated budget, prose is cut on the same page, never the budget raised to
admit the diff. F4 is a gate-coverage gap whose fix lands upstream; here it is simply re-run, so the
ladder-tip claim is checked on every document that carries it including the audits index.

One boundary decides how large this diff should be, and it is easy to get wrong in the churn
direction. A record's own PR re-quotes every mechanical fact its gate reads — the provenance
paragraph, the ladder-tip sentence, the moved rows in both front-door tables, the curated featured
strip, the constant naming its own audit — because otherwise it cannot merge green. Those clauses are
therefore already correct when this task starts. Re-verify each one and leave it alone: this diff is
the *reporting* plus the prose no gate can see, which is exactly where the previous record's drift
survived — a guide sentence still narrating a superseded ballot count while every table the checker
compares had already been corrected. A results task that rewrites what the record already fixed
buries its own signal in noise.

Nothing observable moves. Every deleted branch is the branch production already takes, so the
committed bytes are the invariant: `verify_samples.sh` at 100/100 and the prompt byte-golden green
are what make each deletion provably equivalent, and if either moves, a deletion was not.

Coordination note (for the orchestrator, pre-dispatch — file-scope overlaps this contract cannot
resolve inside its own header). Three files here are also claimed by contracts that lie outside this
task's dependency closure, which the task-doc validator rejects as an unordered parallel edit:
`scripts/check_doc_facts.py` and `tests/scripts/test_check_doc_facts.py` (the prose-truth contract
lands F3's budget gate and F4's document-tuple fix in the same module), and `docs/ml-program.md` (the
ML re-ground re-publishes that page's arms). Both of those merge well before this task can start, so
the cheapest resolution is a dependency edge from this task to each of them; the alternative is to
split the constants half out. Whichever the orchestrator picks, the section-level split inside
`docs/ml-program.md` stands: this task edits ONLY "What the next recording changed under all of this"
(:151-176), and the arms table, the comparator and the erratum above it belong to the re-ground.

**Files in scope:**
- README.md; (the results table's figures and history cells re-quoted from the record's own pins; the verdict passage in the record's two-part shape; the vent headline and the sample-provenance paragraph re-verified against the new MANIFESTs, and left untouched where the record's own PR already moved them correctly)
- docs/reading-guide.md; (the numbers table held to the README's row for row, the §3 cross-tab re-quoted from the deduction pins, the prose that narrates it, and the §2 exhibit paragraph corrected against the new bytes so every game it names is one the picker still features)
- docs/history.md; (the phase-21 section in the file's existing prose shape, linking the record audit; the phase-20 section's stale "In progress" heading and its "the phase stays open behind it" clause resolved against the close audit and README.md:171, which already disagree with it at HEAD)
- docs/ml-program.md; (ONLY the "What the next recording changed under all of this" section at :151-176 — the record's read of what moved, what did not, and the verdict in its two-part shape)
- scripts/check_doc_facts.py; (`_BEFORE_COLUMN_HEADER` and `_PROOF_PARTITION_AUDIT` with its parser re-pointed at the recording the current one replaced; the new prose figures bound to the pins that own them; no check deleted)
- tests/scripts/test_check_doc_facts.py; (a perturbation case per moved or added check, in the copy-the-tree-substitute-one-string shape the file already uses)
- agents/memory/store.py; (the graduated wave-2 resolvers homed here, their `ENV_*` constants and `__all__` entries deleted; each read site replaced by its always-taken side; one trailing history line per mechanism)
- agents/memory/beliefs.py; (the same, where a graduated lever gates a belief-line or render branch)
- agents/strategic/prompts/loader.py; (the live 18.10 resolver STAYS; only a graduated wave-2 template arm's gate and any dangling cross-reference to a deleted sibling change)
- meetings/manager.py; (the same sweep, plus the `env` plumbing that only fed graduated resolvers)
- meetings/transcript.py; (the same, including any private-helper parameter left with no live reader — a parameter its caller ANDs with real data is DATA-gated and stays)
- meetings/constants.py; (graduated resolvers and their `ENV_*` constants go; every threshold constant STAYS, because a graduated lever's threshold is live policy)
- orchestrator/replay.py; (the graduated keys STAY in `_RETIRED_ALWAYS_ON_LEVERS` in graduation order; the resolver imports, identity bindings and `_TOGGLEABLE_LEVER_RESOLVERS` rows for graduated levers go)
- .env.example; (the newly graduated keys join the always-ON note with their adopting record and its spelled-out count; no graduated lever keeps a variable)
- tests/agents/; (resolver-only classes and tautology halves deleted, behaviour tests kept)
- tests/meetings/; (the same, plus `tests/meetings/test_lever_registry.py`'s adopted-key roster extended so a stamp predating this record is still refused)
- tests/orchestrator/test_replay.py; (the graduated resolver and constant imports, and the parameter pins)

**Files NOT in scope:**
- replays/ and every MANIFEST (the record is done; no recorded byte, cost row or provenance row moves in this PR)
- audits/ (the record audit, the pre-registration and the counterfactual are quoted, never rewritten; the audits index entry for the record belongs to the record's own PR and the close's to the close)
- frontend/src/components/ReplayPicker.tsx and tests/api/test_sets.py (the featured curation and its seed pin are the record's; this task reads them and mirrors them into prose, and `check_featured_exhibits` is what binds the two)
- orchestrator/game.py, frontend/src/lib/bodies.test.ts, replays/ml_corpus/README.md (the F2 instances the prose-truth contract owns; re-verified here on the new bytes and ROUTED with file, line and the disagreeing pin if either has re-opened, never edited)
- agents/strategic/prompts/*/ template bodies (no task outside the prompt-set bump edits a template; a graduation deletes the switch, never the rendered bytes)
- any lever the record did NOT adopt (it stays a live env-gated toggle with its resolver, parameter, tests and `.env.example` entry intact — the 18.10 impostor arm is the standing example and must end this PR exactly as it started it)
- `orchestrator/replay.py`'s `substrate_flag_snapshot` and `retired_levers_stamped_off` semantics (registration and refusal are not re-litigated; only the membership of the two registries and the imports of deleted symbols change)
- eval/, training/ (no instrument, floor or fit moves post-record; a gauge that needs re-pointing after the record is the re-ground's, and is reported here rather than edited)

**Definition of done:**
- [ ] The PR opens by naming the record's verdict and the graduation list, read off the record audit and off `orchestrator/replay.py`'s two registries after that commit — never from this contract's expectations. Every later bullet is executed against that list: a lever in `_RETIRED_ALWAYS_ON_LEVERS` is swept, a lever in `_TOGGLEABLE_LEVER_RESOLVERS` is untouched, and if the list is empty the sweep bullets are recorded as a no-op with the registry quoted rather than passed in silence.
- [ ] For every graduated lever: the resolver, its `ENV_*` constant and `__all__` entry are gone; each `if <lever>_enabled():` read site is replaced by its always-taken side; the `env` parameter is deleted from every signature no live resolver is reachable from, with the PR stating per signature which and why; and each surviving mechanism carries at most ONE trailing provenance line naming the adopting record — the deleted docstring's narration is not migrated into it.
- [ ] `grep -rnE 'def [a-z_]+_enabled\(' agents meetings orchestrator | wc -l` reads 2 and both hits are the live 18.10 pair; `uv run pytest tests/meetings/test_lever_registry.py -q` is green, both planted counter-cases still bite, and the adopted-key roster in that module is extended so a stamp recorded before this record is still refused by `retired_levers_stamped_off`.
- [ ] `SUBSTRATE_FLAG_KEYS` is unchanged in content and order for every key it already carried, the graduated keys sit in `_RETIRED_ALWAYS_ON_LEVERS` in graduation order, `substrate_flag_snapshot()` in a bare environment still stamps every retired key `True` and every surviving toggle `False`, and `.env.example`'s always-ON note names each newly graduated lever with its adopting record, carries the corrected spelled-out count, documents no variable for any of them, and still names exactly the live toggles — `check_lever_registry` green, including its default-OFF wording guard.
- [ ] Every figure the record moved is re-quoted on all three front-door surfaces from the pin or audit section that owns it, with its history cell beside it; the PR lists each row against its source, and no figure in the diff was computed by this task. Rows the record did not move still get a history cell, and it says so.
- [ ] The history column means the recording the current one replaced: `_BEFORE_COLUMN_HEADER` and `_PROOF_PARTITION_AUDIT` (with its parser) name that recording, both front-door tables carry the renamed column on every row, `check_before_columns` and `check_unowned_history` are green, and each row claiming a moved figure is either re-derived by the module or named in the compared-only registry — the PR states which set each row landed in and why the unchecked set did not grow.
- [ ] Every results surface states the record's outcome the way the record states it, in that order: the verdict under the pre-registered rule, naming each bar that missed and by how much, THEN any owner action with its date and grounds and a link to the record audit. No sentence in the diff states or implies that a pre-registered bar passed, that a verdict was ADOPTED under the rule where it was not, or that any substrate was adopted on the arithmetic — the standing constraint that already binds the phase-20 override passage at README.md:150 and the warning paragraph at docs/history.md:187-191.
- [ ] The reading guide's §2 exhibit paragraph names only games `FEATURED_GAMES` still carries and tells the story the new bytes actually tell; `check_featured_exhibits` is green and still meets its two-seed floor, and the §3 cross-tab and the prose that narrates it agree with the deduction pins under `check_guide_narrative`.
- [ ] The F2 class is re-run on the committed bytes, not assumed closed: the PR quotes a repo-wide sweep of narration-versus-pin over the census-quoting sentences a record moves — the phantom-frame control's header, the prompt-set archive narration, the corpus README's derived counts — and each hit is either fixed inside this task's files or routed with file, line, the sentence and the pin that disagrees with it.
- [ ] The word budgets are re-run and not raised: the PR quotes `wc -w README.md docs/reading-guide.md docs/ml-program.md docs/lessons.md` before and after, every gated page ends inside its target, and where the reporting did not fit, prose was cut on the same page rather than the budget widened — with the cut named. The ladder-tip check is re-run across every document that carries the claim, the audits index included.
- [ ] Each check this task adds or re-points ships a perturbation case in `tests/scripts/test_check_doc_facts.py` that fails when the fact is drifted — at minimum a history cell naming the wrong prior recording and a narrative figure moved away from its pin — and the unperturbed copy of the real tree still passes.
- [ ] The diff is the reporting, not churn: every clause the record's own PR already satisfied — the provenance paragraph, the ladder-tip sentence, the moved table rows, the featured curation and the constant naming the record audit — is re-verified and, where correct, left untouched, with the PR listing what it checked and did not change.
- [ ] `bash scripts/verify_samples.sh` reports 100/100 and `tests/meetings/test_prompt_byte_golden.py` is green over every committed meeting; the PR demonstrates the golden still failing on a one-byte perturbation of a template body, so the no-behaviour-moved claim rests on a gate that can fail.
- [ ] `uv run python scripts/check_doc_facts.py` passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Step 1 — read the verdict before touching anything, and write it down first. Open the record audit
written by the adopting record and list, explicitly, which wave-2 levers graduated and which did not.
`orchestrator/replay.py`'s `_RETIRED_ALWAYS_ON_LEVERS` after that commit is the authoritative list;
anything still in `_TOGGLEABLE_LEVER_RESOLVERS` is LIVE and nothing in this task may touch its
resolver, its parameter, its tests or its `.env.example` entry. Put that list at the top of the PR
description before editing a line. If the record adopted nothing, the sweep half is over in one
paragraph and the rest of the task proceeds unchanged.

Step 2 — sweep one lever at a time, never as a bulk regex pass, and commit per lever so a bisect
lands on a single symbol. Per symbol: grep the whole tree for the resolver name and its `ENV_*`
constant before deleting either, and read every hit. Expect three shapes — real read sites (collapse
them to the always-taken side), `__all__` entries (delete), and prose cross-references in modules
outside this task's scope (report, do not widen). After each collapse run that module's own test file
plus `tests/meetings/test_prompt_byte_golden.py` before moving on; a wrong collapse shows up as a
prompt-byte diff immediately, and finding it one lever at a time costs minutes instead of a bisect.
The `env` parameter is the subtle part: delete it only where the grep proves no live resolver is
reachable from that call chain, and remember that a data-gated parameter is not a lever-gated one —
folding a parameter whose caller ANDs it with real data to a constant is a silent behaviour change
dressed as a deletion, which is exactly what the previous sweep had to be corrected for.

Step 3 — build the number ledger before touching a document. Read the record audit cell by cell and,
for each figure, find the pin that owns it: the deduction instrument for the proof/no-proof cross-tab,
the honesty instrument for the bar cells, the citation instrument for the ballot row, the set
MANIFESTs for provenance and win rates, `scripts/verify_samples.sh` for the reconstruction claim. Put
the ledger in the PR body first. Anything with no pin does not enter the front door — it goes in the
PR as a question instead.

Step 4 — the history column is two constants and a parser, not a find-and-replace.
`_BEFORE_COLUMN_HEADER` (:450) names the column in both tables and in the error strings;
`_PROOF_PARTITION_AUDIT` (:538) and `phase_19_partition` (:2525) decide which audit the previous
partition is read out of, and `record_partition` (:2587) reads the current one off the record's own
pre-registered bar sections. If the recording the column is history of is now the phase's own
maintenance re-record, its audit's shape is a before/after instrument publication rather than a bar
table, so the parser is re-written for that shape rather than re-pointed at it — and the rewrite
carries a perturbation case, because a parser that returns `None` makes `check_verdict_figures` and
`check_conviction_partition` return early and pass vacuously. That silent-vacuum failure mode is the
one to test for first.

Step 5 — the verdict passage is two sentences and no more, immediately followed by the link to the
record audit: the verdict under the rule with the bars it missed, then any owner action with its date.
Resist every instinct to add a mitigating clause to the first and every instinct to let the second
retroactively soften it. The same two sentences, in the same order, go on all three surfaces; the
record audit carries the reasoning and the next decision, and this task re-argues nothing.

Step 6 — walk the diff sentence by sentence before opening the PR and ask, for each, "what does a
reader run or open to check this?" Then run the budgets. If a page is over, cut prose on that page —
the sentence with no answer to the first question is the one to cut — and never move the budget to
admit the diff. That inversion is the whole content of the finding this task exists not to repeat.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import counterfactual_phase21"`
- `uv run python -c "import meetings.constants"`
- `uv run python -c "import meetings.schemas"`
- `uv run python -c "import agents.strategic.prompts.loader"`
- `uv run python -c "import orchestrator.game"`
- `uv run python -c "import eval.deduction_metrics"`
- `uv run python -c "import meetings.corroboration"`
- `uv run python -c "import meetings.transcript"`
- `uv run python -c "import meetings.manager"`
- `uv run python -c "import meetings.render_contract"`
- `uv run python -c "import orchestrator.game.TacticalAgent"`
- `uv run python -c "import eval.reporter_justice"`
- `uv run python -c "import training.rewards"`
- `uv run python -c "import training.bakeoff.harness"`
- `uv run python -c "import training.surrogate.fidelity"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import eval.replay_walk.ReplayWalkConfig"`
- `uv run python -c "import engine.tick"`
- `uv run python -c "import training.surrogate.dataset"`
- `uv run python -c "import training.surrogate.runner"`
- `uv run python -c "import training.conviction.fidelity"`
- `uv run python -c "import eval.accusation_calibration"`
- `uv run python -c "import eval.meeting_quality"`
- `uv run python -c "import eval.watchability.SupplyFloors"`
- `uv run python -c "import eval.vj_instruments"`
- `uv run python -c "import eval.vj_instruments.VJInstrumentReport"`
- `uv run python -c "import eval.vj_instruments.VJMeetingRow"`
- `uv run python -c "import frontend/src/lib/contradictions"`
- `uv run python -c "import check_doc_facts"`
- `uv run python -c "import scripts.verify_ml_evidence"`

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
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
If the task mentions engine-free boundary schemas, keep agents/ free of engine imports and put engine translation only in orchestrator-owned code.

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-21-postrecord` with a title like `task 21.25: after the record: the graduation sweep, the results on the phase's own bytes, the f-class checks re-run`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing `AGENTS.md`:62-89 (the Graduation-sweeps rule as amended by its own precedent — *delete the mechanism, keep the stamp key and one history line*; the prose sweep named as the smaller half; `orchestrator/replay.py`'s two registries named as the source of truth for what is still live) and `AGENTS.md`:106-108 (craft rule 3, "Retire means delete", which cross-references rather than restates it), with craft rules 2 and 5 at :102-105 and :112-116 binding every gate and every number this task writes; `audits/audit-phase-20-close.md`:115-123 (F2 — two stale narrations whose own committed pins already disagree with them, routed as a prose-sweep item), :125-152 (F3 — three front-door word budgets, un-gated and exceeded at close HEAD, with the finding's own two halves: each budget was already over at the merge of the contract that set it, and four later contracts widened all three; *a budget nothing can fail is prose*), :154-177 (F4 — the audits index stated the wrong ladder tip and no gate could catch it there; the gate-coverage half routed, not fixed); the precedents this contract fuses, `tasks/phase-20.md` Task 20.37 (the post-record graduation sweep — seventeen resolvers, 332 source lines, 227 test env-lines, and the structural gate that stops them regenerating), Task 20.38 (the before/after column and the two-part verdict shape) and Task 20.41 (the tail-truth pass); the phase's own records — the maintenance re-record audit `audits/audit-phase-21-rerecord.md`, the pre-registration and its decision rule, the offline counterfactual, and the adopting record audit written by 21.24, whose path is read off `scripts/check_doc_facts.py`'s `_LADDER_TIP_AUDIT` after that PR rather than guessed here. Anchors re-verified at HEAD `4002f19b`: `orchestrator/replay.py`:524-546 (`_RETIRED_ALWAYS_ON_LEVERS`, TWENTY-ONE keys in graduation order, the comment at :519-523 naming the adopting records and stating the eight Phase-20 keys were adopted *by owner override of a FINDING verdict*), :568-570 (`_TOGGLEABLE_LEVER_RESOLVERS`, ONE live entry — `impostor_roll_call`, bound to the local mirror at :117), :578-588 (`TOGGLEABLE_SUBSTRATE_FLAG_KEYS`, `SUBSTRATE_FLAG_KEYS`), :591-615 (`substrate_flag_snapshot`, retired keys stamped unconditionally `True`), :617 (`env_var_for_lever`, a pure `f"AILIBI_{key.upper()}"` derivation that depends on no `ENV_*` constant), :623-647 (`retired_levers_stamped_off`, the loader's refusal of a legacy stamp); `grep -rnE 'def [a-z_]+_enabled\(' agents meetings orchestrator` returns exactly TWO hits at HEAD — `agents/strategic/prompts/loader.py`:329 and `orchestrator/replay.py`:117, both the live 18.10 pair — so the tree this task inherits is swept clean and the only residue it can create is its own; `tests/meetings/test_lever_registry.py`:1-31 (the module docstring stating the rule), :46 (`_SWEPT_PACKAGES` = `agents`, `meetings`, `orchestrator`), :51-60 (`_PHASE20_ADOPTED`, the eight keys whose absence makes a stamp legacy), :154-163 (`test_no_accept_and_ignore_resolver_survives`, the AST walk over all three packages), :166-185 and :188-211 (its two planted counter-cases), :254 (the legacy-stamp refusal), :290-298 (the pin that a live resolver survives, so the gate is not a ban on the name); `.env.example`:88-121 (the graduated-always-ON note, "Twenty-one" spelled out, the rule that a graduated name carries no `AILIBI_*=` line, and the closing sentence naming the one live toggle) against `scripts/check_doc_facts.py`:1194 (`check_lever_registry`) and its default-OFF wording guard at :1265-1270; `scripts/check_doc_facts.py`:201-208 (`_README`, `_LADDER_TIP_AUDIT` = `audits/audit-phase-20-baseline-7.md`, `_GLOSSARY`, `_HISTORY`, `_READING_GUIDE`, `_AUDITS_INDEX`), :213-223 (`_LINKED_DOCUMENTS`, `_LESSONS`), :233-234 (`_ML_PAGE`, `_CLAIM_DOCUMENTS`), :237-242 (`_LADDER_TIP_DOCUMENTS` — README, glossary, history and the reading guide; `audits/README.md` is still ABSENT at HEAD, which is F4's routed half), :279 (`_AUDIT_LADDER_TIP`), :291-293 (`_REGENERATED_DATE`, `_WIN_RATE_CLAIM`), :444-457 (the results-table locators) and :450 (`_BEFORE_COLUMN_HEADER = "At baseline 6"` — the hard-coded name of the history column), :459-479 (`_DERIVED_BEFORE_CLAIMS`' member claims and the citation pin), :523-533 (`_PICKER`, `_GUIDE_EXHIBIT`, `_MIN_EXHIBIT_SEEDS` = 2), :538 (`_PROOF_PARTITION_AUDIT` = `audits/audit-phase-19-close.md`), :590-603 (`_DERIVED_BEFORE_CLAIMS` / `_QUOTED_BEFORE_CLAIMS`, the registry that keeps the unchecked set from growing), :609-611 (`_INJUSTICE_SENTENCE`), :712-736 (`check_facts`, the whole check order), :1119 (`check_ladder_tip`), :1835-1878 (`check_before_columns`), :1881-1920 (`check_unowned_history`), :2455-2470 (`results_before_column`), :2525-2537 (`phase_19_partition`), :2587-2599 (`record_partition`), :2650-2662 (`audit_partition`), :2743 (`check_volatile_stamps`), :2799-2843 (`check_guide_narrative`, the guide's PROSE bound to the instrument pins), :3006-3074 (`check_verdict_figures`, reading BOTH `_LADDER_TIP_AUDIT` and `_PROOF_PARTITION_AUDIT`), :3077-3117 (`check_featured_exhibits`); `grep -n word scripts/check_doc_facts.py` finds NO budget check at HEAD, so F3 stands until the prose-truth contract lands its ruling; `wc -w README.md docs/reading-guide.md docs/ml-program.md docs/lessons.md` reads 3,425 / 1,303 / 1,838 / 1,491 at HEAD; README.md:132-152 (the results section — :134 the "current recording, with the one it replaced beside it" sentence, :136 the header row carrying the `At baseline 6` column, :138-144 the seven rows, :146 the *valid* gloss, :148 the vent headline, :150 the verdict passage stating FINDING then the dated owner override), :171 (the status paragraph, already recording the phase-20 close), :217 (the sample-provenance paragraph); `docs/reading-guide.md`:11-26 (the numbers table with its own `At baseline 6` column), :49 (§2, the exhibit paragraph), :77-97 (§3 and the vent cross-tab, 69/83 meetings and the 69/0, 16/14 cells), :108 (§4); `docs/history.md`:160-172 (still headed "## In progress: phase 20" and closing "the phase stays open behind it", which README.md:171 and the close audit already contradict at HEAD) and :176-201 ("Where the sample sets came from", twenty-one graduated settings, and the §6.1 warning paragraph); `docs/ml-program.md`:140-149 (the comparator erratum) and :151-176 (the "What the next recording changed under all of this" section — the ONLY section of that page this task may edit); `frontend/src/components/ReplayPicker.tsx`:103-146 (`FEATURED_GAMES`, seven curated games: `9p2i` seeds 2, 23, 13, 46 and `4p1i` seeds 29, 2, 11).), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
