# A3: documentation truth and a typed meeting trigger

**Status:** done

## Outcome

Two changes land together, and neither moves a recorded, rendered or published byte.

1. **The meeting layer reads the trigger's kind, not its wording.** Today
   `meetings.manager._trigger_is_emergency` decides "emergency call or body report" by looking for
   the phrase "called an emergency meeting" inside `MeetingTrigger.description`, although the
   orchestrator already holds the engine's typed kind and drops it when it builds the trigger.
   After this card `MeetingTrigger` carries a required `kind: MeetingTriggerKind` (the existing
   `Literal["report", "emergency"]`) with no default. The production builder sets it from the
   engine's `MeetingTriggeredEvent.trigger`, and every decision the manager makes about the
   trigger reads it. The prompt templates keep their own substring branch, because a template
   cannot import a constant, and a lockstep pin proves the two agree on every trigger the
   production builder constructs.
2. **The prose tells the truth about the code at baseline 9.** The stale passages listed under
   Evidence are corrected in place: code comments and docstrings, the glossary's "hard evidence"
   entry, the substrate-ladder paragraph of `docs/architecture.md` (it stops at baseline 8), and
   the ML tier map's table (it reads as current while it describes the baseline-6 corpus).
   `docs/architecture.md` gains a short game-shape facts note: the vent tell, impostors never
   reporting, player-id order with the trigger-tick throwaway, and, until a coherent-reset
   experiment is adopted, corpses that persist and kill cooldowns that pause over meetings. The
   two crew reward terms that pay for guessing roles right are labelled as role-correct rewards
   in a comment, with no value, signature or behaviour change.

This is card 1 of the Stage-B card set: wave 0, dispatched now, merged first. It adds no
experiment field, no lever and no prompt byte; the record impact is nothing.

## Evidence

**Sources.** The decision memo and the investigation memos are under
`/Users/danielkeinan/.claude/projects/-Users-danielkeinan-projects-AiLibi/stage-b-2026-09-24/`:
`decision-memo.md` sections 0.1, 2.6 ("A3"), 3.1 row 1, 3.2 and 3.4 brief 1; `census_and_record.md`
section 6 (this card's investigation). The stale-text list is Part 2, Q7, "Real gaps" items 4 and 6
of `../analysis-2026-09-24/analysis-memo.md` in that same parent directory, detailed in
`../analysis-2026-09-24/code_reflection.md` ("Stale prose"). `DESIGN.md` is historical rationale:
this card cites it and never edits it.

**Line numbers.** Every `path:line` in this card is at `e886b663` and is paired with a symbol. The
implementer re-anchors each one by its symbol at dispatch, before editing.

**The text match, reproduced at `e886b663`.** A trigger that says "reported a body" and also
contains the emergency wording is filed as an emergency:

```
uv run python -c "from meetings.manager import MeetingTrigger, _trigger_is_emergency; print(_trigger_is_emergency(MeetingTrigger(triggered_by='p-1', trigger_tick=8, description='p-1 reported a body at tick 8 after p-4 called an emergency meeting')))"
# prints True at e886b663
```

- The phrase is `EMERGENCY_TRIGGER_PHRASE` (`meetings/manager.py:598`); `_trigger_is_emergency`
  returns `EMERGENCY_TRIGGER_PHRASE in trigger.description` (`:932-943`).
- `MeetingManager` reads it at five sites: the reporter render id (`:1286`), the contradiction
  trigger kind passed to `_detect_contradictions` (`:1557-1559`), the emergency-opening body strip
  (`:1887`), the impostor reply's `is_body_report` (`:2138`, a direct substring test that skips
  the helper) and the ballot's `reporter_id` in `_collect_one_ballot` (`:2218`).
- The typed kind already exists and is dropped: `orchestrator.game._build_meeting_trigger`
  (`orchestrator/game.py:3399`) returns the engine's `trigger_event.trigger` as its third element
  and builds the DTO without it (`:3477`).
- `tests/_helpers/committed.py::meeting_trigger_kind` (`:377-392`) re-derives the kind the same
  way, through `_trigger_is_emergency` on the rebuilt description.
- Construction sites: `git grep -c "MeetingTrigger(" -- '*.py'` counts **34** at `e886b663`, two
  in production code (`orchestrator/game.py:3477`, `eval/reasoning_evidence.py:284`) and 32 in 13
  test files. The memo's "about 35" is this count; re-count at dispatch. Every site passes
  keywords, starting with `triggered_by=`.
- Template branches: `git grep -n 'set [a-z_]* = "called an emergency meeting"' --
  'agents/strategic/prompts/*.j2'` finds **15** `{% set %}` branch lines in 7 prompt-set
  directories. The served set's three are `qwen3_6_27b/crewmate_report.j2:83`,
  `impostor_report.j2:70` and `impostor_report_roll_call.j2:67`. Re-count at dispatch.

**The stale passages.** Each row says what the text claims and what the code at `e886b663` does,
and names the symbol that enforces the truth.

| where (`e886b663`) | what it says | what is true, and its enforcing symbol |
|---|---|---|
| `meetings/schemas.py:983-991` (`BallotGroundingLabel` docstring) | "Every committed recording reads `None`" | every ballot in the four committed sets carries a label (count below); `None` is what a recording made before the field reads (`meetings.manager.label_ballot_grounding`, `_default_vote`) |
| `meetings/schemas.py:1081-1083` (`counter_reason_id`) | every committed recording "reads `None`" | the committed sets record a counter on some ballots and omit it on the rest (count below) |
| `meetings/manager.py:4294`, `:4522` | name `MeetingManager._collect_vote` | no such method exists; the ballot chain is `_collect_one_ballot` (`:2183`). Rename only after confirming the described order holds there; otherwise correct the sentence |
| `meetings/voting.py:29` | "which of the five" rewrite reasons | `BallotTargetRewriteReason` (`meetings/schemas.py:905`) has six values; name the alias rather than a count that rots |
| `agents/memory/beliefs.py:220-221` (`HARD_EVIDENCE_GATE_RENDER_CEIL`) | the model "reads a MUST-SKIP row rather than the MUST-vote" | the retired directive language: the clamp keeps an all-soft row rendering below the ejection floor, and the ballot, not the render, decides (the layer labels and never rewrites, ruling D6) |
| `agents/memory/store.py:94` | lists "heard vent" among first-hand rows | the audio wire carries only the global sabotage alarm (`ObservationService._audible_events`; `AudibleEvent.kind` is `Literal["sabotage_alarm"]`); a witnessed vent is visual only, so no heard-vent row exists |
| `engine/maps/canonical_1.yaml:50-53` | visibility "is uniform across the map" | a crewmate is downgraded to same-room sight at base visibility (`engine.visibility._resolve_observer_visibility_mode`). The file is NOT edited (orchestrator ruling of 2026-09-24, see the digest pre-check below): the fact is stated in the game-shape note |
| `engine/tick.py:399` (`_apply_kill`) | "DESIGN.md section 3.5 (dropped)" | the map's `dead_task_rule` is `redistribute`: the victim's incomplete instances are re-keyed to a living crewmate (`redistribute_dead_tasks`) and dropped only when none is eligible |
| `observation/service.py:670-673` (`_global_view`) | `_apply_kill` "drops a dead player's incomplete instances" | same rule: under `redistribute` a death re-keys instances, so the total shrinks only when no crewmate can take one; the agent-visible denominator still equals the engine's |
| `docs/glossary.md:157` ("hard evidence") | a witnessed vent **or kill** establishes the role | true of the rules, but in the meeting layer only a grounded spoken vent claim mints a proof flag; a witnessed kill pins the witness's own suspicion (`WITNESSED_KILL_SUSPICION_DELTA`) and mints no flag (`ContradictionRef.kind` has no kill kind) and no ballot evidence row (`_own_channel_evidence_rows`) |
| `docs/architecture.md:116-120` | names baselines 7 and 8 | baseline 9 is the current adopting record: the process re-record, `audits/audit-2026-09-22-process-rerecord.md` (the audit `scripts/check_doc_facts.py` reads as `_LADDER_TIP_AUDIT`) |
| `training/README.md:119-122` (tier map) | "the frozen baseline-6 corpus ... is the substrate every instrument below was measured on", as current | a history label: the table's measured basis is the baseline-6 fits; the corpus is baseline 9 and its current fits are in the reports |
| `training/rewards.py::_crew_terms` | `correct_reports` and `patrol_coverage` read as neutral crew terms | both pay for being right about roles: an ejection of an actual impostor, and shadowing an actual impostor read from engine truth. Labelled in a comment; values unchanged under the ML hold |

The two ballot counts, from the committed bytes (count-only; re-measure at dispatch):

```
uv run python -c 'import glob,json,sys
for d in sys.argv[1:]:
  n=g=c=0
  for p in glob.glob(d+"/replay-seed-*.jsonl"):
    for r in map(json.loads,open(p)):
      for b in r.get("ballots") or []:
        n+=1; g+=b.get("grounding_label") is not None; c+=b.get("counter_reason_id") is not None
  print(d,n,g,c)' replays/samples/9p2i replays/samples/4p1i replays/ml_corpus/9p2i replays/ml_corpus/4p1i
```

At `e886b663` it prints 845/845/382 (s9), 117/117/65 (s4), 2,539/2,539/1,202 (c9) and 129/129/56
(c4): 3,630 ballots, all labelled, 1,705 carrying a counter. Neither count goes into a docstring;
the corrected text states the rule, not the tally.

**Three constraints found at `e886b663`.**

1. **The architecture page is at its word ceiling.** `tests/scripts/test_check_doc_facts.py` holds
   `docs/architecture.md` to `_ARCHITECTURE_WORD_BUDGET = 1_300` words (`_word_budget_problems`,
   whitespace split). `uv run python -c "print(len(open('docs/architecture.md').read().split()))"`
   prints **1295**. The baseline-9 sentence and the game-shape note do not fit without room being
   made. The later writers do not rely on words this card leaves spare: the spine puts the wave's
   arm contract on a new linked page (`docs/experiment-arms.md`) and adds one linking sentence
   here, and the record card places its sentence on that page or swaps it in at equal length
   (decision memo 3.2, as amended for this card set). The constant stays unedited by every card.
2. **The map file's digest is recorded.** Its sha256 at `e886b663` begins `070346ce`; `git grep -l
   070346ce` finds it in nine committed audit records (the deduction-candidate and
   investigation-candidate captures, five held-out manifests, the reasoning-evidence scorecard)
   and in one card, each as the provenance of its own run. Read live, the file is bound only by
   the tournament resume fingerprint (`configuration_fingerprint`), by the version-two derivation
   fingerprint (`training.provenance.derivation_fingerprint`, which no committed stamp uses) and
   by the held-out generator sources (`experiments.held_out_prefixes.GENERATOR_SOURCES`), whose
   bands are all archived or converted, with regeneration retired (the docstring of
   `test_the_archived_band_keeps_the_blocks_it_was_frozen_with`). The pre-check found no gate that
   compares the tree's digest with a committed value. The orchestrator nevertheless ruled on
   2026-09-24 that this card leaves the map file byte-identical: the nine records carry that digest
   as the provenance of the runs they describe, and a comment edit would make the tree disagree
   with every one of them for no behavioural gain. The visibility fact goes in the game-shape note.
3. **ML and held-out closures.** Nine files this card edits are in the 109-file version-two
   derivation closure (`training.provenance.derivation_files`): `training/rewards.py`,
   `agents/memory/beliefs.py`, `agents/memory/store.py`, `meetings/manager.py`,
   `meetings/schemas.py`, `meetings/voting.py`, `engine/tick.py`, `observation/service.py`,
   `orchestrator/game.py`. The committed fits are keyed on the version-one identity (the dated
   ruling of 2026-09-23 in [the re-ground card](ml-reground-baseline-9.md)), so none re-stales;
   the offline `verify_ml_evidence` run is the check. Six edited files are held-out generator
   sources; no band owes a restamp.

## Acceptance

- [x] Review correction: the perturbation table's red counts reproduce (round 2). Every row of
  "Planted and perturbed evidence" was re-run over one stated scope, the whole test tree in both
  tiers (`uv run pytest -m "campaign or not campaign" -n auto --dist loadfile -q -rfE -p
  no:cacheprovider`, 8,704 tests, at `39c84cad`), and the table now lists every red test. Over
  the review's own scopes, `return False` gives 10 red in the new file plus
  `tests/meetings/test_manager.py` and 18 in the four Validation directories (36 over the whole
  tree). The three reasoning test files hold 43 tests, and all 43 stay green under the reasoning
  row's edit. The builder row adds the seven prompt-byte golden cases. Results (round 2) quotes
  each command and its counts.
- [x] Review correction: the lockstep property no longer fails on Hypothesis's
  per-example deadline. `test_the_lockstep_pin_holds_over_every_generated_engine_trigger`
  carries `@settings(deadline=None)`; its strategies, assertions and 100 examples are
  unchanged. Proved by the standalone stress run in Results (round 1): at 30 concurrent
  runs the previous head failed 45 of 60 on the deadline and the repaired head passed 60 of
  60. A scratch copy that slows every example by 250 ms fails with `DeadlineExceeded`
  without the setting and passes with it.
- [x] **The kind is typed and required.** `MeetingTrigger` gains `kind: MeetingTriggerKind` with no
  default. A dataclass field without a default cannot follow the defaulted `body_victim_id`, so the
  field goes before it or is keyword-only; every construction names it either way. An unknown
  value raises `ValueError` in `__post_init__` (AGENTS.md load-bearing rule 5). Planted: omitting
  `kind` raises `TypeError`, and `kind="Emergency"` raises `ValueError`. Perturbed: giving `kind`
  a default of `"report"` turns the omission test red.
- [x] **The builder carries the engine's kind.** `_build_meeting_trigger` sets `kind` from
  `MeetingTriggeredEvent.trigger`, and its third return element equals `trigger.kind` for both
  engine triggers. Enforced by a test over a report event and an emergency event; perturbed: a
  builder that hard-codes `kind="report"` fails it on the emergency event.
- [x] **The planted case: the wording no longer decides.** A report-kind trigger whose description
  contains "called an emergency meeting" runs through `MeetingManager.run` as a report: the ballot
  render receives `reporter_id == trigger.triggered_by` (`_collect_one_ballot`), and
  `_detect_contradictions` receives `trigger_kind="report"`. The mirror case also runs: an
  emergency-kind trigger without the phrase is an emergency (reporter `None`, trigger kind
  `"emergency"`). The Evidence reproduction shows today's code answers the other way. On the
  branch, restoring the substring body of `_trigger_is_emergency` turns the planted test red on
  those semantic assertions, not on a `TypeError`, and Results quotes that red output.
- [x] **Every manager decision reads the kind.** All five consumers go through
  `_trigger_is_emergency`, which returns `trigger.kind == "emergency"`, including the direct
  substring test at `:2138`. `git grep -n "in trigger.description" -- meetings/manager.py` prints
  nothing, and `EMERGENCY_TRIGGER_PHRASE` appears in `meetings/manager.py` only at its definition
  and in `__all__`; the producer in `orchestrator/game.py` keeps using it.
- [x] **The lockstep pin.** For every trigger shape the production builder constructs (emergency;
  report naming a present body; report whose body was already consumed, "a body"; report with
  `temporal_observations=True`, naming the public handle), `trigger.kind` equals `"emergency" if
  EMERGENCY_TRIGGER_PHRASE in trigger.description else "report"`: the templates' own test. A
  second assertion reads every `{% set ... = "..." in meeting_trigger %}` (and `not in`) branch
  literal under `agents/strategic/prompts/` and requires each to equal `EMERGENCY_TRIGGER_PHRASE`.
  Perturbed: a builder variant whose report description contains the phrase fails the first
  assertion; a planted template copy with an edited literal fails the second. No template is
  edited.
- [x] **All construction sites pass the kind.** The two production sites and every test site name
  `kind=` (34 at `e886b663`; re-count). `eval/reasoning_evidence.py:284` passes
  `kind="emergency"`. `tests/_helpers/committed.py::meeting_trigger_kind` returns the rebuilt
  trigger's typed `kind` (the engine event's), with no description read, and its docstring says
  so. Test helpers that mirror the manager's substring (`tests/meetings/test_manager_reporter_render.py:384`)
  read the kind; tests that read the phrase out of recorded prompt text
  (`tests/agents/test_beliefs.py:77-86`) read what the model saw and may stay. Results gives each
  such site's disposition.
- [x] **The comments that describe the trigger tell the truth.** The comment above
  `EMERGENCY_TRIGGER_PHRASE` (`meetings/manager.py:590-597`), the `MeetingTrigger` and
  `_trigger_is_emergency` docstrings, and the `_build_meeting_trigger` docstring stop saying the
  meeting layer carries no structured kind. They say instead that the DTO carries the typed kind,
  the renderers still receive only the description, and the lockstep pin ties the two together.
  Mechanism: a test in `tests/meetings/test_meeting_trigger_kind.py` reads the four passages (the
  comment block from the module source, the three docstrings through `inspect.getdoc`), normalizes
  whitespace, and fails if any still contains "no structured trigger kind" or "the one structured
  trigger fact", or does not name `kind`. Planted: the same check over each passage's `e886b663`
  wording, held in the test as fixed strings, fails on all four.
- [x] **Every stale passage in the Evidence table is corrected**, each to a statement that names
  its enforcing symbol. In code files the edits are comments and docstrings only. Enforced by the
  AST guard in Validation: `meetings/schemas.py`, `meetings/voting.py`, `agents/memory/beliefs.py`,
  `agents/memory/store.py`, `engine/tick.py` and `observation/service.py` parse to equal trees at
  base and head once string-literal statements are dropped, and `training/rewards.py` parses to
  an equal tree with them kept (a comment-only edit). Planted: changing
  `HARD_EVIDENCE_GATE_RENDER_CEIL` to `0.58` in a scratch copy makes the guard exit 1. Results
  quotes both runs.
- [x] **The map file stays byte-identical.** `engine/maps/canonical_1.yaml` is not edited: its
  sha256 at the head equals the base's (`070346ce...`), and `git diff --stat <base> <head> --
  engine/maps/` is empty. The stale visibility sentence at `:50-53` is answered by the game-shape
  note, which states the crewmate same-room downgrade with its enforcing symbol. Mechanism: the
  Results reproduction block (below) compares the digests. Planted: a scratch copy with the comment
  edited makes the digest comparison exit 1.
- [x] **The game-shape note** in `docs/architecture.md` states the four facts, each with its
  enforcing symbol:
  - the vent tell: `engine.rules.resolve_vent` makes vent use observable, and the meeting layer
    certifies a spoken vent claim grounded in the speaker's record as a `vent_sighting` flag
    (`meetings.transcript.detect_contradictions`);
  - impostors never reporting: the default `ImpostorPolicy` emits no report intent (its `COVER`
    branch walks or vents away), and self-report is an OFF experiment (`self_report`);
  - player-id order with the trigger-tick throwaway: `order_actions_for_tick` sorts by actor,
    and `advance_tick` returns at the action that opens a meeting, so later actors' actions that
    tick are not applied and the passive step does not run;
  - until a coherent-reset experiment is adopted (`meeting_reset`, default `preserve`), corpses
    other than the reported one persist across meetings (`apply_meeting_result` consumes only
    the reported body) and kill cooldowns pause (`_decrement_cooldowns` runs only on play ticks).
  The note carries no task or audit IDs, no unexplained jargon and no threshold arithmetic. Any
  new term gets a glossary entry. The page stays within `_ARCHITECTURE_WORD_BUDGET` (the
  `_word_budget_problems` test stays green, and the budget constant is not edited). Make room by
  condensing prose on the same page that restates another document. If the facts still do not
  fit, they become a short new `docs/game-shape.md` linked from one architecture sentence, and
  Results records that decision. Mechanism: a new `tests/scripts/test_architecture_truth.py` reads
  the note (from the page, or from `docs/game-shape.md` under the fallback) and requires one
  enforcing symbol per fact: `resolve_vent`, `ImpostorPolicy`, `order_actions_for_tick` and
  `apply_meeting_result`. Planted: the note with any one of the four removed fails, one case per
  symbol.
- [x] **Baseline 9 is named** in the substrate-ladder paragraph (`docs/architecture.md:116-120`)
  as the current adopting record, citing its audit. The glossary's "hard evidence" heading and
  anchor are unchanged while its body is corrected. The `training/README.md` table carries a
  baseline-6 history label pointing at the current reports. Mechanism for the ladder: the same
  `tests/scripts/test_architecture_truth.py` reads the paragraph that opens "Baselines are adopting
  records" and requires "Baseline 9" and the path held in `check_doc_facts._LADDER_TIP_AUDIT`,
  imported as `tests/scripts/test_check_doc_facts.py` imports it and never typed.
  `check_doc_facts` itself does not check that this page names the tip, so this test is the gate.
  Planted: the `e886b663` paragraph, held as a fixed string, fails it. The glossary body and the
  `training/README.md` label are reviewed prose, not an invariant gate (craft rule 2 does not
  apply): Results quotes each before and after, and `bash scripts/check.sh`, which runs
  `check_doc_facts`, stays green on all three.
- [x] **Nothing recorded, rendered or derived moves.** The prompt-byte golden passes on s9 and s4.
  `bash scripts/verify_samples.sh replays/<set>` passes once per set directory for all four sets.
  The four `build_sample_report.py --check` runs and `publish_process_scorecard.py --check` exit 0.
  `uv run pytest -m campaign` passes, and the offline `verify_ml_evidence.py` reports FAIL 0.
  `git diff --stat e886b663 HEAD -- replays api frontend docs/process-scorecard.md
  docs/process-scorecard.json agents/strategic/prompts` prints nothing.
- [x] **The full gate.** `bash scripts/check.sh` exits 0 in a clean worktree at the branch head,
  and Results quotes the real exit code with the pass counts. `uv run python
  scripts/validate_task_docs.py` and `uv run python scripts/check_doc_facts.py` exit 0.

## Constraints

**Wave and order.** Wave 0. Starts now, on `main` at `e886b663`, with no prerequisite. It runs in
parallel with `gameplay-census` (A1), and it **merges first**, before every other Stage-B card.
The arm spine starts only after this card merges. A1 merges `main` after it (never a rebase),
because both edit `tests/_helpers/committed.py` in disjoint regions. B4 later edits the body of the same
`_build_meeting_trigger`, after the spine adds its keyword. The dated direction addendum lands
before wave 1; this card neither needs nor edits it.

**The owner's rulings of 2026-09-24, verbatim, as this card relies on them.**
- "We should implement stage B": this card is the first of the wave's card set.
- "B4. close the tick kill leak": for sequencing only. B4 edits `_build_meeting_trigger`, so the
  typed kind lands first. This card changes no body id and no description text.
- "Hold off on ML as D suggests until gameplay is finished.": the `training/rewards.py` edit is
  comment-only. No reward value, weight, signature, fit or artifact moves.
- "Tour fix can be deferred to after gameplay is finished": no featured-list, viewer or tour edit.

**The orchestrator's decisions, made under the owner's delegation of 2026-09-24** (decision memo
2.6 "A3", 3.2 and 3.4). The kind is required with no default, because a default would silently
file an emergency as a report. The templates keep their substring, and a lockstep pin ties them to
the kind, because editing them would start the prompt-version cascade for no byte change. A3
lands first. The one-writer map in Expected scope applies. R13 applies: no scorecard cell.

**The partial-record principle, where it binds this card.**
- Only the `replays/samples/9p2i` seed set is ever re-recorded in this wave, and only into a
  candidate directory. That is the record card's job; this card records nothing.
- Every Stage-B switch is a `RecordedExperimentConfig` field, default-OFF and omitted from the
  payload at its default. This card adds none, and no `AILIBI_*` lever.
- Every committed recording, derived view, fixture, gate and doc fact keeps verifying
  byte-identically.
- There is no registry prompt bump: no template is edited, and the registry stays at
  `vote_ballot.qwen3_6_27b.v8` with the three `.v6` stamps.
- Role-correctness is reported and never a gate. The rewards comment names the two role-correct
  terms and changes nothing they compute.
- Nothing pushes an agent toward the correct answer, because no prompt byte moves.
- The meeting layer labels and never rewrites: the typed kind changes no label, ballot, target or
  tally.

**Non-goals.**
- No template or prompt-registry edit.
- No change to report or emergency description text, including the kill-tick body id in report
  openings (B4's leak).
- No `RecordedExperimentConfig`, `MeetingEvidenceProfile` or `EXPERIMENT_ENV_NAMES` change.
- No `DESIGN.md` edit.
- No edit to `audits/workflows/extract_gameplay_facts.py`, whose single writer is the readers
  card. Its comment naming `_trigger_is_emergency` stays true, because the function keeps its
  name.
- No scorecard cell, no census cell and no new instrument.
- No ML fit, artifact or refit.
- No live provider call, no `.env`, no held-out band, and no printed prompt or seed-band prefix.
  Censuses are count-only.

**Delivery (the wave rules).**
- Branch `work/docs-truth-typed-trigger` from `e886b663`, with one pull request into `main`.
- Merge or fast-forward; never squash. Never amend a pushed commit. Bring in `main` by merging,
  never by rebasing.
- Every commit body ends with `Card: tasks/work/docs-truth-typed-trigger.md`, immediately followed
  by the `Co-Authored-By:` attribution line the worker's own session supplies (never a model name copied from this card).
- The PR body has the template's sections: Summary, Definition of done (this Acceptance, ticked
  with evidence), Decisions and Questions (None. when nothing blocks). It ends with the Claude
  Code attribution line.
- Agents post no PR comments. The merge is the owner's.
- Budget: `$0`, fake provider and scripted clients only.

**Craft.** Corrected comments explain current intent, with provenance at most one trailing line
(craft rule 1). A claim names its enforcing mechanism (craft rule 5). Every new invariant test
carries its planted or perturbed failure (craft rule 2). Docs and glossary prose follow craft rule
4.

## Expected scope

**Shared files, per the decision memo's one-writer map (3.2).** A3 is the first writer of each;
the later writers start after A3 merges.

| file | A3's region | later writers, in order |
|---|---|---|
| `orchestrator/game.py` | `_build_meeting_trigger`: the `MeetingTrigger(...)` construction (`:3477`) and its docstring | spine, B4 (the same function's body; region-owned), B2, B6 |
| `meetings/manager.py` | `EMERGENCY_TRIGGER_PHRASE` comment, `MeetingTrigger`, `_trigger_is_emergency`, the `:2138` site, docstrings `:4294`, `:4522` | B2, then B6 |
| `meetings/schemas.py` | docstrings `:983-991`, `:1081-1083` | B6 |
| `tests/meetings/test_manager.py` | its six `MeetingTrigger(` constructions and the `_trigger_is_emergency` assertions (`:6069-6086`) | B6 |
| `agents/memory/store.py` | comment `:94` | B2 |
| `engine/tick.py` | comment `:399` in `_apply_kill` | B0 |
| `tests/_helpers/committed.py` | `meeting_trigger_kind` (`:377-392`) | A1 (census cache region; it merges `main` after A3), readers, record plumbing, B2, all serial |
| `docs/architecture.md` | `:116-120` and the game-shape note | spine (one sentence linking its new arm page), B5 (one sentence at equal length, or on the arm page) |
| `docs/glossary.md` | "hard evidence" (`:157`) | spine, B2 |

**Files 3.2 does not list for A3 that its construction sites require.** Declared here; both merge
before any later writer starts.
- `tests/meetings/test_prompt_byte_golden.py`: the one construction at `:1641` only. Readers, B2
  and B6 write the file after A3.
- `tests/training/test_conviction_serving.py`: the constructions at `:705` and `:744` only. B6
  later edits `:378-380` and `:409-411`.

**Files only A3 writes in this wave.**
- `meetings/voting.py`, `agents/memory/beliefs.py`, `observation/service.py`,
  `eval/reasoning_evidence.py`,
  `training/rewards.py` (comments), `training/README.md`, and optionally `docs/game-shape.md`
  (the Acceptance fallback).
- Test construction sites: `tests/orchestrator/test_meeting_integration.py`,
  `tests/training/test_surrogate_runner.py`, `tests/meetings/test_manager_reporter_render.py`,
  `tests/training/test_composed_runner.py`, `tests/meetings/test_public_accounts.py`,
  `tests/meetings/test_corroboration.py`, `tests/meetings/test_account_turn_refusals.py`,
  `tests/meetings/_manager_helpers.py`, `tests/agents/test_impostor_answer_arm.py`,
  `tests/agents/test_beliefs.py`.
- New: `tests/meetings/test_meeting_trigger_kind.py`, holding the required-field, builder,
  planted, lockstep and comment tests; and `tests/scripts/test_architecture_truth.py`, holding the
  ladder-paragraph and game-shape note tests.
- The card itself, for Results.

**Permitted follow-through.** A comment that names a symbol which no longer exists may be
corrected wherever `git grep` finds it, comment-only, and named in Results. At `e886b663` that is
`_collect_vote` in `tests/eval/test_deduction_metrics.py:2083` and
`tests/meetings/test_grounding_label.py:745`. The same retired "MUST-vote / MUST-skip" language
appears beyond the listed site: `agents/memory/beliefs.py:174` and `:1334`,
`meetings/constants.py:31`, and `meetings/manager.py:321`, `:433`, `:1043`, `:2320` and `:2866`.
Some of it describes history, so this card does not rewrite it. Results lists the count-only grep
as a follow-up.

**Not in scope.** Anything under `replays/`, `api/`, `frontend/`, `agents/strategic/prompts/`,
`audits/`, `docs/process-scorecard.*`, `training/artifacts/` and `training/reports/`. Also out:
`orchestrator/experiment_config.py`, `meetings/evidence_profile.py`, `DESIGN.md`,
`tasks/README.md` beyond the derived inventory sentence, and the direction document.

## Record impact

**Nothing moves, now or at the record card.**
- The DTO gains a field that no recording serializes. The recorded `MeetingReplayEntry` carries no
  trigger description or kind; the golden rebuilds the trigger through the builder.
- Every production trigger's typed kind equals its old substring answer; the lockstep pin
  enforces that. So no rendered prompt, contradiction, label, ballot, tally, state hash, report gz,
  scorecard or census figure changes.
- The four sets, their MANIFESTs and reports, the fixtures, the ML artifacts and stamps, and the
  held-out records keep their bytes.
- The ladder tip stays at baseline 9, and `_LADDER_TIP_AUDIT` is unchanged.

**Compatibility.** `MeetingTrigger` is an in-tree DTO. The added required field breaks any caller
that omits it, which is the point. The only construction sites are the 34 in-tree sites; the
training runners take it as a parameter and construct none. The map file is not edited, so its
sha256 (`070346ce...`) and the nine audit records that carry it as their runs' provenance stay in
agreement, and the tournament resume fingerprint (`configuration_fingerprint`) is unaffected.

**Evaluation.** No verdict, cell or bar changes. The reward terms keep their values; the comment
labels them.

**Publication.** A push to `main` republishes the demo bundle (`.github/workflows/pages.yml`
builds it from `replays/samples`, the featured list and the viewer through
`api.replay_loader.ReplayLoader`). This card touches no file under `api/`, `frontend/` or
`replays/`, and no featured entry. `api/` neither constructs a `MeetingTrigger` nor calls
`_build_meeting_trigger` (`grep -rn -e MeetingTrigger -e _build_meeting_trigger api` prints
nothing at `e886b663`). So the bundle rebuilt on merge has the committed bundle's bytes. The
Validation diff guard is the enforcing check. `npm --prefix frontend test` and the e2e are not
required, because the card touches neither `api/` nor `frontend/`; if the guard ever prints a path
under either, both become required and so does a before-and-after bundle diff.

## Validation

```
# base-only reproduction (the planted case is red today)
uv run python -c "from meetings.manager import MeetingTrigger, _trigger_is_emergency; print(_trigger_is_emergency(MeetingTrigger(triggered_by='p-1', trigger_tick=8, description='p-1 reported a body at tick 8 after p-4 called an emergency meeting')))"

# the typed trigger
uv run pytest tests/meetings/test_meeting_trigger_kind.py tests/scripts/test_architecture_truth.py -q
git grep -c "MeetingTrigger(" -- '*.py'                         # every site names kind=
git grep -n "in trigger.description" -- meetings/manager.py     # prints nothing
git grep -n "EMERGENCY_TRIGGER_PHRASE" -- meetings/manager.py   # the definition and __all__ only
uv run pytest tests/meetings tests/orchestrator tests/agents tests/training -q

# comment/docstring-only guard: strings dropped for six files, kept for rewards.py
# (SCRATCH is any directory outside the worktree; plant the 0.58 edit in a copy to see it fail)
B=e886b663; S="$SCRATCH/a3-base"
for f in meetings/schemas.py meetings/voting.py agents/memory/beliefs.py agents/memory/store.py engine/tick.py observation/service.py training/rewards.py; do mkdir -p "$S/$(dirname $f)"; git show $B:$f > "$S/$f"; done
uv run python - "$S" <<'PY'
import ast, sys
from pathlib import Path
def shape(p, keep):
    t = ast.parse(Path(p).read_text())
    if not keep:
        for n in ast.walk(t):
            for k in ("body", "orelse", "finalbody"):
                b = getattr(n, k, None)
                if isinstance(b, list):
                    setattr(n, k, [s for s in b if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant) and isinstance(s.value.value, str))] or [ast.Pass()])
    return ast.dump(t)
files = {"training/rewards.py": True, **{f: False for f in ("meetings/schemas.py", "meetings/voting.py", "agents/memory/beliefs.py", "agents/memory/store.py", "engine/tick.py", "observation/service.py")}}
bad = [f for f, k in files.items() if shape(Path(sys.argv[1]) / f, k) != shape(f, k)]
print("code changed in:", bad or "none"); sys.exit(1 if bad else 0)
PY
# the map: byte-identical to the base (digest 070346ce... unchanged)
git diff --stat "$B" HEAD -- engine/maps/ | tail -1
test "$(git show "$B":engine/maps/canonical_1.yaml | shasum -a 256 | cut -c1-8)" = "$(shasum -a 256 engine/maps/canonical_1.yaml | cut -c1-8)" && echo "map digest unchanged"
git grep -l 070346ce

# nothing recorded, rendered or derived moves
uv run pytest tests/meetings/test_prompt_byte_golden.py -q
for s in samples/9p2i samples/4p1i ml_corpus/9p2i ml_corpus/4p1i; do bash scripts/verify_samples.sh replays/$s; done
for s in samples/9p2i samples/4p1i ml_corpus/9p2i ml_corpus/4p1i; do uv run python scripts/build_sample_report.py --sample-dir replays/$s --check; done
uv run python scripts/publish_process_scorecard.py --check
uv run python scripts/verify_ml_evidence.py                     # offline; FAIL 0; never --complete
uv run pytest -m campaign -q
git diff --stat e886b663 HEAD -- replays api frontend docs/process-scorecard.md docs/process-scorecard.json agents/strategic/prompts   # empty

# docs and the full gate
uv run python -c "print(len(open('docs/architecture.md').read().split()))"   # at most 1300
uv run python scripts/check_doc_facts.py && uv run python scripts/validate_task_docs.py
bash scripts/check.sh; echo "check.sh exit $?"                  # clean worktree, branch head
```

Also run the census `--check` once A1 has merged, if this branch merges `main` after it. Results
quotes each command's exit code and its pass counts, with the red run of the perturbed planted
test and of the planted AST guard. It cites `docs/architecture.md` ("Enforced boundaries";
"Determinism and the substrate ladder") and the observation contract for the vent and visibility
facts. It records these decisions: field order or keyword-only, the map-comment decision, how the
word budget was met (with the page's final word count, which the spine's linking sentence must fit
beside), and each follow-through site. It closes with its limitations.

## Results

Delivered on `work/docs-truth-typed-trigger`, branched from `13f2c4d3`. That commit's code is the
card's `e886b663`: `git diff --name-only e886b663 13f2c4d3` lists only files under `tasks/`. Commits:
`81288720` (the typed trigger and its tests), `d1ea113a` (documentation truth and its tests), and
this card's Results commit. Record impact as declared: nothing recorded, rendered, derived or
published moves (the Verification block below).

References: `docs/architecture.md` "Enforced boundaries" (the kind crosses from the orchestrator
into `meetings/` as a plain `Literal`; no import contract changes and `lint-imports` stays green)
and "Determinism and the substrate ladder" (baseline 9 is now named there);
[the observation contract](../../docs/observation-contract.md) for the vent-witness and visibility
facts; the decision memo `tasks/decision-2026-09-24-stage-b-wave.md` sections 0.1, 2.6 "A3", 3.1
row 1, 3.2 and 3.4 brief 1; `tasks/investigations-2026-09-24/census_and_record.md` section 6.

### What changed

- `meetings/manager.py`: `MeetingTrigger` gains `kind: MeetingTriggerKind` with no default,
  validated in `__post_init__` against `get_args(MeetingTriggerKind)` (held as
  `_MEETING_TRIGGER_KINDS`). `_trigger_is_emergency` returns `trigger.kind == "emergency"`. The
  reply's `is_body_report` (the base's direct substring test) now reads
  `not _trigger_is_emergency(trigger)`, so all five trigger decisions go through the one function.
  The phrase comment, the `MeetingTrigger` and `_trigger_is_emergency` docstrings, the
  `_collect_vote` references (now `_collect_one_ballot`) and the `_reporter_context_for` docstring
  are corrected.
- `orchestrator/game.py::_build_meeting_trigger` passes `kind=trigger_event.trigger`; its docstring
  says the manager decides from the kind and the renderers still receive only the description.
- `eval/reasoning_evidence.py` passes `kind="emergency"`. `tests/_helpers/committed.py::meeting_trigger_kind`
  returns the rebuilt trigger's `kind` and reads no description.
- Stale prose, comments and docstrings only: `meetings/schemas.py`, `meetings/voting.py`,
  `agents/memory/beliefs.py`, `agents/memory/store.py`, `engine/tick.py`, `observation/service.py`,
  `training/rewards.py` (a `#` comment only), `docs/glossary.md` ("hard evidence" body; heading and
  anchor unchanged), `docs/architecture.md`, `training/README.md` (history label) and the new
  `docs/game-shape.md`.
- New tests: `tests/meetings/test_meeting_trigger_kind.py` (28 tests) and
  `tests/scripts/test_architecture_truth.py` (10 tests).

### Decisions

1. **Field order, not keyword-only.** `kind` is a plain field placed before `body_victim_id`; every
   construction in the tree passes it by keyword. A missing kind is a `TypeError` at runtime and a
   strict-mypy `call-arg` error at every site.
2. **The map comment.** `engine/maps/canonical_1.yaml` is not edited (the orchestrator ruling of
   2026-09-24). The crewmate same-room fact, with
   `engine.visibility._resolve_observer_visibility_mode`, is stated on the game-shape page, which
   also says the map comment describes the base setting, not what each role sees.
3. **The word budget: the fallback page.** The page stood at 1,295 of 1,300 words. The one
   subsection that only restates another document, "Observation timing and public identities",
   was condensed: four sentences the observation contract already carries (exact-once delivery,
   tick-row versions, the duplicate typed-handle sentence and the reserved audio position) and the
   spectator version-5 sentence (the contract's version-5 paragraph) were removed, and the link
   sentence now names delivery, recording versions and spectator versions. The baseline-9 sentence
   (15 words) and the linking sentence (15 words) were added. The page is **1,266 words**, which
   leaves 34 words beside the spine's linking sentence. Without the linking sentence the room for
   an in-page note would have been 49 words including its heading, and the five facts with their
   symbols take 398 words on `docs/game-shape.md` (`wc -w`). The only other restating candidate,
   "Current model evidence", holds facts the training README does not carry, and "Explicit cleanup
   experiments" is the spine's region, so the facts went to `docs/game-shape.md`, linked from one
   sentence in the `engine/` paragraph.
4. **A fifth fact.** The game-shape page states the four facts the card names plus the crewmate
   same-room visibility fact (decision 2), and `test_architecture_truth.py` requires a symbol for
   all five.
5. **Three test sites whose description is the bare word "emergency"**
   (`tests/orchestrator/test_meeting_integration.py`, the parity eject; `tests/training/test_conviction_serving.py:744`;
   `tests/training/test_surrogate_runner.py`, the duo runner) take `kind="emergency"`, the word's
   intent. Nothing at those sites reads the kind (the eject-result builder and the surrogate and
   conviction runners read only `triggered_by` and `trigger_tick`), so no expectation moved.
6. **A source scan as well as the grep.** `test_the_manager_hands_the_wording_on_and_decides_nothing_from_it`
   parses `meetings/manager.py` and fails on any load of the phrase constant and on any read of
   `trigger.description` other than the renderer's `meeting_trigger=` argument, with a planted
   source that fails it. This keeps the card's two greps true after this card.

**Follow-through sites** (comment or docstring only unless marked):

| site | disposition |
|---|---|
| `eval/reporter_justice.py` `_meeting_trigger` docstring | outside Expected scope; it said the layer keeps no structured kind. Now says a recorded meeting carries neither kind nor description. Strings-dropped AST comparison with the base: `code changed: False` |
| `meetings/manager.py` `_reporter_context_for` docstring | said the description is the trigger surface; now names `body_victim_id` and `_discoveries_in_window` |
| `meetings/schemas.py` `BallotDecisionBasis` and `primary_reason_observation_id` docstrings | the same "every committed recording reads None" claim as the two listed rows, adjacent; corrected to the rule |
| `tests/eval/test_deduction_metrics.py:2083`, `tests/meetings/test_grounding_label.py:745` | `_collect_vote` renamed `_collect_one_ballot` (the permitted follow-through) |
| `tests/meetings/test_manager.py` | `test_detection_keys_off_the_trigger_description` renamed `test_detection_reads_the_typed_trigger_kind`, comment rewritten, both assertions kept |
| `tests/meetings/test_manager_reporter_render.py:384` helper | reads `trigger.kind == "report"` (it mirrored the substring); the unused phrase import is dropped; the two-corpse comment names `body_victim_id` |
| `tests/agents/test_beliefs.py` `_recorded_reporter` (`:73-88`) and the comment at `:3587` | keep reading the phrase out of the recorded prompt, which is what the model saw; both now say the manager reads the typed kind and the lockstep pin makes the phrase agree |

**Construction sites.** Every `MeetingTrigger` construction names `kind=`. At `e886b663`
`git grep -c "MeetingTrigger(" -- '*.py'` counted 34 in 15 files; mypy found one more,
`trigger.__class__(...)` in `tests/orchestrator/test_meeting_integration.py` (the second meeting of
the client-swap test). At the head the grep counts 41 in 16 files (the 34 plus seven in the new test
file). A count-only AST scan over tracked `.py` files finds 42 constructions (2 production), 41
naming `kind=`, and the one that omits it is the planted `TypeError` test. Kinds: production
builder `trigger_event.trigger`; `eval/reasoning_evidence.py` `"emergency"`. Of the 33 pre-existing
test sites, 9 whose description carries the phrase take `"emergency"`, 21 take `"report"` (both
equal to the base's substring answer, so their behaviour is unchanged), and the 3 bare-word sites of
decision 5 take `"emergency"`.

### Verification

Measured at `d1ea113a`, the implementation head; the Results commit changes only this card and
`tasks/README.md`'s inventory sentence.

```
# base reproduction, on a `git archive e886b663` extraction via PYTHONPATH=<extract> python -P -c ...
True
# the same call at the head
TypeError: MeetingTrigger.__init__() missing 1 required positional argument: 'kind'
# with kind="report" at the head
False

uv run pytest tests/meetings/test_meeting_trigger_kind.py tests/scripts/test_architecture_truth.py -q
38 passed
git grep -n "in trigger.description" -- meetings/manager.py        # prints nothing
git grep -n "EMERGENCY_TRIGGER_PHRASE" -- meetings/manager.py      # :603 definition, :5425 __all__
git grep -n 'set [a-z_]* = "called an emergency meeting"' -- 'agents/strategic/prompts/*.j2' | wc -l
15
uv run pytest tests/meetings tests/orchestrator tests/agents tests/training -q   (run with -n auto --dist loadfile)
3923 passed, 3 xfailed

# comment/docstring-only guard, the card's script verbatim, base copies from e886b663
code changed in: none                                   (exit 0)
# planted: HARD_EVIDENCE_GATE_RENDER_CEIL = 0.58 in a scratch copy of the base
code changed in: ['agents/memory/beliefs.py']           (exit 1)

# the map
git diff --stat e886b663 HEAD -- engine/maps/            # prints nothing
shasum -a 256: base 070346ceabc3... head 070346ceabc3...  -> "map digest unchanged"
# planted: a scratch copy with the visibility comment edited hashes cc9153c4...; the comparison exits 1
git grep -l 070346ce    # 11 files: the nine audit records, this card and tasks/work/semantic-validation.md

# nothing recorded, rendered or derived moves
uv run pytest tests/meetings/test_prompt_byte_golden.py -q          25 passed
bash scripts/verify_samples.sh replays/samples/9p2i                 All 50 samples verified clean.
bash scripts/verify_samples.sh replays/samples/4p1i                 All 50 samples verified clean.
bash scripts/verify_samples.sh replays/ml_corpus/9p2i               All 150 samples verified clean.
bash scripts/verify_samples.sh replays/ml_corpus/4p1i               All 50 samples verified clean.
build_sample_report.py --sample-dir <each of the four sets> --check   "... is consistent with its replays." x4, exit 0
uv run python scripts/publish_process_scorecard.py --check           consistent, exit 0
uv run python scripts/verify_ml_evidence.py    checks: 61 | OK 49 | FAIL 0 | ABSENT 7 | INFO 5
uv run pytest -m campaign -q                   336 passed (-n auto), exit 0
git diff --stat e886b663 HEAD -- replays api frontend docs/process-scorecard.md docs/process-scorecard.json agents/strategic/prompts
                                               # prints nothing

# docs
uv run python -c "print(len(open('docs/architecture.md').read().split()))"     1266
uv run python scripts/check_doc_facts.py        exit 0
uv run python scripts/validate_task_docs.py     exit 0
```

The full gate, `bash scripts/check.sh`, is quoted in the dated subsection below, pinned to the
commit it ran at.

The ballot census the Evidence quotes, re-run count-only in this worktree before any edit (the diff
guard above shows the recordings unchanged at the head): s9 845/845/382, s4 117/117/65, c9
2,539/2,539/1,202, c4 129/129/56. The same walk also
counted `decision_basis` present on every one of the 3,630 ballots, which is why the
`BallotDecisionBasis` docstring was corrected too.

`npm --prefix frontend test` and the e2e were not required: the diff guard prints no path under
`api/` or `frontend/`, and no featured entry moved, so the demo bundle rebuilt on merge has the
committed bundle's bytes.

### Reviewed prose, before and after

These two are reviewed prose, not invariant gates; `check_doc_facts` and `validate_task_docs` stay
green on both.

`docs/glossary.md`, "hard evidence" (heading and anchor unchanged). Before: "In this game's rules,
an attributed witnessed vent or kill establishes an impostor role. The meeting layer grounds a
spoken vent claim against the speaker's actual observation before publishing its proof flag. Other
spoken placements, contradictions and agreement are different evidence classes; a citation alone
does not certify their inference." After: "In this game's rules, an attributed witnessed vent or
kill establishes an impostor role, but the meeting layer certifies only the vent. It grounds a
spoken vent claim against the speaker's own witness record before publishing a `vent_sighting`
proof flag (meeting detector, `detect_contradictions`). A witnessed kill stays with its witness: it
enters the witness's own memory and raises the witness's own suspicion of the killer
(`WITNESSED_KILL_SUSPICION_DELTA`). It publishes no flag, because no contradiction kind names a kill
(`ContradictionRef.kind`), and it adds no row to the witness's ballot evidence
(`_own_channel_evidence_rows`). Other spoken placements, contradictions and agreement are different
evidence classes; a citation alone does not certify their inference." (The linked file names
after each symbol, and the link targets, are omitted here.)

`training/README.md`, section 2. Before: no label; the corpus row read "The frozen baseline-6 corpus
and its committed by-game splits are the substrate every instrument below was measured on", in the
present tense, under a "Measured basis" column. After, above the first table: "History label:
baseline 6. The tables in this section record the baseline-6 corpus and its fits as they stood when
the map was ruled. Their 'Measured basis' numbers and line citations are that record; the reports
have since been re-grounded, so a cited line may now hold a different figure. The committed corpus
under `replays/ml_corpus/` is the baseline-9 re-record, and its current fits are in each report's
baseline-9 re-ground section" (the ballot surrogate, conviction model, composed runner and anchor
study reports, linked). The rows themselves are unchanged.

### Planted and perturbed evidence

This table was re-measured in round 2. The round-2 subsection below says what the first version
got wrong. Each row names the production line, test line or document changed and the one exact
edit made to it. A scratch harness outside the worktree made each edit in place and ran the scope
below. With the edit still in place, it ran every red test again on its own by node id, and each
one failed again. It then restored the file by copying the saved copy back, and a byte comparison
and the sha256 confirmed each restore. No step used `git checkout`.

The scope for every row is the whole test tree in both tiers, 8,704 tests, at `39c84cad`:

```
uv run pytest -m "campaign or not campaign" -n auto --dist loadfile -q -rfE -p no:cacheprovider
```

Unperturbed, it reports `8681 passed, 20 skipped, 3 xfailed` (exit 0). "Red" counts failed plus
errored tests. "Older red" counts the red tests outside this card's two new test files
(`tests/meetings/test_meeting_trigger_kind.py` and `tests/scripts/test_architecture_truth.py`).

| changed thing | edit | red | older red | the red tests |
|---|---|---|---|---|
| `_trigger_is_emergency` body | `return EMERGENCY_TRIGGER_PHRASE in trigger.description` (the base body) | 4 | 0 | in the new file: the planted report (`assert {None} == {'p-1'}`, ballot `reporter_id`), its mirror (`assert {'p-1'} == {None}`), `test_each_declared_kind_constructs_and_decides[emergency]` and the source scan |
| same | `return False` | 36 | 34 | the new file, 2: the mirror and `test_each_declared_kind_constructs_and_decides[emergency]`. `tests/meetings/test_manager.py`, 8: `test_impostor_reply_in_emergency_meeting_gates_off_body_report`; four `TestEmergencyOpeningNoBody` tests (`test_detection_reads_the_typed_trigger_kind`, `test_stubborn_body_is_stripped_after_one_retry`, `test_retry_recovers_a_clean_opening_without_stripping`, `test_body_only_emergency_opening_degrades_to_unsure_after_strip`); and three structured-turn-marker tests (`test_every_dropped_claim_is_recoverable_in_claim_order`, `test_a_recorded_turn_carries_its_annotations_key`, `test_both_recording_branches_record_the_identical_annotations`). `tests/meetings/test_manager_reporter_render.py`, 1: `test_emergency_meeting_never_annotates`. The prompt-byte golden, 7: `test_every_recorded_prompt_re_renders_byte_identically`, `test_every_reconstruction_divergence_is_a_retired_guard` and `test_defaults_are_the_only_lookup_misses` on 9p2i and on 4p1i, plus `test_reconstructed_transcript_matches_the_recording[9p2i]`. `tests/scripts/test_counterfactual_phase21.py`, 18: 7 failed, and 11 errored at the setup of its module fixtures |
| `kind` field | `kind: MeetingTriggerKind = "report"` | 1 | 0 | `test_omitting_the_kind_raises_type_error` |
| `__post_init__` check | `if False:` | 2 | 0 | `test_a_miscased_kind_raises_value_error` and `test_every_undeclared_kind_raises_value_error` |
| `_MEETING_TRIGGER_KINDS` | `(*get_args(MeetingTriggerKind), "Emergency")` | 1 | 0 | `test_a_miscased_kind_raises_value_error`. The Hypothesis property stays green, because it draws random text |
| reply `is_body_report` site | `(EMERGENCY_TRIGGER_PHRASE not in trigger.description)` (the base test) | 3 | 0 | the planted pair and the source scan |
| reporter render id, detector kind, body strip and ballot reporter (four runs, one site each) | `_trigger_is_emergency(trigger)` becomes `(EMERGENCY_TRIGGER_PHRASE in trigger.description)` | 3 each | 0 | the planted pair and the source scan, at every site |
| builder `kind=trigger_event.trigger` | `kind="report"` | 29 | 25 | the new file, 4: `test_the_builder_copies_the_engine_kind[emergency]`, the emergency lockstep shape, the lockstep property and `test_the_committed_walk_helper_returns_the_engine_kind[emergency]`. The prompt-byte golden, 7 (the same seven as `return False`). `test_counterfactual_phase21.py`, 18 (7 failed, 11 errored) |
| builder report description | the report wording ends `at tick {tick} after p-4 {EMERGENCY_TRIGGER_PHRASE}` | 36 | 31 | the new file, 5: the four report lockstep shapes and the lockstep property. The prompt-byte golden, 8: the seven above plus `test_reconstructed_transcript_matches_the_recording[4p1i]`. `tests/meetings/test_corroboration.py`, 3 (`TestRecordedAnchors`). `tests/agents/test_beliefs_hard_evidence_gate.py`, 1 (`test_soft_only_split_by_role`). `tests/experiments/test_held_out_prefixes.py`, 1 (`test_an_unwitnessed_planted_prefix_passes_and_keeps_the_killer_record`). `test_counterfactual_phase21.py`, 18 (7 failed, 11 errored) |
| `eval/reasoning_evidence.py` `kind="emergency"` | `kind="report"` | 1 | 0 | only `test_the_reasoning_evidence_scenario_opens_a_typed_emergency`. Every older test stays green, including the 43 tests in the three reasoning test files |
| `committed.py::meeting_trigger_kind` | `return "report"` | 1 | 0 | only `test_the_committed_walk_helper_returns_the_engine_kind[emergency]`. Every older test stays green, including the 499 default-tier tests of the four committed-walk suites (`test_evidence_honesty`, `test_contradictions`, `test_schemas_pooling` and `test_transcript`) |
| the phrase comment block | the line `# DESIGN.md keeps no structured trigger kind on the meeting layer.` added to the block | 1 | 0 | `test_the_four_trigger_passages_describe_the_typed_kind` |
| the four trigger passages | none: the `e886b663` wordings are held in the test as fixed strings | n/a | n/a | `test_each_base_wording_fails_the_passage_check` has four cases and passes at the head, so the check rejects each base wording |
| ladder paragraph | `Baseline 9, the current one, is` becomes `The current baseline is` | 1 | 0 | `test_the_ladder_paragraph_names_the_current_baseline`. The `e886b663` paragraph is also planted in the test |
| the architecture link | `[The game-shape page](game-shape.md)` becomes plain text | 3 | 0 | `test_the_game_shape_note_names_every_enforcing_symbol`, `test_an_architecture_page_without_the_link_is_rejected` and `test_a_note_carrying_a_task_id_is_rejected` (the last two compare the whole problem list) |
| a game-shape symbol | `resolve_vent` becomes `vent_resolution` in `docs/game-shape.md` | 4 | 0 | `test_the_game_shape_note_names_every_enforcing_symbol`, `test_a_note_missing_one_fact_symbol_is_rejected[venting is visible]`, and the link and task-id tests. The test also plants one case per symbol |
| a test-site `kind=` | `kind="report",` deleted from `_default_trigger` in `tests/meetings/_manager_helpers.py` | 240 | 240 | every test that builds the default trigger fails at construction with `TypeError: MeetingTrigger.__init__() missing 1 required positional argument: 'kind'`: `test_manager.py` 166, `test_weighing_channel.py` 38, `test_grounding_label.py` 23, `test_ballot_observation_citation.py` 5, `test_elicitation_fixtures.py` 4, `test_vote_guard_rationale.py` 3 and `test_vouch_grounding.py` 1, all under `tests/meetings/`. `uv run mypy .` also fails with 1 error: `Missing positional argument "kind" in call to "MeetingTrigger"` |

Diagnostic for the first row, re-run in round 2 through the planted pair's own `_run_watched`.
Under the base body, the report that carries the phrase gets ballot reporter `None`, detector kind
`emergency`, no opener reporter context, `is_body_report` False and the stale body stripped. The
mirror gets `p-1`, `report`, a context, `is_body_report` True and the body kept. At the head each
decision reads the other way, so all five decisions flip.

In the whole-tree run, 15 of the 19 edits are caught only by this card's new tests. Most of that is
by construction. The kind field and its checks are new code, and the comment edit and the three
document edits break text that only this card's tests read. The base body and the five
decision-site edits give the old substring's answer, which is what the older tests were written
against. Two of the 15 are production lines whose old behaviour older tests could have covered:
`eval/reasoning_evidence.py`'s `kind="emergency"` and the helper's `return trigger.kind`. The
other four edits turn older tests red: `return False`, both builder edits, and the deleted
test-site `kind=`.

### Follow-ups (count-only; not done here)

- The retired "MUST-vote / MUST-skip" directive vocabulary: `git grep -c -i -e "MUST-vote" -e "MUST-skip" -- '*.py'`
  finds 67 lines in 16 files, including the sites the card lists. Much of it names the instruments'
  historical verdict classes, so it needs its own card.
- The same "every committed recording reads `None`" claim in `api/replay_loader.py` (the ballot
  view mirror) and `tests/api/test_view_model.py` (a docstring): out of scope, because `api/` edits
  need the bundle proof.
- "83 committed ballots carry the redirect and 6 the uncited coercion" in
  `meetings/schemas.py` (`BallotTargetRewriteReason`) and `tests/meetings/test_grounding_label.py`:
  the four baseline-9 sets carry 0 of each, so those counts describe earlier records.
- `VoteBallot`'s serializer docstring still speaks of moving report bytes "before the re-record".
- `DESIGN.md` section 3.5 still describes the `drop` rule; it is historical and not edited.

### Limitations

- The lockstep pin covers the triggers the production builder constructs, over the engine's id
  shapes (`p-N` players, `body-p-N-T` ids, `body-p-N` public handles). A hand-built trigger can
  still disagree, and then the manager follows the kind while the templates follow the wording.
  The one other production construction (`eval/reasoning_evidence.py`) is pinned to agree.
- The source scan recognizes reads spelled `trigger.description`; a read through another name
  would escape it.
- `test_architecture_truth.py` checks that each game-shape fact names its enforcing symbol, not
  that the fact holds; the behaviour itself is covered by the existing engine, policy and
  orchestrator tests.
- The Hypothesis property draws random text for undeclared kinds, so it did not find the planted
  `"Emergency"` widening; the explicit miscased test does.

### 2026-09-25: the full gate at `c330cf1c`

`bash scripts/check.sh > <log> 2>&1`, run as its own command (no pipe, no compound) in this
worktree, clean at `c330cf1c` (the Results commit), macOS: **exit code 0**.

```
ruff check: All checks passed!         ruff format --check: 525 files already formatted
lint-imports: Contracts: 4 kept, 0 broken.
validate_task_docs: passed, 390 historical phase tasks and 390 prompts; 88 work cards.
generate_prompts --check: All 390 prompts are in sync.
mypy: Success: no issues found in 496 source files
pytest -n auto --dist loadfile: 8345 passed, 20 skipped, 3 xfailed in 645.53s
frontend: lint, tsc:check, vitest (Test Files 20 passed, Tests 558 passed), build
```

The commit that adds this subsection changes only this card.

### Review corrections, round 1 (2026-09-25)

One review lens (correctness and planted proofs) returned one blocking finding over the head
`32a77ab2`. Codex reviewed `32a77ab2` and left no inline comment. The repair is `9b1ed920`, which
changes only `tests/meetings/test_meeting_trigger_kind.py`; the commit that adds this subsection
changes only this card. Nothing recorded, rendered, derived or published moves (re-measured
below).

**The lockstep property failed intermittently on Hypothesis's per-example deadline.**
`test_the_lockstep_pin_holds_over_every_generated_engine_trigger` ran under Hypothesis's default
200 ms deadline (the repo registers no Hypothesis profile), while every example parses the map
YAML and seeds a world through `_meeting_state`. Timed once at a load average near 7,
`load_canonical_map` took 11.7 ms and `seed_initial_state` 0.1 ms; under heavier load an example
ran past 200 ms and Hypothesis raised `FlakyFailure` ("Unreliable test timings"). The property now
carries `@settings(deadline=None)` beneath its `@given`, where the costly properties in
`tests/engine/test_tick_properties.py`, `tests/meetings/test_contradictions.py` and
`tests/observation/test_leak_property.py` carry theirs, with a comment saying why. Its strategies,
assertions and example count are unchanged: `--hypothesis-show-statistics` reports 100 passing
examples, stopped at `settings.max_examples=100`. The file's only other property, the
undeclared-kind one, builds a dataclass per example and keeps the default deadline. With the
deadline off, a slowdown in this property shows as a slow test, not a failure; nothing else about
its strength changes.

Stress measurement, count-only: a scratch script ran
`uv run pytest tests/meetings/test_meeting_trigger_kind.py -k generated_engine_trigger -q -p no:cacheprovider`
standalone N times, P at a time, and counted exit codes and deadline messages. macOS, 10 cores,
with other worktrees' jobs also running.

| head | runs | at a time | pass | fail | deadline failures |
|---|---|---|---|---|---|
| `32a77ab2` (before) | 18 | 1 | 18 | 0 | 0 |
| `32a77ab2` (before) | 36 | 18 | 36 | 0 | 0 |
| `32a77ab2` (before) | 60 | 30 | 15 | 45 | 45 |
| `9b1ed920` (after) | 60 | 30 | 60 | 0 | 0 |
| `9b1ed920` (after) | 18 | 1 | 18 | 0 | 0 |

At 1 and 18 at a time the old head did not reproduce the verifier's 3 of 18 on this machine. At 30
it did, for example `Unreliable test timings! On an initial run, this test took 294.12ms, which
exceeded the deadline of 200.00ms`.

**Perturbed probe for the setting.** A scratch script inserted `time.sleep(0.25)` at the top of the
property's body, in place, first into the repaired file and then into the `32a77ab2` copy; the
repaired file was then restored by copying its saved copy back (`cmp` identical; no
`git checkout`).

| file under the 250 ms slowdown | result |
|---|---|
| `9b1ed920`, with the setting | `1 passed` in 28.01 s |
| `32a77ab2`, without it | `1 failed`: `hypothesis.errors.DeadlineExceeded: Test took 264.92ms, which exceeds the deadline of 200.00ms` |

Both probes came back as expected the first time. The setting is test configuration, so no
committed test pins it; this probe and the stress table are its evidence. After the restore the
two new test files ran: 38 passed.

**Changed expectations: none.** No test was weakened, skipped or deleted; the property keeps its
examples and assertions, and only the per-example wall-time limit is lifted.

**Validation re-measured at `9b1ed920`** (the card's Validation block, each command on its own,
exit codes captured directly; the worktree was clean before and after):

```
uv run python -c "... MeetingTrigger(..., kind='report') ..."   False
uv run pytest tests/meetings/test_meeting_trigger_kind.py tests/scripts/test_architecture_truth.py -q
                                               38 passed, exit 0
git grep -c "MeetingTrigger(" -- '*.py'        41 in 16 files
git grep -n "in trigger.description" -- meetings/manager.py        prints nothing (exit 1)
git grep -n "EMERGENCY_TRIGGER_PHRASE" -- meetings/manager.py      :603 definition, :5425 __all__
git grep -n 'set [a-z_]* = "called an emergency meeting"' -- 'agents/strategic/prompts/*.j2' | wc -l
                                               15
uv run pytest tests/meetings tests/orchestrator tests/agents tests/training -q -n auto --dist loadfile
                                               3923 passed, 3 xfailed, exit 0
comment/docstring-only guard (the card's script, base copies from e886b663)
                                               code changed in: none (exit 0)
git diff --stat e886b663 HEAD -- engine/maps/  prints nothing
shasum -a 256: base 070346ceabc3, head 070346ceabc3
uv run pytest tests/meetings/test_prompt_byte_golden.py -q        25 passed, exit 0
bash scripts/verify_samples.sh replays/samples/9p2i               All 50 samples verified clean.
bash scripts/verify_samples.sh replays/samples/4p1i               All 50 samples verified clean.
bash scripts/verify_samples.sh replays/ml_corpus/9p2i             All 150 samples verified clean.
bash scripts/verify_samples.sh replays/ml_corpus/4p1i             All 50 samples verified clean.
build_sample_report.py --sample-dir <each of the four sets> --check   consistent x4, exit 0
uv run python scripts/publish_process_scorecard.py --check         consistent, exit 0
uv run python scripts/verify_ml_evidence.py    checks: 61 | OK 49 | FAIL 0 | ABSENT 7 | INFO 5
uv run pytest -m campaign -q -n auto           336 passed, exit 0
git diff --stat e886b663 HEAD -- replays api frontend docs/process-scorecard.md docs/process-scorecard.json agents/strategic/prompts
                                               prints nothing
uv run python -c "print(len(open('docs/architecture.md').read().split()))"     1266
uv run python scripts/check_doc_facts.py       exit 0
uv run python scripts/validate_task_docs.py    exit 0 (88 work cards)
```

`bash scripts/check.sh > <log> 2>&1`, run as its own command in this worktree, clean at
`9b1ed920`, macOS: **exit code 0**.

```
ruff check: All checks passed!         ruff format --check: 525 files already formatted
lint-imports: Contracts: 4 kept, 0 broken.
validate_task_docs: passed, 390 historical phase tasks and 390 prompts; 88 work cards.
generate_prompts --check: All 390 prompts are in sync.
mypy: Success: no issues found in 496 source files
pytest -n auto --dist loadfile: 8345 passed, 20 skipped, 3 xfailed in 735.74s
frontend: lint, tsc:check, vitest (Test Files 20 passed, Tests 558 passed), build
```

An earlier `check.sh` run at `9b1ed920` was stopped part-way through pytest and is not quoted: this
card was edited in the worktree while it ran.

### Review corrections, round 2 (2026-09-25)

One review lens (documentation, evidence claims and Codex review) returned one blocking finding
over the head `39c84cad`: the red counts in "Planted and perturbed evidence" did not reproduce.
Codex has not reviewed the branch since `32a77ab2` and has left no inline comment. This round
changes no code, test or document other than this card. The table in "Planted and perturbed
evidence" was rewritten in place from the re-measurement, and the commit that adds this subsection
changes only this card.

**What was wrong.** The first table named no scope for its red counts. Each count came from a run
over a few chosen files, so red tests elsewhere in the tree were left out. The finding reproduced
three rows against the head. The whole-tree re-measurement found eight of the seventeen rows wrong:

| row | stated at `c330cf1c` | re-measured |
|---|---|---|
| `return False` | 7: the mirror, the declared-kind case and five `test_manager.py` emergency tests | 36 over the whole tree. Over the review's two scopes: 10 in the new file plus `tests/meetings/test_manager.py`, where the eight `test_manager.py` tests include three structured-turn-marker tests; and 18 in the four Validation directories, which add `test_emergency_meeting_never_annotates` and the seven prompt-byte golden cases. The whole tree adds 18 in `tests/scripts/test_counterfactual_phase21.py` |
| the four other decision sites | the planted pair | 3 each: the planted pair and the source scan |
| builder hard-codes `kind="report"` | 4 new-file tests | 29: adds the seven golden cases and the 18 counterfactual tests |
| builder report wording carries the phrase | 5 new-file tests | 36: adds eight golden cases, three corroboration anchors, the hard-evidence gate's role split, one held-out prefix test and the 18 counterfactual tests |
| `eval/reasoning_evidence.py` `kind="report"` | "66 passed" for the existing reasoning tests | the three reasoning test files hold 43 tests, and all 43 pass under the edit. The 66 named no scope and does not reproduce, so it is withdrawn. Over the whole tree the new test is the only red |
| the architecture link removed | 2 | 3: the task-id test also compares the whole problem list |
| `resolve_vent` renamed | 2 | 4: the link and task-id tests also compare the whole problem list |
| a test-site `kind=` deleted | mypy only | mypy reports 1 error, and 240 tests fail with the missing-kind `TypeError` |

The other nine rows reproduced as stated: the base body (4), the `"report"` default (1), `if False:`
(2), the `"Emergency"` widening (1), the reply site (3), the helper's `return "report"` (1, with
the four committed-walk suites' 499 tests green), the phrase comment (1), the ladder paragraph
(1), and the passages planted in the test.

**How it was re-measured.** The scratch harness applied each row's edit as one exact string
replacement, and it refuses an anchor that does not occur exactly once. It ran the whole-tree
command quoted above the table, then ran every red test on its own by node id with the edit still in
place. Last, it restored the file from its saved copy and compared bytes and sha256. For the rows
the finding named, it also ran the finding's scopes under the same edit (each command on its own,
exit codes captured directly):

```
# return False
uv run pytest -q -rfE -p no:cacheprovider tests/meetings/test_meeting_trigger_kind.py tests/meetings/test_manager.py
    10 failed, 287 passed                                      (exit 1)
uv run pytest -q -rfE -p no:cacheprovider -n auto --dist loadfile tests/meetings tests/orchestrator tests/agents tests/training
    18 failed, 3905 passed, 3 xfailed                          (exit 1)
# eval/reasoning_evidence.py kind="report"
uv run pytest -q -rfE -p no:cacheprovider tests/eval/test_reasoning_scorecard.py tests/meetings/test_reasoning_evidence.py tests/scripts/test_reasoning_scorecard_cli.py
    43 passed                                                  (exit 0)
# kind= deleted from tests/meetings/_manager_helpers.py
uv run mypy .
    Found 1 error in 1 file (checked 496 source files)         (exit 1)
```

Each row's whole-tree summary line (every run also reports 20 skipped and 3 xfailed):

```
unperturbed                                  8681 passed                      exit 0
_trigger_is_emergency: the base body         4 failed, 8677 passed            exit 1
_trigger_is_emergency: return False          25 failed, 8645 passed, 11 errors  exit 1
kind defaults to "report"                    1 failed, 8680 passed            exit 1
__post_init__: if False                      2 failed, 8679 passed            exit 1
_MEETING_TRIGGER_KINDS widened               1 failed, 8680 passed            exit 1
reply is_body_report: substring              3 failed, 8678 passed            exit 1
reporter render id: substring                3 failed, 8678 passed            exit 1
detector kind: substring                     3 failed, 8678 passed            exit 1
body strip: substring                        3 failed, 8678 passed            exit 1
ballot reporter: substring                   3 failed, 8678 passed            exit 1
builder kind="report"                        18 failed, 8652 passed, 11 errors  exit 1
builder report wording carries the phrase    25 failed, 8645 passed, 11 errors  exit 1
reasoning_evidence kind="report"             1 failed, 8680 passed            exit 1
committed helper returns "report"            1 failed, 8680 passed            exit 1
phrase comment reintroduces the claim        1 failed, 8680 passed            exit 1
ladder paragraph drops Baseline 9            1 failed, 8680 passed            exit 1
architecture link removed                    3 failed, 8678 passed            exit 1
resolve_vent renamed                         4 failed, 8677 passed            exit 1
test-site kind= deleted                      240 failed, 8441 passed          exit 1
```

Every red test failed again when run on its own, and every restore compared equal. The harness
wrote each run's pytest output to a scratch log and kept the summary line and the red node ids.
The logs were then deleted, because a golden failure can carry recorded prompt text. The worktree
was clean before and after the runs.

**Which probes first came back green.** None this round: every edit turned at least one test red.
Two findings from the first version stand. `eval/reasoning_evidence.py`'s `kind="emergency"` and
the helper's `return trigger.kind` are caught only by this card's new tests. The whole-tree run
now confirms that over both tiers.

**Changed expectations: none.** No test was weakened, skipped or deleted, and no test or code
changed in this round.

**Validation re-measured at `745b4de6`**, the commit that rewrote the table. Its code is identical
to `39c84cad`'s, since it changes only this card. Each command ran on its own with its exit code
captured directly, and the worktree was clean before and after:

```
uv run python -c "... MeetingTrigger(..., kind='report') ..."   False
uv run pytest tests/meetings/test_meeting_trigger_kind.py tests/scripts/test_architecture_truth.py -q
                                               38 passed, exit 0
git grep -c "MeetingTrigger(" -- '*.py'        41 in 16 files
git grep -n "in trigger.description" -- meetings/manager.py        prints nothing (exit 1)
git grep -n "EMERGENCY_TRIGGER_PHRASE" -- meetings/manager.py      :603 definition, :5425 __all__
git grep -n 'set [a-z_]* = "called an emergency meeting"' -- 'agents/strategic/prompts/*.j2' | wc -l
                                               15
uv run pytest tests/meetings tests/orchestrator tests/agents tests/training -q -n auto --dist loadfile
                                               3923 passed, 3 xfailed, exit 0
comment/docstring-only guard (the card's script, base copies from e886b663)
                                               code changed in: none (exit 0)
git diff --stat e886b663 HEAD -- engine/maps/  prints nothing
shasum -a 256: base 070346ceabc3, head 070346ceabc3
uv run pytest tests/meetings/test_prompt_byte_golden.py -q        25 passed, exit 0
bash scripts/verify_samples.sh replays/samples/9p2i               All 50 samples verified clean.
bash scripts/verify_samples.sh replays/samples/4p1i               All 50 samples verified clean.
bash scripts/verify_samples.sh replays/ml_corpus/9p2i             All 150 samples verified clean.
bash scripts/verify_samples.sh replays/ml_corpus/4p1i             All 50 samples verified clean.
build_sample_report.py --sample-dir <each of the four sets> --check   consistent x4, exit 0
uv run python scripts/publish_process_scorecard.py --check         consistent, exit 0
uv run python scripts/verify_ml_evidence.py    checks: 61 | OK 49 | FAIL 0 | ABSENT 7 | INFO 5
uv run pytest -m campaign -q -n auto           336 passed, exit 0
git diff --stat e886b663 HEAD -- replays api frontend docs/process-scorecard.md docs/process-scorecard.json agents/strategic/prompts
                                               prints nothing
uv run python -c "print(len(open('docs/architecture.md').read().split()))"     1266
uv run python scripts/check_doc_facts.py       exit 0
uv run python scripts/validate_task_docs.py    exit 0 (88 work cards)
```

`bash scripts/check.sh > <log> 2>&1` ran as its own command in this worktree, clean at
`745b4de6`, on macOS. It gave **exit code 0**:

```
ruff check: All checks passed!         ruff format --check: 525 files already formatted
lint-imports: Contracts: 4 kept, 0 broken.
validate_task_docs: passed, 390 historical phase tasks and 390 prompts; 88 work cards.
generate_prompts --check: All 390 prompts are in sync.
mypy: Success: no issues found in 496 source files
pytest -n auto --dist loadfile: 8345 passed, 20 skipped, 3 xfailed in 459.65s
frontend: lint, tsc:check, vitest (Test Files 20 passed, Tests 558 passed), build
```

An earlier `check.sh` run at `745b4de6` exited 127 at the first frontend step, `eslint: command
not found`, after its Python legs had passed (8345 passed, 20 skipped, 3 xfailed). This fresh
worktree had not yet installed the frontend's dependencies. `npm --prefix frontend ci` installed
them from the committed lockfile and changed no tracked file. The run quoted above came next. The
commit that adds this paragraph changes only this card.
