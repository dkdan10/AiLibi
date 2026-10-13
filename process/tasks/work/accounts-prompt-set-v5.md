# Revise the accounts prompts to v5: a citable turn id and the SKIP register

**Status:** done

## Outcome

The candidate ballot prompt tells the voter which bracketed id on the page is a
ballot citation, and carries the reference family's SKIP discipline in the same
words. Those are the fifth run's two live candidate-only defects: the arm cited
a public turn on 0 of its 150 ballots, and it authored 119 EJECTs where the
reference authored 14, so the run compared the accounts surface and the ballot
register at once and could attribute neither. `ACCOUNT_PROMPT_SET_REVISION`
reads `v5`, so no recorded stamp straddles two generations of the bodies. The
manifest states, before anything is measured again, that the turn-id repair is
one-sided and RAISES the wrongful net on its own, which is why it ships only in
the wave that also carries the relevance-aware guard. Nothing is recorded and
no rule the run is judged by moves.

## Evidence

[The diagnosis of 2026-09-18](../diagnosis-2026-09-18-fifth-run.md) names both
defects; the owner approved its ten decisions as a set on 2026-09-18 and the
memo's section 11 records the rulings. Decisions 4 (F4) and 6 (F7) are this
card. Only `combined_accounts` renders these bodies, being the arm that sets
both account levers (`experiments/fresh_deduction_instrument.py:1040-1048`),
while `repaired_clock` (`:1034-1039`) renders the reference family. The bytes
that ran are the bytes at `42c7181f`: `vote_ballot_accounts.j2` hashes to
`c97d972e...`, that run's own `checkpoint-final.json` digest for it.

**F4, the dead turn channel.** `_account_transcript.j2:19,22` renders each
evidence row as `[turn:<turn_id>:obs|whereabouts:N]` or
`[turn:<turn_id>:claim:N]`. `meetings/manager.py:3198` recovers a non-canonical
`primary_reason_id` only through `_REASON_ID_TURN_SUFFIX` (`:628`), end-anchored
on `:turn-(\d+)`, so a row suffix blocks recovery and `:3203` nulls the id; with
both fields null, `guard_ballot_citation` (`:3710`, zero-flag branch at
`:3780-3799`) coerces the EJECT to SKIP unless the target carries a flag.

| Figure, of 150 ballots per arm | reference | candidate |
| --- | --- | --- |
| Surviving `primary_reason_id` | 14 | 0 |
| Nulled `primary_reason_id` | 0 | 27 |
| Authored EJECT / SKIP | 14 / 136 | 119 / 31 |
| Guard rewrites | 1 redirect | 44 `uncited_coerced`, 2 redirects |

Every cell is a counts-only re-tally of the ballot records under
`audits/deduction-candidate/run-2026-09-16/`, nulls read off the
`INVALID_REASON_ID_MARKER` prefix (`meetings/manager.py:355`). Of the 27 nulled
ids, 20 end `:claim:N` and 6 `:obs:N`; 26 of 27 strip to a real turn id in that
meeting naming the ballot's own authored target: evidence present, wrong shape.

The ballot prompt is where the shape is missing. `vote_ballot_accounts.j2:21`
works a bare-id example for `primary_reason_observation_id` only and asks an
ejection for "either a public transcript turn or a reference copied from YOUR
OWN private memory" without giving the turn id's form; `:23` prefills
`primary_reason_id` null with no shape and no warning. `vote_ballot.j2:266`
gives both: copy it VERBATIM from the bracketed transcript lines, and never
invent or abbreviate an id. Its skeleton is not portable with them:
`vote_ballot.j2:263` prefills `transcript.turns[-1].turn_id` into the object a
model copies verbatim, and 7 of the reference's 14 surviving citations are that
last-turn id, support without relevance, rejected in memo section 6 and by
[the v4 card](accounts-prompt-set-v4.md) for the observation id.

**The transcript needs no second id, and must not get one.** Decided on the
archive: `_account_transcript.j2:17` already renders the bare canonical turn id
at the head of every turn line and all 150 candidate vote prompts carry it, so
what they lack is an instruction naming it. Those prompts also carry 5,109
sub-row ids, a median of 36.5 each, so a per-row bare id would mint a third
vocabulary and move `accusation_round_accounts.j2:8` with it.

**F7, the register confound.** The arms differ in the accounts surface AND in
the ballot register, so the run cannot attribute the candidate's 8.5x rise in
willingness to accuse to the surface (memo section 4). The reference states the
SKIP discipline twice, at `vote_ballot.j2:114` ("SKIP if the evidence is too
thin") and `:259` ("SKIP is the sound call, and ejecting anyway must rest on
evidence you can cite below, never on momentum"); the candidate gives one
clause each at `:1` and `:21`.

## Acceptance

- [x] Review correction: the BRACKETS. `vote_ballot_accounts.j2:21` says the id
  `primary_reason_id` takes is the one printed INSIDE the brackets that open a
  turn's transcript line, copied without the brackets themselves — not "the
  turn id in the bracket", which a voter satisfies by copying `[<id>]`, a form
  `_normalize_ballot_reason_id` (`meetings/manager.py:3195-3210`) nulls because
  it strips nothing and `_REASON_ID_TURN_SUFFIX` (`:628`) is end-anchored. The
  form is given as the placeholder `<meeting id>:turn-<n>`, the one shape
  `meetings.manager._turn_id` (`:2895-2903`) mints, and no real turn id of the
  rendered meeting reaches the instructions or the skeleton.
- [x] Review correction: the ROWS. The same sentence describes the evidence
  rows as the column-0 bullets `_account_transcript.j2:19,22` actually renders
  (`- [turn:...] ...` at the start of its own line), not as "indented rows",
  and no rendered ballot prompt of any arm calls them indented.
- [x] F4, the shape and the warning, on `vote_ballot_accounts.j2:21`. It names
  the bracket at the head of each transcript turn line as the one id a ballot
  may cite in `primary_reason_id`, names the `[turn:...:claim:N]` rows as
  pointers to evidence INSIDE a turn that are not ballot ids, and ports
  `vote_ballot.j2:266`'s warning rather than re-inventing it: copy it verbatim,
  never abbreviate, never append a row suffix, with the consequence, that an id
  which is not this meeting's turn id is nulled (`meetings/manager.py:3203`)
  and the uncited ejection coerced (`:3792-3799`).
- [x] F4, no prefill and no second id: the skeleton at `:23` still reads
  `"primary_reason_id":null`, no real turn id of the rendered meeting appears in
  the ballot prompt, and `_account_transcript.j2` keeps its bytes.
- [x] F7, the SKIP register. `vote_ballot_accounts.j2:21` carries
  `vote_ballot.j2:259`'s two clauses, that a thin strongest suspect makes SKIP
  the sound call and that ejecting anyway must rest on evidence you can cite
  and never on momentum; `:1` carries `vote_ballot.j2:114`'s "if the evidence
  is too thin". Ported wording, so the arms differ in the accounts surface
  only. The register is all that is ported: no confidence sentence ships, mean
  confidence 0.711 against 0.543 having moved no ejection, with 0 authored
  EJECT in either arm below the 0.6 cutoff `tally_ballots` applies
  (`meetings/voting.py:187`).
- [x] `ACCOUNT_PROMPT_SET_REVISION` advances `v4` to `v5`
  (`agents/strategic/prompts/loader.py:1248`), so the four account bodies
  advance as a unit (`loader.py:1259-1267`) and every stamp
  `public_account_prompt_versions` composes (`:1276-1289`) carries `v5`. Every
  test composing the stamp DERIVES it from the constant rather than hard-coding
  a literal: `tests/agents/test_public_account_prompts.py:190`,
  `_account_stamps` (`:155-172`), the recorded-capture pin (`:204-216`) and the
  pre-v4 frozenset at `:1089`, which becomes the pre-v5 set (`:1228`).
- [x] The arm-surface digest move is declared, not discovered. Every file of
  `agents/strategic/prompts/qwen3_6_27b` is hashed into `arm_surface_digests`
  (`experiments/fresh_deduction_instrument.py:4941-4969`, `ARM_SURFACE_SOURCES`
  at `:4927-4935`), so this edit moves it and the comparison at `:5430-5435`
  refuses a resume begun before this card; the card names the fifth run's
  `checkpoint-final.json` as what stops matching.
- [x] `audits/deduction-candidate/execution-manifest.md` gains a dated section
  "Accounts prompt set v5 (2026-09-18)" stating the change, its basis (the
  diagnosis, linked) and its DECLARED EFFECTS, both one-sided and both on the
  candidate arm. F4 alone RAISES the wrongful net: restoring only the sub-row
  coercions gives the memo's re-tally of 20 ejections, 6 role-correct and 14
  wrongful, moving the net from +7 to +13 against a permitted 2, which is why
  decision 4 ships it only in the wave that also carries [the relevance-aware
  guard](relevance-aware-citation-guard.md). F7 lowers ejection volume and
  removes the register confound, without which the [diagnostics
  card](fresh-deduction-instrument-diagnostics.md)'s per-ballot figures do not
  compare across arms; the frozen analysis is unmoved.
- [x] Planted proofs, each red before the fix and green after, on synthetic
  seed-free inputs through `build_prompt_renderers("qwen3_6_27b",
  public_account_version=1, attributed_testimony_version=1)`, in the idiom of
  `tests/agents/test_public_account_prompts.py:1092-1171`: drop the shape
  sentence; drop the row-suffix clause; prefill the skeleton's
  `primary_reason_id` with the meeting's last turn id; drop either
  SKIP-register sentence; set the revision back to `v4`.
- [x] No recording and no re-record. These templates are reachable only
  behind two default-OFF levers: `public_account_version` and
  `attributed_testimony_version` default to `None`
  (`orchestrator/experiment_config.py:44-45`,
  `meetings/evidence_profile.py:74-75`), `.env.example:249-250` carries both
  switches commented at `0`, and `public_account_prompt_versions` returns
  `None` when neither is set (`loader.py:1272-1273`). The `audits/` byte change
  recomputes `docs/artifacts.md`'s audits row (today `25,974,591 tracked bytes
  / 324 files`, `:109`), `tasks/README.md`'s derived inventory sentence (`:43`)
  is updated for this card, and `scripts/verify_ml_evidence.py` passes offline.

## Constraints

Candidate family only, and within it one rendered template. `vote_ballot.j2`,
`accusation_round.j2`, `_account_transcript.j2`, `_account_rules.j2` and every
other template keep their bytes; this card ports from the reference, never
editing it. No live provider call of any kind: fake and replay providers only,
no calibration, no recording, no re-record, no re-scored report. The primary
outcome, its rubric, the decision rule, the minimum actionable effect,
`WRONGFUL_EJECTION_TRADEOFF` and `STOP_RULE` do not change
(`experiments/fresh_deduction_instrument.py:659`, `:661`, `:672`, `:677`,
`:693`, `:722`); this card changes what the candidate is asked for, never what
it is judged by, and per decision 7 the tradeoff is not restated. No limit moves
([the fifth limits card](fresh-deduction-limits-5.md) fixed them). F5 and F8 are
out of scope of every card of this wave, so the shared reason-id normalizer
(`meetings/manager.py:628`, `:3198`) keeps its bytes and `meetings/schemas.py`
gains no second citation slot.

The owner's merge authorizes the label `v5`, the section date and the declared
effect that F4 alone moves the wrongful net from +7 to +13, which is the memo's
re-tally of an archive counterfactual rather than a new measurement. No run may
be authorized on a tree carrying `v5` without
[the relevance-aware guard](relevance-aware-citation-guard.md) merged: decision
4 ships F4 only in the wave that also carries F6, and
[the third calibration](fresh-deduction-calibration-3.md) is what first renders
these bodies, on converted development bands only. No held-out band prefix is
generated, printed or opened: bands 3000-3999 through 8000-8999 are all
development data, and `audits/deduction-candidate/held-out/manifest.json` still
reads `held_out` for 8000-8999 until
[the sixth freeze](held-out-prefix-freeze-6.md) moves it. This card adds no
import, so `agents/` still imports no `engine/` (`.importlinter:20-26`) and
`meetings/` no `experiments/`. No other card in wave A writes to
`agents/strategic/prompts/` or that directory's tests.

## Expected scope

`agents/strategic/prompts/qwen3_6_27b/vote_ballot_accounts.j2` (the whole change
to rendered bytes), `agents/strategic/prompts/loader.py` (the revision constant
and its docstring), `tests/agents/test_public_account_prompts.py` (the v5 render
tests and the pre-v5 frozenset),
`audits/deduction-candidate/execution-manifest.md` (the dated section),
`docs/artifacts.md` (the `audits/` row), `tasks/README.md`'s derived inventory
sentence, this card. NOT in scope, on the evidence above:
`_account_transcript.j2`, the instrument, `meetings/manager.py` and
`meetings/schemas.py`.

Delivered on `work/accounts-prompt-set-v5` and one pull request into `main`,
merged as a merge commit or a fast-forward and never squashed, with the commit
trailer `Card: tasks/work/accounts-prompt-set-v5.md`. Every acceptance item that
adds a gate carries a planted failure. Wave A is this card in parallel with
[the diagnostics card](fresh-deduction-instrument-diagnostics.md), both based on
`main` and sharing no source file; the execution manifest, `docs/artifacts.md`
and `tasks/README.md` are the three the coordinator reconciles at merge. Wave B
is [the guard](relevance-aware-citation-guard.md) on the diagnostics branch,
then [the third calibration](fresh-deduction-calibration-3.md) on all three,
then, once it reports, the sixth authorization with
[its limits card](fresh-deduction-limits-6.md) and
[the sixth freeze](held-out-prefix-freeze-6.md) dispatched alongside that card.

## Record impact

Moves prompt bytes on the candidate arm only, bumps one constant, and amends
the execution manifest (an `audits/` document) with one dated section. No
recording, report, DTO, metric or weight byte moves; no sample set is rebuilt;
no experiment becomes ON; no adopting record is created. The measured
consequence is that the candidate's arm-surface digest changes, so the fifth
run's 100 units are not poolable with anything measured after this card and its
`checkpoint-final.json` no longer matches the tree.

## Validation

`uv run pytest tests/agents tests/meetings tests/experiments -q` (fake and
replay providers only), `uv run python scripts/validate_task_docs.py`,
`uv run python scripts/check_doc_facts.py`,
`uv run python scripts/verify_ml_evidence.py` (offline; never `--complete`),
`uv run pytest tests/scripts/test_verify_ml_evidence.py -q`, and
`bash scripts/check.sh` run whole in a clean worktree, so no gate after the
first failure is masked. No live evaluation, calibration or provider call.

## Results

Delivered on `work/accounts-prompt-set-v5`, based on `66d5c480`. One rendered
template moves, one constant, one test module, one `audits/` document and the
two derived inventory lines. The engine is untouched, `agents/` gained no
import (`.importlinter:20-26` unmoved), and nothing was recorded.

**Where this sits.** `DESIGN.md` §5.2 (the meeting protocol that mints the
`turn_id` a ballot cites) and §5.5 (the tally the ballot feeds);
`docs/architecture.md` "Layering" and "Packages" — the prompt bodies are
`agents/` assets rendered by `agents/strategic/prompts/loader.py`, and the
meeting layer that nulls a non-canonical id is `meetings/`, which this card did
not touch. The design record for the change itself is
[the diagnosis of 2026-09-18](../diagnosis-2026-09-18-fifth-run.md) §3 (the
dead turn channel), §4 (the register confound) and §11 (the owner's rulings),
and the new manifest section
`audits/deduction-candidate/execution-manifest.md` "Accounts prompt set v5
(2026-09-18)".

### Decisions

1. **The shape is named, never shown filled.** `vote_ballot_accounts.j2:21`
   names the id printed INSIDE the brackets that open a transcript turn line —
   copied without those brackets, as the review correction below repaired it —
   as the one id `primary_reason_id` may carry, gives its form as the
   placeholder `<meeting id>:turn-<n>`, and writes the sub-row tags as
   `[turn:<that turn's id>:claim:N]` and its two siblings — placeholders, so no
   turn id of the rendered meeting reaches the instructions or the skeleton.
   The skeleton at `:23` still reads `"primary_reason_id":null`. This follows
   the v4 precedent for the observation id and the memo's §6: the reference
   skeleton prefills `transcript.turns[-1].turn_id` and 7 of its 14 surviving
   citations were that id, support without relevance.
2. **The warning is ported, not re-invented.** "Never invent or abbreviate an
   id" is `vote_ballot.j2:266`'s own sentence, asserted against the reference's
   bytes in
   `test_the_ballot_names_which_bracket_on_the_page_is_a_ballot_citation` so
   that a re-invention that merely reads similar fails the same test a dropped
   clause does. The never-append-a-row-suffix clause is the candidate-only
   addition the reference has no need of, because only the accounts transcript
   renders sub-rows.
3. **The consequence is stated in the prompt.** "anything that is not one of
   this meeting's turn ids is nulled, and a nulled id leaves your ejection
   uncited, which coerces it to SKIP" — `meetings/manager.py:3203` and the
   zero-flag branch at `:3792-3799`. Stated flatly rather than hedged with the
   guard's flag exception: the branch was live in 49 of the fifth run's 50
   candidate units, and a voter reading a hedge has a reason to gamble.
4. **The skeleton sentence covers both fields.** `:21`'s "The skeleton below is
   a SKIP" sentence now says which null to replace for a public turn and which
   for a memory line. Without it the turn channel is described and then never
   connected to the object the model copies — the defect F4 exists to repair,
   half-repaired.
5. **`_account_transcript.j2` keeps its bytes**, as the card decided on the
   archive: `:17` already prints the bare canonical turn id at the head of
   every turn line, and a per-row bare id would mint a third vocabulary and
   move `accusation_round_accounts.j2:8` with it. `git diff --stat` over
   `agents/strategic/prompts/qwen3_6_27b/` names one file.
6. **The register only.** `vote_ballot.j2:114`'s "SKIP if the evidence is too
   thin" is on `:1` and `:259`'s two clauses are on `:21`, word for word. The
   reference's confidence sentence does NOT ship, and
   `test_the_ballot_carries_the_references_skip_register_and_nothing_else`
   asserts its absence from the candidate and its presence in the reference, so
   a later "while we are here" port is red.
7. **The dry-run paragraph was re-measured, not left stale.** The prompt gained
   bytes, so the fake provider's `len // 4` input heuristic moves on the
   candidate arm, and `tests/experiments/test_fresh_deduction_instrument.py`'s
   `test_the_mechanics_check_paragraph_quotes_the_run_it_describes` pins that
   paragraph to a live `run_dry`. Re-measured on this tree, and re-measured
   again by the review correction below, which moved the same figure once more:
   `combined_accounts` 685,904 against 641,246 under the v4 bodies (+7.0%;
   678,772 before the correction, superseded), `repaired_clock`
   892,718 unmoved, sum 1,578,622, about 2.02 M at the memo's 1.28x ratio
   against the 3,844,000 bound (53%). Every graded count in that paragraph —
   50 ejections, 16 role-correct, 34 wrongful, 16 supported-correct, 100 naming
   ballots, 150 supported ballots and 1 guard-rewritten, an arm — is byte-for-
   byte what it was. Editing that paragraph is inside the Expected scope's
   manifest file and is the change's own follow-through, not a second change.

### Review corrections (2026-09-18)

Two wording defects in F4's own new sentence, found by review after the three
verifier lenses passed and repaired before merge. Both are in
`vote_ballot_accounts.j2:21` and nowhere else; no other file's bytes move for
them, nothing is recorded, and the third calibration is what first renders the
corrected body.

**Finding 1 — the sentence told the voter to copy the brackets.** It read
"`primary_reason_id` takes the turn id in the bracket that OPENS that turn's
transcript line … copied VERBATIM from that line and nothing else". A voter who
does exactly that sends `[<meeting>:turn-0]`, and
`_normalize_ballot_reason_id` (`meetings/manager.py:3195-3210`) strips nothing:
it accepts an id already in the meeting's turn-id set, else re-anchors one whose
trailing ordinal matches `_REASON_ID_TURN_SUFFIX` (`:628`, `r":turn-(\d+)$"`,
END-anchored), else nulls. A bracketed token ends `]`, so it matches neither
branch, is nulled at `:3203` and the now-uncited ejection is coerced to SKIP —
F4's repair reproducing F4's defect, on the one channel F4 exists to open. The
observation half of the same paragraph already said "copy the id WITHOUT the tag
word"; the turn half said no equivalent.

**Finding 2 — the evidence rows are not indented.** The sentence called them
"The indented rows underneath a turn". `_account_transcript.j2:19,22` renders
each as `- [turn:<id>:claim:N] <speaker> stated …` beginning at column 0, flush
with the turn line above it. A voter told to look for indentation is told to
look for something the template never prints.

**The repair.** The two clauses now read, verbatim — fenced rather than quoted
so the placeholders' angle brackets survive as the bytes the template carries:

```text
When a public turn carries the case, "primary_reason_id" takes the turn id
printed INSIDE the brackets that open that turn's transcript line — the id
before "said:", of the form <meeting id>:turn-<n> — copied VERBATIM from
between those brackets, WITHOUT the square brackets themselves, and nothing
else.
```

```text
The rows that follow a turn's line are bullets, each beginning with "- " at
the start of its own line, and are tagged [turn:<that turn's id>:claim:N],
[turn:<that turn's id>:obs:N] and [turn:<that turn's id>:whereabouts:N]: each
points at ONE piece of evidence INSIDE that turn and is not a ballot id, so
cite the turn id from the brackets at the head of the turn's own line and
never append a row suffix (":claim:N", ":obs:N", ":whereabouts:N") to it.
```

(Both are one unwrapped line in the template; the line breaks above are this
card's.)

Everything else the acceptance items name is unmoved: the skeleton at `:23`
still reads `"primary_reason_id":null`, the never-append-a-row-suffix clause is
the same bytes, `vote_ballot.j2`'s ported never-invent-or-abbreviate warning and
the nulled-then-coerced consequence are the same bytes, and no literal turn id
of the rendered meeting appears outside the transcript block
(`test_the_ballot_shows_the_turn_id_shape_without_prefilling_a_real_one`, still
green over the two hand-written ids `m-77:turn-0` / `m-77:turn-1`).

**The form is given, and it is true of every turn id this codebase mints.**
`meetings.manager._turn_id` (`:2895-2903`) is the only site that produces one —
`f"{meeting_id}:turn-{turn_index}"` — and `_collect_turn` overwrites the
identity fields a model sends (`:1866`), so no other shape can reach a
transcript; `meeting_id` is itself `f"{self._game_id()}:meeting-{index}"`
(`orchestrator/game.py:2642`), which is why the placeholder is written
`<meeting id>:turn-<n>` rather than naming a game. `meetings/schemas.py:559` and
the instrument's own `_TRANSCRIPT_TURN_ID` comment
(`experiments/fresh_deduction_instrument.py:2824-2828`) state the same single
form. The placeholder carries angle brackets no real id has and sits in the same
sentence as "copied VERBATIM from between those brackets", so it describes
rather than supplies.

**Gates.** `_TURN_ID_SHAPE` in `tests/agents/test_public_account_prompts.py` is
re-pinned to the corrected span, and the test that owns it,
`test_the_ballot_names_which_bracket_on_the_page_is_a_ballot_citation`, gains
three assertions that are three separate failures: `_TURN_ID_NO_BRACKETS`
("WITHOUT the square brackets themselves"), `_ROW_BULLET_SHAPE` (the bullet
description) and `_ROWS_MISDESCRIBED` — the word "indented" asserted ABSENT from
the ballot every arm renders, over `(1, None)`, `(None, 1)` and `(1, 1)`, since a
misdescription is a property of the body rather than of one lever setting.

**Planted failures.** Each perturbed in the tree, run, and restored. Command
each time, on the bytes this correction delivers:

```sh
uv run pytest tests/agents/test_public_account_prompts.py -q
```

| Perturbation | Red | Failure |
| --- | --- | --- |
| Drop `, WITHOUT the square brackets themselves,` from `:21` | `1 failed, 92 passed` | `test_the_ballot_names_which_bracket_on_the_page_is_a_ballot_citation`: `assert 'WITHOUT the square brackets themselves' in '...'` |
| Restore "The indented rows underneath a turn are tagged" | `1 failed, 92 passed` | the same case, on `assert 'are bullets, each beginning with "- " at the start of its own line' in '...'` |
| Keep the bullet clause and re-insert the word "indented" alone | `1 failed, 92 passed` | the same case, on the `_ROWS_MISDESCRIBED` assertion — so the two gates fire independently rather than one masking the other |

The five planted proofs the card already carried were re-run against the
corrected bytes and are red exactly as recorded above — plants 1 and 2
`2 failed, 91 passed`, plants 3, 4 and 5 `1 failed, 92 passed`, naming the same
cases — and the module is `93 passed` restored.

**The dry-run paragraph moved again.** The corrected sentence is 190 characters
longer, so the fake provider's `len // 4` input heuristic moves on the candidate
arm alone: `test_the_mechanics_check_paragraph_quotes_the_run_it_describes` went
red on `assert '685,904' in ...`. Re-measured by the same procedure the card
used once already, and the manifest paragraph marks the superseded figure the
way it already marks the fourth band's: `combined_accounts` 678,772 → 685,904
(+7.0% over the v4 bodies' 641,246, where the uncorrected v5 read +5.9%),
`repaired_clock` 892,718 unmoved, sum 1,571,490 → 1,578,622, about 2.02 M at the
1.28x ratio against the 3,844,000 bound (53%, from 52%), and the larger arm's
17,854 per unit and its ~22,900 are unmoved because the reference arm is still
the larger. Every graded count in that paragraph is byte-for-byte what it was.
`tests/experiments/test_fresh_deduction_instrument.py` was NOT edited: the pin
test was run only, the sibling card being that module's one writer in this wave.

**The manifest's v5 section is corrected too.** Its F4 bullet described the
change in the imprecise words the prompt used, so it now names the id INSIDE the
brackets and the rows as bullets, and records the correction with its date and
its reason.

### Verification

Run whole, in this clean worktree, at the head this card delivers — and run
whole again after the review correction above, which is the run these cells
record. Every gate reports what it reported before the correction; only the wall
times differ, the machine having carried a concurrent run in another worktree.

| Command | Result |
| --- | --- |
| `uv run pytest tests/agents tests/meetings tests/experiments -q` | `3132 passed in 240.26s` |
| `uv run python scripts/validate_task_docs.py` | `Task docs validation passed: 390 historical phase tasks and 390 prompts; 66 work cards.` |
| `uv run python scripts/check_doc_facts.py` | `Doc facts verified` / `Front door verified` / `Budgets verified`, exit 0 |
| `uv run python scripts/verify_ml_evidence.py` | `checks: 60 \| OK 48 \| FAIL 0 \| ABSENT 7 \| INFO 5`, `every check passed` |
| `uv run pytest tests/scripts/test_verify_ml_evidence.py -q` | `80 passed in 91.95s` |
| `uv run pytest tests/agents/test_public_account_prompts.py -q` | `93 passed` |
| `bash scripts/check.sh` | exit 0, the code read directly and never through a pipe: ruff `All checks passed!`, `lint-imports` `Contracts: 4 kept, 0 broken.`, `validate_task_docs`, `generate_prompts --check`, `mypy` (`Success: no issues found in 480 source files`), `7827 passed, 20 skipped, 3 xfailed` in 727.15s, frontend `19` files / `515` tests and a green build |
| `bash scripts/verify_samples.sh` (not listed by this card; run anyway, the account bodies being reachable from no committed replay) | exit 0, `All 50 samples verified clean.` for `4p1i` and for `9p2i` |

The `audits/` byte change recomputes `docs/artifacts.md:109`: 25,974,591 →
25,980,491 tracked bytes over the same 324 files, and the review correction's
own manifest edits carry it on to 25,981,839
(`git ls-files audits` with the change staged), and
`scripts/verify_ml_evidence.py` compares that row against disk offline.
`tasks/README.md:43`'s derived sentence moves 6 ready / 60 done → 5 ready /
61 done for this card's own flip; the sibling diagnostics card of wave A
touches the same sentence and the same `audits/` row, and the coordinator
reconciles both at merge.

### Planted failures

Five, one per gate this card adds, each perturbed in the tree, run, and
restored from the index. Run as
`uv run pytest tests/agents/test_public_account_prompts.py -q` each time; the
suite is 93 tests and green on the delivered bytes.

| Perturbation | Red | Failure |
| --- | --- | --- |
| Drop the turn-id shape sentence from `vote_ballot_accounts.j2:21` | `2 failed, 91 passed` | `test_the_ballot_names_which_bracket_on_the_page_is_a_ballot_citation`, `test_a_body_carrying_the_v5_bounds_cannot_be_stamped_an_older_revision` |
| Drop the never-append-a-row-suffix clause | `2 failed, 91 passed` | the same two |
| Drop `:259`'s "never on momentum" clause | `1 failed, 92 passed` | `test_the_ballot_carries_the_references_skip_register_and_nothing_else`: `assert 'ejecting anyway must rest on evidence you can cite below, never on momentum' in ...` |
| Prefill the skeleton with `{{ transcript.turns[-1].turn_id }}` | `1 failed, 92 passed` | `test_the_ballot_shows_the_turn_id_shape_without_prefilling_a_real_one`: `assert '"primary_reason_id":null' in '{"voter":"p-1",...,"primary_reason_id":"m-77:turn-1",...}'` |
| Set `ACCOUNT_PROMPT_SET_REVISION` back to `"v4"` | `1 failed, 92 passed` | `test_a_body_carrying_the_v5_bounds_cannot_be_stamped_an_older_revision`: `AssertionError: assert 'v4' not in frozenset({'v1', 'v2', 'v3', 'v4'})` |

Every case renders through
`build_prompt_renderers("qwen3_6_27b", public_account_version=1,
attributed_testimony_version=1)` on synthetic, seed-free inputs — the
`_account_prompts` helper's own one-turn transcript, and for the prefill case a
two-turn transcript with the hand-written ids `m-77:turn-0` and `m-77:turn-1`,
so a prefill of "the last turn" is visible as a plain substring. No band is
generated, opened or read anywhere in this card.

### The arm-surface digest, declared

Every file of `agents/strategic/prompts/qwen3_6_27b` is hashed into
`arm_surface_digests` (`experiments/fresh_deduction_instrument.py:4941-4969`,
`ARM_SURFACE_SOURCES` at `:4927-4935`), so moving
`vote_ballot_accounts.j2` moves that mapping and `loader.py` moves it twice
over. The comparison at `:5430-5435` therefore refuses any resume whose
checkpoint was written before this card: concretely
`audits/deduction-candidate/run-2026-09-16/checkpoint-final.json`, the fifth
run's own, which recorded
`vote_ballot_accounts.qwen3_6_27b.v4.accounts1.attributed1` and the pre-v5
digest for that file. That is the intended refusal, and it is why the fifth
run's 100 units are not poolable with anything measured after this card. No
constant pins the digest, so nothing needed re-pinning.

### The stamp derives, it is not typed

`ACCOUNT_PROMPT_SET_REVISION` is `"v5"` (`agents/strategic/prompts/loader.py`),
with a docstring bullet naming the two edits. The four account bodies advance
as a unit, so every stamp `public_account_prompt_versions` composes reads
`..._accounts.qwen3_6_27b.v5.accounts<N>.attributed<M>`. Every test that
composes a stamp reads it off the constant: `_account_stamps`, the arm test,
the recorded-capture pin (which asserts each composed stamp is absent from the
two 2026-09-06 candidate captures) and the revision test, whose frozenset is
now `_PRE_V5_REVISIONS = {"v1", "v2", "v3", "v4"}`. No literal `"v5"` is typed
into a test.

### Limitations

- **This card cannot say the repair works.** It changes what the candidate is
  asked for; whether a 27B model then cites the head bracket is a question for
  [the third calibration](fresh-deduction-calibration-3.md), on converted
  development bands. Everything measured here is a render assertion and an
  offline heuristic.
- **F4 alone makes the tradeoff worse, by the memo's own re-tally**: 20
  ejections, 6 role-correct, 14 wrongful, wrongful net +7 → +13 against a
  permitted 2. That figure is a counterfactual over the committed archive, not
  a measurement, and it is why no run may be authorized on a tree carrying `v5`
  without [the relevance-aware guard](relevance-aware-citation-guard.md)
  merged. The manifest section states this before anything is measured.
- **F7's direction is asserted from the reference's behaviour, not measured**:
  the reference authored 14 EJECTs under this register against the candidate's
  119 under one clause of it, which is a correlation across two arms that also
  differ in the accounts surface. The claim that F7 LOWERS the candidate's
  volume is a design expectation the third calibration tests, and the reason it
  ships is that leaving the register unequal leaves the diagnostics card's
  per-ballot figures uninterpretable across arms either way.
- **The prompt's stated consequence is slightly stronger than the code's.**
  `guard_ballot_citation` coerces an uncited EJECT only when the target carries
  no contradiction flag; the prompt says it coerces. The gap is deliberate
  (decision 3 above) and is one-way: a voter who cites correctly is never
  penalised by the simplification.
- **"No real turn id in the ballot prompt" is scoped to the instructions.** The
  rendered transcript necessarily prints every turn's id — that is the channel
  being taught. The test excises the `<transcript>`…`</transcript>` block and
  asserts no meeting turn id survives anywhere else, which is the honest
  reading of the acceptance item.
- **Contradiction flags are not addressed.** The candidate's detector went
  nearly silent on the fifth run (1 flag against 14), which is what makes the
  guard's zero-flag branch live in 49 of 50 units. That is F6's and F8's
  territory and out of scope of every card of this wave.
