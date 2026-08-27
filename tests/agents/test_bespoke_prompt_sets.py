"""Validation for the Task 14.5 bespoke per-candidate prompt sets.

Five bespoke sets are authored from the ground up — one per candidate
(model, mode) — under ``agents/strategic/prompts/<set>/`` (owner decision
2026-06-30). The ONE hard invariant is the OUTPUT JSON schema: every set's turns
must emit the SAME :class:`~meetings.schemas.MeetingTurn` / :class:`VoteBallot`
shape so all sets parse identically and the graders / recording seam are
unchanged. These tests pin that contract OFFLINE (no LLM, no network):

* every template of every set renders under :class:`jinja2.StrictUndefined` with
  the exact loader kwargs over a reconstructed context (the render smoke test);
* a canonical ``MeetingTurn`` / ``VoteBallot`` parses against the shared schema
  regardless of which set produced it (the cross-set parse check);
* the cover-consistency directive is wired into the REPLY path gated on
  ``is_impostor`` ALONE (present on an impostor reply with
  ``is_body_report=False``; absent on a crewmate reply) — the gp-1 fix the 14.4
  sweep flagged (experiments/lab/report-featherless-sweep.md);
* each set is registered in the per-set version registry with the four shared
  keys + its own namespaced values, and is selectable via ``AILIBI_PROMPT_SET``.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

import pytest

from agents.strategic.prompts.loader import (
    CANONICAL_MAP_CARD,
    CANONICAL_ROOM_DISPLAY_NAMES,
    DEFAULT_PROMPT_SET,
    _map_card_from_neighbors,
    _PROMPTS_ROOT,
    build_prompt_renderers,
    render_map_card,
    resolve_prompt_set,
)
from engine.world import load_canonical_map
from meetings.manager import PromptRenderInputs, SuspicionEntry
from meetings.schemas import (
    AccusationClaim,
    ContradictionRef,
    FoundBodyObservation,
    MeetingTranscript,
    MeetingTurn,
    SawPlayerObservation,
    SawVentObservation,
    VoteBallot,
)
from meetings.transcript import (
    CANONICAL_ROOM_NEIGHBORS,
    WEAK_CONTRADICTION_MARKER_PREFIX,
)
from orchestrator.boundary import public_map_from_engine_map
from orchestrator.game import (
    DEFAULT_PROMPT_VERSIONS,
    IMPOSTOR_ROLL_CALL_PROMPT_VERSION_SETS,
    PROMPT_VERSION_SETS,
    prompt_versions_for_set,
)

# The five Task 14.5 bespoke sets (each a candidate model/mode), plus the
# Task 16.13 locked-model set (the scratch-ladder style base carrying the
# qwen3_32b v5/v6 mechanics — audits/audit-phase-16-model-lock.md).
BESPOKE_SETS = (
    "qwen3_32b",
    "qwen3_32b_thinking",
    "qwen3_30b_a3b",
    "glm_4_32b",
    "cydonia_24b",
    "qwen3_6_27b",
)

# Sets that legitimately CARRY the measured-defect directive batches: the
# qwen3_32b set they were authored on (Tasks 14.11 / 15.4) and the Task 16.13
# qwen3_6_27b set, whose mechanics-pure contract MERGES every qwen3_32b v5/v6
# mechanical directive (restyled, semantics-identical). The remaining 14.5
# sets are frozen — a directive marker leaking into one of THOSE still means
# an out-of-scope edit.
_DIRECTIVE_CARRYING_SETS = frozenset({"qwen3_32b", "qwen3_6_27b"})

# A small reconstructed body-report meeting context (a found body + an accusation
# chain) — enough to exercise every branch of every template.
_OPENING = MeetingTurn(
    turn_id="m-1:turn-0",
    turn_index=0,
    speaker="p-2",
    turn_kind="opening",
    reply_to=None,
    observations=(
        FoundBodyObservation(
            type="found_body", tick=410, body_of="p-7", room="electrical"
        ),
    ),
    claims=(
        AccusationClaim(
            type="accusation", against="p-3", confidence=0.7, reason="near body"
        ),
    ),
    free_text="Found p-7 in electrical; p-3 was nearby.",
)
_PRIOR = MeetingTurn(
    turn_id="m-1:turn-1",
    turn_index=1,
    speaker="p-4",
    turn_kind="reply",
    reply_to="m-1:turn-0",
    observations=(
        SawPlayerObservation(
            type="saw_player",
            tick=405,
            subject="p-3",
            room="electrical",
            co_present=("p-5",),
        ),
    ),
    claims=(
        AccusationClaim(
            type="accusation", against="p-3", confidence=0.8, reason="seen there"
        ),
    ),
    free_text="p-3 was in electrical at 405.",
)
_TRANSCRIPT = MeetingTranscript(turns=(_OPENING, _PRIOR))
_CONTRAS = (
    ContradictionRef(
        contradiction_id="c-1",
        kind="alibi_vs_sighting",
        event_a_id="e-a",
        event_b_id="e-b",
        subjects=("p-3",),
        description="p-3's alibi conflicts with a sighting",
    ),
)
_SUSP = (
    SuspicionEntry(player_id="p-3", suspicion=0.8, trust=0.5),
    SuspicionEntry(player_id="p-5", suspicion=0.3, trust=0.5),
)
_MEMORY = "## Your role\nIMPOSTOR\n## Observations\n- tick 405: saw p-3 in electrical with p-5\n"

# All sets word the wired reply cover directive around "the body's room".
_COVER_MARKER = "body's room"

# Task 14.11 qwen3_32b v4 directive markers (the measured-defect batch;
# audits/audit-2026-07-01-phase-14-baseline1-characterization.md §4). Only the
# qwen3_32b set carries them — the other bespoke sets stay frozen at this task.
_ALIBI_DISCIPLINE_MARKER = "spans rooms you moved between"  # fix 1 (30/295)
_CONFIDENCE_RUBRIC_MARKER = "Confidence rubric"  # fix 4 (64/505 at 1.0)
_BALLOT_WASTE_MARKER = "wastes your vote"  # fix 2 (27 invalid-target ballots)
_ACCUSE_WASTE_MARKER = "wastes your accusation"  # fix 2, turn-side twin


def _flat(text: str) -> str:
    """Collapse whitespace so a directive marker matches across line wraps."""

    return " ".join(text.split())


def _render_all(set_name: str) -> dict[str, str]:
    """Render every template of ``set_name`` over the reconstructed context."""

    r = build_prompt_renderers(set_name)
    out: dict[str, str] = {}
    for trig in (
        "p-2 reported body of p-7 at tick 410",
        "p-2 called an emergency meeting at tick 410",
    ):
        tag = "body" if "reported" in trig else "emergency"
        out[f"crewmate_report/{tag}"] = r.crewmate_report(
            agent_id="p-2",
            current_tick=410,
            meeting_trigger=trig,
            rendered_memory=_MEMORY,
            public_transcript="",
            living_ids=("p-3", "p-5"),
            dead_ids=("p-7",),
        )
        out[f"impostor_report/{tag}"] = r.impostor_report(
            agent_id="p-3",
            current_tick=410,
            meeting_trigger=trig,
            rendered_memory=_MEMORY,
            public_transcript="",
            fellow_impostor_ids=("p-9",),
            living_ids=("p-2", "p-5"),
            dead_ids=("p-7",),
        )
    for is_imp in (True, False):
        for is_body in (True, False):
            out[f"reply/imp={is_imp}/body={is_body}"] = r.statement(
                agent_id="p-3",
                rendered_memory=_MEMORY,
                transcript=_TRANSCRIPT,
                contradictions=_CONTRAS,
                prior_turn=_PRIOR,
                turn_kind="reply",
                fellow_impostor_ids=(("p-9",) if is_imp else ()),
                living_ids=("p-2", "p-5"),
                dead_ids=("p-7",),
                is_impostor=is_imp,
                is_body_report=is_body,
            )
    out["opt_in"] = r.statement(
        agent_id="p-3",
        rendered_memory=_MEMORY,
        transcript=_TRANSCRIPT,
        contradictions=(),
        prior_turn=None,
        turn_kind="opt_in",
        fellow_impostor_ids=(),
        living_ids=("p-2", "p-5"),
        dead_ids=(),
        is_impostor=False,
        is_body_report=False,
    )
    out["vote"] = r.vote(
        voter_id="p-2",
        rendered_memory=_MEMORY,
        transcript=_TRANSCRIPT,
        contradiction_flags=_CONTRAS,
        suspicion_graph=_SUSP,
        candidate_targets=("p-3", "p-5"),
        skip_confidence_threshold=0.6,
        fellow_impostor_ids=(),
    )
    return out


@pytest.mark.parametrize("set_name", BESPOKE_SETS)
class TestBespokeSetRenders:
    def test_every_template_renders_non_empty_under_strict_undefined(
        self, set_name: str
    ) -> None:
        # StrictUndefined raises on a missing / typo'd kwarg, so a clean render of
        # every branch proves no template kwarg drift (the sweep's abort risk).
        for label, text in _render_all(set_name).items():
            assert text.strip(), f"{set_name}: {label} rendered empty"

    def test_vote_renders_eval_suspicion_parse_line(self, set_name: str) -> None:
        # The recorded-ballot analyzer (eval._suspicion_parse) reads this exact
        # wording; keep it stable across every set for a future re-record.
        vote = _render_all(set_name)["vote"]
        assert "maximum suspicion among the living ejection targets is" in vote

    def test_cover_directive_wired_into_reply_path_gated_on_is_impostor(
        self, set_name: str
    ) -> None:
        rendered = _render_all(set_name)
        # Wired into the REPLY path gated on is_impostor ALONE: present even with
        # is_body_report=False (not gated off the body-report opening as 9B is).
        assert _COVER_MARKER in rendered["reply/imp=True/body=False"].lower()
        # Absent from a crewmate reply (is_impostor=False), even body=True.
        assert _COVER_MARKER not in rendered["reply/imp=False/body=True"].lower()


class TestQwen332bV4Directives:
    """Task 14.11 v4 pins, mirroring the cover-directive gating pins.

    The v4 hardening targets the six defects MEASURED on baseline 1 (audit
    2026-07-01 §4). These pins hold the three template-visible directives the
    task contract names — alibi discipline, dead-roster adjacency, confidence
    rubric — on the qwen3_32b set ONLY (the other bespoke sets are frozen).
    """

    def test_alibi_discipline_present_in_every_turn_template(self) -> None:
        # Fix 1 (30/295 self-alibis self-contradicted by the speaker's own
        # same-turn task observation — the railroad's fuel; seed-44 m1 p-1):
        # every template that emits an alibi claim carries the discipline line.
        rendered = _render_all("qwen3_32b")
        for label in (
            "crewmate_report/body",
            "crewmate_report/emergency",
            "impostor_report/body",
            "impostor_report/emergency",
            "reply/imp=True/body=True",
            "reply/imp=False/body=False",
            "opt_in",
        ):
            assert _ALIBI_DISCIPLINE_MARKER in _flat(rendered[label]), label

    def test_confidence_rubric_present_in_every_turn_template(self) -> None:
        # Fix 4 (64/505 accusation claims at exactly 1.0; claim ECE 0.347): the
        # rubric lands beside the accusation claim shape in every turn template.
        rendered = _render_all("qwen3_32b")
        for label in (
            "crewmate_report/body",
            "impostor_report/body",
            "reply/imp=True/body=False",
            "reply/imp=False/body=True",
            "opt_in",
        ):
            assert _CONFIDENCE_RUBRIC_MARKER in _flat(rendered[label]), label
        # The ballot keeps its own §4.6 confidence guidance — the rubric is a
        # turn-side (accusation-claim) directive, not a ballot one.
        assert _CONFIDENCE_RUBRIC_MARKER not in rendered["vote"]

    def test_ballot_dead_roster_warning_adjacent_to_target_selection(self) -> None:
        # Fix 2 (27 invalid-target ballots): the waste warning sits INSIDE the
        # valid-targets section (adjacent to the roster, not a far-away rule)...
        vote = _render_all("qwen3_32b")["vote"]
        assert "## Valid ejection targets" in vote
        section = vote.split("## Valid ejection targets", 1)[1].split("\n## ", 1)[0]
        assert _BALLOT_WASTE_MARKER in _flat(section)
        # ...and is repeated at the `target` field bullet (the point of choice),
        # alongside the roster itself.
        output_tail = vote.split("## Output", 1)[1]
        assert _BALLOT_WASTE_MARKER in _flat(output_tail)

    def test_reply_dead_roster_warning_gated_on_dead_ids(self) -> None:
        # The turn-side twin: rendered with the dead roster, absent without it
        # (mirroring how the roster lines themselves are guarded).
        rendered = _render_all("qwen3_32b")
        assert _ACCUSE_WASTE_MARKER in _flat(rendered["reply/imp=False/body=True"])
        assert _ACCUSE_WASTE_MARKER not in _flat(rendered["opt_in"])  # dead_ids=()

    def test_ballot_dead_graph_rows_are_tagged_out_of_game(self) -> None:
        # Fix 2, second directive: the recurrence shape on the 27 recorded
        # failure contexts was a DEAD player carrying the graph's top suspicion
        # (0.75-1.00) while the roster warning sat elsewhere — so the graph rows
        # themselves are tagged where the model reads its strongest signal. A
        # graph entry missing from candidate_targets gets the tag; valid
        # entries stay untagged (and ad-hoc renders without targets skip it).
        r = build_prompt_renderers("qwen3_32b")
        dead_susp = _SUSP + (
            SuspicionEntry(player_id="p-9", suspicion=0.95, trust=0.2),
        )
        vote = r.vote(
            voter_id="p-2",
            rendered_memory=_MEMORY,
            transcript=_TRANSCRIPT,
            contradiction_flags=_CONTRAS,
            suspicion_graph=dead_susp,
            candidate_targets=("p-3", "p-5"),
            skip_confidence_threshold=0.6,
            fellow_impostor_ids=(),
        )
        # Exactly the dead entry is tagged; the tag sits AFTER the trust field
        # so the eval-side row parser keeps reading tagged rows (the regex in
        # extract_gameplay_facts is an unanchored finditer over the row shape).
        assert "`p-9`: suspicion 0.95, trust 0.20 — OUT OF THE GAME" in vote
        assert vote.count(" — OUT OF THE GAME (dead or ejected") == 1
        assert "`p-3`: suspicion 0.80, trust 0.50 —" not in vote  # valid: no tag

    def test_ballot_reason_id_example_is_a_real_transcript_turn_id(self) -> None:
        # Fix 3 (20 invalid primary_reason_id nulls): the worked example copies
        # a turn id VERBATIM from the live transcript (DESIGN.md §5.5 — never a
        # hardcoded id). The reconstructed context's latest turn is m-1:turn-1.
        vote = _render_all("qwen3_32b")["vote"]
        assert '"primary_reason_id": "m-1:turn-1"' in vote

    def test_ballot_rationale_carries_two_contrasting_voice_examples(self) -> None:
        # Fix 6 (320/891 ballots shared one literal template family): the
        # rationale bullet shows both registers so the model stops converging
        # on a single stock sentence.
        vote = _render_all("qwen3_32b")["vote"]
        assert "evidence-citing:" in vote
        assert "gut-read:" in vote

    def test_frozen_sets_do_not_carry_the_v4_directives(self) -> None:
        # The task iterates ONLY the locked qwen3_32b set; a v4 marker leaking
        # into a FROZEN set means an out-of-scope edit. The 16.13 qwen3_6_27b
        # set carries the directives by contract (the mechanics merge) and is
        # exempt alongside its source.
        for set_name in BESPOKE_SETS:
            if set_name in _DIRECTIVE_CARRYING_SETS:
                continue
            rendered = _render_all(set_name)
            for text in rendered.values():
                assert _ALIBI_DISCIPLINE_MARKER not in _flat(text), set_name
                assert _CONFIDENCE_RUBRIC_MARKER not in _flat(text), set_name


class TestQwen332bV5VentElicitation:
    """Task 15.4 v5 pins, mirroring the 14.11 v4 directive pins.

    The v5 revision makes witnessed vents speakable: the turn/opening
    templates elicit a structured ``saw_vent`` observation for the
    "You witnessed <player> vent in <room>." rendered-memory line and
    advertise the new union shape. qwen3_32b ONLY — the other bespoke sets
    stay frozen, and ``vote_ballot.j2`` is byte-identical (its next edit is
    Task 15.5's per-template v6 bump).
    """

    # The elicitation instruction (crewmate opening + reply + opt_in) and the
    # union-shape advert (every turn/opening template).
    _ELICITATION_MARKER = "put it on the record as a structured `saw_vent`"
    _SHAPE_MARKER = '"type": "saw_vent"'
    # A rendered memory carrying the exact store.py witnessed-vent line the
    # elicitation keys on (agents/memory/store.py::_render_saw_player).
    _VENT_MEMORY = (
        "## Your role\nCREWMATE\n"
        "## Recent observations (most salient first):\n"
        "- [tick 405] You witnessed p-3 vent in ELECTRICAL.\n"
    )

    def _render_crewmate_with_vent_memory(self) -> str:
        r = build_prompt_renderers("qwen3_32b")
        return r.crewmate_report(
            agent_id="p-2",
            current_tick=410,
            meeting_trigger="p-2 reported body of p-7 at tick 410",
            rendered_memory=self._VENT_MEMORY,
            public_transcript="",
            living_ids=("p-3", "p-5"),
            dead_ids=("p-7",),
        )

    def test_memory_with_vent_renders_the_elicitation_instruction(self) -> None:
        # The DoD's prompt-fixture shape: a memory-with-vent render carries
        # BOTH the witnessed-vent memory line and the instruction to speak it
        # as a structured saw_vent observation.
        rendered = self._render_crewmate_with_vent_memory()
        assert "You witnessed p-3 vent in ELECTRICAL." in rendered
        assert self._ELICITATION_MARKER in _flat(rendered)

    def test_elicitation_present_in_crewmate_and_chain_templates(self) -> None:
        rendered = _render_all("qwen3_32b")
        for label in (
            "crewmate_report/body",
            "crewmate_report/emergency",
            "reply/imp=True/body=True",
            "reply/imp=False/body=False",
            "opt_in",
        ):
            assert self._ELICITATION_MARKER in _flat(rendered[label]), label

    def test_saw_vent_shape_advertised_in_every_turn_template(self) -> None:
        rendered = _render_all("qwen3_32b")
        for label in (
            "crewmate_report/body",
            "crewmate_report/emergency",
            "impostor_report/body",
            "impostor_report/emergency",
            "reply/imp=True/body=False",
            "reply/imp=False/body=True",
            "opt_in",
        ):
            assert self._SHAPE_MARKER in rendered[label], label

    def test_impostor_opening_carries_no_elicitation_ask(self) -> None:
        # Deliberate: vents are impostor-only, so the only witnessed-vent
        # rows an impostor's memory can hold name a TEAMMATE (dropped by the
        # 7.12 observation guard) — eliciting them would only invite
        # fabrication. The shape advert stays (schema completeness).
        rendered = _render_all("qwen3_32b")
        for label in ("impostor_report/body", "impostor_report/emergency"):
            assert self._ELICITATION_MARKER not in _flat(rendered[label]), label

    def test_vote_ballot_carries_no_vent_directive(self) -> None:
        # vote_ballot.j2 is byte-identical at this task (15.5 owns its edit),
        # so no v5 vent marker may appear in the ballot render.
        vote = _render_all("qwen3_32b")["vote"]
        assert self._ELICITATION_MARKER not in _flat(vote)
        assert self._SHAPE_MARKER not in vote

    def test_transcript_loop_renders_spoken_vents(self) -> None:
        # A later speaker must SEE an earlier speaker's structured vent
        # observation (the opt-in eligibility DoD's prompt surface).
        vent_turn = MeetingTurn(
            turn_id="m-1:turn-2",
            turn_index=2,
            speaker="p-5",
            turn_kind="opt_in",
            reply_to=None,
            observations=(
                SawVentObservation(
                    type="saw_vent", tick=406, subject="p-3", room="ELECTRICAL"
                ),
            ),
            claims=(),
            free_text="I watched p-3 vent.",
        )
        r = build_prompt_renderers("qwen3_32b")
        rendered = r.statement(
            agent_id="p-2",
            rendered_memory=_MEMORY,
            transcript=MeetingTranscript(turns=(_OPENING, _PRIOR, vent_turn)),
            contradictions=(),
            prior_turn=None,
            turn_kind="opt_in",
            fellow_impostor_ids=(),
            living_ids=("p-3", "p-5"),
            dead_ids=(),
            is_impostor=False,
            is_body_report=True,
        )
        assert "witnessed p-3 VENT in ELECTRICAL" in rendered

    def test_registry_stamps_vote_ballot_v6_others_v5(self) -> None:
        # Task 15.4 owns the single v4 -> v5 SET bump; Task 15.5 (reporter
        # exculpation) advances vote_ballot ALONE to v6 for its per-template
        # annotation, so the pre- and post-15.5 vote-prompt bodies can never
        # share a provenance stamp. The other three templates stay v5.
        versions = prompt_versions_for_set("qwen3_32b")
        assert versions == {
            "crewmate_report": "crewmate_report.qwen3_32b.v5",
            "impostor_report": "impostor_report.qwen3_32b.v5",
            "accusation_round": "accusation_round.qwen3_32b.v5",
            "vote_ballot": "vote_ballot.qwen3_32b.v6",
        }

    def test_frozen_sets_do_not_carry_the_v5_markers(self) -> None:
        # Same exemption as the v4 batch: qwen3_6_27b merges the v5 vent
        # mechanics (Task 16.13), so only the FROZEN 14.5 sets are swept.
        for set_name in BESPOKE_SETS:
            if set_name in _DIRECTIVE_CARRYING_SETS:
                continue
            rendered = _render_all(set_name)
            for text in rendered.values():
                assert self._ELICITATION_MARKER not in _flat(text), set_name
                assert self._SHAPE_MARKER not in text, set_name


class TestQwen3627bV5InWorldRegister:
    """Version pin for the locked set's current lineage.

    Each layer is exactly one registry entry, so every prompt change is
    separately attributable at the record that adopts it: v1 the baseline-4
    bespoke port, v2 the 16.15 elicitation batch, v3 the 16.16 persona voice
    layer, v4 the 20.31 evidence-honesty batch, v5 the Task-21.1 in-world
    register (the machinery nouns out of every rendered line, the map card's
    prose-name anchor). No two bodies can share a stamp: the committed sample
    sets stamp *.qwen3_6_27b.v4 and re-render through the archived v4 bytes
    until the adopting re-record. The per-ask mechanism fixtures live in
    ``tests/meetings/test_elicitation_fixtures.py``; the persona render
    fixtures in ``tests/meetings/test_persona_render.py``; this pin holds the
    stamp.
    """

    def test_registry_stamps_all_four_templates_v5(self) -> None:
        versions = prompt_versions_for_set("qwen3_6_27b")
        assert versions == {
            "crewmate_report": "crewmate_report.qwen3_6_27b.v5",
            "impostor_report": "impostor_report.qwen3_6_27b.v5",
            "accusation_round": "accusation_round.qwen3_6_27b.v5",
            "vote_ballot": "vote_ballot.qwen3_6_27b.v5",
        }

    def test_bumped_stamps_never_collide_with_prior_bodies(self) -> None:
        # Every earlier lineage stamp is still worn by committed bytes (the
        # sample sets and the ML corpus stamp .v4). The bumped registry must
        # never re-mint one for the v5 bodies.
        for value in prompt_versions_for_set("qwen3_6_27b").values():
            assert value.endswith(".qwen3_6_27b.v5")
            assert ".v1" not in value
            assert ".v2" not in value
            assert ".v3" not in value
            assert ".v4" not in value


def test_cross_set_parse_invariant_is_shared() -> None:
    # The one hard invariant: a canonical MeetingTurn / VoteBallot parses against
    # the shared schema regardless of which set produced it. The set only changes
    # the instruction prose; model_validate_json + the recording seam are
    # set-independent, which is the precondition for later heterogeneous play.
    turn = MeetingTurn.model_validate_json(_OPENING.model_dump_json())
    assert turn == _OPENING
    ballot = VoteBallot(
        voter="p-2",
        target="p-3",
        confidence=0.7,
        primary_reason_id="m-1:turn-0",
        considered_alternatives=("p-5",),
        rationale_text="p-3 near body",
    )
    assert VoteBallot.model_validate_json(ballot.model_dump_json()) == ballot


@pytest.mark.parametrize("set_name", BESPOKE_SETS)
class TestBespokeSetRegistration:
    def test_selectable_via_env(self, set_name: str) -> None:
        assert resolve_prompt_set(env={"AILIBI_PROMPT_SET": set_name}) == set_name
        # The renderers build (the set directory exists and is loadable).
        assert build_prompt_renderers(set_name) is not None

    def test_version_registry_has_shared_keys_and_own_values(
        self, set_name: str
    ) -> None:
        versions = prompt_versions_for_set(set_name)
        # Same FOUR keys as the 9B default (the recording seam is set-independent).
        assert set(versions) == set(DEFAULT_PROMPT_VERSIONS)
        # Own namespaced values, distinct from the pinned 9B set.
        assert versions != DEFAULT_PROMPT_VERSIONS
        for key, value in versions.items():
            assert set_name in value, f"{set_name}: {key} version not namespaced"

    def test_registered_set_is_not_the_default(self, set_name: str) -> None:
        assert set_name in PROMPT_VERSION_SETS
        assert set_name != DEFAULT_PROMPT_SET


class TestQwen3627bV5RenderPins:
    """Render pins for the locked set's live v5 bodies.

    The committed bytes stamp v4 and re-render through the archive, so the
    prompt-byte golden does not exercise these bodies during the bump-in-flight
    window. These renders are what guards them instead.
    """

    def _render(self, *, impostor_count: int) -> dict[str, str]:
        r = build_prompt_renderers("qwen3_6_27b")
        inputs = PromptRenderInputs(impostor_count=impostor_count)
        return {
            "crewmate_report": r.crewmate_report(
                agent_id="p-2",
                current_tick=410,
                meeting_trigger="p-2 reported body of p-7 at tick 410",
                rendered_memory=_MEMORY,
                public_transcript="",
                living_ids=("p-3", "p-5"),
                dead_ids=("p-7",),
                render_inputs=inputs,
            ),
            "impostor_report": r.impostor_report(
                agent_id="p-3",
                current_tick=410,
                meeting_trigger="p-3 reported body of p-7 at tick 410",
                rendered_memory=_MEMORY,
                public_transcript="",
                fellow_impostor_ids=("p-9",),
                living_ids=("p-2", "p-5"),
                dead_ids=("p-7",),
                render_inputs=inputs,
            ),
            "accusation_round": r.statement(
                agent_id="p-3",
                rendered_memory=_MEMORY,
                transcript=_TRANSCRIPT,
                contradictions=_CONTRAS,
                prior_turn=_PRIOR,
                turn_kind="reply",
                fellow_impostor_ids=(),
                living_ids=("p-2", "p-5"),
                dead_ids=("p-7",),
                is_impostor=False,
                is_body_report=True,
                render_inputs=inputs,
            ),
            "vote_ballot": r.vote(
                voter_id="p-2",
                rendered_memory=_MEMORY,
                transcript=_TRANSCRIPT,
                contradiction_flags=_CONTRAS,
                suspicion_graph=_SUSP,
                candidate_targets=("p-3", "p-5"),
                skip_confidence_threshold=0.6,
                fellow_impostor_ids=(),
                render_inputs=inputs,
            ),
        }

    def test_persona_and_win_condition_follow_the_impostor_count(self) -> None:
        # Verdicts claim 11 (b): all six templates hard-coded ONE hidden
        # impostor and a parity sentence that is arithmetically wrong for two.
        # A two-impostor render now says two and states the parity condition;
        # a one-impostor render keeps the singular wording it always had.
        one, two = self._render(impostor_count=1), self._render(impostor_count=2)
        for label in ("crewmate_report", "impostor_report", "accusation_round"):
            assert "a hidden impostor" in one[label], label
            assert "two hidden impostors" in two[label], label
            assert "a hidden impostor" not in two[label], label
            assert "voting the impostor out" in one[label], label
            assert "voting both impostors out" in two[label], label
        # The ballot words the same facts for a voter rather than a speaker.
        assert "a hidden impostor kills crewmates" in one["vote_ballot"]
        assert "two hidden impostors kill crewmates" in two["vote_ballot"]
        # The parity condition -- impostors win at alive_impostors >=
        # alive_crewmates (engine/win_conditions.py) -- is stated in BOTH.
        for rendered in (*one.values(), *two.values()):
            assert "by surviving until they equal or outnumber the crew" in rendered

    def test_a_zero_or_negative_impostor_count_fails_loud(self) -> None:
        # The gate can fail: an impossible roster is a wiring bug, not a
        # wording default (AGENTS.md "no silent fallbacks").
        with pytest.raises(ValueError, match="at least 1"):
            self._render(impostor_count=0)

    def test_teammate_line_agrees_in_number(self) -> None:
        r = build_prompt_renderers("qwen3_6_27b")
        inputs = PromptRenderInputs(impostor_count=3)
        for fellows, singular, plural in (
            (("p-9",), True, False),
            (("p-9", "p-8"), False, True),
        ):
            opening = r.impostor_report(
                agent_id="p-3",
                current_tick=410,
                meeting_trigger="p-3 reported body of p-7 at tick 410",
                rendered_memory=_MEMORY,
                public_transcript="",
                fellow_impostor_ids=fellows,
                living_ids=("p-2", "p-5"),
                dead_ids=("p-7",),
                render_inputs=inputs,
            )
            assert ("Your fellow saboteur:" in opening) is singular, fellows
            assert ("Your fellow saboteurs:" in opening) is plural, fellows
            ballot = r.vote(
                voter_id="p-3",
                rendered_memory=_MEMORY,
                transcript=_TRANSCRIPT,
                contradiction_flags=_CONTRAS,
                suspicion_graph=_SUSP,
                candidate_targets=("p-2", "p-5"),
                skip_confidence_threshold=0.6,
                fellow_impostor_ids=fellows,
                render_inputs=inputs,
            )
            assert ("is your fellow saboteur." in ballot) is singular, fellows
            assert ("are your fellow saboteurs." in ballot) is plural, fellows

    def test_map_card_renders_in_every_meeting_template(self) -> None:
        # R12: 0 of 7,458 recorded prompts carried any room list, adjacency or
        # travel time, while 148 of 234 STRONG alibi_vs_sighting flags named
        # rooms one doorway apart.
        card_lines = CANONICAL_MAP_CARD.splitlines()
        assert len(card_lines) <= 12
        assert CANONICAL_MAP_CARD.count("ONE tick of walking") == 1
        for label, rendered in self._render(impostor_count=2).items():
            assert CANONICAL_MAP_CARD in rendered, label

    def test_map_card_is_the_engine_map_and_the_detectors_table(self) -> None:
        # One adjacency graph, not three: the rendered card, the detector's
        # frozen table, and the engine map must agree, so a prompt can never
        # promise a reconciliation rule the detector does not apply.
        engine_view = public_map_from_engine_map(load_canonical_map())
        assert render_map_card(engine_view) == CANONICAL_MAP_CARD
        rooms = sorted(CANONICAL_ROOM_NEIGHBORS)
        assert len(rooms) == 10
        for room in rooms:
            neighbours = ", ".join(
                f"{CANONICAL_ROOM_DISPLAY_NAMES[n]} ({n})"
                for n in sorted(CANONICAL_ROOM_NEIGHBORS[room])
            )
            named = f"{CANONICAL_ROOM_DISPLAY_NAMES[room]} ({room})"
            assert f"- {named}: {neighbours}" in CANONICAL_MAP_CARD
        # The gate can fail: drop one doorway and the card stops matching.
        thinned = engine_view.model_copy(
            update={
                "room_neighbors": {
                    room: tuple(n for n in neighbours if n != "MEDBAY")
                    for room, neighbours in engine_view.room_neighbors.items()
                }
            }
        )
        assert render_map_card(thinned) != CANONICAL_MAP_CARD

    def test_room_display_names_are_the_engine_maps_own_names(self) -> None:
        # A-48: the agents speak raw ids because no authored surface ever
        # spelled a room out. The card publishes the map's OWN name for each
        # room, so the anchored register cannot drift into a spelling the game
        # does not use ("East Hall" for EAST_HALL, the habit the corpus shows).
        # Tests sit outside the §1.3 firewall, so the engine import is legal
        # exactly here.
        game_map = load_canonical_map()
        assert dict(CANONICAL_ROOM_DISPLAY_NAMES) == {
            room: game_map.rooms[room].name for room in game_map.rooms
        }
        assert CANONICAL_ROOM_DISPLAY_NAMES["EAST_HALL"] == "East Hallway"
        assert CANONICAL_ROOM_DISPLAY_NAMES["WEST_HALL"] == "West Hallway"

    def test_a_wrong_display_name_fails_the_card(self) -> None:
        # The gate can fail: one name off the map's own spelling and the
        # rendered card stops matching the committed one.
        wrong = dict(CANONICAL_ROOM_DISPLAY_NAMES) | {"EAST_HALL": "East Hall"}
        assert (
            _map_card_from_neighbors(CANONICAL_ROOM_NEIGHBORS, names=wrong)
            != CANONICAL_MAP_CARD
        )

    def test_an_unnamed_room_fails_loud(self) -> None:
        # No silent fallback to the bare id: a card that quietly dropped the
        # prose half would un-anchor the register it exists to set.
        missing = {
            room: name
            for room, name in CANONICAL_ROOM_DISPLAY_NAMES.items()
            if room != "REACTOR"
        }
        with pytest.raises(ValueError, match="no display name"):
            _map_card_from_neighbors(CANONICAL_ROOM_NEIGHBORS, names=missing)

    def test_map_card_never_publishes_vent_topology(self) -> None:
        # Vents are impostor-only knowledge the same public view carries;
        # publishing them to the table would convert a legibility fix into a
        # firewall breach. Name every vent id so a widened card cannot pass.
        engine_view = public_map_from_engine_map(load_canonical_map())
        vent_ids = sorted(engine_view.vent_rooms)
        assert vent_ids == [
            "ADMIN_VENT",
            "ENGINEERING_VENT",
            "LABS_VENT",
            "MEDBAY_VENT",
            "REACTOR_VENT",
            "STORAGE_VENT",
        ]
        for label, rendered in self._render(impostor_count=2).items():
            for vent_id in vent_ids:
                assert vent_id not in rendered, (label, vent_id)

    def test_movement_observation_shape_is_offered_by_the_turn_templates(self) -> None:
        # The shape the upstream movement lever reads; a speaker cannot answer
        # with a claim no template names.
        rendered = self._render(impostor_count=2)
        for label in ("crewmate_report", "accusation_round"):
            assert '"type": "saw_move"' in rendered[label], label
            assert '"from_room"' in rendered[label], label
            assert '"to_room"' in rendered[label], label


# --------------------------------------------------------------------------- #
# The dialect net: what a rendered prompt may NOT teach the table to say       #
# --------------------------------------------------------------------------- #

# Out-of-world vocabulary. A prompt that uses these words teaches them: over the
# committed corpus the oracle register appears in 45 of the 326 meetings where
# the proof block rendered and in 0 of the 342 where it did not. The net runs
# over RENDER OUTPUT only — the templates' Jinja identifiers (``flag_groups``,
# ``contradiction_flags``) are control-flow names that never render.
_BANNED_RENDER_VOCABULARY: tuple[str, ...] = (
    "the engine",
    "the system",
    "the detector",
    "certif",
    "flag",
)

_PROOF_FLAG = ContradictionRef(
    contradiction_id="c-proof",
    kind="vent_sighting",
    event_a_id="e-a",
    event_b_id="e-b",
    subjects=("p-3",),
    description="p-2 witnessed p-3 vent in MEDBAY",
)
_CONFLICT_FLAG = ContradictionRef(
    contradiction_id="c-conflict",
    kind="alibi_vs_sighting",
    event_a_id="e-c",
    event_b_id="e-d",
    subjects=("p-5",),
    description="p-5's alibi conflicts with a sighting",
)
_WEAK_FLAG = ContradictionRef(
    contradiction_id="c-weak",
    kind="alibi_conflict",
    event_a_id="e-e",
    event_b_id="e-f",
    subjects=("p-5",),
    description=(
        f"p-5's two alibis disagree {WEAK_CONTRADICTION_MARKER_PREFIX}self-pair]"
    ),
)
_ALL_GROUPS = (_PROOF_FLAG, _CONFLICT_FLAG, _WEAK_FLAG)

# A soft-only row, so the ballot renders the provenance tag and the legend that
# explains it — two more surfaces the sweep has to cover.
_PROV_ROWS = (
    SuspicionEntry(player_id="p-3", suspicion=0.8, trust=0.5, flag_lift=0.2),
    SuspicionEntry(
        player_id="p-5",
        suspicion=0.3,
        trust=0.5,
        testimony_spread=0.2,
        carried_soft=0.1,
    ),
)


def _render_locked_set(root: Path | None = None) -> dict[str, str]:
    """Render all four default templates with every flag group present."""

    r = (
        build_prompt_renderers("qwen3_6_27b")
        if root is None
        else build_prompt_renderers("qwen3_6_27b", root=root)
    )
    inputs = PromptRenderInputs(impostor_count=2)
    return {
        "crewmate_report": r.crewmate_report(
            agent_id="p-2",
            current_tick=410,
            meeting_trigger="p-2 reported body of p-7 at tick 410",
            rendered_memory=_MEMORY,
            public_transcript="",
            living_ids=("p-3", "p-5"),
            dead_ids=("p-7",),
            render_inputs=inputs,
        ),
        "impostor_report": r.impostor_report(
            agent_id="p-3",
            current_tick=410,
            meeting_trigger="p-3 reported body of p-7 at tick 410",
            rendered_memory=_MEMORY,
            public_transcript="",
            fellow_impostor_ids=("p-9",),
            living_ids=("p-2", "p-5"),
            dead_ids=("p-7",),
            render_inputs=inputs,
        ),
        "accusation_round": r.statement(
            agent_id="p-3",
            rendered_memory=_MEMORY,
            transcript=_TRANSCRIPT,
            contradictions=_ALL_GROUPS,
            prior_turn=_PRIOR,
            turn_kind="reply",
            fellow_impostor_ids=(),
            living_ids=("p-2", "p-5"),
            dead_ids=("p-7",),
            is_impostor=False,
            is_body_report=True,
            render_inputs=inputs,
        ),
        "vote_ballot": r.vote(
            voter_id="p-2",
            rendered_memory=_MEMORY,
            transcript=_TRANSCRIPT,
            contradiction_flags=_ALL_GROUPS,
            suspicion_graph=_SUSP,
            candidate_targets=("p-3", "p-5"),
            skip_confidence_threshold=0.6,
            fellow_impostor_ids=(),
            suspicion_provenance=_PROV_ROWS,
            render_inputs=inputs,
        ),
    }


def _dialect_hits(rendered: str) -> list[str]:
    """Every banned out-of-world word this render would teach the table."""

    lowered = rendered.lower()
    return [word for word in _BANNED_RENDER_VOCABULARY if word in lowered]


class TestNoTaughtDialect:
    """No rendered prompt hands the table an out-of-world word to repeat."""

    def test_no_default_render_carries_machinery_vocabulary(self) -> None:
        # Every flag group renders at once, so the proof line, the conflicting
        # paragraph, the weak paragraph, the provenance tag and the ballot's
        # decision prose are all on the page being swept.
        for label, rendered in _render_locked_set().items():
            assert _dialect_hits(rendered) == [], (label, _dialect_hits(rendered))

    def test_the_flag_groups_actually_rendered(self) -> None:
        # The sweep above proves nothing if the block it sweeps was empty.
        for label in ("accusation_round", "vote_ballot"):
            rendered = _render_locked_set()[label]
            assert "<contradictions>" in rendered, label
            assert "Proof. Only an impostor can vent" in rendered, label
            assert "Conflicting accounts." in rendered, label
            assert "Weak signals." in rendered, label
        assert (
            "no contradiction; carried/soft only" in _render_locked_set()["vote_ballot"]
        )

    def test_the_net_bites_a_reworded_body(self, tmp_path: Path) -> None:
        # The gate can fail: restore the v4 oracle sentence in a scratch copy of
        # the set and the same net must catch it.
        root = tmp_path / "prompts"
        shutil.copytree(_PROMPTS_ROOT / "qwen3_6_27b", root / "qwen3_6_27b")
        victim = root / "qwen3_6_27b" / "vote_ballot.j2"
        victim.write_text(
            victim.read_text(encoding="utf-8").replace(
                "Proof. Only an impostor can vent, so a witnessed vent here",
                "Proof. The engine certified these: only an impostor can vent, "
                "so a flag here",
            ),
            encoding="utf-8",
        )

        hits = _dialect_hits(_render_locked_set(root=root)["vote_ballot"])
        assert "the engine" in hits
        assert "certif" in hits
        assert "flag" in hits


# --------------------------------------------------------------------------- #
# The version marker: every template header names the stamp the registry serves #
# --------------------------------------------------------------------------- #

_MARKER_RE = re.compile(r"version\s+(\S+)")


def _marker_version(header: str) -> str:
    """Read the ``version <template>.<set>.<vN>`` marker out of a header."""

    match = _MARKER_RE.search(header)
    if match is None:
        raise AssertionError(f"no version marker in header: {header!r}")
    return match.group(1)


def _template_header(path: Path) -> str:
    with path.open(encoding="utf-8") as handle:
        return "".join(line for _, line in zip(range(8), handle, strict=False))


class TestVersionMarkersMatchTheRegistry:
    """A marker left behind renders nothing, so only a test can catch it.

    The markers live inside the ``{#- ... -#}`` header and never reach a model,
    which is exactly why a stale one survives every render assertion in this
    file. Both registries are covered: the four default bodies and the two
    ``*_roll_call.j2`` variant bodies on their own v1 lineage.
    """

    def test_every_default_marker_equals_its_registry_stamp(self) -> None:
        root = _PROMPTS_ROOT / "qwen3_6_27b"
        for key, stamp in prompt_versions_for_set("qwen3_6_27b").items():
            header = _template_header(root / f"{key}.j2")
            assert _marker_version(header) == stamp, key

    def test_every_variant_marker_equals_its_registry_stamp(self) -> None:
        root = _PROMPTS_ROOT / "qwen3_6_27b"
        variant = IMPOSTOR_ROLL_CALL_PROMPT_VERSION_SETS["qwen3_6_27b"]
        for key in ("impostor_report", "accusation_round"):
            stamp = variant[key]
            # The stamp's template component names the variant FILE on disk.
            header = _template_header(root / f"{stamp.split('.')[0]}.j2")
            assert _marker_version(header) == stamp, key

    def test_a_stale_marker_fails_the_checker(self) -> None:
        # The gate can fail: a header left on the previous version is exactly
        # the drift this test exists to catch.
        stale = "   prompt_id: vote_ballot  --  version vote_ballot.qwen3_6_27b.v4\n"
        assert (
            _marker_version(stale)
            != prompt_versions_for_set("qwen3_6_27b")["vote_ballot"]
        )
