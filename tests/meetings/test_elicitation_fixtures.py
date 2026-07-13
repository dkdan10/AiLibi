"""Task 16.15 — the elicitation batch: per-ask mechanism fixtures.

Five coordinated asks land in the locked ``qwen3_6_27b`` set behind ONE
set-level version bump (v1 -> v2, pinned in
``tests/agents/test_bespoke_prompt_sets.py``):

(a) the J2a provenance surface (post-phase-14 V&J planning §3.4 — the ballot
    renders each candidate's suspicion WITH its carried-vs-this-meeting split,
    soft-only rows annotated);
(b) J3 citation-required confidence (ibid. §3.4 + baseline-4 audit §6 — every
    EJECT sources itself to a turn id or a 16.5 observation id, the sanctioned
    gut-read exemplar is gone, the skip discipline is re-anchored);
(c) roll-call elicitation (baseline-4 audit §6 — the crew surfaces ask for one
    CHECKABLE ``whereabouts`` self-placement, room + tick, 16.7's kind);
(d) the vent tail (phase-15 close audit §11 — the held-vent ask lands harder,
    with the worked example the v5 ladder proved moves uptake);
(e) the self-accusation fix (wave-0 close, 3/851 — the impostor turn/ballot
    framing closes the self-naming slot).

Every fixture proves MECHANISM, never model behavior (the contract's
record-only discipline; uptake is 16.17's measurement): the rendered template
CARRIES the elicitation, and a synthetic compliant response ROUND-TRIPS into
the typed kinds through the real validation path — pydantic
``MeetingTurn``/``VoteBallot`` validation, the real
:class:`meetings.manager.MeetingManager` run (the mark-and-null citation
normalizer included), and the transcript-side placement consumer
(:func:`meetings.transcript.reconstruct_stated_paths`). Renders go through
:func:`agents.strategic.prompts.loader.build_prompt_renderers` — the
production loader over the real template bytes.

The provenance surface is kwarg-gated (DoD): a render whose inputs do not
supply ``suspicion_provenance`` carries none of it, which is what keeps every
committed-set re-render byte-identical (the prompt-byte golden walks the
committed v1 stamps through the archived v1 bodies —
``tests/meetings/test_prompt_byte_golden.py``).
"""

from __future__ import annotations

from agents.memory.beliefs import SUSPICION_PROVENANCE_ATOL, SuspicionProvenance
from agents.strategic.prompts.loader import PromptRenderers, build_prompt_renderers
from eval._suspicion_parse import parse_rendered_max_suspicion
from meetings.manager import SuspicionEntry
from meetings.schemas import (
    AccusationClaim,
    MeetingTranscript,
    MeetingTurn,
    SawVentObservation,
    VoteBallot,
    WhereaboutsClaim,
)
from meetings.transcript import reconstruct_stated_paths
from tests.meetings.test_ballot_observation_citation import (
    _obs_vote_responder,  # noqa: PLC2701
    _participants,  # noqa: PLC2701
)
from tests.meetings.test_manager import (
    _make_responder,  # noqa: PLC2701
    _run_meeting,  # noqa: PLC2701
)

# The locked set (Task 16.2 GO; directory agents/strategic/prompts/qwen3_6_27b/).
_LOCKED_SET = "qwen3_6_27b"

# A small reconstructed body-report context — enough to exercise every branch.
_OPENING = MeetingTurn(
    turn_id="m-1:turn-0",
    turn_index=0,
    speaker="p-2",
    turn_kind="opening",
    reply_to=None,
    observations=(),
    claims=(
        AccusationClaim(
            type="accusation", against="p-3", confidence=0.7, reason="near body"
        ),
    ),
    free_text="p-3 was near where it happened.",
)
_PRIOR = MeetingTurn(
    turn_id="m-1:turn-1",
    turn_index=1,
    speaker="p-4",
    turn_kind="reply",
    reply_to="m-1:turn-0",
    observations=(),
    claims=(
        AccusationClaim(
            type="accusation", against="p-3", confidence=0.8, reason="seen there"
        ),
    ),
    free_text="p-3 was in electrical at 405.",
)
_TRANSCRIPT = MeetingTranscript(turns=(_OPENING, _PRIOR))
_MEMORY = (
    "## Your role\nCREWMATE\n## Observations\n- [tick 405] You saw p-3 in ELECTRICAL.\n"
)

# Provenance rows for the J2a fixtures. All satisfy the 16.3 sum invariant
# (0.5 + sum(components) == suspicion). ``p-3`` carries hard evidence, ``p-5``
# is soft-only (the annotated class), ``p-6`` moved only through the EXEMPT
# ``unattributed`` residual (16.4: neither hard nor soft — never annotated).
_HARD_ROW = SuspicionEntry(
    player_id="p-3",
    suspicion=0.80,
    trust=0.50,
    flag_lift=0.20,
    testimony_spread=0.10,
)
_SOFT_ONLY_ROW = SuspicionEntry(
    player_id="p-5",
    suspicion=0.80,
    trust=0.50,
    testimony_spread=0.20,
    carried_soft=0.10,
)
_UNATTRIBUTED_ROW = SuspicionEntry(
    player_id="p-6",
    suspicion=0.60,
    trust=0.50,
    unattributed=0.10,
)
_PROV_ROWS = (_HARD_ROW, _SOFT_ONLY_ROW, _UNATTRIBUTED_ROW)

_SOFT_ONLY_MARKER = "no flag; carried/soft only"
_SPLIT_MARKER = "built from: this meeting"


def _renderers() -> PromptRenderers:
    return build_prompt_renderers(_LOCKED_SET)


def _render_vote(
    *,
    suspicion_provenance: tuple[SuspicionEntry, ...] = (),
    fellow_impostor_ids: tuple[str, ...] = (),
) -> str:
    return _renderers().vote(
        voter_id="p-2",
        rendered_memory=_MEMORY,
        transcript=_TRANSCRIPT,
        contradiction_flags=(),
        suspicion_graph=_PROV_ROWS,
        candidate_targets=("p-3", "p-5", "p-6"),
        skip_confidence_threshold=0.6,
        fellow_impostor_ids=fellow_impostor_ids,
        suspicion_provenance=suspicion_provenance,
    )


def _render_crewmate(*, emergency: bool = False) -> str:
    trigger = (
        "p-2 called an emergency meeting at tick 410"
        if emergency
        else "p-2 reported body of p-7 at tick 410"
    )
    return _renderers().crewmate_report(
        agent_id="p-2",
        current_tick=410,
        meeting_trigger=trigger,
        rendered_memory=_MEMORY,
        public_transcript="",
        living_ids=("p-3", "p-5"),
        dead_ids=("p-7",),
    )


def _render_impostor_opening() -> str:
    return _renderers().impostor_report(
        agent_id="p-3",
        current_tick=410,
        meeting_trigger="p-3 reported body of p-7 at tick 410",
        rendered_memory=_MEMORY,
        public_transcript="",
        fellow_impostor_ids=("p-9",),
        living_ids=("p-2", "p-5"),
        dead_ids=("p-7",),
    )


def _render_statement(*, turn_kind: str, is_impostor: bool) -> str:
    return _renderers().statement(
        agent_id="p-3",
        rendered_memory=_MEMORY,
        transcript=_TRANSCRIPT,
        contradictions=(),
        prior_turn=_PRIOR if turn_kind == "reply" else None,
        turn_kind=turn_kind,  # type: ignore[arg-type]
        fellow_impostor_ids=(("p-9",) if is_impostor else ()),
        living_ids=("p-2", "p-5"),
        dead_ids=("p-7",),
        is_impostor=is_impostor,
        is_body_report=True,
    )


def _all_locked_set_renders() -> dict[str, str]:
    """Every branch of every template of the locked set (the sweep surface)."""

    return {
        "crewmate_report/body": _render_crewmate(),
        "crewmate_report/emergency": _render_crewmate(emergency=True),
        "impostor_report/body": _render_impostor_opening(),
        "reply/crew": _render_statement(turn_kind="reply", is_impostor=False),
        "reply/impostor": _render_statement(turn_kind="reply", is_impostor=True),
        "opt_in": _render_statement(turn_kind="opt_in", is_impostor=False),
        "vote": _render_vote(),
        "vote/provenance": _render_vote(suspicion_provenance=_PROV_ROWS),
    }


def _suspicion_row(rendered: str, player_id: str) -> str:
    """The one suspicion-graph row for ``player_id`` in a vote render."""

    block = rendered.split("## Your suspicion of each player", 1)[1]
    rows = [line for line in block.splitlines() if line.startswith(f"- `{player_id}`")]
    assert len(rows) == 1, f"expected exactly one row for {player_id}: {rows}"
    return rows[0]


# ---------------------------------------------------------------------------
# (a) The J2a provenance surface
# ---------------------------------------------------------------------------


class TestProvenanceSurface:
    def test_split_renders_when_the_kwarg_supplies_it(self) -> None:
        rendered = _render_vote(suspicion_provenance=_PROV_ROWS)
        # p-3: flag 0.20 + testimony 0.10 this meeting, nothing carried.
        assert (
            "- `p-3`: suspicion 0.80, trust 0.50 — built from: this meeting +0.30, "
            "carried prior +0.00" in rendered
        )
        # p-5: testimony 0.20 this meeting, 0.10 carried — the soft-only class.
        assert (
            "- `p-5`: suspicion 0.80, trust 0.50 — built from: this meeting +0.20, "
            "carried prior +0.10 — no flag; carried/soft only" in rendered
        )
        # The legend that explains the split renders beside the rows.
        assert "carried prior" in rendered
        assert "has no hard evidence behind it anywhere" in rendered

    def test_surface_is_kwarg_gated(self) -> None:
        # DoD: the surface renders ONLY when the render inputs supply it. A
        # render without the kwarg — every committed-set render, every ad-hoc
        # render — carries no trace of it.
        rendered = _render_vote()
        assert _SPLIT_MARKER not in rendered
        assert _SOFT_ONLY_MARKER not in rendered
        assert "has no hard evidence behind it anywhere" not in rendered

    def test_soft_only_annotation_matches_the_typed_decomposition(self) -> None:
        # DoD: the annotation matches 16.3's typed decomposition — the 16.4
        # soft-only predicate (|hard_total| <= atol, |unattributed| <= atol,
        # soft_total > atol) computed over agents.memory.beliefs'
        # SuspicionProvenance, field-by-name the same eight channels the
        # render-side SuspicionEntry carries.
        rendered = _render_vote(suspicion_provenance=_PROV_ROWS)
        for entry in _PROV_ROWS:
            provenance = SuspicionProvenance(
                flag_lift=entry.flag_lift,
                body_proximity=entry.body_proximity,
                kill_or_vent_pin=entry.kill_or_vent_pin,
                testimony_spread=entry.testimony_spread,
                accusation_carry=entry.accusation_carry,
                carried_hard=entry.carried_hard,
                carried_soft=entry.carried_soft,
                unattributed=entry.unattributed,
            )
            soft_only = (
                abs(provenance.hard_total) <= SUSPICION_PROVENANCE_ATOL
                and abs(provenance.unattributed) <= SUSPICION_PROVENANCE_ATOL
                and provenance.soft_total > SUSPICION_PROVENANCE_ATOL
            )
            row = _suspicion_row(rendered, entry.player_id)
            assert (_SOFT_ONLY_MARKER in row) == soft_only, row

    def test_unattributed_movement_is_never_annotated_soft_only(self) -> None:
        # 16.4 classified ``unattributed`` EXEMPT — neither hard nor soft; a
        # row whose movement is wholly unattributed must not read as bare-carry.
        rendered = _render_vote(suspicion_provenance=_PROV_ROWS)
        assert _SOFT_ONLY_MARKER not in _suspicion_row(rendered, "p-6")

    def test_annotated_rows_stay_extractor_readable(self) -> None:
        # The suffix rides AFTER the trust field (the OUT-OF-THE-GAME
        # precedent): the eval-side row shape and the §4.6 max-suspicion line
        # both still parse on a provenance-bearing render.
        rendered = _render_vote(suspicion_provenance=_PROV_ROWS)
        assert parse_rendered_max_suspicion(rendered) == 0.80
        assert "- `p-3`: suspicion 0.80, trust 0.50" in rendered


# ---------------------------------------------------------------------------
# (b) J3 — citation-required confidence
# ---------------------------------------------------------------------------


class TestCitationRequiredConfidence:
    def test_ballot_asks_every_eject_to_cite(self) -> None:
        rendered = _render_vote()
        # The ask, stated at the decision AND at the output contract
        # (instructions at both ends — the style manual).
        assert "Every EJECT names its evidence" in rendered
        assert "Fill at least one of the two reason ids on every EJECT" in rendered
        # The 16.5 private-evidence channel is in the 7-key contract, with the
        # [obs ...] copy instruction 16.5's id-rendering gives teeth to.
        assert "EXACTLY these 7 keys" in rendered
        assert '"primary_reason_observation_id": null' in rendered
        assert "[obs p-2:12:0]" in rendered  # the voter-consistent worked example

    def test_confidence_is_verbalized_against_the_citation(self) -> None:
        rendered = _render_vote()
        assert (
            "judged against the evidence you cite" in rendered
            and "do not report a confidence at or above the skip threshold" in rendered
        )

    def test_memory_based_skip_stays_legitimate_and_uncited(self) -> None:
        # The hint's boundary: invert the exemplar WITHOUT inverting the SKIP
        # allowance — skipping needs no citation.
        rendered = _render_vote()
        assert "a call you cannot source either way is a call to SKIP" in rendered
        assert "a SKIP needs no citation" in rendered
        assert "a SKIP needs neither" in rendered

    def test_skip_discipline_reanchored_without_blessing_overrides(self) -> None:
        # Baseline-4 §6 (missed-skip 11 -> 86): below-threshold SKIP is
        # re-anchored as the sound call and an override must cite, while the
        # threshold stays EVIDENCE, not a command (the 13.13 recorded decision).
        rendered = _render_vote()
        assert "SKIP is the sound call" in rendered
        assert "evidence you can cite" in rendered
        assert "evidence, not a command" in rendered
        assert "the §4.6 reference point" in rendered

    def test_no_sanctioned_null_citation_eject_in_any_template(self) -> None:
        # DoD: the gut-read example is gone — every ballot exemplar cites (turn
        # or observation id) or SKIPs, and no template sanctions a null-citation
        # EJECT ("Use null when your call rests on your own memory" was v1's).
        for label, rendered in _all_locked_set_renders().items():
            assert "Gut-read" not in rendered, label
            assert "gut-read" not in rendered, label
            assert "Use null when your call rests on your own memory" not in rendered, (
                label
            )
        vote = _render_vote()
        assert "Memory-citing" in vote  # the rewritten register cites instead
        assert "Transcript-citing" in vote or "transcript-citing" in vote

    def test_seven_key_compliant_ballot_parses(self) -> None:
        # A response shaped exactly like the skeleton (all 7 keys) parses into
        # the typed VoteBallot with the citation intact.
        parsed = VoteBallot.model_validate_json(
            '{"voter": "p-2", "target": "p-3", "confidence": 0.8, '
            '"primary_reason_id": "m-1:turn-1", '
            '"primary_reason_observation_id": "p-2:405:0", '
            '"considered_alternatives": [], '
            '"rationale_text": "Turn 1 settled it."}'
        )
        assert parsed.primary_reason_id == "m-1:turn-1"
        assert parsed.primary_reason_observation_id == "p-2:405:0"

    def test_observation_cited_eject_roundtrips_through_the_real_manager(
        self,
    ) -> None:
        # The DoD round-trip: a compliant observation-cited ballot survives the
        # REAL manager validation path (the 16.5 mark-and-null normalizer) with
        # the citation intact — the voter's own valid-id set admits it.
        result, _ = _run_meeting(
            _obs_vote_responder(observation_ids_by_voter={"p-2": "p-2:405:0"}),
            participants=_participants({"p-2": ("p-2:405:0",)}),
        )
        p2 = next(b for b in result.ballots if b.voter == "p-2")
        assert p2.primary_reason_observation_id == "p-2:405:0"
        assert "[invalid primary_reason_observation_id" not in p2.rationale_text


# ---------------------------------------------------------------------------
# (c) Roll-call elicitation
# ---------------------------------------------------------------------------


class TestRollCallElicitation:
    def test_crew_surfaces_ask_for_a_checkable_placement(self) -> None:
        # The ask names BOTH halves of checkability (room + tick) and stays one
        # rules line + one schema line (the turn-budget cap): the shape line
        # advertises the 16.7 kind in every crew-visible schema list.
        renders = _all_locked_set_renders()
        for label in (
            "crewmate_report/body",
            "crewmate_report/emergency",
            "reply/crew",
            "opt_in",
        ):
            rendered = renders[label]
            assert "roll-call" in rendered, label
            assert '"type": "whereabouts"' in rendered, label
            assert "one room, one tick" in rendered, label

    def test_crew_surfaces_ask_for_sightings_of_others(self) -> None:
        # The second half of the ask: voice relevant placements of OTHERS
        # (saw_player rows), the material the contradiction detectors check
        # roll-call answers against.
        renders = _all_locked_set_renders()
        assert (
            "placing OTHERS at the tick that matters" in renders["crewmate_report/body"]
        )
        for label in ("reply/crew", "opt_in"):
            assert "ANOTHER player at that tick" in renders[label], label

    def test_impostor_cover_surfaces_carry_no_roll_call_ask(self) -> None:
        # The recorded role-differentiated contract stands: the impostor reply
        # and opening keep the accusation-only structure (observations stay []),
        # so the self-placement ask never lands there — the 16.8 absence prior
        # prices that silence, and a self-placement slot is the surface the
        # ladder measured minting the >=44% self-flag.
        renders = _all_locked_set_renders()
        for label in ("reply/impostor", "impostor_report/body"):
            rendered = renders[label]
            assert "roll-call" not in rendered, label
            assert '"type": "whereabouts"' not in rendered, label

    def test_whereabouts_answer_roundtrips_through_the_real_manager(self) -> None:
        # A compliant turn carrying the roll-call answer parses into the typed
        # WhereaboutsClaim through the real manager run...
        answer = WhereaboutsClaim(type="whereabouts", tick=7, room="ADMIN")
        result, _ = _run_meeting(
            _make_responder(observations={"p-1": (answer,)}),
        )
        opening = result.transcript.turns[0]
        assert opening.speaker == "p-1"
        claims = [
            obs for obs in opening.observations if isinstance(obs, WhereaboutsClaim)
        ]
        assert claims == [answer]

    def test_whereabouts_answer_is_checkable_room_plus_timing(self) -> None:
        # ...and the placement is CHECKABLE: the transcript-side consumer
        # places the speaker by room + tick (the substrate the contradiction
        # detectors and the Phase-10 instrument re-supply from).
        answer = WhereaboutsClaim(type="whereabouts", tick=7, room="ADMIN")
        result, _ = _run_meeting(
            _make_responder(observations={"p-1": (answer,)}),
        )
        placements = reconstruct_stated_paths(result.transcript)["p-1"]
        assert any(
            p.tick == 7 and "ADMIN" in p.rooms and p.speaker == "p-1"
            for p in placements
        )

    def test_spoken_roll_call_answer_renders_to_later_speakers(self) -> None:
        # The transcript loop shows an earlier speaker's roll-call answer to
        # later turns (the 15.4 spoken-vent precedent) — the elicited placement
        # is on the public record, not a write-only field.
        answered = _PRIOR.model_copy(
            update={
                "observations": (
                    WhereaboutsClaim(type="whereabouts", tick=7, room="ADMIN"),
                )
            }
        )
        rendered = _renderers().statement(
            agent_id="p-2",
            rendered_memory=_MEMORY,
            transcript=MeetingTranscript(turns=(_OPENING, answered)),
            contradictions=(),
            prior_turn=None,
            turn_kind="opt_in",
            fellow_impostor_ids=(),
            living_ids=("p-3", "p-5"),
            dead_ids=(),
            is_impostor=False,
            is_body_report=True,
        )
        assert "p-4 places THEMSELVES in ADMIN (roll-call answer)" in rendered


# ---------------------------------------------------------------------------
# (d) The vent tail
# ---------------------------------------------------------------------------


class TestVentTailAsk:
    def test_held_vent_ask_lands_harder_with_priority_and_repetition(self) -> None:
        # The ~20/73 unspoken tail (close audit §11): the ask now leads with
        # priority (speak it FIRST) and closes the stale-vent excuse (even if
        # it happened long ago / was said at an earlier meeting).
        renders = _all_locked_set_renders()
        assert "speak it FIRST" in renders["crewmate_report/body"]
        assert (
            "even if it happened many ticks ago and even if you already said it"
            in renders["crewmate_report/body"]
        )
        for label in ("reply/crew", "opt_in"):
            assert "speak it FIRST" in renders[label], label
            assert "already said it at an earlier meeting" in renders[label], label

    def test_crewmate_opening_carries_the_worked_example(self) -> None:
        # The v5 lesson the hint pins: the example moves uptake more than the
        # instruction — the opening pairs the memory line with the exact JSON
        # row it becomes.
        rendered = _render_crewmate()
        assert "- [tick 12] You witnessed p-3 vent in MEDBAY." in rendered
        assert (
            '{"type": "saw_vent", "tick": 12, "subject": "p-3", "room": "MEDBAY"}'
            in rendered
        )

    def test_witnessed_only_discipline_is_kept(self) -> None:
        # Landing harder must not invite fabrication: the witnessed-only clause
        # survives on every eliciting surface.
        renders = _all_locked_set_renders()
        for label in ("crewmate_report/body", "reply/crew", "opt_in"):
            assert "never one you merely heard about or suspect" in renders[label], (
                label
            )

    def test_spoken_vent_roundtrips_through_the_real_manager(self) -> None:
        vent = SawVentObservation(
            type="saw_vent", tick=12, subject="p-3", room="MEDBAY"
        )
        result, _ = _run_meeting(
            _make_responder(observations={"p-1": (vent,)}),
        )
        opening = result.transcript.turns[0]
        vents = [
            obs for obs in opening.observations if isinstance(obs, SawVentObservation)
        ]
        assert vents == [vent]


# ---------------------------------------------------------------------------
# (e) The self-accusation fix
# ---------------------------------------------------------------------------


class TestSelfAccusationFix:
    def test_impostor_reply_closes_the_self_naming_slot(self) -> None:
        rendered = _render_statement(turn_kind="reply", is_impostor=True)
        # The wave-0 close artifact was an accused impostor ECHOING the
        # accusation against itself; the reply now routes the echo to
        # free_text and pins "against" to another player's name.
        assert 'The name in "against" is always another player\'s' in rendered
        assert "your own name is never on it" in rendered

    def test_impostor_opening_closes_the_self_naming_slot(self) -> None:
        rendered = _render_impostor_opening()
        assert "never yourself" in rendered

    def test_ballot_closes_the_self_vote_slot(self) -> None:
        # Unconditionally at the target bullet, and again beside the team
        # protection block when a teammate list renders.
        rendered = _render_vote()
        assert "never your own name" in rendered
        teamed = _render_vote(fellow_impostor_ids=("p-9",))
        assert 'your own name never goes in "target"' in teamed

    def test_compliant_impostor_reply_accuses_another_player(self) -> None:
        # The compliant shape the framing elicits — observations empty, one
        # accusation naming ANOTHER living player — parses into the typed kind.
        parsed = MeetingTurn.model_validate_json(
            '{"turn_id": "t", "turn_index": 0, "speaker": "p-3", '
            '"turn_kind": "reply", "reply_to": null, "observations": [], '
            '"claims": [{"type": "accusation", "against": "p-5", '
            '"confidence": 0.7, "reason": "odd path"}], '
            '"free_text": "Not me — I answered that already. Watch p-5."}'
        )
        accusation = parsed.claims[0]
        assert isinstance(accusation, AccusationClaim)
        assert accusation.against != parsed.speaker


# ---------------------------------------------------------------------------
# Cross-ask sweep: the elicitation batch never leaks into other sets
# ---------------------------------------------------------------------------


class TestBatchStaysOnTheLockedSet:
    def test_frozen_sets_carry_no_16_15_markers(self) -> None:
        # The batch edits ONLY the locked set: no other registered set may
        # grow the roll-call ask, the provenance legend, or the 7-key ballot.
        for set_name in ("qwen3_5_9b", "qwen3_32b", "glm_4_32b", "cydonia_24b"):
            renderers = build_prompt_renderers(set_name)
            vote = renderers.vote(
                voter_id="p-2",
                rendered_memory=_MEMORY,
                transcript=_TRANSCRIPT,
                contradiction_flags=(),
                suspicion_graph=_PROV_ROWS,
                candidate_targets=("p-3", "p-5"),
                skip_confidence_threshold=0.6,
                fellow_impostor_ids=(),
                suspicion_provenance=_PROV_ROWS,
            )
            assert _SPLIT_MARKER not in vote, set_name
            assert "EXACTLY these 7 keys" not in vote, set_name
