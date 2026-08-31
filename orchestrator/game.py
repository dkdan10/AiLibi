"""Headless game orchestrator (DESIGN.md §1.4, §3.1, §11.4).

:class:`HeadlessGame` wires the engine, observation service, agents,
action-intent translation, meeting dispatch, and replay log into a
single deterministic tick loop. It is the Phase-3 convergence point:
when the engine transitions to ``MEETING`` phase, the orchestrator
dispatches to :class:`~meetings.manager.MeetingManager` (via a
:class:`MeetingRunner`), applies the returned :class:`MeetingResult`
to engine-owned world state through :func:`apply_meeting_result`, and
resumes the tick loop at tick ``t+1`` per DESIGN.md §3.1.

The engine firewall guards the ENGINE-FREE side, not this one:
``agents/``, ``meetings/`` and ``llm/`` import nothing from ``engine/``
(the ``agents/`` ban is a contract -- import-linter's "Agents must not
import engine"; ``meetings/`` and ``llm/`` are engine-free in fact, with
no contract of their own). Many privileged modules DO import
``engine/`` -- ``orchestrator/``, ``observation/``, ``api/``, ``eval/``,
``training/``, ``scripts/`` -- so the orchestrator is one importer among
several; what it owns is the meeting-apply seam itself:
:func:`apply_meeting_result` is DEFINED here, and every consumer (the
replay loader, the eval/training reconstruction walkers) re-applies a
meeting to engine-owned world state through this one function.
(Historical note: the "only non-``engine/`` importer, only mutator"
claim described the Phase-3 layout, before those consumers landed.)
``MeetingManager`` is engine-pure: it receives agent-side inputs
(rendered memory, suspicion graphs) and returns a
:class:`MeetingResult` DTO. Applying that result to the world is the
orchestrator's job (DESIGN.md §1.3).
"""

from __future__ import annotations

import asyncio
import os
from collections.abc import Callable, Coroutine, Mapping, Sequence
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Final, Literal, Protocol, TypeAlias, TypeVar, runtime_checkable

from agents.base import AgentInterface
from agents.memory.beliefs import (
    BODY_PROXIMITY_WINDOW_TICKS,
    OBSERVED_KILL_ACTION,
    OBSERVED_VENT_ACTION,
    hard_evidence_gated_suspicion,
)
from agents.memory.store import (
    DEFAULT_TOKEN_BUDGET,
    AgentMemory,
    absorb_meeting_evidence,
    absorb_reported_testimony,
    record_meeting_outcome,
    render_for_prompt,
)
from agents.perception import (
    EVENT_OWN_KILL,
    EVENT_SAW_BODY,
    EVENT_SAW_PLAYER,
    EVENT_SAW_PLAYER_MOVE,
    EVENT_SELF_STATE,
    PROVENANCE_OBSERVED,
    ingest_packet,
)
from agents.strategic.prompts import (
    DEFAULT_PROMPT_SET,
    build_prompt_renderers,
    resolve_prompt_set,
)
from agents.tactical.crewmate_policy import CrewmatePolicy, EmergencyPacingTracker
from agents.tactical.impostor_policy import ImpostorPolicy
from engine.actions import Action
from engine.entities import BodyId, PlayerId, PlayerState, Role, RoomId
from engine.events import (
    EngineEvent,
    GameOverEvent,
    MeetingTriggeredEvent,
)
from engine.rng import EngineRng, RngStateHashPolicy
from engine.rules import resolve_win_conditions
from engine.tick import advance_tick, redistribute_dead_tasks
from engine.world import Map, WorldState
from llm.budget import GameBudget
from llm.budgeted_client import BudgetedLLMClient
from llm.client import LLMClient, LLMResponse
from llm.client import CallKind as _LLMCallKind
from llm.provider import LLMCallFailure, build_default_client, extract_parse_failure
from meetings.manager import (
    EMERGENCY_TRIGGER_PHRASE,
    BodyDiscoveryRecord,
    DefaultedCall,
    reporter_reasoning_enabled,
    MeetingConfig,
    MeetingDeadlines,
    MeetingManager,
    MeetingParticipant,
    MeetingTrigger,
    ReportPromptRenderer,
    StatementPromptRenderer,
    SuspicionEntry,
    VotePromptRenderer,
    MeetingOutcomeSummary,
    derive_meeting_outcome_summary,
    derive_reported_testimony,
    extract_belief_evidence,
)
from meetings.schemas import (
    FoundBodyObservation,
    MeetingResult,
    MoveWitnessRecord,
    ObservationId,
    ReportedStatement,
    SightingRecord,
    VentWitnessRecord,
)
from meetings.transcript import MeetingTriggerKind
from observation.action_intent import ActionIntent
from observation.packet import ObservationPacket
from observation.public_map import PublicMapView
from observation.service import ObservationService
from orchestrator.boundary import (
    public_map_from_engine_map,
    translate_action_intents_for_tick,
)
from orchestrator.personas import assign_personas
from orchestrator.replay import (
    CrewTacticalPolicyStamp,
    LLMCallRecord,
    ReplayLog,
    TacticalPolicyStamp,
    _state_hash,
    _TOGGLEABLE_LEVER_RESOLVERS,
)
from orchestrator.scheduler import TickScheduler
from orchestrator.seeder import seed_initial_state
from pydantic import BaseModel

AgentFactory: TypeAlias = Callable[[PlayerId, Role], AgentInterface]

Outcome: TypeAlias = Literal[
    "CREWMATES",
    "IMPOSTORS",
    "MEETING_PHASE_REACHED",
    "TICK_BUDGET_REACHED",
]

DEFAULT_MAX_TICKS: Final[int] = 1000
DEFAULT_NUM_PLAYERS: Final[int] = 4
DEFAULT_NUM_IMPOSTORS: Final[int] = 1
# Locked Phase 7 Wave 0 default (diagnosis audit 2026-05-30-1952 §1, §3): one
# task per crewmate ends 4p/1i games by median tick 9, before any
# kill->body->report chain can complete (4/50 meetings). Two tasks per crewmate
# lengthens games so bodies can outlive the win condition. The seeder parameter
# itself stays 1 (see ``orchestrator.seeder.seed_initial_state``); this
# default-of-2 is applied only at the harness/CLI layer, so the committed-replay
# loader keeps re-seeding the 4p/1i baseline byte-identically.
DEFAULT_TASKS_PER_CREWMATE: Final[int] = 2


@dataclass(frozen=True)
class RosterPreset:
    """A named, data-only roster configuration (DESIGN.md §1.4, §3.1).

    Bundles the three roster knobs — ``num_players``, ``num_impostors``, and
    ``tasks_per_crewmate`` — under one name so the eval harness (and, in a later
    frontend task, the replay picker) can refer to a config by name instead of
    restating all three values. Frozen and behaviour-free by design: a future
    frontend task can surface the same names without a code change.
    """

    num_players: int
    num_impostors: int
    tasks_per_crewmate: int


# The two canonical roster presets (DESIGN.md §3.5, §8.1). ``4p1i`` is the flat
# descriptor-less determinism/leak reference, pinned at ``tasks_per_crewmate=1``
# — NOT the new default of 2 — so it reproduces the byte-identical committed
# 4p/1i baseline. ``9p2i`` is the canonical eval roster: parity reaches at 5 crew
# deaths (7 crew), so games run longer and surface more meetings, at 2 tasks per
# crewmate. Per-player task instances (DESIGN.md §3.2; the Phase 8 seed-cap
# removal) let its 7×2=14 task instances overlap the 12 map tasks, which the old
# ``num_crewmates × tasks_per_crewmate ≤ len(map.tasks)`` cap forbade.
ROSTER_PRESETS: Final[Mapping[str, RosterPreset]] = {
    "4p1i": RosterPreset(num_players=4, num_impostors=1, tasks_per_crewmate=1),
    "9p2i": RosterPreset(num_players=9, num_impostors=2, tasks_per_crewmate=2),
}

# Static map of prompt-template id → version string. The versions are
# embedded as comments + a visible "Prompt: <id>" marker line in the .j2
# files (see ``agents/strategic/prompts/*.j2``); maintaining the mapping
# here keeps the replay record's :attr:`MeetingReplayEntry.prompt_versions`
# in sync without a runtime regex over the loaded templates. Bump the
# string here whenever the matching template header is bumped.
#
# Task 8.8 bumped ALL FOUR templates in lockstep because the reactive
# accusation-chain reshape (DESIGN.md §5.2) is a behavior-shifting change
# to every meeting prompt: the four ``.j2`` templates now emit the
# chain shapes (opening / reactive reply / opt-in / vote) against the
# ``MeetingTurn`` schema. The four versions must move together — a partial
# bump fails the manifest/replay provenance cross-check. The reshape is one
# of the Phase-8 byte-breakers, so both committed sets are re-recorded in
# Task 8.12 under these revisions (there is no byte-identity left to
# preserve, which is why the old vote_ballot v1-body / v2-record split is
# also retired here). This map is metadata only (never rendered into a
# prompt); the recorded value is the AUTHORITATIVE revision read by
# replay/eval and the sample MANIFESTs.
#
# Task 8.16 (DESIGN.md §5.5; audit gp-3) bumps ``vote_ballot`` alone to
# vote_ballot/v4: only the vote prompt's `primary_reason_id` example text
# changed (a real transcript turn id, never a hardcoded one), so this is a
# single-template prompt-text revision, not the four-template lockstep of
# 8.8. The committed sample / prompt-regression bytes still record v3 and
# are regenerated in Task 8.18, not here.
#
# Task 9.9 (DESIGN.md §5.1, §5.2, §5.5; audit gp-3) bumps the two TURN
# templates -- crewmate_report v3 -> v4 and accusation_round v5 -> v6: both
# gain the free_text length discipline (the 9B relocates its deliberation
# into free_text and overruns the frozen 2048 turn cap) and the gated
# living-roster accusation block (living players minus the speaker, threaded
# like the vote ballot's candidate_targets). Prompt-text revisions to the two
# turn templates only, not a lockstep bump; the committed sample bytes still
# record v3/v5 and are re-recorded in Task 9.11, not here.
#
# Task 10.3 (DESIGN.md §5.1, §5.2; audit gp-9) bumps the THREE turn templates
# -- crewmate_report v4 -> v5, impostor_report v3 -> v4, accusation_round
# v6 -> v7: the openings make the §5.2 accuse-or-declare-unsure choice a hard
# requirement (backed by the manager's opening retry), all three carry the
# list-each-sighting-once anti-repetition line, and the roster block renders
# the DEAD / ejected players as an explicit do-not-accuse line (the impostor
# template gains the roster block itself). vote_ballot is FROZEN (the §4.6
# render). The committed sample bytes still record v4/v3/v6 and are
# re-recorded in Task 10.5, not here.
#
# Task 10.8 (DESIGN.md §3.2, §5.2; audit gp-3) bumps crewmate_report alone
# v5 -> v6: the template gains an emergency-opening branch (keyed off the
# orchestrator's "called an emergency meeting" trigger description) that
# frames a body-less, called-on-suspicion meeting -- state who you suspect
# and the first-hand basis, or unsure -- now that the suspicion-accumulation
# trigger makes the emergency channel reachable for crew. The body-report
# branch is byte-identical to v5 apart from this version marker (golden-
# pinned). Lineage confirmed at branch time: builds on the v5 merged in
# Wave 0 and recorded by 10.5; no Wave-1 task touches the template in
# parallel (10.7 is prompts-frozen). The committed sample bytes still record
# v5 and are re-recorded in Task 10.9, not here.
#
# Task 10.11 (DESIGN.md §3.2, §5.2, §5.4; audit-2026-06-13-1816 B-B-1) bumps
# crewmate_report alone v6 -> v7: the emergency-opening branch must NOT present
# a `found_body` observation. On the close baseline every emergency opening
# re-narrated a real-but-stale corpse as a fresh discovery and voters anchored
# ejections on the fabrication; v7's emergency job paragraph leads with the
# suspicion that crossed the line and forbids a `found_body`. The body-report
# branch is byte-identical to v6 apart from this version marker (golden-pinned);
# only the emergency job paragraph changed. The engine half is the
# trigger-kind-gated relevance zone (:func:`meetings.transcript.triggering_body_rooms`)
# plus the emergency-opening self-check below. The committed sample bytes still
# record their as-recorded versions and are NOT re-recorded here (recording-side
# only; replays/samples out of scope).
#
# Task 10.14 (DESIGN.md §3.4, §4.5, §5.3; audit-2026-06-13-1816 D-D-1/D-D-2/D-D-7;
# experiments/lab/report-deception-battery-2.md) bumps impostor_report alone
# v4 -> v5: the impostor opening gains an ANTICIPATORY-COVER branch on a
# body-report trigger (the perform-from-a-goal directive that makes the 9B build
# its own sheltered alibi away from the kill scene and PIN the cover room/window
# so the justification does not drift). The emergency branch keeps the v4 frame
# (impostors gain no button this wave). It is the prompt half of the impostor
# toolkit (blending + kill discipline land in agents/tactical + observation). The
# committed sample bytes still record impostor_report_v4 and are re-recorded at
# 10.17, not here (recording-side only; replays/samples out of scope).
#
# Task 11.2 (2026-06-15; DESIGN.md §5.2; experiments/lab/report-vent-escape-lab.md)
# bumps accusation_round alone v7 -> v8: the impostor cover-consistency directive
# (commit to ONE sheltered room + tick-window away from the body and reuse it
# every turn) was stranded on the impostor_report body-report OPENING that
# impostors never take, so on the REPLY turn -- the only turn an impostor ever
# speaks -- its account drifted across turns (the residual self-pair alibi_conflict
# flags the vent fix cannot remove). The directive is ported verbatim into the
# accusation_round reply branch, gated on the new `is_impostor` bool; crewmate
# replies and opt-in turns are byte-unchanged. The committed sample bytes still
# record accusation_round.v7 and are re-recorded at 11.4, not here (recording-side
# only; replays/samples + the prompt-regression baseline out of scope).
#
# Task 13.6 (2026-06-21; report-phase-b-plan "Prompts"; the GATE FINDING in
# tasks/phase-13.md) bumps ALL FOUR together: the meeting templates were reworked so
# the crew STATE richer who/where/when sightings (the two-source material the
# inferential detector starved for -- R7 0/50 on the committed set). crewmate_report
# v7 -> v8 and accusation_round v8 -> v9 are REBUILT from a clean base (a focused
# sighting-elicitation section + the belief-mover framing, every load-bearing guard
# carried forward); impostor_report v5 -> v6 and vote_ballot/v5 -> v6 take the lighter
# trim + the belief-mover framing. The store.py directional movement breadcrumb feeds
# the same who/where/when material into the rendered memory. NO re-record here -- the
# committed sample bytes still record the v7/v5/v8/v5 set and are re-recorded at the
# Wave-B smoke re-record (13.10), not here (recording-side only; replays/samples + the
# prompt-regression baseline out of scope). think=False is preserved (13.9).
#
# Task 13.13 (DESIGN.md §4.6 + §5.5 reconciled; Probe 1) bumps vote_ballot ALONE,
# vote_ballot/v6 -> v7: the §4.6 decision-rule gate is DE-IMPERATIVED -- the
# pre-computed MUST-vote-to-eject / MUST-set-SKIP command becomes a non-directive
# evidence line (max suspicion + the 0.60 reference threshold as ONE input), and the
# emitted confidence is pinned IN PROSE (no code clamp) so a sub-threshold target
# cannot carry a >= threshold confidence. The deterministic tally floor
# (meetings.voting.tally_ballots) and the manager's guard_ballot_target_graph §4.6
# verdict are UNCHANGED -- the anti-cascade backstop is the tally, not the prompt. NO
# re-record here: the committed sample bytes still record vote_ballot/v5 (the 13.6 v6
# bump was never re-recorded either; the manifest pin reads v5 as-recorded) and are
# re-recorded at the held 13.12 combined re-record (recording-side only). The other
# three templates are byte-unchanged at this task.
DEFAULT_PROMPT_VERSIONS: Final[Mapping[str, str]] = {
    "crewmate_report": "crewmate_report.v8",
    "impostor_report": "impostor_report_v6",
    "accusation_round": "accusation_round.v9",
    "vote_ballot": "vote_ballot/v7",
}


# Per-model prompt-set version registry (Task 14.2; owner decision 2026-06-25 —
# per-model prompt sets; DESIGN.md §11.4 replay provenance). The frozen
# ``qwen3.5:9b`` reference set keeps the EXACT ``DEFAULT_PROMPT_VERSIONS``
# mapping above (same symbol, byte-identical keys/values) so the committed
# replays and the ``prompt_versions`` assertions in ``tests/orchestrator/`` and
# ``tests/scripts/`` stay green with ZERO re-record. A new-model set is
# distinguished by its OWN version strings plus the recorded model id -- NOT by
# prefixing or reformatting the 9B set's keys/values. New sets register
# themselves here (Task 14.5) keyed by the same ``AILIBI_PROMPT_SET`` selector
# the loader (:mod:`agents.strategic.prompts.loader`) resolves.
def _bespoke_versions(set_name: str, version: str = "v1") -> Mapping[str, str]:
    """Per-set ``prompt_versions`` for a Task 14.5 bespoke set.

    Every bespoke set carries the SAME four keys as :data:`DEFAULT_PROMPT_VERSIONS`
    (so the recording seam reads them identically — the same-schema invariant,
    owner decision 2026-06-30) but its OWN version VALUES, namespaced by the set
    name (``<template>.<set>.<version>``). A new-model replay is distinguished by
    these strings plus its recorded model id, never by reformatting the 9B set's
    values. ``version`` bumps when a set's templates are revised as a unit (e.g.
    ``glm_4_32b`` -> ``v2`` after the response-shape hardening that lifted its
    structured-output parse-success).
    """

    return {
        "crewmate_report": f"crewmate_report.{set_name}.{version}",
        "impostor_report": f"impostor_report.{set_name}.{version}",
        "accusation_round": f"accusation_round.{set_name}.{version}",
        "vote_ballot": f"vote_ballot.{set_name}.{version}",
    }


# Per-model prompt-set version registry. The frozen ``qwen3_5_9b`` reference set
# keeps the EXACT ``DEFAULT_PROMPT_VERSIONS`` mapping (same object identity); the
# Task 14.5 bespoke sets (one per candidate model/mode) register their OWN version
# strings here, keyed by the same ``AILIBI_PROMPT_SET`` selector the loader
# resolves. A set listed here MUST have a matching template directory under
# ``agents/strategic/prompts/<set>/`` (the loader fails loud otherwise).
PROMPT_VERSION_SETS: Final[Mapping[str, Mapping[str, str]]] = {
    DEFAULT_PROMPT_SET: DEFAULT_PROMPT_VERSIONS,
    # Task 15.4 (vent observability): v5 = the vent-elicitation revision of the
    # turn/opening templates (vote_ballot.j2 byte-identical at the set bump).
    # Task 15.5 (reporter exculpation): vote_ballot ALONE advances v5 -> v6 (its
    # per-template bump for the reporter-exculpation annotation), so the pre- and
    # post-15.5 vote-prompt bodies can never share the ``vote_ballot.qwen3_32b.v5``
    # stamp; the other three templates stay v5.
    "qwen3_32b": {
        **_bespoke_versions("qwen3_32b", version="v5"),
        "vote_ballot": "vote_ballot.qwen3_32b.v6",
    },
    "qwen3_32b_thinking": _bespoke_versions("qwen3_32b_thinking", version="v2"),
    "qwen3_30b_a3b": _bespoke_versions("qwen3_30b_a3b", version="v2"),
    "glm_4_32b": _bespoke_versions("glm_4_32b", version="v3"),
    "cydonia_24b": _bespoke_versions("cydonia_24b", version="v2"),
    # The locked-model bespoke set, and the one every operational surface runs.
    # Its live bodies keep the evidence section inside the fiction: the block
    # renders as ``<contradictions>``, the proof line states the vent mechanic
    # rather than citing an engine, no rendered line names a flag, a detector or
    # a certification, and the ``<map>`` card writes each room as
    # ``Prose Name (ROOM_ID)`` so the table has an authored spelling to speak.
    # Every template renders that card, so the four stamps bump as a unit and no
    # two bodies can ever share one. The committed sample sets stamp v4 and
    # resolve through tests/fixtures/prompt_archive/qwen3_6_27b_v4/ until the
    # adopting record retires that entry.
    # Lineage: 16.13 port, 16.15 elicitation, 16.16 persona, 20.31 evidence
    # honesty, 21.1 in-world register.
    "qwen3_6_27b": _bespoke_versions("qwen3_6_27b", version="v5"),
}


# Task 18.10 (the impostor-answer template arm): the VARIANT version registry,
# served by :func:`prompt_versions_for_set` ONLY while the default-OFF
# ``impostor_roll_call`` lever is ON. The variant swaps the two
# impostor-facing templates for their ``*_roll_call.j2`` siblings (authored
# only in the ``qwen3_6_27b`` set), so exactly those two keys carry variant
# stamps; ``crewmate_report`` / ``vote_ballot`` render the default bodies and
# inherit whatever version the default registry above serves. The two variant
# BODIES render no map card and carry no swept prose, so a default-set bump
# leaves their rendered bytes untouched and they keep their own v1 lineage (an
# unrecorded, default-OFF arm; deliberately, they also keep the singular
# persona the default set has now dropped). The variant stamps follow the
# ``<template>.<set>.<version>`` convention with the template component naming
# the actual variant FILE (``impostor_report_roll_call``) on its OWN v1
# lineage: a variant body can never share a stamp with any default
# ``impostor_report.qwen3_6_27b.vN`` body, past or future — the provenance
# separation audits/audit-phase-17-absence-gate.md Ruling 3(d) requires when
# impostor bytes move (the bar re-reads on the new bytes, distinguished by
# stamp). If the 18.11 gate rules SHIP, Task 18.12 flips these values into
# :data:`PROMPT_VERSION_SETS` as the default-served entries; until then the
# default registry above is untouched and committed recordings resolve
# through it byte-identically.
IMPOSTOR_ROLL_CALL_PROMPT_VERSION_SETS: Final[Mapping[str, Mapping[str, str]]] = {
    "qwen3_6_27b": {
        **_bespoke_versions("qwen3_6_27b", version="v5"),
        "impostor_report": "impostor_report_roll_call.qwen3_6_27b.v1",
        "accusation_round": "accusation_round_roll_call.qwen3_6_27b.v1",
    },
}


def _lever_arm_versions(set_name: str, lever_key: str) -> Mapping[str, str]:
    """Per-template stamps for an arm that RE-BODIES a set's own templates.

    The 18.10 arm swaps template FILES, so its stamps name the variant file. An
    arm that renders the SAME files with a guarded block has no other file to
    name, so its stamps are the set's own values with the arm key appended:
    ``crewmate_report.qwen3_6_27b.v5.reporter_reasoning`` says which body
    rendered AND which arm shaped it, so the stamp moves when EITHER moves.
    No arm value contains ``+``; a composite of two arms does, which is what
    keeps the two kinds of stamp disjoint.
    """

    return {
        template: f"{value}.{lever_key}"
        for template, value in PROMPT_VERSION_SETS[set_name].items()
    }


# The reporter-voice ON-arm version registry, served by
# :func:`prompt_versions_for_set` only while the default-OFF
# ``reporter_reasoning`` lever is ON. The lever swaps no template FILE: it
# renders the SET's own ``crewmate_report.j2`` / ``accusation_round.j2`` with a
# guarded block, so exactly those two keys carry arm stamps and the two the
# lever leaves alone inherit the default registry's values. Provenance moves
# with the BODIES that moved (audits/audit-phase-17-absence-gate.md Ruling
# 3(d)): an arm-rendered opening or reply can never wear a default stamp.
_REPORTER_REASONING_ARM: Final[Mapping[str, str]] = _lever_arm_versions(
    "qwen3_6_27b", "reporter_reasoning"
)
REPORTER_REASONING_PROMPT_VERSION_SETS: Final[Mapping[str, Mapping[str, str]]] = {
    "qwen3_6_27b": {
        **_bespoke_versions("qwen3_6_27b", version="v5"),
        "crewmate_report": _REPORTER_REASONING_ARM["crewmate_report"],
        "accusation_round": _REPORTER_REASONING_ARM["accusation_round"],
    },
}


# The corroboration ON-arm version registry, served while the default-OFF
# ``corroboration_discipline`` lever is ON. Same shape as the reporter arm and
# for the same reason -- the lever swaps no template FILE, it renders the set's
# own ``vote_ballot.j2`` with a guarded source-count block -- so exactly that one
# key carries an arm stamp and the other three inherit the default registry's
# values. A ballot rendered with the block can therefore never share a
# ``vote_ballot`` stamp with one rendered without it.
_CORROBORATION_DISCIPLINE_ARM: Final[Mapping[str, str]] = _lever_arm_versions(
    "qwen3_6_27b", "corroboration_discipline"
)
CORROBORATION_DISCIPLINE_PROMPT_VERSION_SETS: Final[Mapping[str, Mapping[str, str]]] = {
    "qwen3_6_27b": {
        **_bespoke_versions("qwen3_6_27b", version="v5"),
        "vote_ballot": _CORROBORATION_DISCIPLINE_ARM["vote_ballot"],
    },
}


# Every live lever that carries an ON-arm version overlay, keyed by the substrate
# registry key the lever stamps. The fold below iterates
# ``_TOGGLEABLE_LEVER_RESOLVERS`` rather than this mapping, so application order
# is REGISTRATION order and never depends on how the environment was spelled or
# on dict insertion here. A sibling lever registers one entry and costs no new
# branch.
_PROMPT_VERSION_OVERLAYS: Final[Mapping[str, Mapping[str, Mapping[str, str]]]] = {
    "impostor_roll_call": IMPOSTOR_ROLL_CALL_PROMPT_VERSION_SETS,
    "reporter_reasoning": REPORTER_REASONING_PROMPT_VERSION_SETS,
    "corroboration_discipline": CORROBORATION_DISCIPLINE_PROMPT_VERSION_SETS,
}

# The human label each overlay's fail-loud message names, so an operator reads
# WHICH arm has no body for the set they selected rather than a registry key.
_PROMPT_OVERLAY_LABELS: Final[Mapping[str, str]] = {
    "impostor_roll_call": "impostor-answer",
    "reporter_reasoning": "reporter-voice",
    "corroboration_discipline": "source-count",
}


def _arm_is_served(versions: Mapping[str, str], *, template: str, arm: str) -> bool:
    """Whether the served stamp for ``template`` credits ``arm``'s lineage.

    The composite fold joins each contributing arm's own value with ``+`` and no
    arm value contains one (:func:`_lever_arm_versions`), so splitting recovers
    the participating lineages exactly. A renderer that gates on THIS rather than
    on a second environment read cannot render a block the recorded stamp does
    not claim, whoever supplied the versions.
    """

    return arm in versions.get(template, "").split("+")


def enabled_prompt_version_overlays(
    env: Mapping[str, str] | None = None,
) -> tuple[str, ...]:
    """The live overlay keys reading ON, in ``_TOGGLEABLE_LEVER_RESOLVERS`` order.

    One read of the SAME resolvers the substrate stamp uses, so a recording's
    rendered bytes, its recorded ``prompt_versions`` and its substrate stamp can
    never describe three different slates.
    """

    return tuple(
        key
        for key, resolver in _TOGGLEABLE_LEVER_RESOLVERS
        if key in _PROMPT_VERSION_OVERLAYS and resolver(env)
    )


def _overlay_entry(key: str, set_name: str) -> Mapping[str, str]:
    """One overlay's registry entry for ``set_name``, or fail loud.

    The refusal is about a MISSING variant body for the set, never about a
    sibling overlay being on: an all-ON slate is exactly what the adopting record
    runs, so composition must construct.
    """

    registry = _PROMPT_VERSION_OVERLAYS[key]
    try:
        return registry[set_name]
    except KeyError as exc:
        known = ", ".join(sorted(registry))
        label = _PROMPT_OVERLAY_LABELS[key]
        variable = f"AILIBI_{key.upper()}"
        raise ValueError(
            f"Prompt set {set_name!r} has no {label} variant registry "
            f"entry; the {variable} lever is "
            f"only registered for: {known} — unset the lever or select a "
            "variant-capable set"
        ) from exc


def prompt_versions_for_set(
    prompt_set: str | None = None,
    *,
    env: Mapping[str, str] | None = None,
) -> Mapping[str, str]:
    """Return the recorded ``prompt_versions`` mapping for a prompt set.

    Resolves the active set via :func:`resolve_prompt_set` (the same
    ``AILIBI_PROMPT_SET`` selector the loader uses) and looks it up in
    :data:`PROMPT_VERSION_SETS`. An unregistered set raises :class:`ValueError`
    -- no silent fallback (AGENTS.md §"No silent fallbacks"). With the default
    (9B) set and no lever ON this returns :data:`DEFAULT_PROMPT_VERSIONS`
    byte-identically, by identity.

    A lever with an ON-arm overlay moves provenance WITH the rendered bytes:
    while its resolver reads ON from the same ``env``, this serves that arm's
    version strings instead (recorded ``prompt_versions`` come from THIS
    registry, never from the loader — a lever read here and not in
    :func:`build_default_meeting_runner`'s renderer binding, or vice versa, is
    exactly the render-one-stamp-another failure this pairing exists to
    prevent). Lever ON with a set that carries no arm entry raises
    :class:`ValueError` — a MISSING body, and there is no silent fallback.

    Overlays COMPOSE, because the slate the adopting record runs is all-ON.
    Three rules, fixed here and shared by every sibling arm:

    1. application order is registration order (``_TOGGLEABLE_LEVER_RESOLVERS``),
       so the result never depends on environment spelling;
    2. one arm ON serves that arm's own registry entry verbatim; two or more ON
       resolve each template to a COMPOSITE of the values the arms that ACTUALLY
       re-body it contribute, in that same order, so the stamp names exactly the
       lineages that shaped those bytes and moves when any of them moves;
    3. the composite is computed by a fold over the enabled set, not by a
       pairwise table, so a third arm costs a registration and no new branch.

    One constraint the fold cannot enforce and the next arm author must respect:
    an arm that swaps in a variant FILE serves a body written independently of
    every sibling, so a sibling whose block lives in the DEFAULT body does not
    reach the render while that swap is on. Two such arms compose in the stamp
    but not in the bytes. The ``impostor_roll_call`` + ``reporter_reasoning``
    pair is exactly that case today and is pinned as a known gap in
    ``tests/meetings/test_prompt_byte_golden.py``; an arm that swaps a file must
    author its siblings' blocks into the variant.
    """

    name = resolve_prompt_set(prompt_set, env=env)
    enabled = enabled_prompt_version_overlays(env)
    try:
        default = PROMPT_VERSION_SETS[name]
    except KeyError as exc:
        known = ", ".join(sorted(PROMPT_VERSION_SETS))
        raise ValueError(
            f"Unknown prompt set {name!r}: no version registry entry "
            f"(known sets: {known})"
        ) from exc
    if not enabled:
        return default
    entries = [_overlay_entry(key, name) for key in enabled]
    if len(enabled) == 1:
        return entries[0]
    # PER-TEMPLATE, and from each contributing arm's OWN value rather than from
    # the default: an arm that swaps in a variant FILE carries that file's own
    # lineage (``impostor_report_roll_call…v1``), so a composite rebuilt from the
    # default value would not move when that variant body was revised and two
    # different bodies could share one stamp. Joining the contributing values
    # keeps every participating lineage inside the stamp, so ANY of them moving
    # moves it. A template no enabled arm re-bodies keeps its default value --
    # those ARE the default bytes, and giving them a composite would claim a
    # provenance the render does not have.
    versions: dict[str, str] = {}
    for template, value in default.items():
        contributing = [
            entry[template] for entry in entries if entry[template] != value
        ]
        versions[template] = "+".join(contributing) if contributing else value
    return versions


# Headless recording runs meetings deadline-free (DESIGN.md §1.4, §5.2, §8.3:
# "Meeting deadlines off in headless mode; on with generous defaults in live
# mode"). The choice is made explicit HERE, at the production headless
# construction site (:func:`build_default_meeting_runner`), rather than left to
# the interactive ``MeetingDeadlines`` 30 s default: audit gp-2 found the
# headless recorder silently ran the interactive 30 s per-turn/per-vote
# deadlines, so slow local-Ollama calls lost 11 turns (9 of 91 openings) to a
# wall-clock race with no record of any kind. ``None`` disables the deadline
# (passed straight to ``asyncio.wait_for``); a provider-level transport timeout
# remains the fail-loud guard via ``meetings.manager._isolate_provider_timeout``.
HEADLESS_MEETING_DEADLINES: Final[MeetingDeadlines] = MeetingDeadlines(
    turn_seconds=None, vote_seconds=None
)

# Sentinel ``model`` for a ``deadline_default`` failed-call marker. Such a
# marker carries ZERO spend (a wall-clock miss completed nothing; a validation
# default's real spend is already captured in the meeting's ``llm_calls``), so
# it must never be mistaken for a model call -- this clearly-labelled phantom
# keeps it a distinct, non-spend bucket in any per-model cost roll-up.
_DEADLINE_DEFAULT_MODEL: Final[str] = "(deadline_default)"

_T = TypeVar("_T")


# ---------------------------------------------------------------------------
# Meeting wiring — protocols, artifacts, and the default runner.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MeetingArtifacts:
    """Bundle returned by a :class:`MeetingRunner` (DESIGN.md §11.4).

    Carries the :class:`MeetingResult` plus the per-call LLM telemetry
    and the prompt-version metadata the replay log needs to persist a
    full audit trail per the R-9 acceptance gate.

    ``defaulted_calls`` carries any turn / ballot that fell back to its
    placeholder during the meeting (audit gp-2). The orchestrator writes one
    visible ``deadline_default`` :class:`~orchestrator.replay.FailedCallReplayEntry`
    per entry so a defaulted turn is never lost from the replay.

    ``recovered_call_failures`` carries provider parse-failures the manager
    recovered on a SUCCEEDING turn (an earlier retry attempt raised before the
    recording client could log the call, then a later attempt parsed). The
    orchestrator records each so the burned spend stays visible even though the
    turn ultimately succeeded and carries no ``DefaultedCall``.

    Both default to ``()`` so a runner that produces neither -- the common
    case -- need not set them.
    """

    result: MeetingResult
    llm_calls: tuple[LLMCallRecord, ...]
    prompt_versions: Mapping[str, str]
    defaulted_calls: tuple[DefaultedCall, ...] = ()
    recovered_call_failures: tuple[LLMCallFailure, ...] = ()


@runtime_checkable
class MeetingRunner(Protocol):
    """Drive one meeting end-to-end from inside the tick loop.

    The orchestrator dispatches here when ``state.phase == "MEETING"``.
    Implementations own the wiring (LLM client, prompt callables,
    participant construction); the orchestrator only consumes the
    returned :class:`MeetingArtifacts`. The runner MUST NOT mutate
    ``state``; engine-state application happens through
    :func:`apply_meeting_result` after the runner returns
    (DESIGN.md §1.3, §5.1).
    """

    async def run_meeting(
        self,
        *,
        meeting_id: str,
        trigger: MeetingTrigger,
        state: WorldState,
        agents: Mapping[PlayerId, AgentInterface],
    ) -> MeetingArtifacts: ...


@runtime_checkable
class MeetingAwareAgent(Protocol):
    """Agent that exposes the inputs a meeting needs (DESIGN.md §5.1, §6.6).

    The default :class:`MeetingRunner` (:class:`DefaultMeetingRunner`)
    consumes this protocol to build :class:`MeetingParticipant`s from
    each living agent. Tactical agents instantiated by
    :func:`build_default_agent_factory` satisfy this protocol; tests
    that do not exercise meetings can use any
    :class:`AgentInterface` implementer.

    ``vent_witness_records_for_meeting`` (Task 15.4) and
    ``sighting_records_for_meeting`` (Task 16.7) are the two typed
    self-channel accessors on this protocol: the agent's OWN witnessed-vent
    and first-hand-sighting episodic records, the grounding inputs behind
    the meeting layer's ``vent_sighting`` hard flag and the grounded-vouch
    corroboration feed respectively. Both are REQUIRED protocol members
    (not optional sibling capabilities like :class:`BeliefPersistingAgent`)
    because the grounding chokepoints are load-bearing -- a meeting run
    without a channel would silently accept every spoken claim on it as
    ungroundable testimony, an advisory-grounding failure mode the task
    contracts forbid. Firewall-clean: an agent reporting its own witnessed
    events leaks nothing (the packet stamp the records derive from is
    witness-gated, ``eval/leak_test.py``); a canned test double may return
    ``()`` from either.

    ``observation_ids_for_meeting`` (Task 16.5, C8) is the sibling
    self-channel accessor for stable episodic observation ids: the agent's
    OWN ``{agent_id}:{tick}:{seq}`` id set, the valid-citation universe the
    manager validates a ballot's ``primary_reason_observation_id`` against.
    Also REQUIRED and firewall-clean -- the ids name the agent's own memory
    rows and leak nothing; a canned double may return ``()``.

    ``body_discovery_records_for_meeting`` is the self-channel behind the
    reporter-voice lever's co-discovery line: the agent's OWN first-hand body
    discoveries. OPTIONAL, unlike the four above, because nothing is grounded or
    validated against it -- an agent without the accessor simply discovered
    nothing, which is the lever's own OFF behaviour -- so a canned test double
    needs no body bookkeeping to run a meeting.
    """

    @property
    def agent_id(self) -> PlayerId: ...

    @property
    def role(self) -> Role: ...

    def render_memory_for_meeting(
        self,
        *,
        token_budget: int = DEFAULT_TOKEN_BUDGET,
        suspicion_override: Mapping[PlayerId, float] | None = None,
    ) -> str: ...

    def suspicion_graph_for_meeting(self) -> tuple[SuspicionEntry, ...]: ...

    def vent_witness_records_for_meeting(self) -> tuple[VentWitnessRecord, ...]: ...

    def sighting_records_for_meeting(self) -> tuple[SightingRecord, ...]: ...

    def observation_ids_for_meeting(self) -> tuple[ObservationId, ...]: ...


@runtime_checkable
class BeliefPersistingAgent(Protocol):
    """Agent that folds a meeting's evidence into persistent beliefs (Task 9.8).

    The post-meeting half of DESIGN.md §4.4 step 4 (rule-based, no LLM):
    after :func:`apply_meeting_result` the orchestrator calls this on every
    living agent so the meeting's accusation bump, Rule 3 corroboration,
    and Rule 5 decay land in the SAME stored :class:`BeliefState` the next
    meeting's :meth:`MeetingAwareAgent.suspicion_graph_for_meeting` reads --
    the persistence that lets suspicion accumulate across rounds instead of
    being rebuilt and discarded at vote time (audit gp-1 recall).

    Deliberately a separate, OPTIONAL capability rather than an extension
    of :class:`MeetingAwareAgent`: an agent without a persistent belief
    store (a scripted / packet-recording test agent whose suspicion graph
    is canned) has nothing to fold, exactly as ``ingest_packet(beliefs=None)``
    skips the belief rules for store-less runtimes. The production
    :class:`TacticalAgent` implements it; the across-meeting persistence of
    that path is pinned by integration test so a silent regression (the
    "inert accumulator" failure mode) cannot pass CI.
    """

    def absorb_meeting_evidence(
        self,
        *,
        accused: tuple[PlayerId, ...],
        corroborated: tuple[PlayerId, ...],
        contradicted: tuple[PlayerId, ...],
    ) -> None: ...


@runtime_checkable
class ReportedTestimonyAgent(Protocol):
    """Agent that folds a meeting's public testimony into memory as CONTENT (Task 13.5.2).

    The content twin of :class:`BeliefPersistingAgent`: where that capability
    folds a meeting into a scalar suspicion Δ, this one preserves the WHAT of
    public speech as ``provenance="reported"`` episodic rows and populates the
    alibi map (the 2026-06-25 memory diagnosis, workflow ``wg54kfoxy``: "social
    info is a scalar, not content"). A SEPARATE, OPTIONAL capability for the same
    reason :class:`BeliefPersistingAgent` is one -- a scripted / packet-recording
    test agent without a memory store has nothing to ingest -- and additive, so
    no existing agent must implement it. :func:`_absorb_meeting_beliefs` calls it
    per living agent unconditionally since Task 14.9 (the adopted 13.5.2 lever
    is the default substrate).
    """

    def absorb_reported_testimony(
        self,
        *,
        statements: tuple[ReportedStatement, ...],
    ) -> None: ...


@runtime_checkable
class MoveWitnessAgent(Protocol):
    """Agent that exposes its OWN witnessed room→room transitions.

    The grounding feed behind the meeting layer's movement-claim chokepoint
    (:func:`meetings.transcript.detect_contradictions`): a spoken placement is
    only ever re-read at a destination the SPEAKER's own record already holds,
    so the channel is what keeps the rule unable to rewrite testimony nobody
    made. Firewall-clean -- an agent reporting its own
    witnessed events leaks nothing, and the packet the rows derive from is
    witness-gated by the engine (``eval/leak_test.py``).

    OPTIONAL, like :class:`BeliefPersistingAgent`, rather than a member of
    :class:`MeetingAwareAgent`: an agent without the channel simply grounds
    nothing, and a spoken placement of theirs is read exactly as spoken --
    the same no-op the lever's OFF path produces, so a scripted /
    packet-recording test agent needs no movement bookkeeping to run a meeting.
    """

    def move_witness_records_for_meeting(self) -> tuple[MoveWitnessRecord, ...]: ...


@runtime_checkable
class BodyDiscoveryAgent(Protocol):
    """Agent that exposes its OWN first-hand body discoveries.

    The self-channel the reporter-voice lever reads to decide whether a speaker's
    own record places them at the body when the meeting opened. Firewall-clean --
    an agent reporting its own witnessed events leaks nothing, and the packet the
    rows derive from is witness-gated by the engine (``eval/leak_test.py``).

    OPTIONAL, like :class:`MoveWitnessAgent`: an agent without the channel simply
    discovered nothing, and its prompts carry no discovery line -- the same no-op
    the lever's OFF path produces.
    """

    def body_discovery_records_for_meeting(self) -> tuple[BodyDiscoveryRecord, ...]: ...


@runtime_checkable
class MeetingPacingAgent(Protocol):
    """Agent that bookkeeps meeting-end pacing facts (Task 10.8, 18.22).

    After every resolved meeting the orchestrator notifies each living
    agent of four PUBLIC facts -- when gameplay resumes (``end_tick``),
    the announced post-meeting dead roster (deaths and ejections are
    public at meetings, the same knowledge the Task 10.3 DEAD prompt line
    renders), which player's emergency action opened the meeting
    (``None`` for a body report), and the meeting's ejection outcome
    (``ejected_id`` -- the ejected player, or ``None`` for a skip/tie).
    The crewmate emergency trigger's
    :class:`~agents.tactical.crewmate_policy.EmergencyPacingTracker`
    consumes the first three for the global
    :data:`~agents.tactical.crewmate_policy.EMERGENCY_COOLDOWN_TICKS`
    cooldown, the one-call-per-game accounting (a call is spent only when
    a meeting actually OPENS from it -- engine truth, so a pre-empted
    intent does not burn the call), and the crossed-since-meeting reset.

    The ``ejected_id`` fact feeds the meeting-history memory channel the v3
    tactical feature encoder reads: it is the announced ejection everyone at
    the table saw, on the same public footing as ``dead_ids``, so folding it
    into an agent's own memory crosses no firewall.

    Four further announcement facts ride the same payload, all defaulting to
    ``None`` so every existing direct caller keeps working untouched:
    ``ejected_role`` (the confirm-ejects announcement of the EJECTED player's
    role -- never a living player's, never a kill victim's),
    ``votes_for_ejected`` / ``skip_votes`` (the announced tally) and
    ``roster_impostor_count`` (the impostor count stated at game start). The
    orchestrator is the only module that may translate a role out of engine
    state; the meeting layer contributes the role-blind tally, and ``agents/``
    receives the announcement already made.

    Optional capability like :class:`BeliefPersistingAgent`: a scripted /
    packet-recording test agent without pacing bookkeeping is skipped. An
    impostor :class:`TacticalAgent` still folds the outcome into its own
    meeting-history memory (the v3 encoder is impostor-side) but performs no
    tracker/button bookkeeping (impostors gain no button behavior until Wave 2
    decides it).
    """

    def note_meeting_concluded(
        self,
        *,
        end_tick: int,
        dead_ids: tuple[PlayerId, ...],
        emergency_caller_id: PlayerId | None,
        ejected_id: PlayerId | None = None,
        ejected_role: Role | None = None,
        votes_for_ejected: int | None = None,
        skip_votes: int | None = None,
        roster_impostor_count: int | None = None,
    ) -> None: ...


class _RecordingLLMClient:
    """LLM client adapter that captures every call for replay.

    Wraps an inner :class:`LLMClient` and appends one
    :class:`LLMCallRecord` per :meth:`complete` call. The records are
    drained by :class:`DefaultMeetingRunner` after each meeting and
    written into the replay log so LLM-layer determinism can be
    achieved by replaying the recorded outputs rather than re-calling
    the provider (DESIGN.md §11.4).
    """

    def __init__(self, inner: LLMClient) -> None:
        self._inner = inner
        self._calls: list[LLMCallRecord] = []

    @property
    def calls(self) -> tuple[LLMCallRecord, ...]:
        return tuple(self._calls)

    def drain(self) -> tuple[LLMCallRecord, ...]:
        drained = tuple(self._calls)
        self._calls.clear()
        return drained

    async def complete(
        self,
        *,
        prompt: str,
        schema: type[BaseModel] | None,
        max_tokens: int,
        temperature: float,
        call_kind: _LLMCallKind = "meeting",
        model: str | None = None,
        agent_id: str | None = None,
    ) -> LLMResponse:
        response = await self._inner.complete(
            prompt=prompt,
            schema=schema,
            max_tokens=max_tokens,
            temperature=temperature,
            call_kind=call_kind,
            model=model,
            agent_id=agent_id,
        )
        self._calls.append(
            LLMCallRecord(
                call_kind=call_kind,
                model=response.model,
                prompt=prompt,
                response_text=response.text,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                cost_usd=response.cost_usd,
                agent_id=agent_id,
            )
        )
        return response


class DefaultMeetingRunner:
    """Default :class:`MeetingRunner` wiring (DESIGN.md §5.1, §11.4).

    Builds one :class:`MeetingParticipant` per living
    :class:`MeetingAwareAgent`, runs the underlying
    :class:`MeetingManager`, and returns the artifacts plus the
    recorded LLM-call telemetry. The :class:`_RecordingLLMClient`
    wrapper is the integration point: it sits between the manager
    and the user-supplied :class:`LLMClient` so every call lands in
    the replay record without each prompt callable having to know
    about replay.
    """

    def __init__(
        self,
        *,
        llm_client: LLMClient,
        crewmate_report_prompt: ReportPromptRenderer,
        impostor_report_prompt: ReportPromptRenderer,
        statement_prompt: StatementPromptRenderer,
        vote_prompt: VotePromptRenderer,
        config: MeetingConfig | None = None,
        prompt_versions: Mapping[str, str] = DEFAULT_PROMPT_VERSIONS,
        token_budget: int = DEFAULT_TOKEN_BUDGET,
        reporter_reasoning: bool | None = None,
        corroboration_discipline: bool | None = None,
    ) -> None:
        self._recording_client = _RecordingLLMClient(llm_client)
        self._manager = MeetingManager(
            llm_client=self._recording_client,
            crewmate_report_prompt=crewmate_report_prompt,
            impostor_report_prompt=impostor_report_prompt,
            statement_prompt=statement_prompt,
            vote_prompt=vote_prompt,
            config=config,
            # Bound here so the lever that shapes the rendered bytes and the
            # ``prompt_versions`` recorded beside them are ONE decision, taken
            # once. ``None`` leaves the manager on its own per-run env read.
            reporter_reasoning=reporter_reasoning,
            corroboration_discipline=corroboration_discipline,
        )
        self._prompt_versions = dict(prompt_versions)
        self._token_budget = token_budget

    async def run_meeting(
        self,
        *,
        meeting_id: str,
        trigger: MeetingTrigger,
        state: WorldState,
        agents: Mapping[PlayerId, AgentInterface],
    ) -> MeetingArtifacts:
        # Drop any stale captures left over from a prior run that
        # raised mid-meeting. Without this the leftover records would
        # silently attach to this meeting's replay payload and
        # contaminate llm_calls counts + cost metadata.
        self._recording_client.drain()
        participants = _build_participants(
            state=state,
            agents=agents,
            token_budget=self._token_budget,
        )
        # Dead / ejected roster (Task 10.3, audit gp-9): the orchestrator is
        # the only meeting-adjacent layer that may read world state, so it
        # derives the negative list here and the manager threads it into the
        # turn prompts as the explicit do-not-accuse line. "Who is dead" is
        # public knowledge (deaths and ejections are announced), so this
        # stays firewall-safe. Sorted for a deterministic render.
        dead_ids = tuple(
            sorted(
                player_id
                for player_id, player in state.players.items()
                if not player.alive
            )
        )
        # The game's own impostor count (Task 20.31), derived from the same
        # world state and threaded the same render-only way: the templates say
        # how many hidden impostors there are and state the win condition with
        # the right arithmetic instead of hard-coding one. It is the SEEDED
        # count, not the living one -- the roster preset's public setting, so
        # it never moves mid-game and an ejection reveals nothing through it.
        impostor_count = sum(
            1 for player in state.players.values() if player.role == "IMPOSTOR"
        )
        try:
            result = await self._manager.run(
                meeting_id=meeting_id,
                trigger=trigger,
                participants=participants,
                dead_ids=dead_ids,
                impostor_count=impostor_count,
            )
        except BaseException as exc:
            # On failure, drop the partial captures so a retry against
            # the same runner does not double-count completed prefixes.
            self._recording_client.drain()
            # Carry the side-records that fired BEFORE the abort onto the
            # exception so the orchestrator can still persist them (audit gp-2:
            # a default must be visible -- and a recovered provider parse-failure
            # accounted -- even when a LATER call aborts the meeting, where
            # record_meeting and this success-path return never run).
            _attach_meeting_side_records(
                exc,
                _MeetingSideRecords(
                    defaulted_calls=self._manager.defaulted_calls,
                    recovered_call_failures=self._manager.recovered_call_failures,
                ),
            )
            raise
        return MeetingArtifacts(
            result=result,
            llm_calls=self._recording_client.drain(),
            prompt_versions=dict(self._prompt_versions),
            # Surface the manager's side-records (reset at the start of this
            # run): fired turn / ballot defaults (audit gp-2) and provider
            # parse-failures recovered on a succeeding turn, so both reach the
            # replay accurately.
            defaulted_calls=self._manager.defaulted_calls,
            recovered_call_failures=self._manager.recovered_call_failures,
        )


def build_default_meeting_runner(
    *,
    llm_client: LLMClient | None = None,
    budget: GameBudget | None = None,
    config: MeetingConfig | None = None,
    prompt_versions: Mapping[str, str] | None = None,
    token_budget: int = DEFAULT_TOKEN_BUDGET,
) -> DefaultMeetingRunner:
    """Construct the production default meeting runner (DESIGN.md §5.1, §11.4).

    This is the single wire-up surface the public entry-points
    (:mod:`scripts.run_game`, and :mod:`scripts.run_tournament` via
    :func:`eval.balance_eval.run_balance_eval`) use to turn the meeting
    machinery Tasks 3.8-3.12 built into a runnable production default.
    It binds the four canonical ``agents/strategic/prompts`` Jinja
    callables to a :class:`DefaultMeetingRunner`.

    ``llm_client`` defaults to :func:`llm.provider.build_default_client`,
    which selects the adapter from ``AILIBI_LLM_PROVIDER`` (defaulting to
    :class:`llm.fake_provider.FakeProvider` when the env var is unset, so
    CI / headless runs still never touch the network). Setting
    ``AILIBI_LLM_PROVIDER=anthropic`` routes the public entry-points
    through :class:`llm.provider.AnthropicClient`; callers may still pass
    an explicit ``llm_client`` to bypass env selection. When ``budget`` is
    provided the client is wrapped in
    :class:`llm.budgeted_client.BudgetedLLMClient` *before* the runner's
    :class:`_RecordingLLMClient` layer, so the per-game cost cap is
    enforced at call time (pre-flight) rather than measured post-hoc
    from the replay log.

    When ``config`` is omitted the runner is wired deadline-free
    (:data:`HEADLESS_MEETING_DEADLINES`, i.e. ``turn_seconds=None`` /
    ``vote_seconds=None``): this is the production HEADLESS recording surface
    and recording must never lose a turn to a wall-clock race (audit gp-2;
    DESIGN.md §1.4, §8.3). An interactive/live caller passes an explicit
    ``MeetingConfig`` to opt back into the 30 s ``MeetingDeadlines`` default.

    Production callers construct a fresh runner + a fresh
    :class:`llm.budget.GameBudget` per game: the budget must reset
    between games and the recording client carries per-game state. Do
    not share one runner (or one budget) across a tournament.
    """

    # Provenance must match the rendered set (DESIGN.md §11.4). Resolve the
    # active set ONCE and bind both the renderers and the recorded
    # ``prompt_versions`` to it, so a runner never records one set's versions
    # while rendering another's templates -- the failure mode when the module's
    # import-time ``_ENV`` lags an in-process ``AILIBI_PROMPT_SET`` change (Task
    # 14.2; PR #203 review). With the default 9B set the renderers and versions
    # are byte-identical to pre-task HEAD, so committed replays + the version
    # assertions stay green with no re-record. An explicit ``prompt_versions``
    # mapping still wins (the caller pins its own provenance).
    active_prompt_set = resolve_prompt_set()
    renderers = build_prompt_renderers(active_prompt_set)
    resolved_versions = (
        prompt_versions
        if prompt_versions is not None
        else prompt_versions_for_set(active_prompt_set)
    )
    # The meeting-layer levers are resolved HERE, once each, beside the versions
    # they are stamped into -- the same pairing the prompt set gets. Reading one
    # per-run inside the manager instead would let a mid-game export move the
    # rendered bytes while ``resolved_versions`` stayed frozen at what
    # construction saw, which is the render-one-stamp-another failure this whole
    # block exists to prevent.
    resolved_reporter_reasoning = reporter_reasoning_enabled()
    # The source-count arm reads its decision off the versions ACTUALLY SERVED
    # rather than off the environment a second time, so the two cannot disagree
    # by construction -- including when a caller pins ``prompt_versions`` itself.
    # An env-only read would render the block under a caller-pinned default
    # stamp, which is the render-one-stamp-another failure in its exact form.
    resolved_corroboration_discipline = _arm_is_served(
        resolved_versions,
        template="vote_ballot",
        arm=_CORROBORATION_DISCIPLINE_ARM["vote_ballot"],
    )
    inner: LLMClient = llm_client if llm_client is not None else build_default_client()
    client: LLMClient = (
        BudgetedLLMClient(inner=inner, budget=budget) if budget is not None else inner
    )
    # This is the production HEADLESS recording surface, so an unspecified
    # config runs deadline-free (audit gp-2): recording must never lose a turn
    # to a wall-clock race. An explicit ``config`` is honoured unchanged, so an
    # interactive/live caller opts back into the 30 s ``MeetingDeadlines``
    # default by passing its own ``MeetingConfig``.
    resolved_config = (
        config
        if config is not None
        else MeetingConfig(deadlines=HEADLESS_MEETING_DEADLINES)
    )
    return DefaultMeetingRunner(
        llm_client=client,
        crewmate_report_prompt=renderers.crewmate_report,
        impostor_report_prompt=renderers.impostor_report,
        statement_prompt=renderers.statement,
        vote_prompt=renderers.vote,
        config=resolved_config,
        prompt_versions=resolved_versions,
        reporter_reasoning=resolved_reporter_reasoning,
        corroboration_discipline=resolved_corroboration_discipline,
        token_budget=token_budget,
    )


def _memory_rerender_hook(
    agent: MeetingAwareAgent, *, token_budget: int
) -> Callable[[Mapping[PlayerId, float]], str]:
    """Build a participant's ballot re-render hook (Task 13.5.5).

    Returns a callable taking the per-voter ``suspicion_override`` (the
    pre-vote-folded suspicion the ballot's ``suspicion_graph`` carries) and
    re-rendering the agent's standing memory with that suspicion substituted
    into the belief lines, via ``render_memory_for_meeting`` ->
    :func:`agents.memory.store.render_for_prompt`. So the ballot's belief
    lines and its ``suspicion_graph`` kwarg read ONE folded suspicion source
    (the PR #198 review inconsistency, resolved by construction).

    Replay-deterministic: the override is a pure function of the recorded
    transcript + the agent's belief snapshot, and the renderer is itself
    deterministic (no wall-clock / RNG / set-order), so a replay rebuilds an
    identical ballot prompt. The renderer is CALLED, not edited beyond the
    additive ``suspicion_override`` parameter.
    """

    def _rerender(suspicion_override: Mapping[PlayerId, float]) -> str:
        return agent.render_memory_for_meeting(
            token_budget=token_budget, suspicion_override=suspicion_override
        )

    return _rerender


def _build_participants(
    *,
    state: WorldState,
    agents: Mapping[PlayerId, AgentInterface],
    token_budget: int,
) -> tuple[MeetingParticipant, ...]:
    """Build one :class:`MeetingParticipant` per living agent.

    Every living agent referenced in ``state.players`` must be a
    :class:`MeetingAwareAgent`; the firewall (DESIGN.md §1.3) keeps
    rendered memory and suspicion graph on the agent side, so the
    orchestrator can't synthesize them without the agent's
    cooperation. Fail-loud at the boundary rather than silently
    feeding the meeting an empty rendered memory.

    ``fellow_impostor_ids`` (Task 7.12, audit gp-imp-1) is derived here
    from world-state roles — the same firewall-safe self-channel data
    :class:`observation.service.ObservationService` puts on
    ``SelfView`` (Task 7.2) and the kill policy already consumes (Task
    7.9). For an impostor participant it is the sorted ids of the OTHER
    impostors (by role, independent of alive state, so an impostor
    still knows a teammate ejected earlier in the game); it is ``()``
    for every crewmate and for a sole impostor, and never contains the
    participant's own id. The orchestrator is the right place to read
    roles: the meeting layer is engine-pure and must not re-derive them.

    ``persona`` (Task 16.9) is filled from
    :func:`orchestrator.personas.assign_personas`, a pure function of the
    game seed and the FULL fixed roster (dead seats included), so a
    player's card is stable across every meeting regardless of deaths and
    no two living players ever share one (sampling without replacement).
    It is computed with no reference to roles, keeping the assignment
    role-neutral by construction. Inert from 16.9 until Task 16.16; since
    16.16 the locked set renders the text as the guarded <voice> preamble
    block (style only — an empty persona still renders byte-unchanged, and
    the other sets' templates read nothing).
    """

    impostor_ids = tuple(
        sorted(
            player_id
            for player_id, player in state.players.items()
            if player.role == "IMPOSTOR"
        )
    )

    # Task 16.9: deterministic persona assignment -- a pure function of the
    # game seed and the FULL fixed roster (dead seats included), so a
    # player persona is stable across every meeting of a game regardless
    # of deaths, and no two living players ever share a card (sampling
    # without replacement). Rendered since 16.16 as the locked set's guarded
    # <voice> preamble block; an empty persona renders byte-unchanged (the
    # 16.3 golden proves the guard).
    persona_by_id = assign_personas(
        seed=state.seed, roster=tuple(sorted(state.players))
    )

    participants: list[MeetingParticipant] = []
    for player_id in sorted(state.players):
        player = state.players[player_id]
        if not player.alive:
            continue
        agent = agents.get(player_id)
        if agent is None:
            raise ValueError(
                f"orchestrator missing agent for living player {player_id!r}; "
                "every alive player in a meeting-enabled game must have a "
                "constructed agent"
            )
        if not isinstance(agent, MeetingAwareAgent):
            raise TypeError(
                f"agent for {player_id!r} does not implement MeetingAwareAgent; "
                "meeting-enabled HeadlessGame requires agents that expose "
                "render_memory_for_meeting(), suspicion_graph_for_meeting(), "
                "vent_witness_records_for_meeting(), "
                "sighting_records_for_meeting(), and "
                "observation_ids_for_meeting()"
            )
        # Crewmates (and a sole impostor) get ``()``; an impostor gets the
        # other impostors' ids, never its own. This is the meeting-side
        # mirror of the SelfView firewall invariant: teammate identity
        # enters only an impostor's own meeting inputs, never a crewmate's.
        fellow_impostor_ids = (
            tuple(pid for pid in impostor_ids if pid != player_id)
            if player.role == "IMPOSTOR"
            else ()
        )
        # Task 13.5.5 (unconditional since Task 14.9 — the adopted lever is the
        # default substrate): the open-tick render is ALWAYS produced (it is
        # the frozen value every TURN prompt reads), and a re-render hook is
        # attached that the manager calls ONLY for the ballot, with the
        # per-voter pre-vote-folded suspicion, so the ballot's belief lines
        # match the ``suspicion_graph`` it consumes.
        rerender_memory = _memory_rerender_hook(agent, token_budget=token_budget)
        participants.append(
            MeetingParticipant(
                agent_id=player_id,
                role=player.role,
                rendered_memory=agent.render_memory_for_meeting(
                    token_budget=token_budget
                ),
                suspicion_graph=agent.suspicion_graph_for_meeting(),
                fellow_impostor_ids=fellow_impostor_ids,
                rerender_memory=rerender_memory,
                # Task 15.4: the typed grounding channel -- pulled per living
                # agent exactly like ``suspicion_graph``, a meeting-open
                # snapshot of the agent's OWN witnessed-vent episodic records.
                vent_witness_records=agent.vent_witness_records_for_meeting(),
                # Task 16.7: the vent channel's sighting sibling -- the
                # grounded-vouch input, same meeting-open snapshot discipline.
                sighting_records=agent.sighting_records_for_meeting(),
                # The movement-claim lever's grounding channel, same snapshot
                # discipline. An agent without the optional capability grounds
                # nothing, which is the lever's own OFF behaviour.
                move_witness_records=(
                    agent.move_witness_records_for_meeting()
                    if isinstance(agent, MoveWitnessAgent)
                    else ()
                ),
                # Task 16.5 (C8): the voter's OWN stable observation-id set --
                # the valid-citation universe the manager validates
                # ``primary_reason_observation_id`` against, same self-channel
                # snapshot discipline. Enforcement-free until 16.6.
                observation_ids=agent.observation_ids_for_meeting(),
                # Task 16.9's persona-text fill; the locked set's templates
                # render it since 16.16 (the guarded <voice> preamble block).
                persona=persona_by_id[player_id].text,
                # The reporter-voice lever's self-channel, same snapshot
                # discipline. An agent without the optional capability
                # discovered nothing, which is the lever's own OFF behaviour.
                body_discovery_records=(
                    agent.body_discovery_records_for_meeting()
                    if isinstance(agent, BodyDiscoveryAgent)
                    else ()
                ),
            )
        )
    return tuple(participants)


# ---------------------------------------------------------------------------
# Meeting outcome → engine-owned state application.
# ---------------------------------------------------------------------------


def _validate_runner_result(
    *,
    result: MeetingResult,
    expected_meeting_id: str,
    expected_trigger: MeetingTrigger,
) -> None:
    """Reject a :class:`MeetingResult` whose trigger fields drift from the engine.

    The orchestrator builds the canonical :class:`MeetingTrigger` from
    the :class:`MeetingTriggeredEvent` the engine emitted; the runner
    receives it verbatim. The returned :class:`MeetingResult` echoes
    back ``meeting_id`` / ``triggered_by`` / ``trigger_tick`` and the
    orchestrator persists those into the replay record. A buggy or
    custom runner could swap any of those fields, causing the replay
    log to contradict the engine event that actually opened the
    meeting — which silently breaks downstream provenance for
    eval / replay tooling. Fail loud here instead.
    """

    if result.meeting_id != expected_meeting_id:
        raise ValueError(
            "MeetingRunner returned a MeetingResult whose meeting_id "
            f"{result.meeting_id!r} does not match the dispatched "
            f"meeting_id {expected_meeting_id!r}; this is an "
            "orchestrator-runner wiring bug"
        )
    if result.triggered_by != expected_trigger.triggered_by:
        raise ValueError(
            "MeetingRunner returned a MeetingResult whose triggered_by "
            f"{result.triggered_by!r} does not match the engine-emitted "
            f"trigger {expected_trigger.triggered_by!r}"
        )
    if result.trigger_tick != expected_trigger.trigger_tick:
        raise ValueError(
            "MeetingRunner returned a MeetingResult whose trigger_tick "
            f"{result.trigger_tick} does not match the engine-emitted "
            f"trigger_tick {expected_trigger.trigger_tick}"
        )


def apply_meeting_result(
    state: WorldState,
    result: MeetingResult,
    *,
    game_map: Map,
    triggering_body_id: BodyId | None = None,
    rng_hash_policy: RngStateHashPolicy = RngStateHashPolicy.FULL,
) -> tuple[WorldState, list[EngineEvent]]:
    """Apply a :class:`MeetingResult` to engine-owned state (DESIGN.md §3.1, §5.1).

    ``rng_hash_policy`` (Task 15.8.1) selects the meeting-tick rng-state
    serialization, mirroring :func:`engine.tick.advance_tick`. It DEFAULTS to
    :attr:`RngStateHashPolicy.FULL` (byte-identical to the pre-15.8.1 apply, so
    every recorded / reconstructed meeting keeps its committed ``state_hash``);
    the opt-in :attr:`RngStateHashPolicy.TRAINING_FAST` skips the ``json.dumps``
    snapshot for non-recorded training rollouts. The draw is unchanged, so the
    resumed state is trajectory-identical under either policy.

    Lives in the orchestrator (not ``engine/``) because applying a
    meeting outcome is an orchestration concern: the engine remains a
    pure ``(state, actions) -> (state', events)`` function and the
    meeting manager remains engine-pure. The orchestrator is the only
    module allowed to mutate engine-owned state outside an
    ``advance_tick`` call.

    The returned state is ready to be fed back into the next
    :func:`advance_tick`: phase is ``PLAY`` (unless the ejection
    triggered a win), tick is incremented by one (per DESIGN.md §3.1
    "returns control to tick t+1"), and the rng is advanced one step
    so the rng cursor remains in lockstep with the tick counter (a
    successful normal tick advances both, so the meeting tick must do
    the same).

    For an ``EJECTED`` outcome the ejected player's ``alive`` flag is
    cleared, their ``last_action`` is reset to ``None`` so the next
    tick's task-progress pass does not try to continue their task,
    their cooldown entry is removed, and their incomplete tasks are
    resolved per the map's dead-crewmate-task rule (DESIGN.md §3.5;
    same semantics as a kill): dropped under the default ``drop`` and
    re-keyed to living crewmates under ``redistribute``.

    Win conditions are re-evaluated after the ejection. An ejection
    that reaches impostor parity, sabotage timeout, or completes the
    crew task pool emits a :class:`GameOverEvent` and the returned
    state has ``phase == "GAME_OVER"``.

    The cooldown / sabotage / emergency-uses counters are unchanged
    during the meeting tick because DESIGN.md §5.1 freezes engine
    state during a meeting ("kill cooldown paused"). The next normal
    tick will decrement them via the standard step-2 of
    :func:`advance_tick`.
    """

    if state.phase != "MEETING":
        raise ValueError(
            f"apply_meeting_result requires state.phase=='MEETING', got {state.phase!r}"
        )

    events: list[EngineEvent] = []
    working = state

    if result.outcome == "EJECTED":
        ejected_id = result.ejected_player_id
        if ejected_id is None:
            raise ValueError(
                "MeetingResult outcome=='EJECTED' must carry a non-None "
                "ejected_player_id (enforced by MeetingResult validator; this "
                "branch is defense-in-depth)"
            )
        if ejected_id not in working.players:
            raise ValueError(
                f"MeetingResult.ejected_player_id={ejected_id!r} not in state.players"
            )
        if not working.players[ejected_id].alive:
            raise ValueError(
                f"cannot eject already-dead player {ejected_id!r}; the meeting "
                "should never have nominated a dead participant"
            )
        players = dict(working.players)
        ejected = players[ejected_id]
        players[ejected_id] = replace(ejected, alive=False, last_action=None)
        # Dead-crewmate task rule: DESIGN.md §3.5. Mirror
        # ``engine/tick.py::_apply_kill``: drop the ejected player's
        # incomplete tasks so the crew win check counts only alive-
        # owned tasks; completed tasks remain so they still count
        # toward ``crew_tasks_done``.
        surviving_tasks = {
            task_id: task
            for task_id, task in working.tasks.items()
            if not (task.owner == ejected_id and not task.completed)
        }
        # Under ``redistribute`` the dropped incomplete instances are re-keyed to
        # living crewmates instead of vanishing (DESIGN.md §3.5; map-flag-gated).
        # The default ``drop`` leaves ``surviving_tasks`` byte-identical.
        if game_map.dead_task_rule == "redistribute":
            tasks = redistribute_dead_tasks(
                surviving_tasks=surviving_tasks,
                pre_death_tasks=working.tasks,
                players=players,
                victim=ejected_id,
            )
        else:
            tasks = surviving_tasks
        cooldowns = dict(working.cooldowns)
        cooldowns.pop(ejected_id, None)
        working = replace(working, players=players, tasks=tasks, cooldowns=cooldowns)

    # Consume the corpse that triggered a body-report meeting. The
    # engine's visibility layer already hides bodies whose
    # ``discovered_by`` is set, so default tactical agents cannot
    # re-report the body via observation. But ``engine.rules.resolve_report``
    # does not reject already-discovered bodies, so a hardcoded /
    # adversarial intent with the same body_id would otherwise
    # repeatedly re-trigger meetings after gameplay resumes. Drop
    # the body here so the trigger surface is the same as the
    # observation surface.
    if triggering_body_id is not None and triggering_body_id in working.bodies:
        bodies = dict(working.bodies)
        del bodies[triggering_body_id]
        working = replace(working, bodies=bodies)

    # Re-evaluate win conditions on the post-ejection (or
    # post-skip) world. A skipped meeting cannot newly satisfy a win
    # condition by itself, but the check is unconditional so a future
    # mid-meeting state mutation cannot silently bypass the gate.
    win_result = resolve_win_conditions(working)
    if win_result is not None:
        game_over_state = replace(working, phase="GAME_OVER")
        events.append(
            GameOverEvent(
                type="GameOver",
                tick=state.tick,
                winner=win_result.winner,
                reason=win_result.reason,
            )
        )
        return game_over_state, events

    # Advance the rng cursor one step so the per-tick rng-state
    # transition mirrors the end-of-tick advance in
    # :func:`advance_tick`. Without this step the rng cursor would
    # stall across the meeting boundary and a replay that ran with a
    # different meeting outcome could re-sync rng state by accident.
    # The draw is policy-invariant (Task 15.8.1); only the snapshot encoding
    # of the advanced state differs, and FULL is byte-identical to before.
    rng = EngineRng.from_state(working.rng_state)
    _, next_rng_state = rng.randint(0, 2**31 - 1, hash_policy=rng_hash_policy)
    next_state = replace(
        working,
        phase="PLAY",
        tick=working.tick + 1,
        rng_state=next_rng_state,
    )
    return next_state, events


# ---------------------------------------------------------------------------
# Headless game loop.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class HeadlessGameResult:
    """Outcome bundle returned by :meth:`HeadlessGame.run`.

    ``outcome`` is one of:

    - ``CREWMATES`` / ``IMPOSTORS``: an engine ``GameOverEvent`` fired
      and named the winner. ``final_state.phase`` is ``GAME_OVER``.
    - ``MEETING_PHASE_REACHED``: a ``ReportBody`` or ``EmergencyMeeting``
      intent transitioned the engine to ``MEETING`` and no
      :class:`MeetingRunner` was configured to resume the game. The
      orchestrator pauses here without mutating state. ``final_state``
      has ``phase == "MEETING"``. This is the engine-only opt-out for
      Phase 2 byte-identity tests; production paths always pass a
      runner (see :func:`build_default_meeting_runner`) and never reach
      this outcome.
    - ``TICK_BUDGET_REACHED``: :class:`TickScheduler` capped the game
      before it ended naturally. ``final_state.phase`` is ``PLAY``.
      The partial replay is still written to ``replay_path``.
    """

    final_state: WorldState
    outcome: Outcome
    replay_path: Path


@dataclass(frozen=True)
class UnrecordedTickStep:
    """One ``advance_tick`` step captured live in no-replay mode (Task 15.8.1).

    The no-replay training path writes NO replay, so there is nothing on disk to
    reconstruct an episode from. Instead the game surfaces each tick's submitted
    actions, the post-``advance_tick`` engine state, and the typed events the
    training env turns into an :class:`~training.rollout.EpisodeRollout` WITHOUT a
    reconstruction re-walk. ``state`` is the engine truth after the tick — the
    same object the recorder would have hashed — so the descriptors and reward
    channel read identical scalars.
    """

    input_tick: int
    actions: tuple[Action, ...]
    state: WorldState
    events: tuple[EngineEvent, ...]


@dataclass(frozen=True)
class UnrecordedMeetingStep:
    """One applied meeting captured live in no-replay mode (Task 15.8.1).

    Mirrors :class:`UnrecordedTickStep` for the meeting boundary: the resolved
    :class:`~meetings.schemas.MeetingResult`, the corpse that triggered a body
    report (``None`` for an emergency), the post-:func:`apply_meeting_result`
    state (resumed at ``trigger_tick + 1``), and the post-meeting events.
    """

    trigger_tick: int
    result: MeetingResult
    triggering_body_id: BodyId | None
    state: WorldState
    post_events: tuple[EngineEvent, ...]


class _EpisodeTraceCollector:
    """Accumulates the live trajectory of a no-replay game (Task 15.8.1).

    Populated ONLY on the no-replay path (:meth:`HeadlessGame.run_unrecorded`);
    the recorded path (:meth:`HeadlessGame.run`) passes ``None`` so its byte
    output is untouched. Holds engine / orchestrator types only — the training
    env owns turning it into a typed rollout, keeping ``orchestrator/`` free of
    any ``training/`` dependency.
    """

    def __init__(self) -> None:
        self.tick_steps: list[UnrecordedTickStep] = []
        self.meeting_steps: list[UnrecordedMeetingStep] = []

    def record_tick(
        self,
        *,
        input_tick: int,
        actions: Sequence[Action],
        state: WorldState,
        events: Sequence[EngineEvent],
    ) -> None:
        self.tick_steps.append(
            UnrecordedTickStep(
                input_tick=input_tick,
                actions=tuple(actions),
                state=state,
                events=tuple(events),
            )
        )

    def record_meeting(
        self,
        *,
        trigger_tick: int,
        result: MeetingResult,
        triggering_body_id: BodyId | None,
        state: WorldState,
        post_events: Sequence[EngineEvent],
    ) -> None:
        self.meeting_steps.append(
            UnrecordedMeetingStep(
                trigger_tick=trigger_tick,
                result=result,
                triggering_body_id=triggering_body_id,
                state=state,
                post_events=tuple(post_events),
            )
        )


@dataclass(frozen=True)
class UnrecordedGameResult:
    """Outcome bundle returned by :meth:`HeadlessGame.run_unrecorded` (Task 15.8.1).

    The no-replay counterpart of :class:`HeadlessGameResult`: it carries the same
    ``final_state`` / ``outcome`` but NO ``replay_path`` (nothing was written) and
    adds the live-captured trajectory — the seeded ``initial_state`` plus the tick
    and meeting steps — that the training env assembles into a typed
    :class:`~training.rollout.EpisodeRollout` without a replay file.
    """

    final_state: WorldState
    outcome: Outcome
    initial_state: WorldState
    tick_steps: tuple[UnrecordedTickStep, ...]
    meeting_steps: tuple[UnrecordedMeetingStep, ...]


class HeadlessGame:
    """Run one deterministic headless game from a seed."""

    def __init__(
        self,
        *,
        seed: int,
        game_map: Map,
        agent_factory: AgentFactory,
        replay_path: Path | None,
        audit_log_path: Path | None = None,
        num_players: int = DEFAULT_NUM_PLAYERS,
        num_impostors: int = DEFAULT_NUM_IMPOSTORS,
        tasks_per_crewmate: int = DEFAULT_TASKS_PER_CREWMATE,
        scheduler: TickScheduler | None = None,
        meeting_runner: MeetingRunner | None = None,
        force: bool = False,
        tactical_policy_stamp: TacticalPolicyStamp | None = None,
        crew_tactical_policy_stamp: CrewTacticalPolicyStamp | None = None,
        rng_hash_policy: RngStateHashPolicy = RngStateHashPolicy.FULL,
        initial_state: WorldState | None = None,
    ) -> None:
        # No-replay training mode (Task 15.8.1): ``replay_path=None`` runs the
        # game through :meth:`run_unrecorded` writing NOTHING to disk (no
        # ReplayLog, no audit file), and is the ONLY construction that accepts the
        # opt-in :attr:`RngStateHashPolicy.TRAINING_FAST` fast path. The two loud
        # guards below keep the fast bytes off every committed / attributable
        # surface (AGENTS.md "no silent fallbacks"):
        #   1. the fast path serializes ``rng_state`` with a codec that is NOT the
        #      committed JSON encoding, so a replay-WRITING construction (any
        #      ``replay_path``) must refuse it rather than silently record
        #      un-verifiable bytes;
        #   2. a provenance stamp (Task 15.9) exists to attribute a RECORDED game,
        #      so a no-replay construction that receives one is a caller bug — there
        #      is nothing to stamp.
        records_replay = replay_path is not None
        if rng_hash_policy is not RngStateHashPolicy.FULL and records_replay:
            raise ValueError(
                "the training-only RNG hash fast path "
                f"({rng_hash_policy!r}) is refused by a replay-writing "
                "HeadlessGame: it serializes rng_state with a non-committed codec, "
                "so it must run with replay_path=None (no-replay training mode). "
                "Pass replay_path=None to opt into the fast path, or keep "
                "RngStateHashPolicy.FULL to record."
            )
        if not records_replay and tactical_policy_stamp is not None:
            raise ValueError(
                "a no-replay HeadlessGame (replay_path=None) writes no game_over "
                "record, so a tactical_policy_stamp has nothing to attribute; drop "
                "the stamp, or pass a replay_path to record and stamp the game."
            )
        if not records_replay and crew_tactical_policy_stamp is not None:
            raise ValueError(
                "a no-replay HeadlessGame (replay_path=None) writes no game_over "
                "record, so a crew_tactical_policy_stamp has nothing to attribute; "
                "drop the stamp, or pass a replay_path to record and stamp the game."
            )
        # The scenario-staging injection seam (Task 18.23): an explicit
        # ``initial_state`` bypasses ``seed_initial_state`` on the NO-REPLAY
        # training path only. Default ``None`` = absent = the seeded default,
        # byte-identical to today's path on every entry point. The guards below
        # fail loud (AGENTS.md "no silent fallbacks") on every construction that
        # could silently mis-attribute or mis-record an injected episode:
        #   1. a replay-WRITING construction is refused — replay reconstruction
        #      re-seeds from the seed and verifies every recorded state_hash
        #      against that walk, a chain an injected mid-game episode does not
        #      have, so a recorded injected game would be unreconstructable;
        #   2. the injected state must actually be runnable by ``_run_loop``
        #      (``phase == "PLAY"``) on this game's map;
        #   3. the seed / roster constructor parameters ride every consumer
        #      (``_game_id``, the training env's episode record), so a state
        #      whose own ``seed`` / roster disagrees with them is a caller bug,
        #      never silently re-labeled.
        if initial_state is not None:
            if records_replay:
                raise ValueError(
                    "an injected initial_state rides the no-replay training path "
                    "only (Task 18.23): replay reconstruction verifies recorded "
                    "state hashes an injected episode does not have. Pass "
                    "replay_path=None to inject, or drop initial_state to record "
                    "the seeded default."
                )
            if initial_state.phase != "PLAY":
                raise ValueError(
                    "an injected initial_state must be a runnable PLAY-phase "
                    f"state, got phase={initial_state.phase!r}"
                )
            if initial_state.map != game_map.id:
                raise ValueError(
                    f"injected initial_state is for map {initial_state.map!r} but "
                    f"this game runs {game_map.id!r}"
                )
            if initial_state.seed != seed:
                raise ValueError(
                    f"injected initial_state carries seed {initial_state.seed} but "
                    f"the game was constructed with seed {seed}; the constructor "
                    "seed keys every consumer (game id, episode records), so the "
                    "two must agree"
                )
            if len(initial_state.players) != num_players:
                raise ValueError(
                    f"injected initial_state has {len(initial_state.players)} "
                    f"players but the game was constructed with "
                    f"num_players={num_players}"
                )
            state_impostors = sum(
                1
                for player in initial_state.players.values()
                if player.role == "IMPOSTOR"
            )
            if state_impostors != num_impostors:
                raise ValueError(
                    f"injected initial_state has {state_impostors} impostors but "
                    f"the game was constructed with num_impostors={num_impostors}"
                )
        self._initial_state = initial_state
        self._seed = seed
        self._game_map = game_map
        self._agent_factory = agent_factory
        self._replay_path = replay_path
        self._records_replay = records_replay
        # The training-only RNG hash policy (Task 15.8.1). FULL (default) keeps
        # every recorded/committed path byte-identical; TRAINING_FAST is only
        # reachable in no-replay mode (guarded above) and skips the per-tick
        # json.dumps snapshot of the Mersenne state.
        self._rng_hash_policy = rng_hash_policy
        # The tactical-policy provenance stamp (Task 15.9): the PRODUCTION
        # injection seam. Every recorder (run_tournament, the 15.12 corpus
        # wrapper, Wave-2 champion recordings) reaches replay-writing ONLY through
        # this constructor, so a learned-policy recording can be stamped without a
        # later out-of-scope edit. Default ``None`` = absent = scripted FSM
        # default, byte-identical to today's path; the stamp is threaded straight
        # into the per-game ``ReplayLog`` (the writer) in :meth:`run`.
        self._tactical_policy_stamp = tactical_policy_stamp
        # The CREW-side provenance stamp (Task 18.7): the mirror of the tactical
        # stamp above, threaded straight into the per-game ``ReplayLog`` in
        # :meth:`run`. Default ``None`` = absent = scripted crew default,
        # byte-identical to today's path.
        self._crew_tactical_policy_stamp = crew_tactical_policy_stamp
        # Passed through to ReplayLog: force=True truncates a pre-existing
        # replay file at construction (just before this game writes it),
        # force=False (default) makes a re-run against an existing path fail
        # loud (DESIGN.md §11.4; Task 4.16). run() keeps its existing
        # signature; the flag rides the constructor.
        self._force = force
        # No-replay mode writes nothing, so the observation audit log (which the
        # ObservationService writes a row to per packet) is routed to the null
        # device: the service requires a Path, and os.devnull discards every write
        # so the "nothing on disk" contract holds without widening the
        # out-of-scope service surface. An EXPLICIT audit_log_path contradicts
        # that contract, so it is refused rather than silently honoured (a
        # no-replay run must never leave an audit JSONL behind) -- AGENTS.md "no
        # silent fallbacks".
        if not records_replay:
            if audit_log_path is not None:
                raise ValueError(
                    "a no-replay HeadlessGame (replay_path=None) writes NOTHING to "
                    "disk, so an explicit audit_log_path is refused; omit it (the "
                    "audit is routed to the null device) or pass a replay_path to "
                    "record."
                )
            self._audit_log_path = Path(os.devnull)
        else:
            assert replay_path is not None  # records_replay == replay_path is not None
            self._audit_log_path = (
                audit_log_path
                if audit_log_path is not None
                else replay_path.parent / f"{replay_path.stem}.audit.jsonl"
            )
        self._num_players = num_players
        self._num_impostors = num_impostors
        self._tasks_per_crewmate = tasks_per_crewmate
        self._scheduler = (
            scheduler
            if scheduler is not None
            else TickScheduler(max_ticks=DEFAULT_MAX_TICKS)
        )
        self._public_map = public_map_from_engine_map(game_map)
        self._meeting_runner = meeting_runner

    @property
    def public_map(self) -> PublicMapView:
        return self._public_map

    @property
    def replay_path(self) -> Path | None:
        """The replay file this game writes, or ``None`` in no-replay mode (15.8.1)."""

        return self._replay_path

    def run(self) -> HeadlessGameResult:
        """Run the headless tick loop until terminate, meeting, or tick budget.

        Each iteration: build observations for every alive agent,
        dispatch them, collect :class:`ActionIntent`s, translate to
        engine actions, advance the engine one tick, and append to
        the replay log. When the engine transitions to ``MEETING``
        and a :class:`MeetingRunner` is configured, dispatch to the
        runner, persist the meeting artifacts in the replay log,
        apply the outcome to engine-owned state through
        :func:`apply_meeting_result`, and continue. When no runner
        is configured the loop returns ``MEETING_PHASE_REACHED`` as
        in Phase 2.

        This is the RECORDING path and requires a ``replay_path`` (Task
        15.8.1); a no-replay training game (``replay_path=None``) is run through
        :meth:`run_unrecorded` instead — fail loud rather than silently record
        under a mismatched construction.
        """

        replay_path = self._replay_path
        if replay_path is None:
            raise ValueError(
                "HeadlessGame.run() records a replay and requires a replay_path; "
                "a no-replay training game (replay_path=None) must use "
                "run_unrecorded()."
            )

        state = seed_initial_state(
            seed=self._seed,
            game_map=self._game_map,
            num_players=self._num_players,
            num_impostors=self._num_impostors,
            tasks_per_crewmate=self._tasks_per_crewmate,
        )
        observation_service = ObservationService(
            game_map=self._game_map,
            audit_log_path=self._audit_log_path,
        )
        replay = ReplayLog(
            replay_path,
            game_id=self._game_id(),
            force=self._force,
            tactical_policy_stamp=self._tactical_policy_stamp,
            crew_tactical_policy_stamp=self._crew_tactical_policy_stamp,
        )
        agents = self._build_agents(state.players)

        # Close the per-game replay + audit handles deterministically at every
        # loop exit (game over, tick budget, meeting pause, or exception). Both
        # logs flush each row as it is written, so this only releases the file
        # descriptors (Task 5.9 write-cadence pass); the recorded bytes — and
        # therefore the determinism contract — are unchanged.
        try:
            final_state, outcome = self._run_loop(
                state=state,
                observation_service=observation_service,
                replay=replay,
                agents=agents,
                trace=None,
            )
        finally:
            replay.close()
            observation_service.close()
        return HeadlessGameResult(
            final_state=final_state, outcome=outcome, replay_path=replay_path
        )

    def run_unrecorded(self) -> UnrecordedGameResult:
        """Run a no-replay training game, writing NOTHING to disk (Task 15.8.1).

        The training-only counterpart of :meth:`run`: same engine, same
        observation firewall, same meeting manager, but no :class:`ReplayLog` is
        constructed and the observation audit is routed to the null device, so
        the whole run leaves nothing on disk. This is the ONLY entry point that
        honours the opt-in :attr:`RngStateHashPolicy.TRAINING_FAST` fast path (the
        constructor already refused a fast policy on any replay-writing
        construction). Because nothing is recorded, the run surfaces its live
        trajectory in an :class:`UnrecordedGameResult` — the seeded initial state
        plus every tick / meeting step — that the training env turns into a typed
        rollout WITHOUT a reconstruction re-walk. Requires ``replay_path=None``;
        a recording construction uses :meth:`run`.
        """

        if self._records_replay:
            raise ValueError(
                "HeadlessGame.run_unrecorded() runs the no-replay training mode "
                "and requires replay_path=None; a recording game uses run()."
            )

        # The Task 18.23 injection seam: an explicit initial_state (validated at
        # construction) replaces the seeded default. With the seam unused this
        # branch is the pre-18.23 seeding, byte-identical.
        if self._initial_state is not None:
            state = self._initial_state
        else:
            state = seed_initial_state(
                seed=self._seed,
                game_map=self._game_map,
                num_players=self._num_players,
                num_impostors=self._num_impostors,
                tasks_per_crewmate=self._tasks_per_crewmate,
            )
        initial_state = state
        observation_service = ObservationService(
            game_map=self._game_map,
            audit_log_path=self._audit_log_path,
        )
        agents = self._build_agents(state.players)
        trace = _EpisodeTraceCollector()
        try:
            final_state, outcome = self._run_loop(
                state=state,
                observation_service=observation_service,
                replay=None,
                agents=agents,
                trace=trace,
            )
        finally:
            observation_service.close()
        return UnrecordedGameResult(
            final_state=final_state,
            outcome=outcome,
            initial_state=initial_state,
            tick_steps=tuple(trace.tick_steps),
            meeting_steps=tuple(trace.meeting_steps),
        )

    def _run_loop(
        self,
        *,
        state: WorldState,
        observation_service: ObservationService,
        replay: ReplayLog | None,
        agents: dict[PlayerId, AgentInterface],
        trace: _EpisodeTraceCollector | None,
    ) -> tuple[WorldState, Outcome]:
        """Drive the tick loop until terminate, meeting, or tick budget.

        Shared by the recorded path (:meth:`run`: ``replay`` set, ``trace``
        ``None``) and the no-replay training path (:meth:`run_unrecorded`:
        ``replay`` ``None``, ``trace`` set). Every ``replay`` write is guarded so
        the no-replay run persists nothing and skips the per-tick state-hash
        entirely (Task 15.8.1); ``trace`` captures the live trajectory the
        training env reconstructs from. The recorded path is byte-identical to
        before: with ``replay`` set and ``trace`` ``None`` and the default FULL
        rng policy, every recorded row is unchanged. Returns
        ``(final_state, outcome)``; the caller wraps it in the appropriate result.
        """

        last_events: tuple[EngineEvent, ...] = ()
        meeting_counter = 0
        while state.phase != "GAME_OVER":
            if not self._scheduler.should_continue(state.tick):
                return state, "TICK_BUDGET_REACHED"

            packets = self._build_packets(
                state=state,
                observation_service=observation_service,
                last_events=last_events,
            )
            intents = self._collect_intents(packets=packets, agents=agents)
            actions = list(translate_action_intents_for_tick(intents))
            input_tick = state.tick
            state, events = advance_tick(
                state,
                actions,
                game_map=self._game_map,
                rng_hash_policy=self._rng_hash_policy,
            )
            last_events = tuple(events)
            if replay is not None:
                replay.record_tick(input_tick, actions, state, events=events)
            if trace is not None:
                trace.record_tick(
                    input_tick=input_tick,
                    actions=actions,
                    state=state,
                    events=events,
                )

            if state.phase == "MEETING":
                if self._meeting_runner is None:
                    # Engine-only opt-out for Phase 2 byte-identity tests;
                    # production paths always pass a runner. The public
                    # entry-points (scripts/run_*.py, eval/balance_eval.py)
                    # build a DefaultMeetingRunner via
                    # build_default_meeting_runner and never reach this
                    # branch; only callers that explicitly pass
                    # meeting_runner=None (engine-only replay) land here.
                    return state, "MEETING_PHASE_REACHED"
                pre_meeting_events = last_events
                state, post_events = self._run_and_apply_meeting(
                    state=state,
                    events=pre_meeting_events,
                    agents=agents,
                    replay=replay,
                    trace=trace,
                    meeting_index=meeting_counter,
                )
                meeting_counter += 1
                # Preserve the events the engine emitted on the
                # meeting-trigger tick (e.g. a ``KilledEvent`` that
                # landed in the same action queue as the report).
                # ``ObservationService._observed_actions_for_agent``
                # reads ``engine_events`` to surface kills and vent
                # uses as observed actions; dropping the pre-meeting
                # events here would silently regress agent perception
                # on the resume tick.
                last_events = pre_meeting_events + tuple(post_events)

        # The engine fired a GameOverEvent (the while loop only exits
        # GAME_OVER via that event). Persist the decisive outcome as the
        # final replay row so win-rate is recoverable from any replay log,
        # including a partial tournament that crashed mid-run (Task 3.19
        # finding 3).
        game_over_event = self._game_over_event(last_events)
        if replay is not None:
            replay.record_game_end(
                winner=game_over_event.winner,
                reason=game_over_event.reason,
                tick=game_over_event.tick,
            )
        return state, game_over_event.winner

    def _run_and_apply_meeting(
        self,
        *,
        state: WorldState,
        events: Sequence[EngineEvent],
        agents: Mapping[PlayerId, AgentInterface],
        replay: ReplayLog | None,
        trace: _EpisodeTraceCollector | None,
        meeting_index: int,
    ) -> tuple[WorldState, list[EngineEvent]]:
        if self._meeting_runner is None:
            raise RuntimeError(
                "_run_and_apply_meeting called without a configured meeting runner"
            )
        trigger, triggering_body_id, trigger_kind = _build_meeting_trigger(
            state=state, events=events
        )
        meeting_id = f"{self._game_id()}:meeting-{meeting_index}"
        try:
            artifacts = _drive_async(
                self._meeting_runner.run_meeting(
                    meeting_id=meeting_id,
                    trigger=trigger,
                    state=state,
                    agents=agents,
                )
            )
        except BaseException as exc:
            # A meeting that aborts because a structured-output response
            # failed schema validation carries the rejected call's cost +
            # partial response on the propagating ValidationError (see
            # llm.provider.extract_parse_failure). Persist it before the
            # crash propagates so per-meeting cost is auditable for the
            # meeting that broke the run (Task 3.19 finding 2). The meeting
            # still aborts — the caller cannot proceed without a valid
            # response — so the exception is re-raised unchanged. On the
            # no-replay path (``replay`` None) there is nothing to persist, so
            # the guarded writes are skipped and the exception still propagates.
            failure = extract_parse_failure(exc)
            if failure is not None and replay is not None:
                replay.record_failed_call(
                    meeting_id=meeting_id,
                    tick=trigger.trigger_tick,
                    model=failure.model,
                    prompt_length=failure.prompt_length,
                    raw_response=failure.raw_response,
                    input_tokens=failure.input_tokens,
                    output_tokens=failure.output_tokens,
                    cost_usd=failure.cost_usd,
                    error_type=failure.error_type,
                    error_message=failure.error_message,
                )
            # Persist the side-records that fired BEFORE this abort (audit
            # gp-2): record_meeting never runs for an aborted meeting, so
            # without this the earlier default / recovered failure would vanish.
            # The DefaultMeetingRunner attached them to the propagating exception.
            side_records = _extract_meeting_side_records(exc)
            _record_deadline_defaults(
                replay=replay,
                meeting_id=meeting_id,
                tick=trigger.trigger_tick,
                defaulted_calls=side_records.defaulted_calls,
            )
            _record_recovered_failures(
                replay=replay,
                meeting_id=meeting_id,
                tick=trigger.trigger_tick,
                failures=side_records.recovered_call_failures,
            )
            raise
        _validate_runner_result(
            result=artifacts.result,
            expected_meeting_id=meeting_id,
            expected_trigger=trigger,
        )
        # The before/after state hashes are RECORDING artifacts only, so the
        # no-replay path (``replay`` None) skips them entirely (Task 15.8.1) —
        # the whole point of the fast training mode is to not serialize state.
        # ``state`` is frozen and ``apply_meeting_result`` returns a new state,
        # so computing ``state_hash_before`` after the apply is byte-equivalent
        # to before it (kept here to guard both computations under one branch).
        next_state, post_events = apply_meeting_result(
            state,
            artifacts.result,
            game_map=self._game_map,
            triggering_body_id=triggering_body_id,
            rng_hash_policy=self._rng_hash_policy,
        )
        # Task 10.11 self-check (audit-2026-06-13-1816 B-B-1): an EMERGENCY
        # meeting has NO kill scene by design (§5.2 PHASE 1) -- the caller
        # pressed the button on suspicion, no body was reported. The 10.8
        # check ("engine body_id is None") was TRUE yet MASKED a transcript
        # fabrication: every emergency opening re-narrated a stale corpse as a
        # fresh `found_body`. Fail loud on any emergency opening that still
        # carries one, so a model that ignores the v7 prompt is caught at the
        # source rather than silently anchoring votes on a non-existent body.
        _assert_no_emergency_opening_body(
            trigger_kind=trigger_kind, result=artifacts.result
        )
        if replay is not None:
            replay.record_meeting(
                meeting_id=meeting_id,
                result=artifacts.result,
                llm_calls=artifacts.llm_calls,
                prompt_versions=artifacts.prompt_versions,
                state_hash_before=_state_hash(state),
                state_hash_after=_state_hash(next_state),
            )
        # Persist the meeting's side-records: a visible ``deadline_default``
        # marker per fired default (audit gp-2), and the recovered provider
        # parse-failures whose burned spend is absent from llm_calls.
        _record_deadline_defaults(
            replay=replay,
            meeting_id=meeting_id,
            tick=trigger.trigger_tick,
            defaulted_calls=artifacts.defaulted_calls,
        )
        _record_recovered_failures(
            replay=replay,
            meeting_id=meeting_id,
            tick=trigger.trigger_tick,
            failures=artifacts.recovered_call_failures,
        )
        # Surface the applied meeting to the no-replay trace (Task 15.8.1) so the
        # training env can rebuild the episode's meeting records + post-meeting
        # frames without a replay file.
        if trace is not None:
            trace.record_meeting(
                trigger_tick=trigger.trigger_tick,
                result=artifacts.result,
                triggering_body_id=triggering_body_id,
                state=next_state,
                post_events=post_events,
            )
        # Post-meeting belief fold (Task 9.8, DESIGN.md §4.4 step 4; audit
        # gp-1 recall): write the meeting's public evidence into each living
        # agent's PERSISTENT belief state so suspicion accumulates across
        # meetings and decays between them. Runs AFTER apply_meeting_result
        # (the ejected player's beliefs are never read again) and OUTSIDE it
        # (the replay re-walk re-applies recorded results through that pure
        # function with no agents in hand -- engine bytes stay untouched).
        _absorb_meeting_beliefs(
            result=artifacts.result,
            state=next_state,
            agents=agents,
            trigger_kind=trigger_kind,
        )
        # Meeting-end pacing notification (Task 10.8). Runs AFTER the belief
        # fold so the emergency tracker's post-meeting over-gate baseline
        # samples the folded beliefs -- only a fresh below-to-above crossing
        # after this point re-arms the suspicion trigger.
        _notify_meeting_concluded(
            state=next_state,
            agents=agents,
            emergency_caller_id=(
                trigger.triggered_by if trigger_kind == "emergency" else None
            ),
            outcome=derive_meeting_outcome_summary(artifacts.result),
            roster_impostor_count=self._num_impostors,
        )
        return next_state, post_events

    def _build_agents(
        self,
        players: Mapping[PlayerId, PlayerState],
    ) -> dict[PlayerId, AgentInterface]:
        agents: dict[PlayerId, AgentInterface] = {}
        for player_id in sorted(players):
            agents[player_id] = self._agent_factory(player_id, players[player_id].role)
        return agents

    def _build_packets(
        self,
        *,
        state: WorldState,
        observation_service: ObservationService,
        last_events: tuple[EngineEvent, ...],
    ) -> dict[PlayerId, ObservationPacket]:
        packets: dict[PlayerId, ObservationPacket] = {}
        for player_id in sorted(state.players):
            if not state.players[player_id].alive:
                continue
            packets[player_id] = observation_service.build_packet(
                world_state=state,
                agent_id=player_id,
                engine_events=last_events,
            )
        return packets

    def _collect_intents(
        self,
        *,
        packets: Mapping[PlayerId, ObservationPacket],
        agents: Mapping[PlayerId, AgentInterface],
    ) -> list[ActionIntent]:
        """Ask every living agent for its intent, refusing any forged ``actor``.

        The identity check is the whole of the orchestrator's trust in an agent's
        return value: ``ActionIntent.actor`` is a plain field the agent fills in,
        and everything downstream — ``translate_action_intents_for_tick``, the
        engine's per-actor legality checks, the replay row — takes it as the
        acting seat. An agent that returns an intent naming a DIFFERENT player
        therefore acts as that player: it could move, kill, or call a meeting on
        someone else's behalf, and the replay would record it as that player's
        action with nothing marking the substitution.

        Nothing in the ``AgentInterface`` Protocol prevents it, and the seam is
        widening on purpose — a learned mover (Phase 15+) constructs its intent
        from a policy head's output rather than copying the packet's ``agent_id``,
        so a mask/decode bug produces exactly this shape. Fail loud here
        (AGENTS.md "no silent fallbacks"): the dispatch loop knows which seat it
        asked, so the mismatch is detectable at the only place that still holds
        both halves.
        """

        intents: list[ActionIntent] = []
        for player_id in sorted(packets):
            intent = agents[player_id].decide(packets[player_id], self._public_map)
            if intent.actor != player_id:
                raise ValueError(
                    f"agent for {player_id!r} returned an intent acting as "
                    f"{intent.actor!r} (type {intent.type!r}); an ActionIntent may "
                    "only act as the player it was asked to decide for"
                )
            intents.append(intent)
        return intents

    def _game_over_event(self, last_events: tuple[EngineEvent, ...]) -> GameOverEvent:
        for event in last_events:
            if isinstance(event, GameOverEvent):
                return event
        raise RuntimeError("game loop exited PLAY without emitting a GameOverEvent")

    def _game_id(self) -> str:
        return f"headless-seed-{self._seed}"


@dataclass(frozen=True)
class _MeetingSideRecords:
    """Meeting side-records that must survive a meeting abort (audit gp-2).

    Bundles the two non-result outputs the orchestrator persists -- fired
    ``deadline_default`` markers and recovered provider parse-failures -- so a
    LATER aborting call (after which ``record_meeting`` never runs) does not
    lose them. Rides the propagating exception like ``llm.provider``'s
    parse-failure-on-exception pattern, which keeps the ``MeetingRunner``
    Protocol unchanged (a custom runner that does not attach simply yields an
    empty bundle here) and avoids module-level mutable state.
    """

    defaulted_calls: tuple[DefaultedCall, ...] = ()
    recovered_call_failures: tuple[LLMCallFailure, ...] = ()


_MEETING_SIDE_RECORDS_ATTR: Final[str] = "_ailibi_meeting_side_records"


def _attach_meeting_side_records(
    exc: BaseException, records: _MeetingSideRecords
) -> None:
    setattr(exc, _MEETING_SIDE_RECORDS_ATTR, records)


def _extract_meeting_side_records(exc: BaseException) -> _MeetingSideRecords:
    """Return the :class:`_MeetingSideRecords` carried by ``exc`` (empty if none)."""

    value = getattr(exc, _MEETING_SIDE_RECORDS_ATTR, None)
    return value if isinstance(value, _MeetingSideRecords) else _MeetingSideRecords()


def _record_recovered_failures(
    *,
    replay: ReplayLog | None,
    meeting_id: str,
    tick: int,
    failures: Sequence[LLMCallFailure],
) -> None:
    """Record provider parse-failures recovered on a succeeding turn (gp-2).

    A real provider validates internally and raises before the recording client
    can log the call, so a retry that fails once then parses would otherwise
    lose the failed attempt's spend (absent from ``llm_calls``, and a success
    carries no ``DefaultedCall``). Each is written into the existing failed-call
    channel with its REAL model / response / tokens / cost -- the same fields
    the meeting-abort path records for the aborting call, since both are genuine
    provider parse-failures -- so call count and cost stay accurate.

    A ``None`` ``replay`` is the no-replay training path (Task 15.8.1): nothing
    is recorded, so this is a no-op.
    """

    if replay is None:
        return
    for failure in failures:
        replay.record_failed_call(
            meeting_id=meeting_id,
            tick=tick,
            model=failure.model,
            prompt_length=failure.prompt_length,
            raw_response=failure.raw_response,
            input_tokens=failure.input_tokens,
            output_tokens=failure.output_tokens,
            cost_usd=failure.cost_usd,
            error_type=failure.error_type,
            error_message=failure.error_message,
        )


def _record_deadline_defaults(
    *,
    replay: ReplayLog | None,
    meeting_id: str,
    tick: int,
    defaulted_calls: Sequence[DefaultedCall],
) -> None:
    """Record each fired meeting default as a visible replay entry (audit gp-2).

    A ``None`` ``replay`` is the no-replay training path (Task 15.8.1): nothing
    is recorded, so this is a no-op.

    A turn / ballot that fell back to its placeholder is written into the
    EXISTING failed-call channel as a
    :class:`~orchestrator.replay.FailedCallReplayEntry` with
    ``error_type="deadline_default"`` -- no new replay record kind, since
    ``FailedCallReplayEntry.error_type`` is a free string. The defaulted phase
    and the trigger kind (deadline vs validation) are named in ``error_message``
    so the husk is auditable -- the headless recorder previously lost such turns
    with no record of any kind while telemetry reported ``failed_calls=0`` (true
    of the records, false of the run).

    Spend is preserved accurately. When a default carries ``parse_failures`` --
    a REAL provider validated internally and raised *before* the recording
    client could log the call, so that spend is absent from ``llm_calls`` -- one
    row is written per burned call with its real model / response / tokens /
    cost (the same per-call granularity ``llm_calls`` uses). Otherwise the row
    is a ZERO-spend visibility marker: a deadline miss completed nothing, and a
    manager-side validation of a returned-but-invalid payload already has its
    spend in ``llm_calls``, so charging it here too would double-count.

    De-dup (Task 9.10, audit gp-4): a deterministic provider regenerates the
    SAME failing response on the in-turn retry, so a single default can carry
    the same burned generation twice; :meth:`ReplayLog.record_failed_call`
    drops the byte-identical second row at the write chokepoint, so each
    distinct burned generation -- and each distinct zero-spend marker, whose
    ``error_message`` names its participant -- records exactly once.
    """

    if replay is None:
        return
    for default in defaulted_calls:
        # The rendered §4.6 verdict max rides ONLY a defaulted vote (Task 10.12,
        # audit H-H-2): it is the sole telemetry that recovers a defaulted
        # ballot's MUST-vote / MUST-skip verdict, lost when the vote call failed
        # before the recording client logged its prompt. ``None`` for turns.
        if default.parse_failures:
            for failure in default.parse_failures:
                replay.record_failed_call(
                    meeting_id=meeting_id,
                    tick=tick,
                    model=failure.model,
                    prompt_length=failure.prompt_length,
                    raw_response=failure.raw_response,
                    input_tokens=failure.input_tokens,
                    output_tokens=failure.output_tokens,
                    cost_usd=failure.cost_usd,
                    error_type="deadline_default",
                    error_message=_deadline_default_message(default, failure),
                    rendered_vote_max=default.rendered_vote_max,
                )
            continue
        replay.record_failed_call(
            meeting_id=meeting_id,
            tick=tick,
            model=_DEADLINE_DEFAULT_MODEL,
            prompt_length=0,
            raw_response="",
            input_tokens=0,
            output_tokens=0,
            cost_usd=0.0,
            error_type="deadline_default",
            error_message=_deadline_default_message(default),
            rendered_vote_max=default.rendered_vote_max,
        )


def _deadline_default_message(
    default: DefaultedCall, failure: LLMCallFailure | None = None
) -> str:
    """Human-readable ``error_message`` for a ``deadline_default`` record.

    Names the defaulted phase and the trigger kind (``deadline`` vs
    ``validation``) plus the participant who submitted nothing; the meeting id
    and tick ride the entry's own fields. When a provider ``failure`` is
    supplied its underlying error is appended so the husk's original cause is
    auditable alongside the preserved spend.
    """

    if default.phase == "vote":
        base = (
            f"vote defaulted ({default.trigger}); "
            f"{default.agent_id} submitted no ballot"
        )
    else:
        index = "" if default.turn_index is None else f" (turn {default.turn_index})"
        base = (
            f"{default.phase} turn{index} defaulted ({default.trigger}); "
            f"{default.agent_id} submitted no turn"
        )
    if failure is None:
        return base
    return f"{base} [{failure.error_type}: {failure.error_message}]"


def _absorb_meeting_beliefs(
    *,
    result: MeetingResult,
    state: WorldState,
    agents: Mapping[PlayerId, AgentInterface],
    trigger_kind: MeetingTriggerKind,
) -> None:
    """Fold a resolved meeting's evidence into living agents' beliefs (Task 9.8).

    The orchestrator-owned fan-out of the persistent post-meeting belief
    path: one :func:`meetings.manager.extract_belief_evidence` reduction,
    then one :meth:`BeliefPersistingAgent.absorb_meeting_evidence` per
    player still alive in the post-meeting ``state`` (a player alive after
    the meeting was necessarily a participant -- meetings only remove
    players). Iteration is sorted for determinism. The fold itself fires
    even when the meeting produced no evidence at all: an evidence-free
    round is exactly when §6.3 Rule 5 decays every unreinforced suspicion
    toward 0.5.

    Agents that do not implement the optional
    :class:`BeliefPersistingAgent` capability (scripted test agents with
    no belief store) are skipped -- see the protocol docstring for why
    that is a capability gate, not a silent fallback.

    Task 10.11 (audit-2026-06-13-1816 B-B-1): the engine-authoritative
    ``trigger_kind`` is threaded into the evidence reduction so the §6.3
    Rule-3 relevance gate treats an EMERGENCY meeting as having no kill
    scene -- a (fabricated) opening ``found_body`` can never widen the
    exclusion zone that the persisted corroborations / voices fold through.
    """

    evidence = extract_belief_evidence(result, trigger_kind=trigger_kind)
    # Task 13.5.2: the reported-testimony content fold rides the SAME
    # per-living-agent loop as the scalar belief fold, unconditionally since
    # Task 14.9 (the adopted lever is the default substrate). The derivation is
    # a pure function of the recorded ``result``, identical to the replay
    # loader's, so reconstruction stays byte-identical.
    statements: tuple[ReportedStatement, ...] = derive_reported_testimony(result)
    for player_id in sorted(state.players):
        if not state.players[player_id].alive:
            continue
        agent = agents.get(player_id)
        if isinstance(agent, BeliefPersistingAgent):
            agent.absorb_meeting_evidence(
                accused=evidence.accused,
                corroborated=evidence.corroborated,
                contradicted=evidence.contradicted,
            )
        # Reported content is ADDITIVE narrative, never a suspicion Δ -- it runs
        # AFTER the scalar fold (so the meeting-boundary marker is already
        # appended) and is wholly separate from it. NOT teammate-firewalled: the
        # capability ingests public speech faithfully (the scalar firewall above
        # is unchanged).
        if isinstance(agent, ReportedTestimonyAgent):
            agent.absorb_reported_testimony(statements=statements)


def _assert_no_emergency_opening_body(
    *,
    trigger_kind: MeetingTriggerKind,
    result: MeetingResult,
) -> None:
    """Fail loud if an emergency opening fabricates a body (Task 10.11).

    DESIGN.md §5.2 PHASE 1: an EMERGENCY meeting has no body -- the caller
    pressed the button on suspicion, no corpse was reported. The 10.8
    self-check ("engine ``body_id is None``") was true yet MASKED a
    transcript-level fabrication: on the close baseline every emergency
    opening re-narrated a real-but-stale corpse as a fresh ``found_body``
    (audit-2026-06-13-1816 B-B-1), and voters anchored ejections on it.
    This check looks at the OPENING TURN's observations, not the engine
    field, so a model that ignores the v7 prompt and still emits a
    ``found_body`` on an emergency opening is caught at the source instead
    of silently widening the §6.3 Rule-3 exclusion zone. Non-emergency
    meetings and empty transcripts are no-ops.
    """

    if trigger_kind != "emergency":
        return
    turns = result.transcript.turns
    if not turns:
        return
    fabricated = [
        observation
        for observation in turns[0].observations
        if isinstance(observation, FoundBodyObservation)
    ]
    if fabricated:
        bodies = ", ".join(
            f"{observation.body_of} in {observation.room}@t{observation.tick}"
            for observation in fabricated
        )
        raise RuntimeError(
            "Task 10.11 invariant violated: emergency meeting "
            f"{result.meeting_id!r} opening turn carries a fabricated "
            f"found_body observation ({bodies}). An emergency meeting reports "
            "no body (DESIGN.md §5.2 PHASE 1); the crewmate_report v7 emergency "
            "branch forbids a found_body observation."
        )


def _notify_meeting_concluded(
    *,
    state: WorldState,
    agents: Mapping[PlayerId, AgentInterface],
    emergency_caller_id: PlayerId | None,
    outcome: MeetingOutcomeSummary,
    roster_impostor_count: int,
) -> None:
    """Fan one concluded meeting's announced facts out to living agents.

    The orchestrator-owned mirror of :func:`_absorb_meeting_beliefs` for the
    :class:`MeetingPacingAgent` capability: every player still alive in the
    post-meeting ``state`` learns the tick gameplay resumes at (``state.tick``
    -- :func:`apply_meeting_result` already advanced it), the announced dead
    roster (sorted, post-ejection -- everyone at the table saw who is gone), the
    meeting's emergency caller (``None`` for a body report), the ejection
    outcome and its tally (``outcome``, the meeting layer's role-blind
    reduction), and the impostor count stated at game start.

    THE ROLE IS TRANSLATED HERE AND ONLY HERE. Confirm-ejects makes the ejected
    player's role public at the table on exactly the footing ``dead_ids`` and
    the tally already cross on (DESIGN.md §4.7), so it is read off the
    post-meeting ``state`` for the EJECTED player alone. A skip discloses
    nothing, and a KILLED player's role is never read: nobody at the table saw
    it. ``agents/`` may not import ``engine`` and the meeting layer never sees a
    role, which is what keeps the disclosure auditable rather than a hole --
    ``eval.leak_scan`` asserts the rendered end of the same rule.

    Iteration is sorted for determinism; agents without the capability are
    skipped (capability gate, not a silent fallback -- see
    :class:`MeetingPacingAgent`).
    """

    dead_ids = tuple(
        sorted(
            player_id for player_id, player in state.players.items() if not player.alive
        )
    )
    ejected_id = outcome.ejected_id
    ejected_role = None if ejected_id is None else state.players[ejected_id].role
    for player_id in sorted(state.players):
        if not state.players[player_id].alive:
            continue
        agent = agents.get(player_id)
        if isinstance(agent, MeetingPacingAgent):
            agent.note_meeting_concluded(
                end_tick=state.tick,
                dead_ids=dead_ids,
                emergency_caller_id=emergency_caller_id,
                ejected_id=ejected_id,
                ejected_role=ejected_role,
                votes_for_ejected=outcome.votes_for_ejected,
                skip_votes=outcome.skip_votes,
                roster_impostor_count=roster_impostor_count,
            )


def _build_meeting_trigger(
    *,
    state: WorldState,
    events: Sequence[EngineEvent],
) -> tuple[MeetingTrigger, BodyId | None, Literal["report", "emergency"]]:
    """Construct a :class:`MeetingTrigger` from the engine's transition events.

    The engine emits a :class:`MeetingTriggeredEvent` from
    :mod:`engine.tick._apply_report` / ``_apply_emergency`` whenever a
    valid ``ReportBody`` / ``EmergencyMeeting`` action drives the
    world into ``MEETING`` phase. The orchestrator pulls the most
    recent such event off the engine's emitted event list and renders
    it into the human-readable description the report prompt
    surfaces.

    The emergency description's "called an emergency meeting" phrase is
    load-bearing (Task 10.8): ``crewmate_report.j2`` v6 branches its
    emergency-opening frame on exactly that substring of the rendered
    ``meeting_trigger`` (the meeting layer threads no structured trigger
    kind to the prompt renderers, by design — the description IS the
    trigger surface). A wording change here must move in lockstep with
    the template branch; the strategic-prompt tests pin both ends.

    The second element of the returned tuple is the ``body_id`` of
    the corpse that triggered a ``report`` meeting (``None`` for an
    ``emergency`` meeting). :func:`apply_meeting_result` consumes
    that body so a hardcoded second report cannot re-trigger a meeting
    on the same corpse after gameplay resumes (defense in depth — the
    visibility layer already hides discovered bodies from default
    tactical agents, but the engine's ``resolve_report`` does not
    reject already-discovered bodies, so an adversarial / scripted
    intent could otherwise replay the trigger).

    The third element is the engine's trigger kind, consumed by the
    Task 10.8 post-meeting pacing notification (an ``emergency``
    meeting spends its caller's one emergency call per game).
    """

    trigger_event: MeetingTriggeredEvent | None = None
    for event in events:
        if isinstance(event, MeetingTriggeredEvent):
            trigger_event = event
    if trigger_event is None:
        raise RuntimeError(
            "engine transitioned to MEETING phase without emitting a "
            "MeetingTriggeredEvent; this is an engine invariant violation"
        )
    body_id: BodyId | None
    victim_id: PlayerId | None = None
    if trigger_event.trigger == "report":
        body_id = trigger_event.body_id
        # The corpse this meeting was opened on, read off engine state rather
        # than parsed out of the body id. A speaker can hold discoveries of two
        # corpses a tick apart, so a render that says "the body" needs to know
        # which; a body already consumed leaves this ``None`` and the render
        # names no victim rather than guessing one.
        if body_id is not None:
            corpse = state.bodies.get(body_id)
            victim_id = corpse.player_id if corpse is not None else None
        description = (
            f"{trigger_event.actor} reported "
            + (f"body {body_id} " if body_id is not None else "a body ")
            + f"at tick {trigger_event.tick}"
        )
    else:
        body_id = None
        description = (
            f"{trigger_event.actor} {EMERGENCY_TRIGGER_PHRASE} at tick "
            f"{trigger_event.tick}"
        )
    trigger = MeetingTrigger(
        triggered_by=trigger_event.actor,
        trigger_tick=trigger_event.tick,
        description=description,
        body_victim_id=victim_id,
    )
    return trigger, body_id, trigger_event.trigger


def _drive_async(coro: Coroutine[object, object, _T]) -> _T:
    """Run an async coroutine to completion from a synchronous context.

    Refuses to run when the caller is already inside an event loop —
    that would deadlock or silently spawn a nested loop. The
    orchestrator's :meth:`HeadlessGame.run` is synchronous by
    contract; the only sanctioned path into the meeting subsystem
    runs through this helper.
    """

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    raise RuntimeError(
        "HeadlessGame.run() must not be called from a running event loop; "
        "the orchestrator drives async meeting code via asyncio.run()"
    )


# ---------------------------------------------------------------------------
# Typed episodic records the tactical agent projects at meeting-open.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class KillWitnessRecord:
    """One first-hand witnessed-kill episodic record, typed (Task 18.30).

    The kill twin of :class:`~meetings.schemas.VentWitnessRecord`: the
    ``subject`` is the WITNESSED KILLER named at ``room``/``tick`` in a
    first-hand ``saw_player`` row whose action stamp is ``"kill"``. Emitted by
    :meth:`TacticalAgent.kill_witness_records_for_meeting` and consumed only by
    the training-side conviction assembler
    (:mod:`training.conviction.serving`) — never by the meeting layer, so it is
    NOT part of the :class:`MeetingAwareAgent` protocol. Defined in ``game.py``
    (not ``meetings/schemas.py``, which the 18.30 scope freezes) beside the
    other game-local frozen records (:class:`MeetingArtifacts`), and a plain
    dataclass rather than a pydantic schema because it never flows through
    LLM structured output.
    """

    subject: PlayerId
    room: RoomId
    tick: int


@dataclass(frozen=True)
class BodyProximityRecord:
    """One §6.3 Rule-1 body-proximity pin, typed (Task 18.30).

    The ``subject`` is a player the agent saw co-present in ``room`` shortly
    before it FIRST discovered a body there, the candidate the DESIGN.md §6.3
    Rule 1 body-proximity rule pins; ``tick`` is that discovery tick (the
    first ``saw_body`` sighting). Emitted by
    :meth:`TacticalAgent.body_proximity_records_for_meeting` and consumed only
    by the training-side conviction assembler
    (:mod:`training.conviction.serving`); like :class:`KillWitnessRecord` it is
    game-local, frozen, and off the :class:`MeetingAwareAgent` protocol.
    """

    subject: PlayerId
    room: RoomId
    tick: int


# ---------------------------------------------------------------------------
# Tactical agent — composite memory + tactical policy.
# ---------------------------------------------------------------------------


class TacticalAgent:
    """Default tactical agent that bridges perception, memory, and policy.

    The orchestrator's default :data:`AgentFactory`
    (:func:`build_default_agent_factory`) returns one of these per
    player. Each agent owns a private :class:`AgentMemory`;
    :func:`agents.perception.ingest_packet` writes packets into the
    composite memory's episodic store, then the tactical policy reads
    the same episodic store and returns an :class:`ActionIntent`.

    The class lives in the orchestrator because it composes pieces
    from ``agents/`` (perception + memory + tactical) without leaking
    that wiring back into ``agents/runtime.py``; that file's stubs are
    owned by future tasks.

    For Phase 3.12, :class:`TacticalAgent` implements the
    :class:`MeetingAwareAgent` protocol: it exposes
    :meth:`render_memory_for_meeting` (token-budgeted Markdown view of
    its composite memory via :func:`render_for_prompt`) and
    :meth:`suspicion_graph_for_meeting` (a tuple of
    :class:`SuspicionEntry` rows pulled from the agent's belief
    state). The default-game integration test exercises these methods
    end-to-end through the meeting protocol.
    """

    def __init__(
        self,
        *,
        agent_id: PlayerId,
        policy: CrewmatePolicy | ImpostorPolicy,
        role: Role | None = None,
        memory: AgentMemory | None = None,
    ) -> None:
        self._agent_id = agent_id
        self._policy = policy
        # ``role`` is optional because the legacy Phase-2 tests
        # construct a :class:`TacticalAgent` without specifying it.
        # Phase 3.12 meetings need a concrete role for participant
        # construction; the orchestrator's default agent factory
        # always passes one. Tests that bypass the factory get
        # ``"CREWMATE"`` / ``"IMPOSTOR"`` inferred from the policy
        # type so the meeting wiring still works without an extra
        # kwarg at every call site.
        self._role: Role = role if role is not None else _infer_role_from_policy(policy)
        self._memory = memory if memory is not None else AgentMemory()
        # Emergency pacing bookkeeping (Task 10.8) exists only for a
        # crewmate running the crewmate FSM: the suspicion-accumulation
        # trigger is crew-only, and an impostor agent must carry NO button
        # bookkeeping at all (impostors gain no button behavior until
        # Wave 2 decides it -- this gate is what the no-impostor-emergency
        # pin asserts against).
        self._emergency_tracker: EmergencyPacingTracker | None = (
            EmergencyPacingTracker()
            if self._role == "CREWMATE" and isinstance(policy, CrewmatePolicy)
            else None
        )

    @property
    def agent_id(self) -> PlayerId:
        return self._agent_id

    @property
    def role(self) -> Role:
        return self._role

    @property
    def memory(self) -> AgentMemory:
        return self._memory

    def decide(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
    ) -> ActionIntent:
        if packet.agent_id != self._agent_id:
            raise ValueError(
                f"observation packet for agent {packet.agent_id!r} given to "
                f"tactical agent bound to {self._agent_id!r}"
            )
        ingest_packet(
            packet=packet,
            memory=self._memory.episodic,
            beliefs=self._memory.beliefs,
        )
        # Crewmate path (Task 10.8): sample the emergency tracker AFTER
        # perception (so this tick's §6.3 belief updates are visible) and
        # hand the policy the immutable eligibility snapshot. The sample is
        # idempotent for a given state, so repeated decide() calls stay
        # equal (the policy-determinism contract).
        if self._emergency_tracker is not None and isinstance(
            self._policy, CrewmatePolicy
        ):
            view = self._emergency_tracker.observe_tick(
                tick=packet.tick,
                memory=self._memory.episodic,
                beliefs=self._memory.beliefs,
                own_id=self._agent_id,
            )
            return self._policy.decide(
                self._memory.episodic, public_map, emergency=view
            )
        return self._policy.decide(self._memory.episodic, public_map)

    def render_memory_for_meeting(
        self,
        *,
        token_budget: int = DEFAULT_TOKEN_BUDGET,
        suspicion_override: Mapping[PlayerId, float] | None = None,
    ) -> str:
        """Token-budgeted rendered memory view (DESIGN.md §6.6).

        ``suspicion_override`` (Task 13.5.5) is forwarded to
        :func:`render_for_prompt` so the meeting can render a ballot's
        belief-line suspicion from the pre-vote-folded numbers; ``None``
        (every non-ballot render) is byte-identical to pre-task HEAD.
        """

        return render_for_prompt(
            self._memory,
            token_budget=token_budget,
            suspicion_override=suspicion_override,
        )

    def suspicion_graph_for_meeting(self) -> tuple[SuspicionEntry, ...]:
        """Snapshot of the agent's belief state as a suspicion graph.

        DESIGN.md §5.5 feeds the suspicion graph straight into the
        vote-ballot prompt. The entries are sorted by ``player_id``
        for deterministic prompt-input ordering.

        Task 16.3: each row also carries the belief's
        :class:`~agents.memory.beliefs.SuspicionProvenance` decomposition,
        mapped field-by-name onto the widened :class:`SuspicionEntry` (the
        render-contract leaf mirrors the provenance shape without importing
        ``agents.*``). It rode the graph inertly until Task 16.15; since the
        16.15 elicitation batch the ``qwen3_6_27b`` vote-ballot template
        renders the split per row (the J2a provenance surface). The surface is
        TEMPLATE-GATED: no other set's ballot references
        ``suspicion_provenance``, so under the default ``qwen3_5_9b`` set or
        the other bespoke sets the split still rides the graph inertly. Fed
        from HERE, the one production builder, populating it keeps ``0.5 +
        sum(the eight fields) == suspicion`` on every live row (the belief
        store's own invariant, on the STORED belief -- an entirely-soft row
        OVER the J1 ceiling renders its scalar clamped below that sum, while
        one at or under 0.59 renders it unchanged; see Task 16.4 below), so
        the 16.15 surface reads real hard/soft data rather than defaults.

        The J1 render clamp. A row whose typed provenance is entirely soft renders its
        ``suspicion`` scalar clamped to
        :data:`~agents.memory.beliefs.HARD_EVIDENCE_GATE_RENDER_CEIL`, just below
        the §4.6 gate; hard-backed rows and the stored :class:`BeliefState` are
        untouched. The eight provenance kwargs stay the RAW 16.3 decomposition --
        the true evidence record -- so a clamped row's scalar deliberately renders
        below its decomposition sum, and the manager's ``seed_player`` reconciling
        that shortfall as an ``unattributed`` residual is the ALWAYS-ON
        reconciliation.
        """

        entries: list[SuspicionEntry] = []
        for player_id in sorted(self._memory.beliefs.known_players()):
            belief = self._memory.beliefs.view(player_id)
            provenance = belief.provenance
            suspicion = hard_evidence_gated_suspicion(belief.suspicion, provenance)
            entries.append(
                SuspicionEntry(
                    player_id=player_id,
                    suspicion=suspicion,
                    trust=belief.trust,
                    flag_lift=provenance.flag_lift,
                    body_proximity=provenance.body_proximity,
                    kill_or_vent_pin=provenance.kill_or_vent_pin,
                    testimony_spread=provenance.testimony_spread,
                    accusation_carry=provenance.accusation_carry,
                    carried_hard=provenance.carried_hard,
                    carried_soft=provenance.carried_soft,
                    unattributed=provenance.unattributed,
                )
            )
        return tuple(entries)

    def vent_witness_records_for_meeting(self) -> tuple[VentWitnessRecord, ...]:
        """The agent's OWN witnessed-vent episodic records, typed (Task 15.4).

        The grounding input behind the meeting layer's ``vent_sighting``
        hard flag: a straight read of the episodic log --
        first-hand (``provenance == "observed"``) ``saw_player`` rows whose
        witness-gated action stamp is ``"vent"`` -- projected into
        :class:`~meetings.schemas.VentWitnessRecord` rows. Reads the SAME
        rows the §6.6 renderer turns into "You witnessed {player} vent in
        {room}." lines, so the typed channel and the rendered prose the
        model speaks from can never drift. Firewall-clean: every row was
        witness-gated by the engine before it reached this agent's packet
        (``eval/leak_test.py``), and the accessor reports only this agent's
        own log. Payload reads are defensive per the store convention -- a
        malformed row contributes nothing. Append order is non-decreasing
        in tick (the episodic-store invariant), so the returned tuple is
        deterministic and tick-sorted.
        """

        records: list[VentWitnessRecord] = []
        for event in self._memory.episodic.recent(since_tick=0):
            if event.type != EVENT_SAW_PLAYER:
                continue
            if event.provenance != PROVENANCE_OBSERVED:
                continue
            if event.payload.get("action") != OBSERVED_VENT_ACTION:
                continue
            player_id = event.payload.get("player_id")
            room = event.payload.get("room")
            if not isinstance(player_id, str) or not isinstance(room, str):
                continue
            records.append(
                VentWitnessRecord(subject=player_id, room=room, tick=event.tick)
            )
        return tuple(records)

    def sighting_records_for_meeting(self) -> tuple[SightingRecord, ...]:
        """The agent's OWN first-hand sighting episodic records, typed (Task 16.7).

        The vent accessor's sibling with the polarity inverted: the same
        first-hand (``provenance == "observed"``) ``saw_player`` rows,
        but capturing ORDINARY sightings (the vent accessor's role-proving
        ``vent`` filter is dropped) rather than restricting to vents, plus
        the ``co_present`` projection: the OTHER subjects this agent saw in
        the same room on the same tick, the same Task 13.9 grouping the
        §6.6 renderer's "(with ...)" suffix is built from. The meeting
        layer grounds a speaker's spoken ``saw_player`` observation ONLY
        against the speaker's own rows here (the grounded-vouch feed into
        the existing corroboration channel -- never a flag, never trust).

        Incriminating-action rows are EXCLUDED: a witnessed ``kill`` or
        ``vent`` names its subject an impostor, and the grounded-vouch
        channel is the -0.05 EXCULPATION path (the contract's "not
        role-proving"), so grounding a spoken sighting against one would
        lower a witnessed killer's/venter's suspicion. Their subjects are
        impostors by construction, so no legitimate vouch is lost; the
        role-proving signal stays in its own channel (vent -> the 15.4
        STRONG flag; kill -> the Rule-4 witness pin).
        Firewall-clean: every row was witness-gated by the engine before
        it reached this agent's packet (``eval/leak_test.py``), and the
        accessor reports only this agent's own log.

        Unlike the §6.6 render this does NOT apply the §4.7
        ``_sighting_is_suppressed`` teammate-at-kill-window drop, so an
        impostor's record CAN name a teammate seen at a kill window that
        the rendered prose hides. That is safe for the ONE consumer this
        channel has: grounding only ever CORROBORATES (a teammate
        corroboration is retained by the §4.7 firewall, unlike a teammate
        accusation), a kill-scene vouch is dropped by the relevance gate
        (:func:`meetings.transcript.grounded_vouch_subjects`), and a
        ``SightingRecord`` never reaches a prompt or the recorded
        ``MeetingResult``. A future consumer beyond grounding must re-apply
        the suppression rather than assume it here. Payload reads are
        defensive per the store convention -- a malformed row contributes
        nothing. Append order is non-decreasing in tick (the
        episodic-store invariant), so the returned tuple is deterministic
        and tick-sorted.
        """

        sightings: list[tuple[str, str, int]] = []
        co_present: dict[tuple[int, str], set[str]] = {}
        for event in self._memory.episodic.recent(since_tick=0):
            if event.type != EVENT_SAW_PLAYER:
                continue
            if event.provenance != PROVENANCE_OBSERVED:
                continue
            # An INCRIMINATING-action observation is not a corroboration-class
            # sighting and must never seed the exculpation channel: a witnessed
            # ``kill`` or ``vent`` names its subject an impostor, so grounding a
            # spoken sighting against it would lower a witnessed killer's/venter's
            # suspicion through the -0.05 vouch. Both subjects are impostors by
            # construction, so no legitimate vouch is lost. This refines the
            # contract's "drop the vent-action filter" to its intent (the vouch
            # channel is "not role-proving"): the accessor no longer restricts to
            # vents, but the ROLE-PROVING actions stay in their own channels
            # (vent -> the 15.4 STRONG flag; kill -> the Rule-4 witness pin).
            action = event.payload.get("action")
            if action in (OBSERVED_VENT_ACTION, OBSERVED_KILL_ACTION):
                continue
            player_id = event.payload.get("player_id")
            room = event.payload.get("room")
            if not isinstance(player_id, str) or not isinstance(room, str):
                continue
            sightings.append((player_id, room, event.tick))
            co_present.setdefault((event.tick, room), set()).add(player_id)
        return tuple(
            SightingRecord(
                subject=player_id,
                room=room,
                tick=tick,
                co_present=tuple(
                    sorted(co_present.get((tick, room), set()) - {player_id})
                ),
            )
            for player_id, room, tick in sightings
        )

    def move_witness_records_for_meeting(self) -> tuple[MoveWitnessRecord, ...]:
        """The agent's OWN witnessed room→room transitions, typed.

        Implements :class:`MoveWitnessAgent`. A straight read of the episodic
        log -- first-hand (``provenance == "observed"``) ``saw_player_move``
        rows -- projected into :class:`~meetings.schemas.MoveWitnessRecord`
        rows. These are the SAME rows the §6.6 renderer turns into "You saw
        {player} move from {from_room} to {to_room}." lines, so the typed
        channel the meeting layer grounds against and the prose the model speaks
        from cannot drift.

        The §4.7 TEAMMATE firewall is applied here, not inherited. Re-indexing a
        placement can mint a contradiction the meeting did not have, so a
        transition the §6.6 render deliberately hides from an impostor -- a
        teammate's transit at a kill room/tick, dropped by
        ``_sighting_is_suppressed`` so the impostor cannot narrate its own
        partner at the scene -- must not reach the meeting layer through this
        channel and place that partner anyway. The guard here is broader than
        the render's kill-window rule: an impostor's records naming a FELLOW
        IMPOSTOR are dropped outright (the same shape
        :meth:`kill_witness_records_for_meeting` uses), which contains the
        own-goal class without this accessor having to reconstruct the render's
        body-sighting inputs, and costs nothing real -- a dropped record only
        means that placement is read exactly as the impostor spoke it. The
        fellow set is this agent's own
        (:meth:`_fellow_impostor_ids_from_store`); it is empty for every
        crewmate and a sole impostor, so the crew path drops nothing.

        Firewall-clean: every row was witness-gated by the engine before it
        reached this agent's packet (``eval/leak_test.py``), and the accessor
        reports only this agent's own log. Payload reads are defensive per the
        store convention -- a malformed row contributes nothing. Append order is
        non-decreasing in tick (the episodic-store invariant), so the returned
        tuple is deterministic and tick-sorted.
        """

        fellows = self._fellow_impostor_ids_from_store()
        records: list[MoveWitnessRecord] = []
        for event in self._memory.episodic.recent(since_tick=0):
            if event.type != EVENT_SAW_PLAYER_MOVE:
                continue
            if event.provenance != PROVENANCE_OBSERVED:
                continue
            player_id = event.payload.get("player_id")
            if player_id in fellows or player_id == self.agent_id:
                continue
            from_room = event.payload.get("from_room")
            to_room = event.payload.get("to_room")
            if (
                not isinstance(player_id, str)
                or not isinstance(from_room, str)
                or not isinstance(to_room, str)
            ):
                continue
            records.append(
                MoveWitnessRecord(
                    subject=player_id,
                    from_room=from_room,
                    to_room=to_room,
                    tick=event.tick,
                )
            )
        return tuple(records)

    def _fellow_impostor_ids_from_store(self) -> frozenset[str]:
        """The agent's OWN fellow-impostor set, read from its ``self_state`` log.

        The §4.7 teammate firewall's input, read the SAME way
        ``agents.memory.store._latest_self_guard_fields`` reads it: the latest
        first-hand (``provenance == "observed"``) ``self_state`` row's
        ``fellow_impostor_ids`` payload wins (a defensive ``.get`` +
        ``isinstance`` read — a malformed payload contributes nothing). It is
        ``()`` for every crewmate and a sole impostor, so the crew read path is
        an empty set and filters nothing. Used only by the kill/body accessors
        below to inherit the production belief rules' teammate guard; never
        leaves this agent's own log, so the firewall is preserved.
        """

        fellows: tuple[str, ...] = ()
        for event in self._memory.episodic.recent(since_tick=0):
            if event.type != EVENT_SELF_STATE:
                continue
            if event.provenance != PROVENANCE_OBSERVED:
                continue
            raw = event.payload.get("fellow_impostor_ids")
            if isinstance(raw, (list, tuple)) and all(isinstance(x, str) for x in raw):
                fellows = tuple(raw)
        return frozenset(fellows)

    def kill_witness_records_for_meeting(self) -> tuple[KillWitnessRecord, ...]:
        """The agent's OWN witnessed-kill episodic records, typed (Task 18.30).

        The kill twin of :meth:`vent_witness_records_for_meeting`: first-hand
        (``provenance == "observed"``) ``saw_player`` rows whose witness-gated
        action stamp is ``"kill"``, projected into :class:`KillWitnessRecord`
        rows naming the witnessed killer. Consumed by the training-side
        conviction assembler (:mod:`training.conviction.serving`) — the game-long
        ``kill_pin_pairs`` / ``kill_pinned_candidates`` features — NOT by the
        meeting layer, so it is deliberately off the :class:`MeetingAwareAgent`
        protocol.

        Unlike the vent accessor's passive firewall inheritance, this accessor
        ACTIVELY applies the DESIGN.md §4.7 teammate guard. The episodic
        ``saw_player`` action-``kill`` row exists for EVERY witness of a kill,
        crew AND impostor teammate alike — the write path stamps it for every
        ``agent_id in event.witnesses`` with no teammate filter
        (``observation/service.py`` ``_observed_actions_for_agent``). But the
        production witnessed-kill belief PIN carries the guard ``player.id not
        in fellow_impostor_ids`` (``agents/memory/beliefs.py`` Rule 4 kill
        branch), and the offline conviction target restricts the pin to
        crew witnesses only (``training/surrogate/dataset.py::_WindowStats``).
        Since every impostor shares one team, an impostor's killer is always a
        fellow impostor, so ``subject in fellows`` is exactly the crew-only
        restriction. Omitting the guard would surface an impostor's
        teammate-kill row the offline table excludes and break the parity pin on
        any meeting where an impostor co-located with a teammate's kill (the
        routine case). The fellow set is this agent's own
        (:meth:`_fellow_impostor_ids_from_store`).

        Firewall-clean: every row was witness-gated by the engine before it
        reached this agent's packet (``eval/leak_test.py``), and the accessor
        reports only this agent's own log; the teammate guard reads only this
        agent's own ``self_state``. Payload reads are defensive per the store
        convention — a malformed row contributes nothing. Append order is
        non-decreasing in tick (the episodic-store invariant), so the returned
        tuple is deterministic and tick-sorted.
        """

        fellows = self._fellow_impostor_ids_from_store()
        records: list[KillWitnessRecord] = []
        for event in self._memory.episodic.recent(since_tick=0):
            if event.type != EVENT_SAW_PLAYER:
                continue
            if event.provenance != PROVENANCE_OBSERVED:
                continue
            if event.payload.get("action") != OBSERVED_KILL_ACTION:
                continue
            player_id = event.payload.get("player_id")
            room = event.payload.get("room")
            if not isinstance(player_id, str) or not isinstance(room, str):
                continue
            if player_id in fellows:
                # §4.7: a witnessed TEAMMATE kill never pins — the production
                # belief rule's ``player.id not in fellow_impostor_ids`` guard,
                # equivalently the offline pin's crew-witnesses-only restriction.
                continue
            records.append(
                KillWitnessRecord(subject=player_id, room=room, tick=event.tick)
            )
        return tuple(records)

    def body_discovery_records_for_meeting(self) -> tuple[BodyDiscoveryRecord, ...]:
        """The agent's OWN first-hand body discoveries, typed.

        Implements :class:`BodyDiscoveryAgent`. A straight episodic filter in the
        shape of :meth:`vent_witness_records_for_meeting` -- first-hand
        (``provenance == "observed"``) ``saw_body`` rows -- NOT the re-deriving
        join :meth:`body_proximity_records_for_meeting` performs. These are the
        SAME rows the §6.6 renderer turns into "You discovered {victim}'s body in
        {room}." lines, and the two dedupe identically: a body reports on its
        FIRST sighting only, so a second look at the same corpse adds nothing.

        The killer's OWN victim is excluded, exactly as the render suppresses that
        discovery line (DESIGN.md §6.2): the kill is already narrated as a kill,
        and telling a killer their record places them at the body they made would
        put its own kill back in front of it under a discovery framing. The victim
        set is this agent's own ``own_kill`` rows, so the crew path drops nothing.

        Firewall-clean: every row was witness-gated by the engine before it
        reached this agent's packet (``eval/leak_test.py``), and the accessor
        reports only this agent's own log. Payload reads are defensive per the
        store convention -- a malformed row contributes nothing. Append order is
        non-decreasing in tick (the episodic-store invariant), so the returned
        tuple is deterministic and tick-sorted.
        """

        own_kill_victims: set[str] = set()
        for event in self._memory.episodic.recent(since_tick=0):
            if event.type != EVENT_OWN_KILL:
                continue
            victim = event.payload.get("victim_id")
            if isinstance(victim, str):
                own_kill_victims.add(victim)

        seen_bodies: set[str] = set()
        records: list[BodyDiscoveryRecord] = []
        for event in self._memory.episodic.recent(since_tick=0):
            if event.type != EVENT_SAW_BODY:
                continue
            if event.provenance != PROVENANCE_OBSERVED:
                continue
            body_id = event.payload.get("body_id")
            victim_id = event.payload.get("victim_id")
            room = event.payload.get("room")
            if not (
                isinstance(body_id, str)
                and isinstance(victim_id, str)
                and isinstance(room, str)
            ):
                continue
            if body_id in seen_bodies:
                continue
            seen_bodies.add(body_id)
            if victim_id in own_kill_victims:
                continue
            records.append(
                BodyDiscoveryRecord(
                    victim_id=victim_id,
                    room=room,
                    tick=event.tick,
                    observation_id=event.observation_id,
                )
            )
        return tuple(records)

    def body_proximity_records_for_meeting(self) -> tuple[BodyProximityRecord, ...]:
        """The agent's OWN §6.3 Rule-1 body-proximity pins, typed (Task 18.30).

        The game-long body-proximity substrate the conviction assembler
        (:mod:`training.conviction.serving`) reads for the
        ``body_proximity_pairs`` / ``body_proximity_candidates`` features. This
        is NOT a straight episodic filter like the vent/kill accessors: it
        REDERIVES the DESIGN.md §6.3 Rule 1 join over this agent's own episodic
        log, mirroring ``agents/memory/beliefs.py`` ``apply_observation_rules``'
        body loop together with ``agents/perception.py``'s
        ``_previously_seen_body_ids`` (first-sighting-only) and
        ``_recent_co_presence`` (the strictly-before proximity window). The
        offline twin is ``training/surrogate/dataset.py::_absorb_body_proximity``.
        The ``SuspicionEntry.body_proximity`` provenance channel is NOT a valid
        source: it carries only the current window's pins — older ones roll into
        the undifferentiated ``carried_hard`` bucket at the meeting boundary — so
        the honest game-long source is the episodic store.

        For each ``saw_body`` row on its FIRST sighting of that ``body_id``, the
        pin set is every player this agent saw in the body's room within
        ``BODY_PROXIMITY_WINDOW_TICKS`` ticks strictly before the discovery,
        excluding the victim (a corpse seen alive is not a suspect) and, by the
        §4.7 teammate firewall, excluding this agent's fellow impostors (so a
        witnessed teammate kill never manufactures evidence against the team in
        the witness's own graph). Co-presence reads ALL observed ``saw_player``
        rows including kill/vent-stamped ones — the production ``_recent_co_
        presence`` applies no action filter, and a venting actor hidden in the
        vent still lands a row — so this accessor does not filter on action.
        Append order is non-decreasing in tick, so same-tick ``saw_player`` rows
        precede the ``saw_body`` row in the scan and are excluded by the strict
        ``tick < discovery_tick`` window, exactly the current-tick exclusion
        production applies.

        Firewall-clean: every row was witness-gated by the engine before it
        reached this agent's packet (``eval/leak_test.py``), and the accessor
        reports only this agent's own log; the teammate guard reads only this
        agent's own ``self_state``. Payload reads are defensive per the store
        convention — a malformed row contributes nothing. The returned tuple is
        deterministic: chronological discovery order, with the pinned subjects
        of each discovery emitted in sorted order.
        """

        fellows = self._fellow_impostor_ids_from_store()
        seen_bodies: set[str] = set()
        sightings: list[tuple[int, str, str]] = []  # (tick, room, player_id)
        records: list[BodyProximityRecord] = []
        for event in self._memory.episodic.recent(since_tick=0):
            if event.provenance != PROVENANCE_OBSERVED:
                continue
            if event.type == EVENT_SAW_PLAYER:
                player_id = event.payload.get("player_id")
                room = event.payload.get("room")
                if isinstance(player_id, str) and isinstance(room, str):
                    sightings.append((event.tick, room, player_id))
            elif event.type == EVENT_SAW_BODY:
                body_id = event.payload.get("body_id")
                room = event.payload.get("room")
                victim = event.payload.get("victim_id")
                if not (
                    isinstance(body_id, str)
                    and isinstance(room, str)
                    and isinstance(victim, str)
                ):
                    continue
                if body_id in seen_bodies:
                    # Rule 1 fires on a body's FIRST sighting only.
                    continue
                seen_bodies.add(body_id)
                co_present = {
                    pid
                    for tick, sroom, pid in sightings
                    if sroom == room
                    and 0 <= event.tick - tick <= BODY_PROXIMITY_WINDOW_TICKS
                    and tick < event.tick
                    and pid != victim
                    and pid not in fellows
                }
                for pid in sorted(co_present):
                    records.append(
                        BodyProximityRecord(subject=pid, room=room, tick=event.tick)
                    )
        return tuple(records)

    def observation_ids_for_meeting(self) -> tuple[ObservationId, ...]:
        """The agent's OWN stable episodic observation-id set (Task 16.5, C8).

        The self-channel accessor for the private-hard-evidence citation
        universe: every first-hand id-stamped episodic row's
        ``{agent_id}:{tick}:{seq}`` observation id, in append order. The
        manager validates a ballot's ``primary_reason_observation_id``
        against this set (:func:`meetings.manager._normalize_ballot_observation_id`)
        so a voter can only cite an observation it actually holds; an
        out-of-set citation nulls with the audit marker. Enforcement-free:
        no gate/guard/tally reads it until Task 16.6.

        Reads only ids stamped in perception at OBSERVED-event write sites,
        so reported testimony and the inferred global aggregate (both carry
        ``observation_id is None``) are naturally excluded -- the citation
        universe is first-hand evidence only. Firewall-clean: the ids name
        this agent's own memory rows and leak nothing. Append order is
        non-decreasing in tick (the episodic-store invariant) and the
        derivation is a pure function of the append history, so two
        reconstructions of the same replay return an identical tuple.
        """

        return tuple(
            event.observation_id
            for event in self._memory.episodic.recent(since_tick=0)
            if event.observation_id is not None
        )

    def absorb_meeting_evidence(
        self,
        *,
        accused: tuple[PlayerId, ...],
        corroborated: tuple[PlayerId, ...],
        contradicted: tuple[PlayerId, ...],
    ) -> None:
        """Fold one meeting's public evidence into stored beliefs (Task 9.8).

        Implements :class:`BeliefPersistingAgent` by delegating to the
        composite store (``agents.memory.store.absorb_meeting_evidence``),
        which mutates the SAME :class:`AgentMemory` belief state
        :meth:`suspicion_graph_for_meeting` snapshots -- so the bump a
        meeting writes here is what the next meeting's vote prompt sees.
        """

        absorb_meeting_evidence(
            self._memory,
            accused=accused,
            corroborated=corroborated,
            contradicted=contradicted,
        )

    def absorb_reported_testimony(
        self,
        *,
        statements: tuple[ReportedStatement, ...],
    ) -> None:
        """Fold one meeting's public testimony into memory as content (Task 13.5.2).

        Implements :class:`ReportedTestimonyAgent` by delegating to the composite
        store (``agents.memory.store.absorb_reported_testimony``), which appends
        ``provenance="reported"`` rows for OTHER speakers' structured claims and
        populates the alibi map on the SAME :class:`AgentMemory` the scalar fold
        and the meeting renderer read.
        """

        absorb_reported_testimony(self._memory, statements=statements)

    def note_meeting_concluded(
        self,
        *,
        end_tick: int,
        dead_ids: tuple[PlayerId, ...],
        emergency_caller_id: PlayerId | None,
        ejected_id: PlayerId | None = None,
        ejected_role: Role | None = None,
        votes_for_ejected: int | None = None,
        skip_votes: int | None = None,
        roster_impostor_count: int | None = None,
    ) -> None:
        """Fold one meeting's announced facts into memory + the tracker.

        Implements :class:`MeetingPacingAgent`. Two folds, in order:

        FIRST the meeting-history memory channel: the resume tick, the announced
        ejection with its tally, the ejected player's announced role and the
        roster impostor count -- all public at the table -- are recorded into
        this agent's OWN memory via
        :func:`~agents.memory.store.record_meeting_outcome`, which the v3
        tactical feature encoder reads and the ``## Meetings so far:`` render
        block renders. This fold is UN-gated by the
        emergency tracker: it runs for BOTH roles because the v3 encoder is
        impostor-side too, and an impostor has no tracker. The hook only ever
        reaches living agents, so the append is monotone in ``end_tick`` and
        the recorded history length IS this agent's meetings-survived count.

        THEN the crewmate emergency tracker (Task 10.8), unchanged: a no-op
        for an impostor agent (no tracker -- impostors gain no button
        behavior). The orchestrator calls this AFTER
        :meth:`absorb_meeting_evidence`, so the tracker's post-meeting
        over-gate baseline reads the folded beliefs and only a fresh
        below-to-above crossing re-arms the suspicion trigger.
        """

        record_meeting_outcome(
            self._memory,
            end_tick=end_tick,
            ejected_id=ejected_id,
            revealed_role=ejected_role,
            votes_for_ejected=votes_for_ejected,
            skip_votes=skip_votes,
            roster_impostor_count=roster_impostor_count,
        )
        if self._emergency_tracker is None:
            return
        self._emergency_tracker.observe_meeting_end(
            end_tick=end_tick,
            announced_dead=dead_ids,
            was_own_emergency_call=emergency_caller_id == self._agent_id,
            memory=self._memory.episodic,
            beliefs=self._memory.beliefs,
            own_id=self._agent_id,
        )


def _infer_role_from_policy(policy: CrewmatePolicy | ImpostorPolicy) -> Role:
    if isinstance(policy, ImpostorPolicy):
        return "IMPOSTOR"
    return "CREWMATE"


def build_default_agent_factory() -> AgentFactory:
    """Return the orchestrator's default :data:`AgentFactory`.

    Each constructed agent is a :class:`TacticalAgent` with the role-
    appropriate policy. Useful for ``scripts/run_game.py`` and for
    tests that just want a real, deterministic agent without
    scripting one.
    """

    def factory(agent_id: PlayerId, role: Role) -> AgentInterface:
        policy: CrewmatePolicy | ImpostorPolicy
        if role == "IMPOSTOR":
            policy = ImpostorPolicy(agent_id=agent_id)
        else:
            policy = CrewmatePolicy(agent_id=agent_id)
        return TacticalAgent(agent_id=agent_id, policy=policy, role=role)

    return factory


__all__ = [
    "AgentFactory",
    "BeliefPersistingAgent",
    "BodyDiscoveryAgent",
    "BodyProximityRecord",
    "DEFAULT_MAX_TICKS",
    "DEFAULT_NUM_IMPOSTORS",
    "DEFAULT_NUM_PLAYERS",
    "DEFAULT_PROMPT_VERSIONS",
    "DEFAULT_TASKS_PER_CREWMATE",
    "DefaultMeetingRunner",
    "HEADLESS_MEETING_DEADLINES",
    "HeadlessGame",
    "HeadlessGameResult",
    "IMPOSTOR_ROLL_CALL_PROMPT_VERSION_SETS",
    "KillWitnessRecord",
    "MeetingArtifacts",
    "MeetingAwareAgent",
    "MeetingPacingAgent",
    "MoveWitnessAgent",
    "MeetingRunner",
    "Outcome",
    "PROMPT_VERSION_SETS",
    "REPORTER_REASONING_PROMPT_VERSION_SETS",
    "ROSTER_PRESETS",
    "ReportedTestimonyAgent",
    "RosterPreset",
    "TacticalAgent",
    "UnrecordedGameResult",
    "UnrecordedMeetingStep",
    "UnrecordedTickStep",
    "apply_meeting_result",
    "build_default_agent_factory",
    "build_default_meeting_runner",
    "enabled_prompt_version_overlays",
    "prompt_versions_for_set",
]
