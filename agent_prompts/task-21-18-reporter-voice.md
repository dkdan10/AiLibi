# Agent Prompt — 21.18 The reporter gets a voice: the exculpation reaches speech, and the discovery account becomes speakable (lever `reporter_reasoning`, default OFF)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-21.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 21.18 — The reporter gets a voice: the exculpation reaches speech, and the discovery account becomes speakable (lever `reporter_reasoning`, default OFF), anchored to audits/review-2026-08-26/A/collated-findings.md §A-5 (ADJUSTED, P1, design-hole — the verifier reproduced EVERY figure exactly: 3312/3312 body-report ballot prompts carry the exculpation block, 0 of 2694 non-reporter speech prompts carry any structured statement that a body was reported, turns-per-speaker `{1: 3312}`, reporter turn kinds `{'opening': 618}`, 1061 accusation claims against reporters all at turn index ≥ 1 with the histogram `{1:455, 2:219, 3:156, 4:113, 5:70, 6:35, 7:13}`, and 508/618 meetings accuse the reporter after their only turn; the verifier's FRAMING correction binds — lead with "accusation_round.j2 never receives `reporter_id` at all", NOT with the 0/2694 memory census, which is partly structural because the meeting opens on the same tick as the report); §A-4 (ADJUSTED, P1 — 618 body-report + 50 emergency meetings over 668, reporter is CREWMATE in 618/618, reporter ejected 30/618 = 4.85% against innocent non-reporter 12/1844 = 0.65%, RR 7.46x, z = 6.98, 30 of the 42 pooled innocent ejections, pooled ejection accuracy 387/429 = 90.2% → 387/399 = 97.0% with zero impostor convictions lost; the verifier's three corrections bind — the reporter's EJECTABILITY is a recorded design decision, the base rate is IMPROVING across baselines (22/106 = 20.8% at baseline 2 → 30/379 = 7.9% here), and the decision-relevant new content is that the ballot-time guard degraded); §A-24 (ADJUSTED, P2 — impostor 521/737 = 70.7% of its accusations at the reporter against crew 540/1513 = 35.7%; the verifier's re-anchor binds: the SPEECH ratio is flat like-for-like on the same samples/9p2i seeds (impostor 64.2% → 65.9%, crew 34.5% → 37.1%) and what moved is the BALLOT follow-through — crew 2.2% → 9.6%, impostor 4.1% → 17.1%, reporter ejections 2 over 151 body-report meetings → 10 over 144); §A-37 (ADJUSTED, P3, instrumentation gap — the verifier corrected the invocation numbers to 113/3312 = 3.41% rationales mentioning a report, 28 = 0.85% co-mentioning one with an exculpatory hinge of which ~19–20 are genuine, 8 = 0.24% speech turns and 0 by the reporter, and corrected the causal attribution: the lever's PRIMARY channel is `REPORTER_EXCULPATION_SOFT_LIFT_CAP`, not the generic under-gate redirect, whose own cells are 83 redirects + 3 coercions off a pre-guard intent of 364 = 11.0%, suppression 86/364 = 23.6%, 54/618 meetings, 2 of the 30 convictions); §A-38 (ADJUSTED, P3, acceptable-emergent, **fix_sketch REJECTED as written** — 121/618 meetings carry a non-reporter with the identical discovery line at the report tick, innocent co-discoverer slots eject 3/89 = 3.37% against 9/1755 = 0.51% (6.57x, Fisher two-sided p = 0.01742) and draw ≥ 2 accusers 13/89 = 14.61% against 60/1755 = 3.42% (4.27x, p = 2.564e-05), but the verifier's DISCONFIRMING measurement binds: non-reporter co-discoverer slots are 89 CREWMATE / 51 IMPOSTOR = 36.4% impostor, so rendering exculpatory framing over a discoverer set would launder an impostor in over a third of the meetings it fires in — "the most that is defensible is a neutral factual line naming who was at the body, with no exculpatory framing"; also 607/625 not 625/625, the 18 misses carrying the line at tick − 1). Phase-20 close: audits/audit-phase-20-close.md:280-281 (bar 1 non-direct conviction accuracy 61/103 = 0.5922 against ≥ 0.60, MISSED by 0.0078; bar 2 innocent ejections 42 against < 35, MISSED) and :321 (the pre-registered rule returned FINDING). Anchors re-verified at HEAD 4002f19b: `grep -c reporter` over the served set returns 0 for accusation_round.j2, accusation_round_roll_call.j2, crewmate_report.j2, impostor_report.j2 and impostor_report_roll_call.j2 and 5 for vote_ballot.j2, whose block is exactly agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2:171-175; meetings/manager.py:1762-1779 derives `reporter_id` at meeting scope and :1831 threads `reporter_id=render_reporter` into the ballot renderer and into nothing else; meetings/manager.py:1625 `_render_turn_prompt`, :1653 the opening dispatch and :1678 the statement dispatch, neither of which passes any reporter input; meetings/manager.py:694-704 the `MeetingParticipant` field list and :723-734 `_trigger_is_emergency` / :489 `EMERGENCY_TRIGGER_PHRASE`; meetings/render_contract.py:99-127 `PromptRenderInputs`, :129-183 / :187-256 / :260-315 the three renderer Protocols; agents/strategic/prompts/loader.py:323-363 the live lever-resolver shape this task clones and :537-554 `_render_inputs_for`, :709-836 `accusation_round_prompt`; agents/memory/beliefs.py:174 `REPORTER_EXCULPATION_SOFT_LIFT_CAP = 0.0` applied at :1680 and :1708 (the register cites :1704-1707 — the second application has drifted to :1708); orchestrator/replay.py:88 (this module ALREADY imports `meetings.manager`), :524-546 the 21 retired levers, :562-564 the missing-key-reads-False rule, :568-570 `_TOGGLEABLE_LEVER_RESOLVERS` with its single entry, :585-588 `SUBSTRATE_FLAG_KEYS`, :591-614 `substrate_flag_snapshot`; orchestrator/game.py:304-309 `DEFAULT_PROMPT_VERSIONS`, :391 the `qwen3_6_27b` registry entry, :424-467 `prompt_versions_for_set`; tests/meetings/test_prompt_byte_golden.py:183 `ARCHIVED_PROMPT_VERSION_SETS` (empty at HEAD) and :424-451 the exact-mapping reverse lookup; tests/meetings/test_lever_registry.py:291-299 `test_the_one_live_resolver_in_the_tree_is_not_reported`; training/surrogate/dataset.py:240 + :831 the `is_reporter` feature (read as evidence, not edited here).. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-21.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-21-reporter-voice`
**Depends on:** 21.15
**Section refs:** audits/review-2026-08-26/A/collated-findings.md §A-5 (ADJUSTED, P1, design-hole — the verifier reproduced EVERY figure exactly: 3312/3312 body-report ballot prompts carry the exculpation block, 0 of 2694 non-reporter speech prompts carry any structured statement that a body was reported, turns-per-speaker `{1: 3312}`, reporter turn kinds `{'opening': 618}`, 1061 accusation claims against reporters all at turn index ≥ 1 with the histogram `{1:455, 2:219, 3:156, 4:113, 5:70, 6:35, 7:13}`, and 508/618 meetings accuse the reporter after their only turn; the verifier's FRAMING correction binds — lead with "accusation_round.j2 never receives `reporter_id` at all", NOT with the 0/2694 memory census, which is partly structural because the meeting opens on the same tick as the report); §A-4 (ADJUSTED, P1 — 618 body-report + 50 emergency meetings over 668, reporter is CREWMATE in 618/618, reporter ejected 30/618 = 4.85% against innocent non-reporter 12/1844 = 0.65%, RR 7.46x, z = 6.98, 30 of the 42 pooled innocent ejections, pooled ejection accuracy 387/429 = 90.2% → 387/399 = 97.0% with zero impostor convictions lost; the verifier's three corrections bind — the reporter's EJECTABILITY is a recorded design decision, the base rate is IMPROVING across baselines (22/106 = 20.8% at baseline 2 → 30/379 = 7.9% here), and the decision-relevant new content is that the ballot-time guard degraded); §A-24 (ADJUSTED, P2 — impostor 521/737 = 70.7% of its accusations at the reporter against crew 540/1513 = 35.7%; the verifier's re-anchor binds: the SPEECH ratio is flat like-for-like on the same samples/9p2i seeds (impostor 64.2% → 65.9%, crew 34.5% → 37.1%) and what moved is the BALLOT follow-through — crew 2.2% → 9.6%, impostor 4.1% → 17.1%, reporter ejections 2 over 151 body-report meetings → 10 over 144); §A-37 (ADJUSTED, P3, instrumentation gap — the verifier corrected the invocation numbers to 113/3312 = 3.41% rationales mentioning a report, 28 = 0.85% co-mentioning one with an exculpatory hinge of which ~19–20 are genuine, 8 = 0.24% speech turns and 0 by the reporter, and corrected the causal attribution: the lever's PRIMARY channel is `REPORTER_EXCULPATION_SOFT_LIFT_CAP`, not the generic under-gate redirect, whose own cells are 83 redirects + 3 coercions off a pre-guard intent of 364 = 11.0%, suppression 86/364 = 23.6%, 54/618 meetings, 2 of the 30 convictions); §A-38 (ADJUSTED, P3, acceptable-emergent, **fix_sketch REJECTED as written** — 121/618 meetings carry a non-reporter with the identical discovery line at the report tick, innocent co-discoverer slots eject 3/89 = 3.37% against 9/1755 = 0.51% (6.57x, Fisher two-sided p = 0.01742) and draw ≥ 2 accusers 13/89 = 14.61% against 60/1755 = 3.42% (4.27x, p = 2.564e-05), but the verifier's DISCONFIRMING measurement binds: non-reporter co-discoverer slots are 89 CREWMATE / 51 IMPOSTOR = 36.4% impostor, so rendering exculpatory framing over a discoverer set would launder an impostor in over a third of the meetings it fires in — "the most that is defensible is a neutral factual line naming who was at the body, with no exculpatory framing"; also 607/625 not 625/625, the 18 misses carrying the line at tick − 1). Phase-20 close: audits/audit-phase-20-close.md:280-281 (bar 1 non-direct conviction accuracy 61/103 = 0.5922 against ≥ 0.60, MISSED by 0.0078; bar 2 innocent ejections 42 against < 35, MISSED) and :321 (the pre-registered rule returned FINDING). Anchors re-verified at HEAD 4002f19b: `grep -c reporter` over the served set returns 0 for accusation_round.j2, accusation_round_roll_call.j2, crewmate_report.j2, impostor_report.j2 and impostor_report_roll_call.j2 and 5 for vote_ballot.j2, whose block is exactly agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2:171-175; meetings/manager.py:1762-1779 derives `reporter_id` at meeting scope and :1831 threads `reporter_id=render_reporter` into the ballot renderer and into nothing else; meetings/manager.py:1625 `_render_turn_prompt`, :1653 the opening dispatch and :1678 the statement dispatch, neither of which passes any reporter input; meetings/manager.py:694-704 the `MeetingParticipant` field list and :723-734 `_trigger_is_emergency` / :489 `EMERGENCY_TRIGGER_PHRASE`; meetings/render_contract.py:99-127 `PromptRenderInputs`, :129-183 / :187-256 / :260-315 the three renderer Protocols; agents/strategic/prompts/loader.py:323-363 the live lever-resolver shape this task clones and :537-554 `_render_inputs_for`, :709-836 `accusation_round_prompt`; agents/memory/beliefs.py:174 `REPORTER_EXCULPATION_SOFT_LIFT_CAP = 0.0` applied at :1680 and :1708 (the register cites :1704-1707 — the second application has drifted to :1708); orchestrator/replay.py:88 (this module ALREADY imports `meetings.manager`), :524-546 the 21 retired levers, :562-564 the missing-key-reads-False rule, :568-570 `_TOGGLEABLE_LEVER_RESOLVERS` with its single entry, :585-588 `SUBSTRATE_FLAG_KEYS`, :591-614 `substrate_flag_snapshot`; orchestrator/game.py:304-309 `DEFAULT_PROMPT_VERSIONS`, :391 the `qwen3_6_27b` registry entry, :424-467 `prompt_versions_for_set`; tests/meetings/test_prompt_byte_golden.py:183 `ARCHIVED_PROMPT_VERSION_SETS` (empty at HEAD) and :424-451 the exact-mapping reverse lookup; tests/meetings/test_lever_registry.py:291-299 `test_the_one_live_resolver_in_the_tree_is_not_reported`; training/surrogate/dataset.py:240 + :831 the `is_reporter` feature (read as evidence, not edited here).
**Complexity:** Integration
**Record impact:** lever-gated (default-OFF) until the Phase-21 adopting record
**Measurement:** `uv run pytest tests/meetings tests/orchestrator/test_meeting_integration.py tests/eval/test_reporter_justice.py -q` green; `bash scripts/verify_samples.sh` 100/100 and `uv run pytest tests/meetings/test_prompt_byte_golden.py -q` green with the lever unset (the OFF-path proof); the PR Summary quotes the eligibility census over the re-recorded corpus — body-report meetings, non-reporter speech prompts that gain the listener block, meetings with ≥ 1 co-discoverer, and the added characters per prompt at the 5th/50th/95th percentile — and states which outcome cells are NOT-PREDICTABLE-OFFLINE.

The project wrote the reporter's defence once and delivered it to the wrong room. Every
body-report ballot carries it — 3312 of 3312 prompts hold "`p-N` reported the body that opened
this meeting … being first to the scene is not by itself evidence of guilt"
(vote_ballot.j2:171-175) — and not one accusation-round prompt does. `grep -c reporter` over the
served set, re-run at HEAD, returns 5 for the ballot template and 0 for all five turn templates.
The manager's own code says why: `reporter_id` is derived at meeting scope
(meetings/manager.py:1762-1779) and threaded at :1831 into `self._vote_prompt(...)` and nowhere
else, with a comment recording that whether it renders "is the serving template's call". This is
not an oversight to be scolded — the shipping contract scoped it that way, and the register
classifies it as a design-hole in the repo's own sense: works exactly as specified, the spec's
render scope is the gap.

The cost is measured and it is the largest one Wave 0 found. Over the four committed sets the
reporter draws ≥ 1 formal accusation in 508 of 618 body-report meetings and ≥ 2 in 267, and every
one of the 1061 accusation claims against a reporter lands at turn index ≥ 1 — after the
reporter's only turn. Turns-per-speaker is `{1: 3312}` and the reporter's turn kind is `opening`
in 618 of 618: the accused has already spent their voice before the first word against them, and
the table that answers them has never been told the prior. The result is the reporter ejected
30/618 = 4.85% of the time against an innocent non-reporter's 12/1844 = 0.65% — a relative risk
of 7.46x at z = 6.98 — and those 30 are 30 of the 42 pooled innocent ejections. Pooled ejection
accuracy is 387/429 = 90.2%; the same table without those 30 is 387/399 = 97.0%, with zero
impostor convictions lost, because the reporter is a CREWMATE in 618 of 618 body-report meetings
and 0 of the 387 impostor ejections ever removed one.

Two corrections from the verifiers bind the framing and are stated here so nobody re-reads this
task as a repair of a bug. First, the reporter's EJECTABILITY is a recorded design decision:
agents/memory/beliefs.py:182-190 states that "a reporter caught by a real contradiction or a
vent/kill flag still crosses the 4.6 gate — no immunity, only removal of the proximity prior",
and Task 15.5 chartered exactly that. This task does not touch it. A hard ballot gate making the
reporter ineligible was proposed and is NOT what ships: it reverses a decision the project made
on purpose, and it would remove the one channel through which a genuinely guilty reporter could
ever be convicted. Second, the channel is SHRINKING, not growing: the same beliefs.py docstring
records 22 of 106 report-meeting ejections at baseline 2 = 20.8% against 30/379 = 7.9% here, a
2.6x fall. The 71.4%-of-innocent-ejections headline is high because the other innocent-ejection
routes were closed. What IS newly adverse — the verifier's re-anchor of the impostor-deflection
item — is that the ballot-time defence degraded across the last record: like-for-like on the same
samples/9p2i seeds, ballots targeting the reporter went 2.2% → 9.6% for crew and 4.1% → 17.1% for
impostors, and reporter ejections went 2 over 151 body-report meetings to 10 over 144, while the
impostor's speech ratio stayed flat (64.2% → 65.9%). The lever is aimed at the surface that
moved.

Why this belongs to Wave 2 rather than to the balance backlog: baseline 7 is canon by explicit
owner override of a FINDING verdict — its own pre-registered rule returned FINDING because bars 1
and 2 missed — and the two bars that missed are the two this class sits inside. Bar 2 counted 42
innocent ejections against a bar of fewer than 35; 30 of those 42 are reporter convictions. Bar 1
counted non-direct conviction accuracy at 61/103 = 0.5922 against ≥ 0.60, and all 30 reporter
convictions are non-direct (28 of the 30 carry no engine contradiction naming the reporter at
all; the 2 that do carry `alibi_vs_sighting`, not a direct proof). Nothing here claims a bar
would have passed — the bars did not pass, and the pre-registration task owns any successor bar.
What is claimable is that this is the single largest addressable class inside the miss, and that
it is addressable in language rather than in the tally.

The lever installs three render effects, all behind one env gate, all default OFF. **(a) The
listener context.** Every non-reporter turn prompt in a body-report meeting receives the reporter
identity and the discovery facts the meeting trigger already states publicly, plus the same
base-rate reasoning the ballot carries — reusing the ballot's sentence VERBATIM so the two
surfaces cannot drift, and so the register's separate P3 note about "almost never" versus a
measured zero is not silently re-opened on a second surface. **(b) The discovery account.** The
reporter's own opening prompt gains a line making the discovery account a thing to state plainly
rather than a thing to volunteer; the compelled-disclosure null result the register recorded
(disclosure does not change the accusation rate — the reporter's movement into the body room is
already in other players' memory) is why this half is framed as clarity, not as advocacy. **(c)
Co-discoverers.** A non-reporter who holds the identical "You discovered X's body" row at the
report tick — 121 of 618 meetings have at least one — gets a NEUTRAL factual line in their OWN
turn prompt saying they were at the body when it was reported, with no exculpatory framing and no
broadcast of a discoverer roster to the table. This is the verifier's ruling, not a softened
version of the filed fix, and its reason is arithmetic: 51 of the 140 non-reporter
co-discoverer slots are IMPOSTORS (36.4%), so exculpatory framing over that set would print
"being first to the scene is not by itself evidence of guilt" about an impostor in over a third
of the meetings it fires in, re-opening the laundering hole beliefs.py's own docstring certifies
as absent for reporters. Rendering the roster to everyone would also leak position facts that not
every listener perceived; the co-discovery line is therefore a SELF-channel input, derived from
the participant's own memory exactly as the vent, sighting and move channels are.

Turn structure does not move. The second half of the register's fix — a right of reply, or moving
the body-report opener to the end of the round-robin — is explicitly OUT of scope: it rewrites
the chain every meeting test, the transcript shape and the prompt-byte golden are built on, and
the register itself severity-splits it for that reason. This task is a threading-and-render
lever; the mute-after-turn-0 structure it works around is named here as the deferred half so the
next planner does not have to rediscover it.

Finally the instrument. The register's own fix sketch is "once the exculpation reaches the
accusation round, instrument it", and the same track asks for the impostor's
accusations-at-reporter ratio as a standing gauge. Both land here as one small instrument module
whose cells the pre-registration task can cite: the reporter-conviction count, the reporter's
per-slot ejection rate against the innocent non-reporter baseline, the invocation rate of the
exculpation in ballots and in speech, the impostor and crew at-reporter accusation and ballot
shares, and the co-discoverer split. Every one of those cells is pinned from the corpus THIS task
lands on — the re-recorded bytes — not from the baseline-7 numbers quoted above, which are the
reference the register measured and are certain to move.

**Files in scope:**
- meetings/render_contract.py; (the leaf DTOs: `ReporterContext` and `BodyDiscoveryRecord`, plus the one additive defaulted keyword on the report and statement renderer Protocols — stdlib + `meetings.schemas` imports only, the leaf rule)
- meetings/manager.py; (the `reporter_reasoning_enabled` resolver read ONCE per run; `MeetingParticipant.body_discovery_records`; the reporter context built beside `render_inputs` and threaded into `_render_turn_prompt`'s two dispatches; OFF-path threading identical to today)
- agents/strategic/prompts/loader.py; (pass-through of the new keyword on `crewmate_report_prompt`, `impostor_report_prompt` and `accusation_round_prompt`; no lever read here — the loader stays env-free for this lever)
- agents/strategic/prompts/qwen3_6_27b/accusation_round.j2; (the guarded listener block and the guarded co-discovery line; absent when the context is not threaded)
- agents/strategic/prompts/qwen3_6_27b/crewmate_report.j2; (the guarded discovery-account line on the reporter's own opening)
- orchestrator/game.py; (`body_discovery_records_for_meeting` on the agent protocol and on `TacticalAgent`, populated into `_build_participants`; and `REPORTER_REASONING_PROMPT_VERSION_SETS` — the ON-arm version overlay in the 18.10 shape, plus its arm in `prompt_versions_for_set`. The DEFAULT `PROMPT_VERSION_SETS` entry does NOT move: the whole-set bump was 21.1's v5 and no lever re-bumps it)
- orchestrator/replay.py; (register `reporter_reasoning` in `_TOGGLEABLE_LEVER_RESOLVERS`, binding the manager's resolver directly — this module already imports `meetings.manager`, so no local mirror and no equivalence pin is needed)
- eval/reporter_justice.py; (NEW instrument module: the reporter-justice cells, computed from recorded bytes)
- tests/meetings/test_manager_reporter_render.py; (the 15.5 render test module grows the speech-side cases: OFF-path identity, ON-path blocks, emergency meetings arm nothing)
- tests/meetings/test_lever_registry.py; (the tree now holds a second live resolver — the test that says "the one live resolver" is renamed and generalised, and both are asserted clean by the same predicate)
- tests/meetings/test_prompt_byte_golden.py; (ONE added assertion: with the lever ON the served stamps come from the overlay registry and never from the default one, so ON-arm bytes can never wear a default stamp. No archive entry is created — the default registry does not move and the OFF-path render is byte-identical, which is what makes that possible)
- tests/orchestrator/test_replay.py; (the stamp key appears, defaults False on a bare env, and a legacy stamp missing the key still reads False)
- tests/eval/test_reporter_justice.py; (the instrument's cells pinned over the re-recorded corpus, with a planted perturbation proving each cell can fail)
- .env.example; (the lever documented in the same voice as the existing default-OFF arm)

**Files NOT in scope:**
- agents/memory/beliefs.py (the soft-lift cap at :174 and its two applications at :1680 / :1708 are the lever's belief-side sibling and are READ as evidence; this task changes no suspicion arithmetic and no gate — the register's own correction is that the cap is the primary channel, and it already works)
- meetings/voting.py, meetings/transcript.py (no flag is minted, re-banded or suppressed here; the §4.6 gate, the guard redirects and the citation gate are untouched — this lever changes what a speaker READS, never what the referee concludes)
- the meeting turn chain in meetings/manager.py beyond the two `_render_turn_prompt` dispatches (no right of reply, no opener reordering, no extra turn: the register severity-splits that half precisely because it rewrites recorded structure)
- agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2 (the ballot block already ships and is the wording this task reuses; changing it would move the surface the whole finding is measured against)
- agents/strategic/prompts/qwen3_6_27b/impostor_report.j2 and the two `*_roll_call.j2` variants (the impostor cannot be the reporter — 618/618 — so the impostor opening has no discovery account to state; the variant files belong to the other default-OFF arm and keep their own lineage)
- the other per-model prompt sets under agents/strategic/prompts/ (only the served set renders these blocks; the frozen reference set's bytes and stamp never move)
- training/surrogate/dataset.py (the `is_reporter` feature at :240/:831 is a perfect impostor-exclusion oracle given the 0/618 invariant — recorded here as a finding for the fit-hygiene and re-ground tasks to rule on, and read-only in this PR)
- eval/evidence_honesty.py, eval/deduction_metrics.py (existing instrument modules owned by other Phase-21 contracts; the new cells go in their own module rather than colliding with an unordered sibling)
- replays/ (no committed byte moves; the census and the instrument read them and write nothing)

**Definition of done:**
- [ ] `meetings.manager.reporter_reasoning_enabled(env)` follows the resolver shape at agents/strategic/prompts/loader.py:329-363: defaults OFF on unset/empty/unrecognised, accepts `1/true/yes/on` case-insensitively, takes an optional `env` mapping so tests never mutate `os.environ`, and is read EXACTLY ONCE per `run()` with the boolean threaded down.
- [ ] The lever is inert twice over: OFF by default, and a NO-OP when the caller supplies no reporter context — an emergency meeting (`_trigger_is_emergency` true, so `reporter_id` is `None`) arms nothing, and a direct-construction caller with no `body_discovery_records` gets today's prompts exactly.
- [ ] OFF-path byte identity is proved, not asserted: `uv run pytest tests/meetings/test_prompt_byte_golden.py -q` green over every committed meeting with the lever unset, and `bash scripts/verify_samples.sh` reports 100/100.
- [ ] Rule (a) is fixture-pinned in `tests/meetings/test_manager_reporter_render.py`: with the lever ON, every non-reporter reply and opt-in prompt of a body-report meeting names the reporter and carries the base-rate sentence BYTE-IDENTICAL to vote_ballot.j2:171-175 (asserted by comparing against the ballot render, not by re-typing the string), and the reporter's own turn prompt does not carry the listener block addressed at themselves.
- [ ] Rule (b) is fixture-pinned: the reporter's opening prompt gains the discovery-account line only in a body-report meeting and only for the reporter; the perturbation — make the same participant a non-reporter — removes it.
- [ ] Rule (c) is fixture-pinned AND its over-damping canary is pinned: a co-discoverer's own turn prompt carries the neutral "you were at the body when it was reported" line; an IMPOSTOR co-discoverer's prompt carries the SAME neutral line with no exculpatory phrase in it (asserted as an explicit absence check against the ballot sentence's distinctive words); no participant's prompt lists any other player as a co-discoverer; and a participant holding no discovery row at the report tick gets no line.
- [ ] `MeetingParticipant.body_discovery_records` is a self-channel like its four siblings at meetings/manager.py:700-703: populated by `_build_participants` from `body_discovery_records_for_meeting()`, firewall-clean (episodic memory only), defaulting to `()` meaning "this speaker discovered nothing"; a test asserts the accessor returns only rows the agent itself holds and that a co-present player who never perceived the body yields none.
- [ ] The rendered blocks carry no internal dialect (craft rule 4): a test greps the ON-path renders for task ids, audit paths, threshold arithmetic and `flag`/`engine`/`gate` used as jargon, and fails on a planted violation. The blocks introduce no new term — every word is plain English or already defined in docs/glossary.md, which this task therefore does not edit; if a needed term is missing, say so in the PR rather than widening scope.
- [ ] `reporter_reasoning` is registered in `orchestrator.replay._TOGGLEABLE_LEVER_RESOLVERS` bound to the manager's resolver (no local mirror — orchestrator/replay.py:88 already imports `meetings.manager`), so `SUBSTRATE_FLAG_KEYS` grows by a pure append at the live-toggle end and every already-recorded key keeps its index; `tests/orchestrator/test_replay.py` pins that a bare env stamps it `False` and that a stamp recorded before the key existed still reads `False` through the missing-key rule at orchestrator/replay.py:562-564.
- [ ] `tests/meetings/test_lever_registry.py` is generalised rather than loosened: the resolver sweep still reports zero accept-and-ignore functions, and the discrimination case now names BOTH live resolvers and asserts each reads `env` — the test's name and docstring stop claiming there is one.
- [ ] The prompt-version policy is ONE story across the whole Wave-2 slate and this task builds its seam: `orchestrator/game.py` gains `REPORTER_REASONING_PROMPT_VERSION_SETS` — the ON-arm overlay, in the shape `IMPOSTOR_ROLL_CALL_PROMPT_VERSION_SETS` established at Task 18.10 — plus its arm in `prompt_versions_for_set`, so a lever-ON recording stamps the overlay's version strings for the two templates it changes and a lever-OFF recording stamps the default set's, byte for byte as today. The DEFAULT `PROMPT_VERSION_SETS["qwen3_6_27b"]` entry is UNCHANGED and asserted so in this PR: the whole-set bump was 21.1's v5 and no lever re-bumps the default registry.
- [ ] **The seam COMPOSES, and this task defines how — because the slate that matters is all-ON.** 21.23 smokes and 21.24 records with all three Wave-2 levers enabled together, so a seam that refused a second overlay could not construct a renderer or a stamp for the only configuration the record ever uses. `prompt_versions_for_set` therefore resolves a SET of enabled overlays rather than one, and this contract fixes the three rules its siblings register into: (a) **application order is registration order** — the order the keys appear in `orchestrator.replay._TOGGLEABLE_LEVER_RESOLVERS` — so composition is deterministic and independent of how the environment happened to be spelled; (b) each enabled combination resolves to a **composite version stamp** per template, derived from the participating overlays' names in that same order, so the stamp names exactly which levers shaped the bytes; (c) the composite for the ALL-ON arm is materialised and pinned by name, since it is the one 21.23 and 21.24 spend a record on. A helper computes the composite from the enabled set rather than each lever hand-writing pairwise combinations, so the third lever costs no new branch.
- [ ] The composition's invariant is the one Ruling 3(d) cares about and it is pinned exhaustively: over EVERY subset of the live overlay keys, no two distinct subsets resolve to the same version string for any template, and no subset resolves to a default-set value. In particular an ON ballot can never share a `vote_ballot` stamp with an OFF one. The test enumerates the subsets rather than spot-checking a few, so a sibling lever added later cannot quietly collide, and a planted case that makes two subsets collide is asserted to fail. A set that carries no variant body for an enabled overlay still raises `ValueError` at construction — that refusal is about a MISSING body, not about a sibling being on, and the two must not be conflated.
- [ ] Because the default registry does not move, NO bump-in-flight archive is created and none is needed: `ARCHIVED_PROMPT_VERSION_SETS` stays `{}` and `tests/fixtures/prompt_archive/` stays absent. That is only sound if the OFF-path render is byte-identical, so it is proved rather than assumed — the guarded blocks render nothing when the reporter context is not threaded, `uv run pytest tests/meetings/test_prompt_byte_golden.py -q` walks every committed meeting green with the lever unset, and the golden's one-byte perturbation leg is run and its red output quoted so the walk is shown to be a real gate and not a skipped one.
- [ ] `eval/reporter_justice.py` computes, from recorded bytes alone, at minimum: body-report and emergency meeting counts; reporter role census; reporter ejections and their share of innocent ejections; per-slot ejection rate for reporter, innocent non-reporter and impostor with the relative risk; accusations-at-reporter share for crew and impostor, in speech and in ballots; the exculpation-invocation rate in ballot rationales and in speech; and the co-discoverer split by role. Each cell ships with a planted perturbation proving it bites.
- [ ] The instrument's pins in `tests/eval/test_reporter_justice.py` are RE-DERIVED over the corpus this task lands on and the PR states the baseline-7 reference beside each — the register's 618/668, 30/42, 4.85% vs 0.65%, 508/618, 70.7% vs 35.7%, 3.41%/0.85%, 121/618 and 89 vs 51 — with any cell that moved by more than its Wilson interval called out rather than quietly re-pinned.
- [ ] The eligibility census is published in the PR Summary from a fresh walk: how many meetings and prompts each of the three rules fires in, and the added characters per prompt at the 5th/50th/95th percentile, so the render-budget cost of the lever is a number and not an impression.
- [ ] The PR states plainly which cells are NOT-PREDICTABLE-OFFLINE: this is a PROMPT lever, so no offline replay of committed bytes can predict what the model says or how the table votes under it. The offline counterfactual can publish the eligibility census, the byte deltas and the budget cost; conviction and accuracy movement are measurable only at a record.
- [ ] `.env.example` documents `AILIBI_REPORTER_REASONING` in the voice of the existing default-OFF entry at .env.example:135-141, including the warning that flipping it for a serving or verify run against committed bytes produces a substrate mismatch.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

BLOCK 1 — the input seam, before any template. Add two frozen dataclasses to
meetings/render_contract.py beside `PromptRenderInputs` (:99-127): `BodyDiscoveryRecord`
(`victim_id`, `room`, `tick`, `observation_id`) and `ReporterContext` (`reporter_id`,
`victim_id`, `room`, `tick`). Keep the module a leaf — stdlib and `meetings.schemas` only, per its
own docstring. Then add ONE additive, defaulted keyword to `ReportPromptRenderer.__call__`
(:169-183) and `StatementPromptRenderer.__call__` (:239-256) — `reporter_context:
ReporterContext | None = None` — plus a second, `at_body: bool = False`, for rule (c); a `None` /
`False` render is byte-identical because jinja ignores a name no template references, which is
the widen-the-contract-inert pattern the module already documents. Do NOT put the reporter
context on `PromptRenderInputs`: that DTO is per-GAME and is composed at loader-construction time
with the map card (loader.py:537-554), while this is per-MEETING and per-SPEAKER.

BLOCK 2 — the manager. Home the resolver in meetings/manager.py, not in the loader: the loader
builds its Jinja environment at import time and is deliberately env-free for render inputs, while
the manager is where the threading decision is made. `ENV_REPORTER_REASONING =
"AILIBI_REPORTER_REASONING"` plus a `frozenset({"1","true","yes","on"})`, mirroring loader.py:323-326
byte-for-byte. Read it once in `run()` next to where `render_inputs` is built (:1009) and carry
the boolean into `_render_turn_prompt` (:1625). Build the `ReporterContext` from the SAME
`trigger.triggered_by` / `_trigger_is_emergency` derivation the ballot path already uses at
:1776-1778 — one derivation, two consumers, so the ballot annotation and the speech annotation
can never disagree about who reported. In `_render_turn_prompt`, pass the context on the opening
dispatch (:1653-1676) only when the participant IS the reporter, and on the statement dispatch
(:1678-1706) only when they are NOT; compute `at_body` from
`participant.body_discovery_records` filtered to the trigger tick. When the lever is OFF, pass
nothing — that is the OFF-path identity, and it is one `if`, not a second code path.

BLOCK 3 — the self-channel. `body_discovery_records_for_meeting()` joins the `MeetingAwareAgent`
protocol beside `vent_witness_records_for_meeting` (orchestrator/game.py:603-607) and is
implemented on `TacticalAgent` as a straight episodic filter over the agent's own `saw_body`
rows — the same shape as the vent accessor, NOT the re-deriving shape
`body_proximity_records_for_meeting` uses. Populate it in `_build_participants` (:1029) alongside
the four existing channels. Two details the register measured: filter on the MEETING's tick, and
expect a small tail of rows stamped at tick − 1 (18 of 625 reporter prompts carried the line
there), so decide the window explicitly and pin it rather than letting an off-by-one silently
drop discoverers. Firewall: this is episodic memory only; nothing engine-side is read.

BLOCK 4 — the templates. In accusation_round.j2 the block goes near the turn header at :108-114,
BEFORE the transcript, so the prior is in front of the reader before they form a target — the
register's own placement note about the ballot sentence sitting after the candidate roster is the
reason. Reuse the ballot's sentence verbatim; the test asserts equality against the ballot render
rather than against a re-typed literal, so a future edit to one surface fails loudly instead of
drifting. The co-discovery line is one neutral sentence with no exculpatory clause and names only
the reader. In crewmate_report.j2 the discovery-account line joins the existing opening
instructions. Both blocks are `{% if %}`-guarded on the threaded value, so an unthreaded render
is byte-identical. Nothing goes in impostor_report.j2: the impostor never reports.

BLOCK 5 — the stamp. Append `("reporter_reasoning", reporter_reasoning_enabled)` to
`_TOGGLEABLE_LEVER_RESOLVERS` (orchestrator/replay.py:568-570), importing the manager's resolver
directly — the module already imports `meetings.manager` at :88, so the mirror-plus-equivalence-pin
dance the other arm needs does not apply here, and one source of truth is better than two that
agree. Both halves of `SUBSTRATE_FLAG_KEYS` only ever grow at their own end, so this is a pure
append. Then fix `tests/meetings/test_lever_registry.py:291-299`, whose name and body assert
there is exactly one live resolver in the tree.

BLOCK 6 — the versions. Do NOT touch `PROMPT_VERSION_SETS`. Read it at branch time to learn the
served set's current strings — they are whatever 21.1's v5 bump left — and build
`REPORTER_REASONING_PROMPT_VERSION_SETS` beside `IMPOSTOR_ROLL_CALL_PROMPT_VERSION_SETS`
(orchestrator/game.py:415-421), overriding only the two templates whose bodies you edited and
inheriting the rest, then add the matching arm to `prompt_versions_for_set` (:424-467) reading the
same resolver the renderer reads. This is the 18.10 shape, but do NOT stop at 18.10's arity: that
arm resolves ONE lever, and the record this phase spends runs all three Wave-2 overlays at once.
Write `prompt_versions_for_set` to fold the SET of enabled overlays — iterate the keys in
`_TOGGLEABLE_LEVER_RESOLVERS` order so the result never depends on environment spelling, apply each
enabled overlay's per-template entries in that order, and derive the composite version string from
the participating overlay names in the same order. One fold, not a pairwise table: the third lever
must cost a registration and no new branch. The exhaustive subset test in the DoD is the cheapest
way to know you got it right — enumerate every subset of the live overlay keys and assert the
version strings are pairwise distinct and disjoint from the default set's. There is no archive to
populate: `ARCHIVED_PROMPT_VERSION_SETS` stays `{}`
because no committed recording's stamp is orphaned — the default strings never move. Run the byte
golden with a bare environment before you run anything else; if it goes red, a guarded block is
rendering when it should not, and that is the bug, not the golden.

BLOCK 7 — the instrument. `eval/reporter_justice.py` reads recorded bytes only: derive the
meeting kind from the recorded tick action stream or the trigger phrase (meetings/manager.py:489),
never from an eval report, which is the route both Wave-0 finders and the verifier used
independently and got identical counts. Roles come from `eval.validity.roles_by_seed`, not from
prompt-string markers. For the invocation cell, state the hinge list in the module as data and
pin the count for the list AS STATED — the register's own filing was off by 4x precisely because
the hinge list was implicit — and record in the docstring that a hinge match is an upper bound on
genuine invocation, with the manual-read ratio the verifier reported as the calibration note.

## Public types this task introduces
- `meetings.manager.reporter_reasoning_enabled`
- `meetings.manager.ENV_REPORTER_REASONING`
- `meetings.render_contract.ReporterContext`
- `meetings.render_contract.BodyDiscoveryRecord`
- `orchestrator.game.TacticalAgent.body_discovery_records_for_meeting`
- `orchestrator.game.REPORTER_REASONING_PROMPT_VERSION_SETS`
- `eval.reporter_justice.compute_reporter_justice`
- `eval.reporter_justice.ReporterJusticeCells`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

This lever threads a new per-meeting, per-speaker input through four packages and adds the
second live toggle the project has carried since the last graduation. Five risks.

Risk 1 — the co-discovery half re-opening a hole the project already closed. 51 of the 140
non-reporter co-discoverer slots are IMPOSTORS. Any exculpatory wording on that surface prints a
defence of an impostor in 36.4% of the meetings it fires in, which is exactly the laundering risk
agents/memory/beliefs.py:190-200 certifies as absent for the REPORT action and cannot certify
here. The fix as filed was rejected by the verifier for this reason and this contract implements
the rejection: neutral, self-addressed, and pinned by an explicit absence assertion on an impostor
co-discoverer's own prompt. A reviewer who sees exculpatory language on that surface should
refuse the PR.

Risk 2 — a broadcast that leaks perception. The co-discoverer set is derived from who held the
discovery row, and not every listener perceived those players at the body. Rendering a discoverer
roster into every prompt would put unperceived position facts on the table under the project's
own name. The line is therefore SELF-channel — each reader is told only about themselves — and a
test asserts no participant's prompt names another player as a co-discoverer.

Risk 3 — the OFF path drifting while nobody looks. The 21.15 bytes are the reference the whole of
Wave 2 is measured against, and this task lands on them. Two gates protect them and both must be
run with a bare environment: the prompt-byte golden over every committed meeting, and
`verify_samples.sh` at 100/100. Because the default version registry does not move, the golden's
exact-mapping lookup still resolves the committed stamps and the walk still executes — which means
a green golden here is a real statement about RENDERED bytes and not an accident of a lookup that
found nothing to do. Run the perturbation leg to prove exactly that.

Risk 4 — three sibling lever tasks writing the same shared surfaces. `orchestrator/replay.py`,
`tests/meetings/test_lever_registry.py`, `tests/orchestrator/test_replay.py`, `.env.example` and
the ON-arm version-overlay seam are needed identically by every Wave-2 lever, and
`scripts/validate_task_docs.py::validate_parallel_file_scope` rejects two tasks that share a
scope item without an ordering between them. This contract claims them; if the sibling contracts
also claim them the phase file will not validate until the siblings are serialised behind this
one or a single owner is named for the registration seam. The instrument lives in its own module
for the same reason, and `eval/evidence_honesty.py` is deliberately left alone. The same check
binds `orchestrator/game.py`, which this task needs for the agent accessor and the prompt-version
registry and which the prose-truth contract also edits from an unordered position in the wave
graph. This is flagged for the assembler, not resolved here.

Risk 5 — reading this lever as a fix for the tally. It is not. It changes only what a speaker
READS: no flag is minted or re-banded, no gate threshold moves, the soft-lift cap is untouched,
and the reporter stays ejectable exactly as Task 15.5 chartered. Whether more language changes
more verdicts is not knowable offline — it is a prompt lever, and the honest cells are the
eligibility census and the byte deltas until a record is spent. Any PR text that predicts an
accuracy movement from this change is over-claiming, and the phase's decision rule is owned by
the pre-registration, not by this task.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import training.rewards"`
- `uv run python -c "import training.bakeoff.harness"`
- `uv run python -c "import training.surrogate.fidelity"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import eval.meeting_quality"`
- `uv run python -c "import meetings.schemas"`
- `uv run python -c "import engine.tick"`
- `uv run python -c "import training.surrogate.dataset"`
- `uv run python -c "import training.surrogate.runner"`
- `uv run python -c "import training.conviction.fidelity"`
- `uv run python -c "import eval.accusation_calibration"`
- `uv run python -c "import eval.deduction_metrics"`
- `uv run python -c "import meetings.transcript"`
- `uv run python -c "import eval.vj_instruments"`
- `uv run python -c "import eval.vj_instruments.VJInstrumentReport"`
- `uv run python -c "import eval.vj_instruments.VJMeetingRow"`
- `uv run python -c "import agents.strategic.prompts.loader"`
- `uv run python -c "import frontend/src/lib/contradictions"`
- `uv run python -c "import check_doc_facts"`

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
Open a PR from branch `phase-21-reporter-voice` with a title like `task 21.18: the reporter gets a voice: the exculpation reaches speech, and the discovery account becomes speakable (lever `reporter_reasoning`, default off)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/review-2026-08-26/A/collated-findings.md §A-5 (ADJUSTED, P1, design-hole — the verifier reproduced EVERY figure exactly: 3312/3312 body-report ballot prompts carry the exculpation block, 0 of 2694 non-reporter speech prompts carry any structured statement that a body was reported, turns-per-speaker `{1: 3312}`, reporter turn kinds `{'opening': 618}`, 1061 accusation claims against reporters all at turn index ≥ 1 with the histogram `{1:455, 2:219, 3:156, 4:113, 5:70, 6:35, 7:13}`, and 508/618 meetings accuse the reporter after their only turn; the verifier's FRAMING correction binds — lead with "accusation_round.j2 never receives `reporter_id` at all", NOT with the 0/2694 memory census, which is partly structural because the meeting opens on the same tick as the report); §A-4 (ADJUSTED, P1 — 618 body-report + 50 emergency meetings over 668, reporter is CREWMATE in 618/618, reporter ejected 30/618 = 4.85% against innocent non-reporter 12/1844 = 0.65%, RR 7.46x, z = 6.98, 30 of the 42 pooled innocent ejections, pooled ejection accuracy 387/429 = 90.2% → 387/399 = 97.0% with zero impostor convictions lost; the verifier's three corrections bind — the reporter's EJECTABILITY is a recorded design decision, the base rate is IMPROVING across baselines (22/106 = 20.8% at baseline 2 → 30/379 = 7.9% here), and the decision-relevant new content is that the ballot-time guard degraded); §A-24 (ADJUSTED, P2 — impostor 521/737 = 70.7% of its accusations at the reporter against crew 540/1513 = 35.7%; the verifier's re-anchor binds: the SPEECH ratio is flat like-for-like on the same samples/9p2i seeds (impostor 64.2% → 65.9%, crew 34.5% → 37.1%) and what moved is the BALLOT follow-through — crew 2.2% → 9.6%, impostor 4.1% → 17.1%, reporter ejections 2 over 151 body-report meetings → 10 over 144); §A-37 (ADJUSTED, P3, instrumentation gap — the verifier corrected the invocation numbers to 113/3312 = 3.41% rationales mentioning a report, 28 = 0.85% co-mentioning one with an exculpatory hinge of which ~19–20 are genuine, 8 = 0.24% speech turns and 0 by the reporter, and corrected the causal attribution: the lever's PRIMARY channel is `REPORTER_EXCULPATION_SOFT_LIFT_CAP`, not the generic under-gate redirect, whose own cells are 83 redirects + 3 coercions off a pre-guard intent of 364 = 11.0%, suppression 86/364 = 23.6%, 54/618 meetings, 2 of the 30 convictions); §A-38 (ADJUSTED, P3, acceptable-emergent, **fix_sketch REJECTED as written** — 121/618 meetings carry a non-reporter with the identical discovery line at the report tick, innocent co-discoverer slots eject 3/89 = 3.37% against 9/1755 = 0.51% (6.57x, Fisher two-sided p = 0.01742) and draw ≥ 2 accusers 13/89 = 14.61% against 60/1755 = 3.42% (4.27x, p = 2.564e-05), but the verifier's DISCONFIRMING measurement binds: non-reporter co-discoverer slots are 89 CREWMATE / 51 IMPOSTOR = 36.4% impostor, so rendering exculpatory framing over a discoverer set would launder an impostor in over a third of the meetings it fires in — "the most that is defensible is a neutral factual line naming who was at the body, with no exculpatory framing"; also 607/625 not 625/625, the 18 misses carrying the line at tick − 1). Phase-20 close: audits/audit-phase-20-close.md:280-281 (bar 1 non-direct conviction accuracy 61/103 = 0.5922 against ≥ 0.60, MISSED by 0.0078; bar 2 innocent ejections 42 against < 35, MISSED) and :321 (the pre-registered rule returned FINDING). Anchors re-verified at HEAD 4002f19b: `grep -c reporter` over the served set returns 0 for accusation_round.j2, accusation_round_roll_call.j2, crewmate_report.j2, impostor_report.j2 and impostor_report_roll_call.j2 and 5 for vote_ballot.j2, whose block is exactly agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2:171-175; meetings/manager.py:1762-1779 derives `reporter_id` at meeting scope and :1831 threads `reporter_id=render_reporter` into the ballot renderer and into nothing else; meetings/manager.py:1625 `_render_turn_prompt`, :1653 the opening dispatch and :1678 the statement dispatch, neither of which passes any reporter input; meetings/manager.py:694-704 the `MeetingParticipant` field list and :723-734 `_trigger_is_emergency` / :489 `EMERGENCY_TRIGGER_PHRASE`; meetings/render_contract.py:99-127 `PromptRenderInputs`, :129-183 / :187-256 / :260-315 the three renderer Protocols; agents/strategic/prompts/loader.py:323-363 the live lever-resolver shape this task clones and :537-554 `_render_inputs_for`, :709-836 `accusation_round_prompt`; agents/memory/beliefs.py:174 `REPORTER_EXCULPATION_SOFT_LIFT_CAP = 0.0` applied at :1680 and :1708 (the register cites :1704-1707 — the second application has drifted to :1708); orchestrator/replay.py:88 (this module ALREADY imports `meetings.manager`), :524-546 the 21 retired levers, :562-564 the missing-key-reads-False rule, :568-570 `_TOGGLEABLE_LEVER_RESOLVERS` with its single entry, :585-588 `SUBSTRATE_FLAG_KEYS`, :591-614 `substrate_flag_snapshot`; orchestrator/game.py:304-309 `DEFAULT_PROMPT_VERSIONS`, :391 the `qwen3_6_27b` registry entry, :424-467 `prompt_versions_for_set`; tests/meetings/test_prompt_byte_golden.py:183 `ARCHIVED_PROMPT_VERSION_SETS` (empty at HEAD) and :424-451 the exact-mapping reverse lookup; tests/meetings/test_lever_registry.py:291-299 `test_the_one_live_resolver_in_the_tree_is_not_reported`; training/surrogate/dataset.py:240 + :831 the `is_reporter` feature (read as evidence, not edited here).), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
