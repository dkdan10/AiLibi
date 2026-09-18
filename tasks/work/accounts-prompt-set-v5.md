# Revise the accounts prompts to v5: a citable turn id and the SKIP register

**Status:** ready

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

- [ ] F4, the shape and the warning, on `vote_ballot_accounts.j2:21`. It names
  the bracket at the head of each transcript turn line as the one id a ballot
  may cite in `primary_reason_id`, names the `[turn:...:claim:N]` rows as
  pointers to evidence INSIDE a turn that are not ballot ids, and ports
  `vote_ballot.j2:266`'s warning rather than re-inventing it: copy it verbatim,
  never abbreviate, never append a row suffix, with the consequence, that an id
  which is not this meeting's turn id is nulled (`meetings/manager.py:3203`)
  and the uncited ejection coerced (`:3792-3799`).
- [ ] F4, no prefill and no second id: the skeleton at `:23` still reads
  `"primary_reason_id":null`, no real turn id of the rendered meeting appears in
  the ballot prompt, and `_account_transcript.j2` keeps its bytes.
- [ ] F7, the SKIP register. `vote_ballot_accounts.j2:21` carries
  `vote_ballot.j2:259`'s two clauses, that a thin strongest suspect makes SKIP
  the sound call and that ejecting anyway must rest on evidence you can cite
  and never on momentum; `:1` carries `vote_ballot.j2:114`'s "if the evidence
  is too thin". Ported wording, so the arms differ in the accounts surface
  only. The register is all that is ported: no confidence sentence ships, mean
  confidence 0.711 against 0.543 having moved no ejection, with 0 authored
  EJECT in either arm below the 0.6 cutoff `tally_ballots` applies
  (`meetings/voting.py:187`).
- [ ] `ACCOUNT_PROMPT_SET_REVISION` advances `v4` to `v5`
  (`agents/strategic/prompts/loader.py:1248`), so the four account bodies
  advance as a unit (`loader.py:1259-1267`) and every stamp
  `public_account_prompt_versions` composes (`:1276-1289`) carries `v5`. Every
  test composing the stamp DERIVES it from the constant rather than hard-coding
  a literal: `tests/agents/test_public_account_prompts.py:190`,
  `_account_stamps` (`:155-172`), the recorded-capture pin (`:204-216`) and the
  pre-v4 frozenset at `:1089`, which becomes the pre-v5 set (`:1228`).
- [ ] The arm-surface digest move is declared, not discovered. Every file of
  `agents/strategic/prompts/qwen3_6_27b` is hashed into `arm_surface_digests`
  (`experiments/fresh_deduction_instrument.py:4941-4969`, `ARM_SURFACE_SOURCES`
  at `:4927-4935`), so this edit moves it and the comparison at `:5430-5435`
  refuses a resume begun before this card; the card names the fifth run's
  `checkpoint-final.json` as what stops matching.
- [ ] `audits/deduction-candidate/execution-manifest.md` gains a dated section
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
- [ ] Planted proofs, each red before the fix and green after, on synthetic
  seed-free inputs through `build_prompt_renderers("qwen3_6_27b",
  public_account_version=1, attributed_testimony_version=1)`, in the idiom of
  `tests/agents/test_public_account_prompts.py:1092-1171`: drop the shape
  sentence; drop the row-suffix clause; prefill the skeleton's
  `primary_reason_id` with the meeting's last turn id; drop either
  SKIP-register sentence; set the revision back to `v4`.
- [ ] No recording and no re-record. These templates are reachable only
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
