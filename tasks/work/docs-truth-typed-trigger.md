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

Each row: the production line or document changed, the perturbation, the command, and the result.
Every perturbation was made in place, run, and restored by copying the saved file back
(`cmp` confirmed each restore); none used `git checkout`. The new test files alone ran after each
restore: 28 and 10 passed.

| changed thing | perturbation | red tests | green before this card? |
|---|---|---|---|
| `_trigger_is_emergency` body | restore the base substring body | 4 red in the new file: the planted report, its mirror, the declared-kind case and the source scan. The planted report reads `assert {None} == {'p-1'}` (ballot `reporter_id`), the mirror `assert {'p-1'} == {None}`; a diagnostic run over the pair showed all five decisions flipped: report kind with the phrase gave reporter `None`, detector kind `emergency`, no opener reporter context, `is_body_report` False and the stale body stripped, and the mirror gave `p-1`, `report`, a context, True and the body kept | the planted pair is new |
| same | `return False` | 7 red: the mirror, the declared-kind case, and five existing emergency tests in `test_manager.py` | no |
| `kind` field | give it a default of `"report"` | `test_omitting_the_kind_raises_type_error` | new |
| `__post_init__` check | `if False:` | the miscased and the Hypothesis undeclared-kind tests | new |
| `_MEETING_TRIGGER_KINDS` | add `"Emergency"` | the miscased test | the Hypothesis property alone stayed green |
| reply `is_body_report` site | revert to the base substring test | the planted pair (`assert {False} == {True}` and the reverse) and the source scan | new |
| each of the other four decision sites (reporter render id, detector kind, body strip, ballot reporter) | swap `_trigger_is_emergency(trigger)` for the substring, one site at a time | the planted pair, every time | new |
| builder `kind=trigger_event.trigger` | hard-code `kind="report"` | the builder emergency case, the emergency lockstep shape, the lockstep property, the committed-helper emergency case | new |
| builder report description | append the phrase to the report wording | the four report lockstep shapes and the lockstep property | new |
| `eval/reasoning_evidence.py` `kind="emergency"` | `kind="report"` | `test_the_reasoning_evidence_scenario_opens_a_typed_emergency` only (the existing reasoning-scorecard and reasoning-evidence tests: 66 passed) | **yes: green under every existing test** |
| `committed.py::meeting_trigger_kind` | `return "report"` | the committed-helper emergency case only; the four committed-walk suites (`test_evidence_honesty`, `test_contradictions`, `test_schemas_pooling`, `test_transcript`) stayed green, 499 passed | **yes: green under every existing test** |
| the phrase comment block | reintroduce "no structured trigger kind" | the four-passage test | new |
| the four trigger passages | the `e886b663` wordings held as fixed strings | fail the check, one case each | planted in-test |
| ladder paragraph | drop "Baseline 9" | `test_the_ladder_paragraph_names_the_current_baseline`; the `e886b663` paragraph is also planted in-test | new |
| the architecture link | unlink `game-shape.md` | the committed-note test and the link test | new |
| a game-shape symbol | rename `resolve_vent` | the committed-note test and its planted case; one planted case per symbol runs in-test | new |
| a test-site `kind=` | delete it (`tests/meetings/_manager_helpers.py`) | `mypy`: `Missing positional argument "kind" in call to "MeetingTrigger"` | n/a |

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
