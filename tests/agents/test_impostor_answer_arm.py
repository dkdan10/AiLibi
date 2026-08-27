"""Routing fixtures for the Task 18.10 impostor-answer template arm.

The gate's highest-variance arm, built inert: behind the default-OFF
``impostor_roll_call_enabled`` lever (``AILIBI_IMPOSTOR_ROLL_CALL``), the two
impostor-facing templates of the locked ``qwen3_6_27b`` set are swapped for
their ``*_roll_call.j2`` variant siblings, in which the impostor opening and
reply ANSWER the whereabouts ask with one structured ``whereabouts``
self-placement instead of the hard-coded ``"observations": []``
(audits/audit-phase-18-planning.md §3.4 — the structural refusal; the ladder's
>=44% self-flag caution is quoted in the variant headers, judged by the 18.11
bars). These fixtures pin the Task 18.10 DoD:

* **the default path renders byte-identically** — lever OFF, every routed
  template of every registered set renders byte-for-byte what a direct
  (routing-bypassing) render of the committed default template file produces,
  across the reconstructed fixture sweep;
* **the variant path renders the self-placement contract** — lever ON, the
  impostor opening and reply carry the whereabouts ask + shape, drop the
  hard-coded empty-observations contract and the explain-nothing cover
  directive, keep the teammate firewall (audits' §7.12 input-side guard: a
  self-placement never places or implicates the co-impostor), and every
  crew-rendered branch stays byte-identical;
* **version stamps distinguish the variant** in the registry AND in recorded
  bytes — ``prompt_versions_for_set`` serves the variant stamps while the
  lever is ON (fail-loud for sets without a variant entry), and a meeting
  recorded through the production ``build_default_meeting_runner`` wire-up
  carries them in its ``MeetingArtifacts`` / serialized
  :class:`~orchestrator.replay.MeetingReplayEntry` bytes
  (audits/audit-phase-17-absence-gate.md Ruling 3(d): the bar re-reads on new
  bytes, so variant bytes must never wear a default stamp).

The reconstructed meeting context mirrors ``test_bespoke_prompt_sets.py``
(one body-report chain, enough to exercise every branch of every template).
"""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
from dataclasses import replace

import pytest

from agents.strategic.prompts.loader import (
    ACCUSATION_ROUND_ROLL_CALL_TEMPLATE,
    ACCUSATION_ROUND_TEMPLATE,
    CANONICAL_MAP_CARD,
    ENV_IMPOSTOR_ROLL_CALL,
    ENV_PROMPT_SET,
    IMPOSTOR_REPORT_ROLL_CALL_TEMPLATE,
    IMPOSTOR_REPORT_TEMPLATE,
    PromptRenderers,
    accusation_round_prompt,
    build_environment,
    build_prompt_renderers,
    impostor_report_prompt,
    impostor_roll_call_enabled,
)
from engine.entities import Role
from engine.world import WorldState, load_canonical_map
from meetings.manager import MeetingTrigger, PromptRenderInputs, SuspicionEntry
from meetings.schemas import (
    AccusationClaim,
    ContradictionRef,
    MeetingTranscript,
    MeetingTurn,
    ObservationId,
    PlayerId,
    SawPlayerObservation,
    SightingRecord,
    VentWitnessRecord,
    WhereaboutsClaim,
)
from observation.action_intent import ActionIntent
from observation.packet import ObservationPacket
from observation.public_map import PublicMapView
from orchestrator.game import (
    DEFAULT_PROMPT_VERSIONS,
    IMPOSTOR_ROLL_CALL_PROMPT_VERSION_SETS,
    PROMPT_VERSION_SETS,
    build_default_meeting_runner,
    prompt_versions_for_set,
)
from orchestrator.replay import MeetingReplayEntry
from orchestrator.seeder import seed_initial_state

# The locked set that carries the variant templates (the canonical eval set
# since Phase 14; model locked at Task 16.2) and the lever-ON env mapping the
# deterministic ``env=`` seam takes.
_VARIANT_SET = "qwen3_6_27b"
_ON = {ENV_IMPOSTOR_ROLL_CALL: "1"}
_OFF: dict[str, str] = {}

# The two variant stamps (the ``<template>.<set>.<version>`` convention with
# the template component naming the variant FILE on its own v1 lineage).
_VARIANT_IMPOSTOR_STAMP = "impostor_report_roll_call.qwen3_6_27b.v1"
_VARIANT_ACCUSATION_STAMP = "accusation_round_roll_call.qwen3_6_27b.v1"

# The BASE the two variant bodies were authored against was the v3 default set,
# archived at the Task-20.31 bump and RETIRED at the baseline-7 record (no
# committed set stamps v3 any more). The variant arm is unrecorded and
# default-OFF, so its bodies stay frozen on their v1 lineage while the default
# set advances: "the variant swaps ONLY the impostor surfaces" can no longer be
# asserted against a base, and is left to the re-authoring that puts the arm
# back on the current lineage.

# A small reconstructed body-report meeting context (a found body + an
# accusation chain) — the ``test_bespoke_prompt_sets.py`` shape, enough to
# exercise every branch of the two routed templates.
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
_TRANSCRIPT = MeetingTranscript(turns=(_PRIOR,))
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
_MEMORY = "## Your role\nIMPOSTOR\n## Observations\n- tick 405: saw p-3 in electrical with p-5\n"

# The variant's self-placement contract markers.
_WHEREABOUTS_SHAPE = '{"type": "whereabouts", "tick": <int>, "room": "<room id>"}'
_ROLL_CALL_ASK = "Answer the roll-call"
_EMPTY_LIST_CONTRACT = 'Keep "observations" as an empty list'
_EXPLAIN_NOTHING = "must be about OTHER players"
# A turn that carries an observation item must advertise the discriminator on
# BOTH item kinds — the claims-only wording beside a required whereabouts row
# contradicts itself and invites type-less rows the schema rejects (PR #297
# review). The default impostor opening keeps the claims-only wording because
# its observations really are hard-coded empty.
_TYPE_ON_BOTH_KINDS = '"type" appears only inside each observation/claim item'
_TYPE_ON_CLAIMS_ONLY = '"type" appears only inside each claim item'
_TEAMMATE_FIREWALL = (
    "never claim you were with a teammate, and never place them anywhere"
)
# The default / variant impostor persona sentences the accusation-round swap
# trades (the ONLY moving line on an impostor opt-in render).
_PERSONA_DEFAULT = (
    "You stay safe by being brief, calm, and by keeping the meeting's "
    "attention on other players — never on yourself."
)
_PERSONA_VARIANT = (
    "You stay safe by being brief, calm, and by giving one steady, boring "
    "account of yourself while keeping the meeting's suspicion on other players."
)
# The default / variant fellow-saboteurs clauses (the guarded <players> block
# renders on every impostor turn with a living teammate, opt-in included).
_FELLOWS_DEFAULT = (
    "backing a teammate's account in your own words is fine when it helps "
    "your cover. Aim any accusation at a crewmate."
)
_FELLOWS_VARIANT = (
    "backing a teammate's account in your own words is fine when it helps "
    "your cover, but your whereabouts answer places YOU alone — never claim "
    "you were with a teammate, and never place them anywhere. Aim any "
    "accusation at a crewmate."
)


def _flat(text: str) -> str:
    """Collapse whitespace so a directive marker matches across line wraps."""

    return " ".join(text.split())


class _CannedMeetingAgent:
    """Minimal :class:`~orchestrator.game.MeetingAwareAgent` double.

    Canned rendered memory + empty typed channels — enough for the production
    ``DefaultMeetingRunner`` to build participants and run a full meeting on
    the fake provider without a perception walk (the recorded-bytes fixture
    asserts on provenance stamps, not on turn content). A canned double may
    return ``()`` from every typed channel (the protocol's documented test
    seam), and ``decide`` satisfies :class:`agents.base.AgentInterface` but is
    never called inside ``run_meeting``.
    """

    def __init__(self, *, agent_id: PlayerId, role: Role) -> None:
        self._agent_id = agent_id
        self._role: Role = role

    @property
    def agent_id(self) -> PlayerId:
        return self._agent_id

    @property
    def role(self) -> Role:
        return self._role

    def decide(
        self, packet: ObservationPacket, public_map: PublicMapView
    ) -> ActionIntent:
        raise NotImplementedError("meeting-only double; decide() is never dispatched")

    def render_memory_for_meeting(
        self,
        *,
        token_budget: int = 1500,
        suspicion_override: Mapping[PlayerId, float] | None = None,
    ) -> str:
        return f"## Your role\n{self._role}\n## Observations\n- (none)\n"

    def suspicion_graph_for_meeting(self) -> tuple[SuspicionEntry, ...]:
        return ()

    def vent_witness_records_for_meeting(self) -> tuple[VentWitnessRecord, ...]:
        return ()

    def sighting_records_for_meeting(self) -> tuple[SightingRecord, ...]:
        return ()

    def observation_ids_for_meeting(self) -> tuple[ObservationId, ...]:
        return ()


def _render_sweep(renderers: PromptRenderers) -> dict[str, str]:
    """Render every branch of the two ROUTED templates through ``renderers``.

    Labels mirror ``test_bespoke_prompt_sets._render_all`` (opening split by
    trigger; reply split by role x body; opt_in split by role), restricted to
    the two templates the Task 18.10 lever routes — ``crewmate_report`` /
    ``vote_ballot`` are not routed and carry their own ON==OFF equality pins.
    """

    out: dict[str, str] = {}
    for trig in (
        "p-2 reported body of p-7 at tick 410",
        "p-2 called an emergency meeting at tick 410",
    ):
        tag = "body" if "reported" in trig else "emergency"
        out[f"impostor_report/{tag}"] = renderers.impostor_report(
            agent_id="p-3",
            current_tick=410,
            meeting_trigger=trig,
            rendered_memory=_MEMORY,
            public_transcript="",
            fellow_impostor_ids=("p-9",),
            living_ids=("p-2", "p-5"),
            dead_ids=("p-7",),
        )
    out["impostor_report/body/sole"] = renderers.impostor_report(
        agent_id="p-3",
        current_tick=410,
        meeting_trigger="p-2 reported body of p-7 at tick 410",
        rendered_memory=_MEMORY,
        public_transcript="",
        fellow_impostor_ids=(),
        living_ids=("p-2", "p-5"),
        dead_ids=("p-7",),
    )
    for is_imp in (True, False):
        for is_body in (True, False):
            out[f"reply/imp={is_imp}/body={is_body}"] = renderers.statement(
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
    for is_imp in (True, False):
        out[f"opt_in/imp={is_imp}"] = renderers.statement(
            agent_id="p-3",
            rendered_memory=_MEMORY,
            transcript=_TRANSCRIPT,
            contradictions=(),
            prior_turn=None,
            turn_kind="opt_in",
            fellow_impostor_ids=(("p-9",) if is_imp else ()),
            living_ids=("p-2", "p-5"),
            dead_ids=(),
            is_impostor=is_imp,
            is_body_report=False,
        )
    out["reply/imp=True/persona"] = renderers.statement(
        agent_id="p-3",
        rendered_memory=_MEMORY,
        transcript=_TRANSCRIPT,
        contradictions=_CONTRAS,
        prior_turn=_PRIOR,
        turn_kind="reply",
        fellow_impostor_ids=("p-9",),
        living_ids=("p-2", "p-5"),
        dead_ids=("p-7",),
        is_impostor=True,
        is_body_report=True,
        persona="clipped, wry, counts on their fingers",
    )
    return out


class TestImpostorRollCallResolver:
    """The lever semantics — the project's ONE surviving env-gated toggle."""

    def test_default_is_off(self) -> None:
        assert impostor_roll_call_enabled(env={}) is False

    def test_unrelated_env_key_stays_off(self) -> None:
        assert impostor_roll_call_enabled(env={"AILIBI_SOMETHING_ELSE": "1"}) is False

    @pytest.mark.parametrize("value", ["1", "true", "TRUE", " yes ", "On"])
    def test_truthy_values_enable(self, value: str) -> None:
        assert impostor_roll_call_enabled(env={ENV_IMPOSTOR_ROLL_CALL: value}) is True

    @pytest.mark.parametrize("value", ["", "0", "false", "off", "enabled", "  "])
    def test_falsy_or_unrecognised_values_stay_off(self, value: str) -> None:
        assert impostor_roll_call_enabled(env={ENV_IMPOSTOR_ROLL_CALL: value}) is False

    def test_reads_process_env_by_default(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv(ENV_IMPOSTOR_ROLL_CALL, "1")
        assert impostor_roll_call_enabled() is True
        assert impostor_roll_call_enabled(env=None) is True
        monkeypatch.delenv(ENV_IMPOSTOR_ROLL_CALL)
        assert impostor_roll_call_enabled() is False


@pytest.mark.parametrize("set_name", sorted(PROMPT_VERSION_SETS))
class TestDefaultPathRendersByteIdentically:
    """Lever OFF: the routed path serves the committed default files, byte-for-byte.

    The pin bypasses the ROUTING — each comparison render names the default
    template FILE explicitly (``template_name=``), which no lever can change —
    and compares the lever-OFF bundle against it across the fixture sweep, for
    EVERY registered set (the variant must not move a single committed byte
    anywhere while OFF). The construction-bound map card is passed explicitly
    for the same reason: it is what the bundle binds, so a difference here can
    only come from the filename.
    """

    def test_off_bundle_equals_direct_default_template_render(
        self, set_name: str
    ) -> None:
        renderers = build_prompt_renderers(set_name, env=_OFF)
        environment = build_environment(set_name)
        direct: dict[str, str] = {}
        for trig in (
            "p-2 reported body of p-7 at tick 410",
            "p-2 called an emergency meeting at tick 410",
        ):
            tag = "body" if "reported" in trig else "emergency"
            direct[f"impostor_report/{tag}"] = impostor_report_prompt(
                environment=environment,
                template_name=IMPOSTOR_REPORT_TEMPLATE,
                map_card=CANONICAL_MAP_CARD,
                agent_id="p-3",
                current_tick=410,
                meeting_trigger=trig,
                rendered_memory=_MEMORY,
                public_transcript="",
                fellow_impostor_ids=("p-9",),
                living_ids=("p-2", "p-5"),
                dead_ids=("p-7",),
                persona="",
                suspicion_provenance=(),
            )
        direct["impostor_report/body/sole"] = impostor_report_prompt(
            environment=environment,
            template_name=IMPOSTOR_REPORT_TEMPLATE,
            map_card=CANONICAL_MAP_CARD,
            agent_id="p-3",
            current_tick=410,
            meeting_trigger="p-2 reported body of p-7 at tick 410",
            rendered_memory=_MEMORY,
            public_transcript="",
            fellow_impostor_ids=(),
            living_ids=("p-2", "p-5"),
            dead_ids=("p-7",),
            persona="",
            suspicion_provenance=(),
        )
        for is_imp in (True, False):
            for is_body in (True, False):
                direct[f"reply/imp={is_imp}/body={is_body}"] = accusation_round_prompt(
                    environment=environment,
                    template_name=ACCUSATION_ROUND_TEMPLATE,
                    map_card=CANONICAL_MAP_CARD,
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
                    persona="",
                    suspicion_provenance=(),
                )
        for is_imp in (True, False):
            direct[f"opt_in/imp={is_imp}"] = accusation_round_prompt(
                environment=environment,
                template_name=ACCUSATION_ROUND_TEMPLATE,
                map_card=CANONICAL_MAP_CARD,
                agent_id="p-3",
                rendered_memory=_MEMORY,
                transcript=_TRANSCRIPT,
                contradictions=(),
                prior_turn=None,
                turn_kind="opt_in",
                fellow_impostor_ids=(("p-9",) if is_imp else ()),
                living_ids=("p-2", "p-5"),
                dead_ids=(),
                is_impostor=is_imp,
                is_body_report=False,
                persona="",
                suspicion_provenance=(),
            )
        direct["reply/imp=True/persona"] = accusation_round_prompt(
            environment=environment,
            template_name=ACCUSATION_ROUND_TEMPLATE,
            map_card=CANONICAL_MAP_CARD,
            agent_id="p-3",
            rendered_memory=_MEMORY,
            transcript=_TRANSCRIPT,
            contradictions=_CONTRAS,
            prior_turn=_PRIOR,
            turn_kind="reply",
            fellow_impostor_ids=("p-9",),
            living_ids=("p-2", "p-5"),
            dead_ids=("p-7",),
            is_impostor=True,
            is_body_report=True,
            persona="clipped, wry, counts on their fingers",
            suspicion_provenance=(),
        )
        routed = _render_sweep(renderers)
        assert routed.keys() == direct.keys()
        for label, text in routed.items():
            assert text == direct[label], f"{set_name}: {label} drifted lever-OFF"

    def test_explicit_zero_matches_unset(self, set_name: str) -> None:
        # "0" and an absent key are both OFF — the routed bundle is the same.
        off = _render_sweep(build_prompt_renderers(set_name, env=_OFF))
        zero = _render_sweep(
            build_prompt_renderers(set_name, env={ENV_IMPOSTOR_ROLL_CALL: "0"})
        )
        assert off == zero


class TestVariantRendersSelfPlacementContract:
    """Lever ON: the impostor surfaces answer the whereabouts ask."""

    def _on(self) -> dict[str, str]:
        return _render_sweep(build_prompt_renderers(_VARIANT_SET, env=_ON))

    def _off(self) -> dict[str, str]:
        return _render_sweep(build_prompt_renderers(_VARIANT_SET, env=_OFF))

    def test_every_branch_renders_non_empty_under_strict_undefined(self) -> None:
        # StrictUndefined raises on a missing / typo'd kwarg, so a clean render
        # of every branch proves the variant templates introduce no kwarg drift.
        for label, text in self._on().items():
            assert text.strip(), f"{label} rendered empty"

    def test_impostor_opening_answers_the_whereabouts_ask(self) -> None:
        rendered = self._on()
        for label in ("impostor_report/body", "impostor_report/emergency"):
            text = rendered[label]
            assert _ROLL_CALL_ASK in text, label
            assert _WHEREABOUTS_SHAPE in text, label
            assert _EMPTY_LIST_CONTRACT not in text, label
            assert _EXPLAIN_NOTHING not in _flat(text), label
            # The output contract advertises the discriminator on both item
            # kinds now that an observation item is required (PR #297 review:
            # the claims-only wording beside a required whereabouts row invites
            # type-less rows the MeetingTurn schema rejects).
            assert _TYPE_ON_BOTH_KINDS in text, label
            assert _TYPE_ON_CLAIMS_ONLY not in text, label

    def test_impostor_reply_answers_the_whereabouts_ask(self) -> None:
        text = self._on()["reply/imp=True/body=True"]
        assert _ROLL_CALL_ASK in text
        assert _WHEREABOUTS_SHAPE in text
        assert _EMPTY_LIST_CONTRACT not in text
        assert _EXPLAIN_NOTHING not in _flat(text)
        assert _TYPE_ON_BOTH_KINDS in text
        # The (e) self-accusation fix survives the variant: the accusation slot
        # stays closed to the speaker's own name.
        assert "your own name is never on it" in _flat(text)

    def test_self_placement_keeps_the_teammate_firewall(self) -> None:
        # The §7.12 input-side guard: a self-placement places the SPEAKER
        # alone. Present wherever the guarded fellow-saboteurs block renders;
        # absent for a sole impostor (the block is fellow-gated, unchanged).
        rendered = self._on()
        assert _TEAMMATE_FIREWALL in _flat(rendered["impostor_report/body"])
        assert _TEAMMATE_FIREWALL in _flat(rendered["reply/imp=True/body=True"])
        assert _TEAMMATE_FIREWALL not in _flat(rendered["impostor_report/body/sole"])
        assert "never accuse or incriminate them" in _flat(
            rendered["impostor_report/body"]
        )

    def test_variant_keeps_the_ladder_cover_guards(self) -> None:
        # The v1+v2 phrasing rules that killed the reply tell stay: never in
        # the body's room / around its tick, "reported it", "where it
        # happened", the same account every time.
        rendered = self._on()
        opening = _flat(rendered["impostor_report/body"])
        assert "never place yourself in the body's room" in opening
        assert "where it happened" in opening
        reply = _flat(rendered["reply/imp=True/body=True"])
        assert "never place yourself in the body's room" in reply
        assert "reported it" in reply

    def test_machine_anchors_are_preserved(self) -> None:
        # extract_gameplay_facts._classify_call_slot reads the first markdown
        # header; the variant must keep the exact anchor strings.
        rendered = self._on()
        assert "## This meeting" in rendered["impostor_report/body"]
        assert "## Your cover" in rendered["impostor_report/body"]
        assert "## Your cover" not in rendered["impostor_report/emergency"]
        assert "## Your turn: a reply" in rendered["reply/imp=True/body=True"]
        assert "## Your turn: an info-share" in rendered["opt_in/imp=True"]

    # RETIRED at the baseline-7 record: ``test_crew_branches_are_byte_identical_
    # to_the_variant_base`` and ``test_impostor_opt_in_differs_only_by_the_two_
    # guarded_lines`` compared the variant against the ARCHIVED v3 default bodies,
    # and that archive retired with the record (no committed set stamps v3 any
    # more). The comparison has no base to make; what the variant still promises
    # is pinned by the live ON/OFF tests around this note.

    def test_the_variant_arm_has_diverged_from_the_live_default_set(self) -> None:
        # The deferral, stated as a gate: the variant bodies do NOT carry the
        # v4 batch, so a crew branch rendered through the variant differs from
        # the live default, and the variant's persona still hard-codes ONE
        # hidden impostor where the default now says how many there are.
        # Delete this test when the arm is re-authored onto the current
        # lineage (or retired).
        on, off = self._on(), self._off()
        assert on["reply/imp=False/body=True"] != off["reply/imp=False/body=True"]
        two = PromptRenderInputs(impostor_count=2)
        opening_kwargs = dict(
            agent_id="p-3",
            current_tick=410,
            meeting_trigger="p-2 reported body of p-7 at tick 410",
            rendered_memory=_MEMORY,
            public_transcript="",
            fellow_impostor_ids=("p-9",),
            living_ids=("p-2", "p-5"),
            dead_ids=("p-7",),
            render_inputs=two,
        )
        variant = build_prompt_renderers(_VARIANT_SET, env=_ON).impostor_report(
            **opening_kwargs  # type: ignore[arg-type]
        )
        default = build_prompt_renderers(_VARIANT_SET, env=_OFF).impostor_report(
            **opening_kwargs  # type: ignore[arg-type]
        )
        assert "a hidden impostor" in variant
        assert "two hidden impostors" in default
        assert "a hidden impostor" not in default

    def test_unrouted_templates_render_byte_identically_on_vs_off(self) -> None:
        # crewmate_report and vote_ballot are not routed by the lever at all.
        on = build_prompt_renderers(_VARIANT_SET, env=_ON)
        off = build_prompt_renderers(_VARIANT_SET, env=_OFF)
        crew_kwargs = dict(
            agent_id="p-2",
            current_tick=410,
            meeting_trigger="p-2 reported body of p-7 at tick 410",
            rendered_memory=_MEMORY,
            public_transcript="",
            living_ids=("p-3", "p-5"),
            dead_ids=("p-7",),
        )
        assert on.crewmate_report(**crew_kwargs) == off.crewmate_report(  # type: ignore[arg-type]
            **crew_kwargs  # type: ignore[arg-type]
        )
        vote_kwargs = dict(
            voter_id="p-2",
            rendered_memory=_MEMORY,
            transcript=_TRANSCRIPT,
            contradiction_flags=_CONTRAS,
            suspicion_graph=(),
            candidate_targets=("p-3", "p-5"),
            skip_confidence_threshold=0.6,
            fellow_impostor_ids=(),
        )
        assert on.vote(**vote_kwargs) == off.vote(**vote_kwargs)  # type: ignore[arg-type]

    def test_module_wrapper_resolves_the_lever_live(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # The module-level wrapper (no bound bundle) reads the lever per call;
        # an explicit template_name pins the decision and wins over the lever.
        environment = build_environment(_VARIANT_SET)
        monkeypatch.setenv(ENV_IMPOSTOR_ROLL_CALL, "1")
        live = impostor_report_prompt(
            agent_id="p-3",
            current_tick=410,
            meeting_trigger="p-2 reported body of p-7 at tick 410",
            rendered_memory=_MEMORY,
            public_transcript="",
            fellow_impostor_ids=("p-9",),
            living_ids=("p-2", "p-5"),
            dead_ids=("p-7",),
            environment=environment,
        )
        assert _WHEREABOUTS_SHAPE in live
        pinned_default = impostor_report_prompt(
            agent_id="p-3",
            current_tick=410,
            meeting_trigger="p-2 reported body of p-7 at tick 410",
            rendered_memory=_MEMORY,
            public_transcript="",
            fellow_impostor_ids=("p-9",),
            living_ids=("p-2", "p-5"),
            dead_ids=("p-7",),
            environment=environment,
            template_name=IMPOSTOR_REPORT_TEMPLATE,
        )
        assert _EMPTY_LIST_CONTRACT in pinned_default

    def test_variant_contract_shape_parses_against_the_shared_schema(self) -> None:
        # The one hard cross-set invariant: the variant's answered turn (one
        # whereabouts self-placement + one accusation) is a plain MeetingTurn.
        turn = MeetingTurn(
            turn_id="m-1:turn-2",
            turn_index=2,
            speaker="p-3",
            turn_kind="reply",
            reply_to="m-1:turn-1",
            observations=(
                WhereaboutsClaim(type="whereabouts", tick=405, room="medbay"),
            ),
            claims=(
                AccusationClaim(
                    type="accusation", against="p-5", confidence=0.7, reason="odd path"
                ),
            ),
            free_text="I was in medbay; p-5 was on an odd path.",
        )
        assert MeetingTurn.model_validate_json(turn.model_dump_json()) == turn

    def test_lever_on_fails_loud_for_a_set_without_variant_templates(self) -> None:
        with pytest.raises(ValueError, match="no impostor-answer variant template"):
            build_prompt_renderers("qwen3_5_9b", env=_ON)
        with pytest.raises(ValueError, match="no impostor-answer variant template"):
            build_prompt_renderers("qwen3_32b", env=_ON)


class TestVariantVersionStamps:
    """The registry half of Ruling 3(d): variant bytes never wear default stamps."""

    def test_lever_on_serves_the_variant_registry_entry(self) -> None:
        assert dict(prompt_versions_for_set(_VARIANT_SET, env=_ON)) == {
            "crewmate_report": "crewmate_report.qwen3_6_27b.v5",
            "impostor_report": _VARIANT_IMPOSTOR_STAMP,
            "accusation_round": _VARIANT_ACCUSATION_STAMP,
            "vote_ballot": "vote_ballot.qwen3_6_27b.v5",
        }

    def test_lever_off_serves_the_default_registry_byte_identically(self) -> None:
        assert (
            prompt_versions_for_set(_VARIANT_SET, env=_OFF)
            is PROMPT_VERSION_SETS[_VARIANT_SET]
        )
        assert prompt_versions_for_set(env=_OFF) is DEFAULT_PROMPT_VERSIONS

    def test_variant_entry_keeps_the_shared_four_keys(self) -> None:
        # The recording seam reads the same four keys regardless of the lever
        # (the same-schema invariant, owner decision 2026-06-30).
        variant = IMPOSTOR_ROLL_CALL_PROMPT_VERSION_SETS[_VARIANT_SET]
        assert set(variant) == set(DEFAULT_PROMPT_VERSIONS)

    def test_variant_stamps_collide_with_no_default_stamp(self) -> None:
        # A variant body and a default body can never share a provenance
        # stamp — across EVERY registered set, past bumps included.
        default_stamps = {
            value
            for versions in PROMPT_VERSION_SETS.values()
            for value in versions.values()
        }
        assert _VARIANT_IMPOSTOR_STAMP not in default_stamps
        assert _VARIANT_ACCUSATION_STAMP not in default_stamps
        # The untouched templates keep their exact default stamps: only the
        # two swapped files re-stamp.
        variant = IMPOSTOR_ROLL_CALL_PROMPT_VERSION_SETS[_VARIANT_SET]
        default = PROMPT_VERSION_SETS[_VARIANT_SET]
        assert variant["crewmate_report"] == default["crewmate_report"]
        assert variant["vote_ballot"] == default["vote_ballot"]
        assert variant["impostor_report"] != default["impostor_report"]
        assert variant["accusation_round"] != default["accusation_round"]

    def test_variant_stamps_name_the_variant_template_files(self) -> None:
        # The stamp's template component is the actual .j2 basename rendered,
        # so provenance reads straight back to bytes on disk.
        assert _VARIANT_IMPOSTOR_STAMP.startswith(
            IMPOSTOR_REPORT_ROLL_CALL_TEMPLATE.removesuffix(".j2") + "."
        )
        assert _VARIANT_ACCUSATION_STAMP.startswith(
            ACCUSATION_ROUND_ROLL_CALL_TEMPLATE.removesuffix(".j2") + "."
        )

    def test_lever_on_fails_loud_for_a_set_without_a_variant_entry(self) -> None:
        for set_name in sorted(PROMPT_VERSION_SETS):
            if set_name in IMPOSTOR_ROLL_CALL_PROMPT_VERSION_SETS:
                continue
            with pytest.raises(
                ValueError, match="no impostor-answer variant registry entry"
            ):
                prompt_versions_for_set(set_name, env=_ON)


class TestVariantStampInRecordedBytes:
    """The recorded-bytes half of the DoD, through the production wire-up.

    ``build_default_meeting_runner`` resolves the active set once and pairs
    ``build_prompt_renderers`` with ``prompt_versions_for_set`` on it (the
    DESIGN.md §11.4 provenance invariant); the returned
    ``MeetingArtifacts.prompt_versions`` is what ``HeadlessGame`` persists
    VERBATIM into :class:`~orchestrator.replay.MeetingReplayEntry`. Running a
    real meeting (fake provider — the conftest pin) under the lever proves the
    variant stamps reach recorded bytes; the serialized entry makes the byte
    claim literal.
    """

    @staticmethod
    def _meeting_state() -> WorldState:
        base = seed_initial_state(
            seed=2026, game_map=load_canonical_map(), num_players=4
        )
        return replace(base, phase="MEETING", tick=7)

    @classmethod
    def _run_meeting(cls) -> tuple[dict[str, str], MeetingReplayEntry]:
        state = cls._meeting_state()
        agents: dict[PlayerId, _CannedMeetingAgent] = {
            player_id: _CannedMeetingAgent(agent_id=player_id, role=player.role)
            for player_id, player in state.players.items()
        }
        runner = build_default_meeting_runner()
        trigger = MeetingTrigger(
            triggered_by="p-1",
            trigger_tick=7,
            description="p-1 called an emergency meeting at tick 7",
        )
        loop = asyncio.new_event_loop()
        try:
            artifacts = loop.run_until_complete(
                runner.run_meeting(
                    meeting_id="m-1", trigger=trigger, state=state, agents=agents
                )
            )
        finally:
            loop.close()
        entry = MeetingReplayEntry(
            game_id="game-2026",
            meeting_id="m-1",
            tick=7,
            triggered_by="p-1",
            outcome=artifacts.result.outcome,
            ejected_player_id=artifacts.result.ejected_player_id,
            transcript=artifacts.result.transcript,
            ballots=artifacts.result.ballots,
            contradictions=artifacts.result.contradictions,
            llm_calls=artifacts.llm_calls,
            prompt_versions=artifacts.prompt_versions,
            state_hash_before="00000000",
            state_hash_after="00000000",
        )
        return dict(artifacts.prompt_versions), entry

    def test_lever_on_stamps_the_variant_versions_into_recorded_bytes(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv(ENV_PROMPT_SET, _VARIANT_SET)
        monkeypatch.setenv(ENV_IMPOSTOR_ROLL_CALL, "1")
        versions, entry = self._run_meeting()
        assert versions == dict(IMPOSTOR_ROLL_CALL_PROMPT_VERSION_SETS[_VARIANT_SET])
        recorded = entry.model_dump_json()
        assert _VARIANT_IMPOSTOR_STAMP in recorded
        assert _VARIANT_ACCUSATION_STAMP in recorded

    def test_lever_off_stamps_the_default_versions(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv(ENV_PROMPT_SET, _VARIANT_SET)
        monkeypatch.delenv(ENV_IMPOSTOR_ROLL_CALL, raising=False)
        versions, entry = self._run_meeting()
        assert versions == dict(PROMPT_VERSION_SETS[_VARIANT_SET])
        recorded = entry.model_dump_json()
        assert _VARIANT_IMPOSTOR_STAMP not in recorded
        assert _VARIANT_ACCUSATION_STAMP not in recorded
