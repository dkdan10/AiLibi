"""Append-only JSONL replay log (DESIGN.md §11.4).

Each game produces a single replay file. Records are JSON objects, one
per line. The replay log has two kinds of records, discriminated by the
``kind`` field:

* ``"tick"`` — a :class:`ReplayEntry` written each tick by
  :meth:`ReplayLog.record_tick`. Carries the SUBMITTED actions, a state
  hash, and — when the recorder hands over the tick's engine events — an
  ``action_dispositions`` tuple saying which of those actions the engine
  applied, refused, or never reached because a meeting cut the tick off.
  This shape pre-dates Task 3.12 and is preserved for the existing
  engine-determinism tests (Task 2.8 byte-identity gate).
* ``"meeting"`` — a :class:`MeetingReplayEntry` written each time the
  orchestrator dispatches to ``MeetingManager`` and applies the
  :class:`MeetingResult`. Carries every artifact needed to reconstruct
  the meeting for replay/eval per DESIGN.md §11.4: the transcript
  (reports + statements), ballots, contradiction flags, the LLM-call
  records (prompt, response text, usage, cost, model) and the prompt
  template versions in play. The before/after state hashes pin the
  engine-owned mutation that resulted from applying the meeting
  outcome.

Engine determinism is unchanged: state hashes + recorded actions cover
the engine layer. LLM-layer determinism is achieved by replaying the
recorded LLM outputs rather than re-calling the provider; the records
written here are the per-meeting payload that future record/replay
clients consume.

Versioning (decision 10; DESIGN.md §11.4). The replay JSONL is
intentionally **unversioned**: none of the replay entry models
(:class:`ReplayEntry`, :class:`MeetingReplayEntry`,
:class:`GameEndReplayEntry`, :class:`FailedCallReplayEntry`) carries a
``format_version`` field, and none is added when the engine state model or
the meeting transcript shape changes. Two guards already reject any replay
recorded under a different model, so a version field would be redundant:
the per-tick ``state_hash`` byte-rejects a replay whose engine-state
serialization differs (a stale replay fails reconstruction rather than
mis-parsing), and the per-set ``roster.json`` sidecar pins the roster the
set was recorded at. The fail-loud version gate lives only on the offline
eval **report** (:data:`eval.report_schema.CURRENT_FORMAT_VERSION`), whose
shape is a fresh artifact; the replay bytes rely on the hash + sidecar
instead.

Provenance stamps on the ``game_over`` record (Task 15.9; audit
post-phase-14-ML-planning.md §7.2-7.3). Two ADDITIVE, OPTIONAL blocks
self-describe what generated a recording, so a replay answers *which* substrate
and *which* tactical policy produced its bytes without the operator remembering
the environment: :attr:`GameEndReplayEntry.substrate_flags` (Task 14.7) stamps
the substrate levers, and :attr:`GameEndReplayEntry.tactical_policy` (a
:class:`TacticalPolicyStamp`) stamps the tactical policy — ``{policy_id, method,
encoder_version, weights_sha256, anchor_policy}``, five plain strings set by the
recorder (no import of any training / agent code, keeping ``orchestrator/``'s
dependency direction clean for the phase-15 import-linter contracts). An ABSENT
tactical stamp means "scripted FSM default" and stays fully valid — the
committed canonical sets carry no stamp and reconstruct unchanged. Because
reconstruction re-feeds the recorded actions and never re-invokes a policy
(§3.4), the stamp is provenance, not a replay input — which keeps learned-policy
replays byte-identical regardless of inference-float questions. Task 15.12
corpus rows stamp the FSM default explicitly (:func:`fsm_default_tactical_policy_stamp`)
and Wave 2 stamps a champion's weights hash; the loader honors the stamp via
:class:`api.replay_loader.ReplayPolicyMismatchError`. Task 18.7 adds the parallel
CREW-side stamp (:attr:`GameEndReplayEntry.crew_tactical_policy`, a
:class:`CrewTacticalPolicyStamp`) in its own DISTINCT record class so a learned-crew
recording can never wear the impostor champion's stamp — ADDITIVE and OPTIONAL, an
absent crew stamp meaning the scripted :class:`agents.tactical.crewmate_policy.CrewmatePolicy`
default. Task 18.19 recordings carry BOTH stamps on one ``game_over`` row (a
dual-role co-evo game); :func:`read_policy_stamps` reads the pair back in one walk
into a :class:`PolicyStamps` named-slot tuple, each identity in its own typed slot
so the two can never be positionally conflated.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import fields, is_dataclass
import hashlib
import json
import os
from pathlib import Path
from typing import Annotated, Any, Final, Literal, NamedTuple, TextIO, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from orchestrator.experiment_config import (
    RecordedExperimentConfig,
    normalize_experiment_config,
    validate_recorded_experiment_config,
)
from agents.memory.store import (
    AgentMemory,
    record_meeting_outcome,
)
from engine.actions import Action
from engine.events import ActionRejectedEvent, EngineEvent, MeetingTriggeredEvent
from engine.world import WorldState
from meetings.constants import testimony_shapes_enabled
from meetings.corroboration import corroboration_discipline_enabled
from meetings.manager import (
    derive_meeting_outcome_summary,
    reporter_reasoning_enabled,
)
from meetings.schemas import (
    ContradictionRef,
    MeetingOutcome,
    MeetingResult,
    MeetingTranscript,
    PlayerId,
    VoteBallot,
)
from observation.version import temporal_observations_enabled

# The Task-18.10 impostor-answer lever, resolved LOCALLY instead of importing
# ``agents.strategic.prompts.loader.impostor_roll_call_enabled``: the loader
# builds its Jinja environment at IMPORT time from ``AILIBI_PROMPT_SET`` and
# raises on an unknown set, so importing it here would make every replay-only
# consumer (sample byte-verification, MANIFEST reads, the API replay loader)
# fail on a stray prompt-set export before reading a single JSONL row. The env
# name and truthy-token set mirror the loader's
# ``ENV_IMPOSTOR_ROLL_CALL`` / ``_IMPOSTOR_ROLL_CALL_FLAG_TRUE`` byte-for-byte,
# and ``tests/orchestrator/test_replay.py`` pins the two resolvers EQUIVALENT
# over the env grid (the CI substitute for the identity binding the other three
# levers keep — read-site and stamp cannot drift without that pin failing).
ENV_IMPOSTOR_ROLL_CALL: Final[str] = "AILIBI_IMPOSTOR_ROLL_CALL"
_IMPOSTOR_ROLL_CALL_FLAG_TRUE: Final[frozenset[str]] = frozenset(
    {"1", "true", "yes", "on"}
)


def _impostor_roll_call_enabled(env: Mapping[str, str] | None = None) -> bool:
    """The 18.10 lever's stamp-side resolver (mirrors the loader's, see above)."""

    environment = env if env is not None else os.environ
    return (
        environment.get(ENV_IMPOSTOR_ROLL_CALL, "").strip().lower()
        in _IMPOSTOR_ROLL_CALL_FLAG_TRUE
    )


class LLMCallRecord(BaseModel):
    """One LLM call captured during a meeting (DESIGN.md §11.4).

    Carries every field a record/replay client needs to reproduce the
    response without re-calling the provider: the prompt text, the
    structured response text, the provider-neutral token usage, the
    USD cost, and the model id the adapter actually called. The
    ``call_kind`` ("meeting" / "trigger") tag mirrors the LLM Protocol
    so replay records preserve which model-tier the call routed
    through.

    ``agent_id`` records which game-agent originated the call (the
    speaking participant for meeting calls), so per-call attribution
    survives into replay tooling (DESIGN.md §5, §11.4). It defaults to
    ``None`` so replay JSONLs written before this field existed still
    deserialize: ``extra="forbid"`` rejects unknown fields but permits a
    missing optional one. ``None`` also stands for genuinely agentless
    (system-level) calls.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    call_kind: Literal["meeting", "trigger"]
    model: str
    prompt: str
    response_text: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    agent_id: str | None = None


ActionDisposition: TypeAlias = Literal["applied", "rejected", "discarded_by_meeting"]
"""What the engine did with one submitted action on the tick that recorded it.

``applied`` -- the engine carried the action out. ``rejected`` -- the engine
attempted it and refused it (an ``ActionRejected`` event names the actor).
``discarded_by_meeting`` -- the action was never visited: an earlier-ordered
action in the same batch convened a meeting and ``engine.tick.advance_tick``
returned from inside the apply loop, so the action produced no effect and no
event of any kind.
"""


def classify_action_dispositions(
    actions: Sequence[Action], events: Sequence[EngineEvent]
) -> tuple[ActionDisposition, ...]:
    """Say what the engine did with each submitted action, in submitted order.

    ``events`` is the list :func:`engine.tick.advance_tick` returned for the
    SAME ``actions`` batch. Returns one :data:`ActionDisposition` per action,
    positionally aligned with ``actions``. Pure: no RNG, no clock, no I/O.

    Classification is by ACTOR, never by event position -- ``advance_tick``
    appends passive-effect events and a possible ``GameOver`` after the apply
    loop, so the event list is not positionally aligned with the action list.
    An actor index over ``actions`` is total because the orchestrator boundary
    admits exactly one action per actor per tick
    (:func:`orchestrator.action_ordering.order_actions_for_tick` raises
    ``ActionBatchValidationError`` on a duplicate).

    The two non-``applied`` verdicts are disjoint on engine output by
    construction: everything after the meeting cutoff is unreachable, so it can
    emit no rejection to be classified.
    """

    index_by_actor = {action.actor: index for index, action in enumerate(actions)}
    rejected_actors = frozenset(
        event.actor for event in events if isinstance(event, ActionRejectedEvent)
    )
    # A meeting cuts the tick off at the triggering actor's own action; every
    # later-ordered action in the batch is discarded unattempted.
    cutoff: int | None = None
    for event in events:
        if not isinstance(event, MeetingTriggeredEvent):
            continue
        triggered_at = index_by_actor.get(event.actor)
        if triggered_at is None:
            continue
        cutoff = triggered_at if cutoff is None else min(cutoff, triggered_at)

    dispositions: list[ActionDisposition] = []
    for index, action in enumerate(actions):
        if action.actor in rejected_actors:
            dispositions.append("rejected")
        elif cutoff is not None and index > cutoff:
            dispositions.append("discarded_by_meeting")
        else:
            dispositions.append("applied")
    return tuple(dispositions)


class ReplayEntry(BaseModel):
    """One per-tick replay record written by :meth:`ReplayLog.record_tick`.

    ``action_dispositions`` says what the engine DID with each submitted
    action, positionally aligned with :attr:`actions` (see
    :data:`ActionDisposition`). Additive and optional per the DESIGN.md §11.4
    unversioned-replay policy: ``None`` means the recording predates the field
    or was written without an event stream, and is NOT a claim that every
    action applied. A non-``None`` tuple must cover every action.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: Literal["tick"] = "tick"
    game_id: str
    tick: int
    actions: tuple[dict[str, Any], ...]
    action_dispositions: tuple[ActionDisposition, ...] | None = None
    state_hash: str
    temporal_observation_version: Literal[1] | None = None
    experiment_config: RecordedExperimentConfig | None = None

    @model_validator(mode="after")
    def _dispositions_cover_every_action(self) -> ReplayEntry:
        if self.action_dispositions is None:
            return self
        if len(self.action_dispositions) != len(self.actions):
            raise ValueError(
                f"action_dispositions has {len(self.action_dispositions)} entries "
                f"for {len(self.actions)} actions; the tuple is positional, so a "
                "length mismatch mis-attributes every entry past the gap and "
                "fails loud rather than being padded or truncated"
            )
        return self


class MeetingReplayEntry(BaseModel):
    """One meeting replay record (Task 3.12, DESIGN.md §11.4).

    Bundles every artifact the orchestrator persists when a meeting
    resolves. The :attr:`transcript`, :attr:`ballots`, and
    :attr:`contradictions` fields hold the structured payloads from
    :class:`MeetingResult` so eval scripts can read them without
    re-running the meeting. :attr:`llm_calls` carries the captured
    per-call telemetry needed for LLM-layer replay determinism.
    :attr:`prompt_versions` records the static version markers for
    each prompt template in play; bumping a template version while
    keeping the old replay around lets future tooling diff outputs
    across prompt revisions.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: Literal["meeting"] = "meeting"
    game_id: str
    meeting_id: str
    tick: int
    triggered_by: PlayerId
    outcome: MeetingOutcome
    ejected_player_id: PlayerId | None
    transcript: MeetingTranscript
    ballots: tuple[VoteBallot, ...]
    contradictions: tuple[ContradictionRef, ...]
    llm_calls: tuple[LLMCallRecord, ...]
    prompt_versions: Mapping[str, str]
    state_hash_before: str
    state_hash_after: str


class AbortedMeetingReplayEntry(BaseModel):
    """Captured calls from an unresolved meeting, without an engine transition."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: Literal["meeting_aborted"] = "meeting_aborted"
    game_id: str
    meeting_id: str
    tick: int
    llm_calls: tuple[LLMCallRecord, ...]
    prompt_versions: Mapping[str, str]
    error_type: str
    error_message: str


WinnerSide: TypeAlias = Literal["CREWMATES", "IMPOSTORS"]


def _validated_stamp_field(value: str) -> str:
    """Validate one provenance-stamp field, returning it unchanged or raising.

    The shared mechanics behind both provenance-stamp classes' ``@field_validator``
    (Task 15.9's :class:`TacticalPolicyStamp` and Task 18.7's
    :class:`CrewTacticalPolicyStamp`, audits/audit-phase-18-planning.md §4 #7): a
    stamp field is a single-line provenance token rendered into line-based
    artifacts — the JSONL replay row and the Markdown MANIFEST ``policy`` cell
    (``scripts/_manifest_writer.py``) — so a blank / whitespace-only value or one
    carrying a ``"|"`` / newline / carriage-return fails loud at the stamp boundary
    BEFORE any bad bytes are written (AGENTS.md "no silent fallbacks"). Extracting
    the mechanics here lets the crew stamp share the EXACT same discipline as the
    impostor stamp; see :meth:`TacticalPolicyStamp._reject_malformed_stamp_field`
    for the full per-shape rationale.
    """

    if not value.strip():
        raise ValueError(
            "tactical-policy stamp fields must be non-empty tokens; a blank / "
            f"whitespace-only value is forbidden (got {value!r})"
        )
    for forbidden, name in (
        ("|", "pipe"),
        ("\n", "newline"),
        ("\r", "carriage return"),
    ):
        if forbidden in value:
            raise ValueError(
                "tactical-policy stamp fields must be single-line and "
                f"MANIFEST-table-safe; a {name} is forbidden (got {value!r})"
            )
    return value


class TacticalPolicyStamp(BaseModel):
    """Provenance stamp for the tactical policy that produced a game's actions.

    Answers "which tactical policy produced these bytes" (Task 15.9; audit
    post-phase-14-ML-planning.md §7.2-7.3) the same way
    :attr:`GameEndReplayEntry.substrate_flags` answers "which substrate levers":
    a small block stamped onto the ``game_over`` record, beside the substrate
    stamp. Five plain-string fields, set by the RECORDER — no import of any
    training or agent code — so ``orchestrator/`` never gains a dependency on
    ``agents/`` or ``training/`` and the phase-15 import-linter contracts' clean
    dependency direction is preserved:

    * ``policy_id`` — the human identifier of the policy that decided the
      recorded tactical actions (``"fsm-default"`` for the scripted FSM, or a
      Wave-2 champion's id).
    * ``method`` — how the policy was produced (``"scripted-fsm"``, or a training
      method label such as ``"neuroevolution"`` / ``"ppo"``).
    * ``encoder_version`` — the observation-featurization version the policy
      consumes (``"none"`` for the FSM, which reads the typed packet directly).
    * ``weights_sha256`` — the content hash of the policy's committed weights
      artifact (``"none"`` for the FSM, which has no weights); for a learned
      policy this is the sha256 sidecar Task 15.11 commits under
      ``training/artifacts/surrogate/`` (or a champion's weights hash).
    * ``anchor_policy`` — the reference policy the learner stayed near (the
      piKL/CICERO anchor; ``"fsm-default"`` for the FSM, which is its own anchor).

    ADDITIVE and OPTIONAL on the replay (:attr:`GameEndReplayEntry.tactical_policy`
    defaults to ``None``): an ABSENT stamp means "scripted FSM default" and is
    fully valid — the committed canonical sets carry no stamp and keep loading,
    byte-verifying, and serving unchanged. Reconstruction re-feeds the recorded
    actions and NEVER re-invokes a policy (§3.4; §7.2), so the stamp is
    provenance, not a replay input — which is what keeps learned-policy replays
    byte-identical regardless of inference-float questions. The loader honors it
    (:class:`api.replay_loader.ReplayPolicyMismatchError`) by refusing to SERVE a
    stamped replay under a conflicting policy claim.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    policy_id: str
    method: str
    encoder_version: str
    weights_sha256: str
    anchor_policy: str

    @field_validator("*")
    @classmethod
    def _reject_malformed_stamp_field(cls, value: str) -> str:
        """Fail loud on a blank or line/table-breaking stamp field.

        A stamp is a single-line provenance token rendered into line-based
        artifacts — the JSONL replay row and the Markdown MANIFEST ``policy``
        cell (``scripts/_manifest_writer.py``). Two malformed shapes are rejected
        at the stamp boundary (model construction / ``--tactical-policy-stamp``
        JSON parse / replay read-back) so they fail loud BEFORE any bad bytes are
        written (AGENTS.md "no silent fallbacks"):

        * a ``"|"`` / newline / carriage-return — a pipe emits an unescaped extra
          MANIFEST column and a newline splits the row, so ``parse_manifest`` sees
          the wrong cell count and SILENTLY DROPS the row on the next manifest
          merge, losing that seed's provenance;
        * an EMPTY / whitespace-only field — an empty ``policy_id`` is
          indistinguishable from an ABSENT stamp at the MANIFEST renderer
          (``_render_policy`` would misattribute it as the ``fsm-default`` label
          even though the recording DID carry a stamp), and a whitespace-only cell
          round-trips to empty through ``parse_manifest``'s ``.strip()``. A
          well-formed stamp field is always a non-blank token.

        Every legitimate value — the ``fsm-default`` label, a champion id, a hex
        weights hash, a method / encoder / anchor label — is a single-line,
        non-blank, pipe-free token, so nothing valid is rejected. The mechanics
        live in the module-level :func:`_validated_stamp_field` so the Task-18.7
        crew stamp shares them byte-for-byte.
        """

        return _validated_stamp_field(value)


# The ``policy_id`` of the canonical scripted-FSM stamp (Task 15.9). It doubles
# as the MANIFEST ``policy`` column's label for an unstamped row, so a
# stamped-FSM replay and an unstamped one render IDENTICALLY — the "FSM default
# everywhere" invariant. An ABSENT stamp already means FSM default; an explicit
# ``--tactical-policy-stamp fsm-default`` recording stamps the full block below
# so a Task-15.12 corpus row can attribute the FSM default the SAME way a learned
# recording attributes a champion.
FSM_DEFAULT_POLICY_ID: Final[str] = "fsm-default"


def fsm_default_tactical_policy_stamp() -> TacticalPolicyStamp:
    """The canonical scripted-FSM :class:`TacticalPolicyStamp` (Task 15.9).

    The explicit stand-in for an absent stamp: the FSM has no encoder and no
    weights, so those two fields carry the ``"none"`` sentinel, and the FSM is its
    own piKL anchor. A recording made with ``--tactical-policy-stamp fsm-default``
    stamps exactly this (Task 15.12), so a corpus row attributes the FSM default
    the same way a Wave-2 champion recording attributes its weights hash.
    """

    return TacticalPolicyStamp(
        policy_id=FSM_DEFAULT_POLICY_ID,
        method="scripted-fsm",
        encoder_version="none",
        weights_sha256="none",
        anchor_policy=FSM_DEFAULT_POLICY_ID,
    )


class CrewTacticalPolicyStamp(BaseModel):
    """The CREW-side provenance stamp for a learned-crew recording (Task 18.7).

    The crew twin of :class:`TacticalPolicyStamp` (audits/audit-phase-18-planning.md
    §4 #7): a learned-crew recording names its crew policy in a DISTINCT record
    class so a crew recording can NEVER wear the impostor champion's stamp — the
    conflation guard (the CLI arm asserts distinct ``policy_id`` /
    ``weights_sha256`` namespaces across the two stamps). It carries the SAME five
    plain-string fields as the tactical stamp — ``policy_id`` / ``method`` /
    ``encoder_version`` / ``weights_sha256`` / ``anchor_policy`` — set by the
    RECORDER with no import of any training or agent code, so ``orchestrator/``
    keeps the clean phase-15 import-linter dependency direction; the shared
    :func:`_validated_stamp_field` helper enforces the single-line, non-blank,
    MANIFEST-table-safe token discipline on each, byte-for-byte with the impostor
    stamp.

    ADDITIVE and OPTIONAL on the replay
    (:attr:`GameEndReplayEntry.crew_tactical_policy` defaults to ``None``): an
    ABSENT crew stamp means the scripted
    :class:`agents.tactical.crewmate_policy.CrewmatePolicy` default (the untouched
    anchor), so a game with no crew stamp records and reconstructs
    byte-identically. Task 18.19 consumes this for dual-stamp recordings that
    carry BOTH an impostor tactical stamp and a crew stamp.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    policy_id: str
    method: str
    encoder_version: str
    weights_sha256: str
    anchor_policy: str

    @field_validator("*")
    @classmethod
    def _reject_malformed_stamp_field(cls, value: str) -> str:
        """Fail loud on a blank or line/table-breaking crew-stamp field.

        Delegates to the shared :func:`_validated_stamp_field` mechanics, so the
        crew stamp enforces the SAME single-line, non-blank, MANIFEST-table-safe
        token discipline as
        :meth:`TacticalPolicyStamp._reject_malformed_stamp_field` — the crew and
        impostor stamps render into the same line-based artifacts.
        """

        return _validated_stamp_field(value)


GameStopReason: TypeAlias = Literal["TICK_BUDGET_REACHED", "MEETING_PHASE_REACHED"]
CompletionStatus: TypeAlias = Literal[
    "completed", "aborted", "tick_limited", "unfinished"
]


class GameStopReplayEntry(BaseModel):
    """A normal nonterminal exit, labelled with the next engine tick.

    This additive row records why the runner stopped without claiming a winner.
    Older recordings without a stop row remain unfinished; their missing footer
    cannot distinguish a tick limit from an interruption.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: Literal["game_stopped"] = "game_stopped"
    game_id: str
    tick: int = Field(ge=0)
    reason: GameStopReason


class GameEndReplayEntry(BaseModel):
    """One game-outcome replay record (DESIGN.md §11.4; Task 3.19 finding 3).

    Written once per game by :meth:`ReplayLog.record_game_end` after the
    engine emits its ``GameOverEvent``, as the LAST row of a completed
    game's replay. Persisting the decisive outcome makes win-rate
    computable from any replay log via :func:`read_game_outcome` —
    including a partial tournament that crashed mid-run, where a
    ``game_over`` row is present for every game that finished before the
    crash. ``winner`` is ``None`` only for an unfinished / drawn game; the
    engine always names a side, so orchestrator-written rows always carry
    a winner.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: Literal["game_over"] = "game_over"
    game_id: str
    tick: int | None = None
    winner: WinnerSide | None
    reason: str
    # The substrate-lever config the game was recorded under (Task 14.7;
    # DESIGN.md §11.4 replay provenance). Stamps which levers
    # (``testimony_as_content`` / ``witnessed_kill_evidence`` /
    # ``movement_perception`` / ``unfreeze_memory``, all unconditionally ON
    # since Task 14.9) were active, so a replay SELF-DESCRIBES which substrate
    # generated it instead of relying on the operator remembering the env.
    # ADDITIVE and OPTIONAL, mirroring
    # ``FailedCallReplayEntry.rendered_vote_max``: it is ``None`` for every
    # legacy pre-stamp replay (the committed final-9B baseline predates the
    # field), so the reader tolerates its absence and those bytes reconstruct
    # unchanged; every post-14.9 recording stamps the full snapshot. The loader
    # honors it (``api.replay_loader``) by refusing to reconstruct a stamped
    # replay under a DIFFERENT ambient substrate — no silent cross-substrate
    # replay.
    substrate_flags: Mapping[str, bool] | None = None
    experiment_config: RecordedExperimentConfig | None = None
    # The tactical-policy provenance stamp (Task 15.9; DESIGN.md §11.4; audit
    # post-phase-14-ML-planning.md §7.2-7.3). Answers "which tactical policy
    # produced these bytes" the same way ``substrate_flags`` answers "which
    # substrate levers" — a five-string block set by the recorder, sitting beside
    # the substrate stamp. ADDITIVE and OPTIONAL: ``None`` means the scripted FSM
    # default (every committed canonical replay, which predates the stamp), so the
    # reader tolerates its absence and those bytes reconstruct unchanged; the
    # writer OMITS the key entirely when ``None`` (``ReplayLog.record_game_end``)
    # so an unstamped re-record stays byte-identical to the pre-15.9 game_over
    # row. A learned-policy (or explicit ``fsm-default``) recording stamps the
    # full block. The loader honors it (``api.replay_loader``) by refusing to
    # serve a stamped replay under a CONFLICTING policy claim.
    tactical_policy: TacticalPolicyStamp | None = None
    # The CREW-side tactical-policy provenance stamp (Task 18.7;
    # audits/audit-phase-18-planning.md §4 #7). Mirrors ``tactical_policy`` but
    # names the CREW policy in its own DISTINCT :class:`CrewTacticalPolicyStamp`
    # record class, so a learned-crew recording can never wear the impostor
    # champion's stamp (the conflation guard). ADDITIVE and OPTIONAL: ``None``
    # means the scripted crew default
    # (``agents.tactical.crewmate_policy.CrewmatePolicy``, the untouched anchor),
    # so the reader tolerates its absence and those bytes reconstruct unchanged;
    # the writer OMITS the key entirely when ``None``
    # (``ReplayLog.record_game_end``) so an unstamped re-record stays
    # byte-identical, and the committed sets — which predate the field — keep
    # parsing. A learned-crew recording stamps the full block; Task 18.19
    # consumes it for dual-stamp recordings.
    crew_tactical_policy: CrewTacticalPolicyStamp | None = None


class FailedCallReplayEntry(BaseModel):
    """A reported provider failure or a meeting-default visibility marker.

    Reported failures carry their actual usage and partial response. A default
    without separate usage is a zero-spend marker. Newly captured attempts carry
    ``call_id`` so identical paid responses are not collapsed by content.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: Literal["failed_call"] = "failed_call"
    game_id: str
    meeting_id: str
    tick: int
    model: str
    prompt_length: int
    raw_response: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    error_type: str
    error_message: str
    # The rendered §4.6 max suspicion of a DEFAULTED VOTE (Task 10.12; audit
    # 2026-06-13-1816 H-H-2). A defaulted ballot's vote call fails before the
    # recording client can log its prompt, so the offline §4.6 verdict
    # reconstruction (which reads the rendered max off successful meeting
    # ``llm_calls`` only) had no way to classify the defaulted ballot's true
    # MUST-vote / MUST-skip verdict -- it always read ``no-render``. The
    # manager now stamps the rendered max onto the ``deadline_default`` vote
    # row here. ADDITIVE and OPTIONAL: ``None`` for every non-vote failed call
    # and for every committed single-era replay (which predates the field), so
    # the reader tolerates its absence and existing bytes reconstruct
    # unchanged.
    rendered_vote_max: float | None = None
    # Present on newly captured attempts so identical responses from
    # distinct paid calls remain distinct. Legacy rows retain content dedup.
    call_id: str | None = None


ReplayLogEntry: TypeAlias = Annotated[
    ReplayEntry
    | MeetingReplayEntry
    | AbortedMeetingReplayEntry
    | GameEndReplayEntry
    | GameStopReplayEntry
    | FailedCallReplayEntry,
    Field(discriminator="kind"),
]


def recorded_experiment_config(
    entries: Sequence[ReplayLogEntry],
) -> RecordedExperimentConfig | None:
    """Resolve one immutable experimental profile, including partial recordings."""

    ends = [entry for entry in entries if isinstance(entry, GameEndReplayEntry)]
    if len(ends) > 1:
        raise ValueError("multiple terminal experiment configurations")
    return validate_recorded_experiment_config(
        [
            entry.experiment_config
            for entry in entries
            if isinstance(entry, ReplayEntry)
        ],
        terminal_config=ends[0].experiment_config if ends else None,
        terminal_present=bool(ends),
    )


def require_baseline_experiments(
    entries: Sequence[ReplayLogEntry], *, consumer: str
) -> None:
    """Refuse experimental runs in an instrument that implements baseline rules."""

    if recorded_experiment_config(entries) is not None:
        raise ValueError(f"{consumer} does not support experimental recordings")


def recorded_testimony_shapes(entries: Sequence[ReplayLogEntry]) -> bool:
    """Bind testimony reconstruction to recorded versions, never the shell.

    Resolved meetings carry prompt versions even in interrupted recordings.
    Pre-version custom/legacy meetings use the historical OFF fold. A terminal
    stamp may identify a custom runner, but cannot contradict versioned speech.
    """

    versions = {
        any(
            part.endswith(".testimony_shapes")
            for value in entry.prompt_versions.values()
            for part in value.split("+")
        )
        for entry in entries
        if isinstance(entry, MeetingReplayEntry) and entry.prompt_versions
    }
    if len(versions) > 1:
        raise ValueError("testimony shape version changes between meetings")
    flags = [
        entry.substrate_flags
        for entry in entries
        if isinstance(entry, GameEndReplayEntry) and entry.substrate_flags is not None
    ]
    if flags:
        stamped = flags[0].get("testimony_shapes", False)
        if versions and stamped not in versions:
            raise ValueError("testimony shape version disagrees with substrate stamp")
        return stamped
    return versions == {True}


def recorded_temporal_observations(entries: Sequence[ReplayLogEntry]) -> bool:
    """Read and validate the evidence version, including interrupted prefixes."""

    versions = {
        entry.temporal_observation_version
        for entry in entries
        if isinstance(entry, ReplayEntry)
    }
    if len(versions) > 1:
        raise ValueError("mixed temporal observation versions in one replay")
    enabled = versions == {1}
    for entry in entries:
        if isinstance(entry, GameEndReplayEntry) and entry.substrate_flags is not None:
            if (
                bool(entry.substrate_flags.get("temporal_observations", False))
                != enabled
            ):
                raise ValueError(
                    "temporal observation version disagrees with substrate stamp"
                )
    return enabled


def require_legacy_observations(
    entries: Sequence[ReplayLogEntry], *, consumer: str
) -> None:
    """Refuse new evidence in a frozen instrument that has no temporal adapter."""

    if recorded_temporal_observations(entries):
        raise ValueError(f"{consumer} does not support temporal observations")


def recorded_completion_status(entries: Sequence[ReplayLogEntry]) -> CompletionStatus:
    """Classify recorded evidence without certifying its integrity or outcome."""
    if any(isinstance(entry, GameEndReplayEntry) for entry in entries):
        return "completed"
    if any(isinstance(entry, AbortedMeetingReplayEntry) for entry in entries):
        return "aborted"
    for entry in entries:
        if isinstance(entry, GameStopReplayEntry):
            return (
                "tick_limited"
                if entry.reason == "TICK_BUDGET_REACHED"
                else "unfinished"
            )
    # Older providers retained a failed attempt without an explicit abort row.
    # A failed attempt associated with a completed meeting is recovered, not an abort.
    completed = {
        entry.meeting_id for entry in entries if isinstance(entry, MeetingReplayEntry)
    }
    if any(
        isinstance(entry, FailedCallReplayEntry) and entry.meeting_id not in completed
        for entry in entries
    ):
        return "aborted"
    return "unfinished"


# The substrate levers a baseline record has ADOPTED: unconditionally ON, their
# ``AILIBI_*`` env gates deleted, kept in the snapshot as provenance so the
# loader can still refuse a legacy stamp that recorded one of them OFF. Mirrors
# ``experiments.lab.probe_backends.active_substrate_flags`` exactly, so the
# recorded MANIFEST ``flags`` column, the sweep result rows and the replay stamp
# all describe the same levers with identical keys. A bare-environment recording
# stamps every key in THIS tuple ``True`` and every live toggle below ``False`` —
# which IS the committed baseline-7 substrate.
#
# Order is graduation order and only ever grows at the end, so every already
# recorded key keeps its index. The adopting records: Task 14.9 (the four
# Phase-13.5 levers), 14.12, 15.7, 16.17 (the three Phase-16 levers), 18.12 (the
# four meeting-layer levers, CREW-ONLY ruling) and the baseline-7 record (the
# eight Phase-20 evidence-honesty levers, adopted by owner override of a FINDING
# verdict — audits/audit-phase-20-baseline-7.md §6.1).
_RETIRED_ALWAYS_ON_LEVERS: Final[tuple[str, ...]] = (
    "testimony_as_content",
    "witnessed_kill_evidence",
    "movement_perception",
    "unfreeze_memory",
    "evidence_quality_lift",
    "reporter_exculpation",
    "hard_evidence_gate",
    "observation_id_rendering",
    "citation_gate",
    "absence_prior",
    "roll_call_round",
    "whereabouts_interior_flags",
    "vent_placement_contradictions",
    "task_completion_from_events",
    "self_location_trail",
    "movement_claim_shape",
    "grounded_prosecution",
    "map_aware_arbitration",
    "structured_turn_markers",
    "meeting_outcome_memory",
    "coalesced_memory_render",
)

# (key, resolver) pairs for every lever that still consults an ``AILIBI_*`` env
# var. Declared here in source and never mutated at runtime (an immutable
# ``Final`` tuple, per AGENTS.md "no module-level mutable state"), so nothing can
# silently change a replay stamp or the loader's mismatch check mid-process. Each
# resolver takes the optional ``env`` mapping and returns the lever's live state.
#
# FOUR live toggles, all DEFAULT-OFF:
#
# * ``impostor_roll_call`` — 18.10's impostor-answer template arm, bound to a
#   LOCAL mirror with a CI equivalence pin standing in for the identity (the
#   mirror's own comment block states why it is local);
# * ``reporter_reasoning`` — the reporter-voice arm, bound to the manager's
#   resolver BY IDENTITY. This module already imports ``meetings.manager``, and
#   that module's own imports never reach ``agents.strategic.prompts.loader``, so
#   the import-time Jinja build that forced the other arm's mirror does not apply
#   and one source of truth beats two that agree;
# * ``corroboration_discipline`` — the ballot's source-count block, bound BY
#   IDENTITY to ``meetings.corroboration``, whose own imports reach only
#   ``meetings.schemas`` / ``constants`` / ``transcript`` and so trigger no Jinja
#   build either;
# * ``testimony_shapes`` — what a witness may SAY and what a listener KEEPS of
#   it, bound BY IDENTITY to ``meetings.constants``. That module is a
#   stdlib-only leaf, which is exactly why the lever is homed there: the meeting
#   reduction and the prompt loader must read ONE lever and the ``agents ↛
#   meetings.manager`` contract forbids the manager as its home.
#
# * ``temporal_observations`` — source-time evidence delivery, bound to the
#   stdlib-only observation version resolver.
#
# All five are LEVERS: an arm a future gate may decide to ship, which would
# graduate it into ``_RETIRED_ALWAYS_ON_LEVERS`` at its adopting record.
#
# A bare environment stamps all five ``False``, which IS the committed substrate: the
# missing-key-reads-False rule makes a stamp recorded before a key existed agree
# with a build that has it. A lever graduates by moving into
# ``_RETIRED_ALWAYS_ON_LEVERS`` at the record that adopts it — which appends it
# to the retired half and so shifts every remaining toggle's index in
# ``SUBSTRATE_FLAG_KEYS``. A REPAIR gate is not a lever and graduates differently:
# it is deleted outright and promoted nowhere, which is what keeps the retired
# half's twenty-one-key string — and the MANIFEST ``flags`` cell derived from it —
# byte-identical across the flip. Registration order, newest last.
_TOGGLEABLE_LEVER_RESOLVERS: Final[
    tuple[tuple[str, Callable[[Mapping[str, str] | None], bool]], ...]
] = (
    ("impostor_roll_call", _impostor_roll_call_enabled),
    ("reporter_reasoning", reporter_reasoning_enabled),
    ("corroboration_discipline", corroboration_discipline_enabled),
    ("testimony_shapes", testimony_shapes_enabled),
    ("temporal_observations", temporal_observations_enabled),
)

# The still-toggleable subset of ``SUBSTRATE_FLAG_KEYS`` (Task 14.10):
# levers whose active state is an ``AILIBI_*`` env read, so a stamp/ambient
# mismatch on one of THESE is remediable by matching the environment to the
# stamp — unlike the retired levers, whose OFF derivation no longer exists.
# The loader's substrate-mismatch error branches its remediation hint on
# this split.
TOGGLEABLE_SUBSTRATE_FLAG_KEYS: Final[tuple[str, ...]] = tuple(
    key for key, _ in _TOGGLEABLE_LEVER_RESOLVERS
)

# The canonical stamp key order: the retired levers in graduation order, then the
# live toggles in registration order. Both halves only ever grow at their own end,
# so every already-recorded key keeps its index and a new lever is a pure append.
SUBSTRATE_FLAG_KEYS: Final[tuple[str, ...]] = (
    *_RETIRED_ALWAYS_ON_LEVERS,
    *TOGGLEABLE_SUBSTRATE_FLAG_KEYS,
)


def substrate_flag_snapshot(
    env: Mapping[str, str] | None = None,
) -> dict[str, bool]:
    """Snapshot the live substrate-lever config a recording stamps.

    The twenty-one retired levers report unconditionally ``True``: their
    ``*_enabled()`` env gates were deleted at the records that adopted them, so
    the unconditional derivation is the only substrate this build can produce.
    They stay in the snapshot as provenance, which is what lets the loader's
    mismatch guard still refuse a legacy stamp recording one of them OFF.

    The live toggles resolve from the immutable ``_TOGGLEABLE_LEVER_RESOLVERS``
    table with ``env`` threaded through (defaulting to the live process
    environment). Each is DEFAULT-OFF, so a bare environment agrees with the
    committed stamp — which names ``impostor_roll_call`` OFF and predates
    ``reporter_reasoning``, ``corroboration_discipline`` and
    ``testimony_shapes`` entirely (a missing key reads OFF) — and each
    ``AILIBI_*`` export flips exactly its own key: the deterministic seam the
    recorders, the MANIFEST ``flags`` column and the sweep configs rely on to
    prove which arms a recording ran under.
    """

    snapshot = dict.fromkeys(_RETIRED_ALWAYS_ON_LEVERS, True)
    for key, resolver in _TOGGLEABLE_LEVER_RESOLVERS:
        snapshot[key] = resolver(env)
    return snapshot


def env_var_for_lever(key: str) -> str:
    """The ``AILIBI_*`` variable a substrate-lever registry key derives."""

    return f"AILIBI_{key.upper()}"


def retired_levers_stamped_off(
    substrate_flags: Mapping[str, bool] | None,
) -> list[str]:
    """Retired levers a recording's stamp claims were OFF, in registry order.

    A retired lever has no env gate: its OFF derivation was deleted at the
    record that adopted it, so a stamp naming one OFF describes a substrate this
    build cannot reproduce. Consumers that re-derive from recorded bytes WITHOUT
    going through the API replay loader's own substrate guard -- the audit
    workflows' ``$0`` re-extraction spine -- call this and refuse on a non-empty
    result, rather than silently scoring legacy bytes with the current detector.

    An UNSTAMPED recording (``None``) returns empty: its substrate is unknown,
    not OFF, and it is never checked -- mirroring
    :class:`api.replay_loader.ReplaySubstrateMismatchError`, which skips an
    unstamped replay entirely. Within a stamp that IS present, a MISSING key
    reads OFF exactly as the loader's ``bool(recorded.get(key))`` reads it: a
    recording made before a lever existed ran without it, which is precisely the
    substrate this build can no longer produce.

    One half of one axis: :func:`substrate_stamp_mismatches` is the full
    comparison, which also reports live toggles set the other way and keys the
    recording carries that this build's registry does not.
    """

    if substrate_flags is None:
        return []
    return [
        key for key in _RETIRED_ALWAYS_ON_LEVERS if not bool(substrate_flags.get(key))
    ]


class SubstrateStampMismatch(BaseModel):
    """How a recording's substrate stamp diverges from an ambient snapshot.

    Two classes, reported separately because they mean different things and
    remediate differently. ``differing`` names registry keys whose recorded
    boolean disagrees with the ambient one -- a lever this build knows, recorded
    the other way. ``unknown`` names keys the recording carries that this
    build's registry does not: the stamp was written by a build that had
    registered a lever this one has never heard of, so no export can reach that
    substrate and the recording is simply from the future.

    Empty on both axes is a match, which is what ``bool()`` reports, so a caller
    reads the verdict rather than re-deriving it.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    differing: tuple[str, ...]
    unknown: tuple[str, ...]

    def __bool__(self) -> bool:
        return bool(self.differing or self.unknown)


def substrate_stamp_mismatches(
    recorded: Mapping[str, bool] | None,
    *,
    ambient: Mapping[str, bool] | None = None,
) -> SubstrateStampMismatch:
    """Compare a recording's substrate stamp against a snapshot, BOTH directions.

    The shared comparison behind every substrate refusal: the API loader's
    reconstruction guard and the audit workflows' ``$0`` re-extraction spine both
    call it, so a stamp is judged the same way wherever it is read. ``ambient``
    defaults to :func:`substrate_flag_snapshot`, the live slate.

    Both directions matter because the registry is append-only at each half's own
    end: a stamp from an OLDER build is a strict SUBSET of this one's keys, and
    the missing ones read OFF on both sides, so it compares cleanly. A stamp from
    a NEWER build carries keys this registry never had -- a lever whose behavior
    this build cannot reproduce and cannot even name -- and comparing only the
    keys this build knows would wave it through silently.

    An UNSTAMPED recording (``None``) is never checked: its substrate is unknown,
    not divergent.
    """

    if recorded is None:
        return SubstrateStampMismatch(differing=(), unknown=())
    snapshot = ambient if ambient is not None else substrate_flag_snapshot()
    return SubstrateStampMismatch(
        differing=tuple(
            sorted(
                key
                for key in SUBSTRATE_FLAG_KEYS
                if bool(recorded.get(key)) != bool(snapshot.get(key))
            )
        ),
        unknown=tuple(sorted(set(recorded) - set(SUBSTRATE_FLAG_KEYS))),
    )


def substrate_slate_mismatches(
    expected_on: Iterable[str],
    *,
    env: Mapping[str, str] | None = None,
) -> list[str]:
    """Compare the live lever slate against the slate an operator expects ON.

    The recorders' pre-spend gate: a multi-hour record is only worth starting
    once the environment it will record under is the environment that was ruled.
    ``expected_on`` names the TOGGLEABLE keys the operator intends ON; every
    other toggleable key must be OFF. Returns one human-readable line per
    deviation, and an EMPTY list when the slate matches -- so a caller refuses on
    a non-empty result and never re-derives the comparison itself.

    Three failure classes, all fatal to a record:

    * an expectation that is not a live toggle -- a typo, or a graduated lever
      whose env gate no longer exists. An expectation that is silently ignored
      would defeat the whole point of a positive check, so it is reported first;
    * a toggleable lever whose live state differs from the expectation, in
      EITHER direction (an expected-ON lever left unexported is as fatal as a
      stale export nobody asked for);
    * a lever registered as BOTH graduated and toggleable -- a half-finished
      graduation (the retired entry added, the resolver not deleted). Checked
      STRUCTURALLY, not by value: it is the registry that is broken, so a truthy
      stale export must not make it look healthy, and no declaration may excuse
      it. It is also the only way a graduated lever can read OFF at all --
      :func:`substrate_flag_snapshot` seeds every retired key ``True`` and only a
      surviving resolver can overwrite one.
    """

    wanted = set(expected_on)
    live = substrate_flag_snapshot(env)
    toggleable = set(TOGGLEABLE_SUBSTRATE_FLAG_KEYS)
    registry = set(SUBSTRATE_FLAG_KEYS)
    problems: list[str] = []
    for key in sorted(wanted - toggleable):
        if key in registry:
            problems.append(
                f"{key!r} is a graduated lever (unconditionally ON, no env gate) "
                "and cannot be named as an expected toggle"
            )
        else:
            problems.append(f"{key!r} is not a lever in the registry")
    for key in sorted(toggleable & set(_RETIRED_ALWAYS_ON_LEVERS)):
        problems.append(
            f"{key} is registered as BOTH a graduated lever and a live toggle "
            "(a half-finished graduation: delete its resolver, or drop the "
            "retired entry) -- this build cannot produce the substrate the "
            "record would claim"
        )
    for key in TOGGLEABLE_SUBSTRATE_FLAG_KEYS:
        want = key in wanted
        if bool(live.get(key, False)) is not want:
            problems.append(
                f"{key} must be {'ON' if want else 'OFF'} but the live slate "
                f"reads {'ON' if live.get(key, False) else 'OFF'} "
                f"({env_var_for_lever(key)})"
            )
    return problems


def fold_meeting_outcome_into_memories(
    result: MeetingResult,
    *,
    state: WorldState,
    memories: Mapping[str, AgentMemory],
) -> None:
    """Fold one applied meeting's public outcome into every living agent's memory.

    The ONE reconstruction-side implementation of the live loop's post-meeting
    meeting-history fold (``orchestrator.game._notify_meeting_concluded``): the
    replay loader, the prompt byte-golden walk and the evidence-honesty walk all
    call THIS function, so no reconstruction can render a ``## Meetings so far:``
    block the live run that recorded the bytes would not have rendered.

    ``state`` is the POST-``apply_meeting_result`` world -- its ``tick`` is the
    resume tick every player heard announced -- and ``result`` the recorded
    meeting. Everything folded is public at the table: the resume tick, the
    announced ejection and its tally, the ejected player's confirm-ejects role,
    and the impostor count stated at game start (a roster count, which is why it
    is read off the roles in ``state`` rather than threaded in). A KILLED
    player's role is never read: nobody at the table saw it.

    It lives beside the substrate stamp because this is the module every
    reconstruction path already imports, and because the fold's own stamp key
    (``meeting_outcome_memory``) is registered here. It graduated at the
    baseline-7 record, so the channel reaches every rendered byte.
    """

    summary = derive_meeting_outcome_summary(result)
    ejected_id = summary.ejected_id
    revealed_role = None if ejected_id is None else state.players[ejected_id].role
    roster_impostor_count = sum(
        1 for player in state.players.values() if player.role == "IMPOSTOR"
    )
    for player_id in sorted(state.players):
        if not state.players[player_id].alive:
            continue
        record_meeting_outcome(
            memories[player_id],
            end_tick=state.tick,
            ejected_id=ejected_id,
            revealed_role=revealed_role,
            votes_for_ejected=summary.votes_for_ejected,
            skip_votes=summary.skip_votes,
            roster_impostor_count=roster_impostor_count,
        )


class ReplayLog:
    """Append-only JSONL replay log for deterministic game replays.

    Fail-loud on an already-existing target (DESIGN.md §11.4; Task 4.16):
    constructing a log against a path that already holds a file raises
    :class:`AlreadyExistsError` unless ``force=True`` is passed, which
    truncates the existing file first. This guards the silent doubled-file
    corruption that bit the project in Phase 4 UX prep — two tournament runs
    against the same ``--output-dir`` concatenated per-seed JSONL files,
    breaking the loader's ``meeting_by_tick`` dedup. The read side
    (:func:`read_all_entries`) detects the same doubled pattern after the
    fact and raises :class:`CorruptedFileError`.
    """

    class AlreadyExistsError(FileExistsError):
        """Raised when a :class:`ReplayLog` targets an existing path without
        ``force=True``.

        Prevents the doubled-files corruption pattern (two runs appending to
        the same per-seed JSONL) that broke ``meeting_by_tick`` dedup in
        Phase 4 UX prep. Subclasses :class:`FileExistsError` so callers that
        only catch the stdlib type still intercept it.
        """

    class CorruptedFileError(RuntimeError):
        """Raised by :func:`read_all_entries` when it detects the doubled-file
        pattern: two ``kind="tick"`` rows sharing a ``tick`` value, or more
        than one ``kind="game_over"`` row in a single replay file.
        """

    def __init__(
        self,
        path: Path,
        game_id: str,
        *,
        force: bool = False,
        tactical_policy_stamp: TacticalPolicyStamp | None = None,
        crew_tactical_policy_stamp: CrewTacticalPolicyStamp | None = None,
        temporal_observations: bool | None = None,
        substrate_flags: Mapping[str, bool] | None = None,
        experiment_config: RecordedExperimentConfig | None = None,
    ) -> None:
        # ``tactical_policy_stamp`` is the recorder-supplied provenance stamp
        # (Task 15.9) written onto the ``game_over`` record by
        # :meth:`record_game_end`. Default ``None`` = absent = scripted FSM
        # default, byte-identical to the pre-15.9 writer. The stamp rides the
        # WRITER (not ``record_game_end``'s signature) so the many direct
        # ``record_game_end`` callers (unit tests, eval/determinism_test.py) stay
        # untouched and record the FSM default.
        self._tactical_policy_stamp = tactical_policy_stamp
        # ``crew_tactical_policy_stamp`` is the CREW-side twin (Task 18.7): the
        # recorder-supplied crew provenance stamp written onto the same
        # ``game_over`` record. Default ``None`` = absent = scripted crew default
        # (``agents.tactical.crewmate_policy.CrewmatePolicy``), byte-identical to
        # the pre-18.7 writer. Kept in its own DISTINCT field so a crew recording
        # can never wear the impostor champion's stamp (the conflation guard).
        self._crew_tactical_policy_stamp = crew_tactical_policy_stamp
        self.temporal_observations = (
            temporal_observations_enabled()
            if temporal_observations is None
            else temporal_observations
        )
        self._substrate_flags = dict(
            substrate_flag_snapshot() if substrate_flags is None else substrate_flags
        )
        self._substrate_flags["temporal_observations"] = self.temporal_observations
        self.experiment_config = normalize_experiment_config(experiment_config)
        # Assigned first so __del__ is safe even if construction raises below
        # (e.g. AlreadyExistsError on an existing path).
        self._handle: TextIO | None = None
        if path.exists():
            if not force:
                raise self.AlreadyExistsError(
                    f"Replay file already exists: {path}. Pass force=True to "
                    "overwrite it, or choose a different path. (Re-using a "
                    "replay path silently doubled per-seed files in Phase 4 "
                    "and broke the loader's dedup — DESIGN.md §11.4.)"
                )
            # force=True: truncate via delete-then-recreate so the new game
            # starts from an empty file rather than appending to the old one.
            path.unlink()
        self._path = path
        self._game_id = game_id
        self._path.parent.mkdir(parents=True, exist_ok=True)
        # Single-write guard for failed-call rows (Task 9.10, audit gp-4):
        # every row already written by :meth:`record_failed_call`, keyed by
        # the full frozen entry. See that method for the dedup contract.
        self._recorded_failed_calls: set[FailedCallReplayEntry] = set()

    @property
    def path(self) -> Path:
        return self._path

    @property
    def game_id(self) -> str:
        return self._game_id

    def record_tick(
        self,
        tick: int,
        actions: list[Action],
        state: WorldState,
        *,
        events: Sequence[EngineEvent] | None = None,
    ) -> None:
        """Persist one tick: the submitted actions and the post-advance hash.

        Pass ``events`` -- the list :func:`engine.tick.advance_tick` returned
        for this same batch -- and the row also records what the engine DID
        with each action (:func:`classify_action_dispositions`). Omit it and the
        ``action_dispositions`` key is left OUT of the row entirely: a recorder
        with no event stream cannot claim a disposition, and an absent key must
        stay distinguishable from a recorded all-``applied`` tick.
        """

        entry: dict[str, Any] = {
            "kind": "tick",
            "game_id": self._game_id,
            "tick": tick,
            "actions": _serialize_actions(actions),
            "state_hash": _state_hash(state),
        }
        if events is not None:
            entry["action_dispositions"] = list(
                classify_action_dispositions(actions, events)
            )
        if self.temporal_observations:
            entry["temporal_observation_version"] = 1
        if self.experiment_config is not None:
            entry["experiment_config"] = self.experiment_config.model_dump(mode="json")
        self._append(entry)

    def record_meeting(
        self,
        *,
        meeting_id: str,
        result: MeetingResult,
        llm_calls: Sequence[LLMCallRecord],
        prompt_versions: Mapping[str, str],
        state_hash_before: str,
        state_hash_after: str,
    ) -> None:
        """Persist one resolved meeting (DESIGN.md §11.4).

        ``state_hash_before`` / ``state_hash_after`` pin the engine
        state on either side of :meth:`HeadlessGame._apply_meeting_result`
        so a replay can verify the meeting outcome was applied byte-
        identically to the engine-owned world state.
        """

        entry = MeetingReplayEntry(
            game_id=self._game_id,
            meeting_id=meeting_id,
            tick=result.trigger_tick,
            triggered_by=result.triggered_by,
            outcome=result.outcome,
            ejected_player_id=result.ejected_player_id,
            transcript=result.transcript,
            ballots=result.ballots,
            contradictions=result.contradictions,
            llm_calls=tuple(llm_calls),
            prompt_versions=dict(prompt_versions),
            state_hash_before=state_hash_before,
            state_hash_after=state_hash_after,
        )
        self._append(entry.model_dump(mode="json"))

    def record_game_stop(self, *, tick: int, reason: GameStopReason) -> None:
        """Persist a normal nonterminal stop after the last recorded transition."""
        entry = GameStopReplayEntry(game_id=self._game_id, tick=tick, reason=reason)
        self._append(entry.model_dump(mode="json"))

    def record_game_end(
        self,
        *,
        winner: WinnerSide | None,
        reason: str,
        tick: int | None = None,
    ) -> None:
        """Persist the decisive game outcome (DESIGN.md §11.4; Task 3.19).

        Emitted once by :meth:`HeadlessGame.run` after the engine fires
        its ``GameOverEvent``, as the final row of a completed game's
        replay. :func:`read_game_outcome` reads it back so win-rate is
        evaluable from any replay log, including partial tournaments.
        ``tick`` defaults to ``None`` for callers (e.g. unit tests) that
        only care about the winner; the orchestrator passes the
        game-over tick.
        """

        # Stamp the active substrate config (Task 14.7) so the replay
        # self-describes which levers generated it. Since Task 14.9 the four
        # 13.5 levers are unconditionally ON, so every new recording carries a
        # full snapshot (matching the committed 14.7 baseline's stamp); the
        # omit-when-all-OFF branch that kept a flag-OFF run byte-identical to
        # the pre-14.7 format is retired with the flags. Legacy unstamped
        # replays are a READ-side concern only (the loader tolerates the
        # field's absence).
        entry = GameEndReplayEntry(
            game_id=self._game_id,
            tick=tick,
            winner=winner,
            reason=reason,
            substrate_flags=self._substrate_flags,
            experiment_config=self.experiment_config,
            tactical_policy=self._tactical_policy_stamp,
            crew_tactical_policy=self._crew_tactical_policy_stamp,
        )
        payload = entry.model_dump(mode="json")
        if entry.experiment_config is None:
            del payload["experiment_config"]
        # Byte-identity carve-out for the tactical-policy stamp (Task 15.9): an
        # ABSENT stamp is the FSM default and MUST record byte-identically to the
        # pre-15.9 game_over row, so the optional field is OMITTED from the JSON
        # when ``None`` rather than written as ``"tactical_policy": null`` (which
        # would perturb the committed-sample bytes and every unstamped re-record).
        # A present stamp is written as the nested five-string block beside
        # ``substrate_flags``; ``_stable_json`` sorts keys, so field order never
        # matters.
        if entry.tactical_policy is None:
            del payload["tactical_policy"]
        # Mirrored byte-identity carve-out for the crew stamp (Task 18.7): an
        # ABSENT crew stamp is the scripted crew default and MUST record
        # byte-identically to the pre-18.7 game_over row, so the optional field is
        # OMITTED when ``None`` rather than written as ``"crew_tactical_policy":
        # null``. A present crew stamp is written as its own nested five-string
        # block beside ``tactical_policy``.
        if entry.crew_tactical_policy is None:
            del payload["crew_tactical_policy"]
        self._append(payload)

    def record_aborted_meeting(
        self,
        *,
        meeting_id: str,
        tick: int,
        llm_calls: Sequence[LLMCallRecord],
        prompt_versions: Mapping[str, str],
        error_type: str,
        error_message: str,
    ) -> None:
        """Persist a drained attempt's calls without claiming a resolution.

        Each call in the tuple is a distinct response, even if two responses
        have identical content. The runner transfers the buffer once.
        """

        entry = AbortedMeetingReplayEntry(
            game_id=self._game_id,
            meeting_id=meeting_id,
            tick=tick,
            llm_calls=tuple(llm_calls),
            prompt_versions=prompt_versions,
            error_type=error_type,
            error_message=error_message[:200],
        )
        self._append(entry.model_dump(mode="json"))

    def record_failed_call(
        self,
        *,
        meeting_id: str,
        tick: int,
        model: str,
        prompt_length: int,
        raw_response: str,
        input_tokens: int,
        output_tokens: int,
        cost_usd: float,
        error_type: str,
        error_message: str,
        rendered_vote_max: float | None = None,
        call_id: str | None = None,
    ) -> None:
        """Persist reported failure usage or a zero-spend default marker.

        Identical rows are written once. Callers recording distinct paid
        attempts supply distinct ``call_id`` values even when response content
        matches. Calls without an identity retain the legacy content-based
        deduplication and omit the new field from serialized bytes.
        """

        entry = FailedCallReplayEntry(
            game_id=self._game_id,
            meeting_id=meeting_id,
            tick=tick,
            model=model,
            prompt_length=prompt_length,
            raw_response=raw_response,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
            error_type=error_type,
            error_message=error_message,
            rendered_vote_max=rendered_vote_max,
            call_id=call_id,
        )
        if entry in self._recorded_failed_calls:
            return
        self._recorded_failed_calls.add(entry)
        payload = entry.model_dump(mode="json")
        if call_id is None:
            del payload["call_id"]
        self._append(payload)

    def read_entries(self) -> tuple[ReplayEntry, ...]:
        return read_replay_entries(self._path)

    def read_all_entries(self) -> tuple[ReplayLogEntry, ...]:
        """Read every replay record (tick + meeting) from the JSONL file."""

        return read_all_entries(self._path)

    def read_meeting_entries(self) -> tuple[MeetingReplayEntry, ...]:
        """Read just the meeting replay records from the JSONL file."""

        return read_meeting_entries(self._path)

    def close(self) -> None:
        """Flush and release the append handle (idempotent).

        Per-tick games open and append thousands of times; re-opening the
        file for every line (the original ``open("a")``-per-write) was a
        per-tick syscall cost the Task 5.9 profile surfaced. The handle is
        now opened lazily on the first append (:meth:`_append`) and reused,
        and ``close`` releases the descriptor at end of game. This is a
        write-cadence change only — the bytes written are byte-identical, so
        the determinism contract (state hashes + recorded actions) is
        unchanged.

        Lazy open also preserves the force=True "nothing on disk until the
        next append" contract (DESIGN.md §11.4, Task 4.16): a log that never
        recorded anything closes to a no-op and leaves no file.
        """

        handle = self._handle
        if handle is not None:
            self._handle = None
            handle.close()

    def __enter__(self) -> ReplayLog:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    def __del__(self) -> None:
        # Best-effort descriptor release for callers that never close the log
        # (e.g. the direct-construction paths in eval/determinism_test.py).
        # Per-write flush already persisted every line, so this only frees the
        # file descriptor; swallow errors because __del__ must never raise.
        try:
            self.close()
        except Exception:
            pass

    def _append(self, entry: Mapping[str, Any]) -> None:
        handle = self._handle
        if handle is None:
            # Lazy open: the file is created on the first append, not at
            # construction, so force=True leaves nothing on disk until a row
            # is written (DESIGN.md §11.4, Task 4.16).
            handle = self._path.open("a", encoding="utf-8")
            self._handle = handle
        handle.write(_stable_json(entry))
        handle.write("\n")
        # Flush each row so a reader that opens the path while the log is still
        # alive (eval/determinism_test.py reads bytes without closing the log)
        # sees every recorded line — the same on-disk visibility the original
        # open/close-per-write gave, minus the per-write open/close syscalls.
        handle.flush()


def read_replay_entries(path: Path) -> tuple[ReplayEntry, ...]:
    """Read the tick replay records (``kind == "tick"``) from the JSONL file.

    Meeting records are skipped — call :func:`read_meeting_entries`
    for those, or :func:`read_all_entries` for the discriminated
    union. This preserves the pre-Task-3.12 contract: callers that
    only care about tick-by-tick state hashes can stay untouched
    while Phase 3 grows the replay format.
    """

    return tuple(
        entry for entry in read_all_entries(path) if isinstance(entry, ReplayEntry)
    )


def read_meeting_entries(path: Path) -> tuple[MeetingReplayEntry, ...]:
    """Read the meeting replay records (``kind == "meeting"``) from the JSONL file."""

    return tuple(
        entry
        for entry in read_all_entries(path)
        if isinstance(entry, MeetingReplayEntry)
    )


def read_failed_call_entries(path: Path) -> tuple[FailedCallReplayEntry, ...]:
    """Read the failed-call records (``kind == "failed_call"``) from the JSONL file.

    These are the LLM calls that aborted a meeting on schema-validation
    failure (Task 3.19 finding 2). Empty for any game whose meetings all
    completed; carries the rejected-call spend otherwise.
    """

    return tuple(
        entry
        for entry in read_all_entries(path)
        if isinstance(entry, FailedCallReplayEntry)
    )


def read_game_outcome(path: Path) -> WinnerSide | None:
    """Return the winner from the last game-end record in a replay log.

    Scans for ``kind == "game_over"`` records and returns the winner of
    the last one (a game writes exactly one, as its final row). Returns
    ``None`` when no game-end record is present — a partial / crashed game
    whose outcome was never decided (Task 3.19 finding 3) — so a
    tournament's win rate can be computed across every replay log,
    skipping the undecided ones.
    """

    outcome: WinnerSide | None = None
    for entry in read_all_entries(path):
        if isinstance(entry, GameEndReplayEntry):
            outcome = entry.winner
    return outcome


def read_substrate_flags(path: Path) -> dict[str, bool] | None:
    """Return the stamped Phase-13.5 substrate config of a replay (Task 14.7).

    Reads the ``substrate_flags`` stamp off the game's ``game_over`` record (the
    last one wins, mirroring :func:`read_game_outcome`). Returns ``None`` for a
    legacy (pre-14.7) replay that carries no stamp — the committed final-9B
    baseline — so callers (the MANIFEST ``flags`` column, the loader's
    substrate guard) treat an unstamped replay as "substrate unspecified"
    rather than misreporting it as all-OFF. A stamped replay returns its full
    snapshot.
    """

    flags: dict[str, bool] | None = None
    for entry in read_all_entries(path):
        if isinstance(entry, GameEndReplayEntry) and entry.substrate_flags is not None:
            flags = dict(entry.substrate_flags)
    return flags


def read_tactical_policy_stamp(path: Path) -> TacticalPolicyStamp | None:
    """Return the stamped tactical policy of a replay (Task 15.9).

    Reads the ``tactical_policy`` block off the game's ``game_over`` record (the
    last one wins, mirroring :func:`read_substrate_flags`). Returns ``None`` for a
    replay that carries no stamp — a legacy / FSM-default recording (the committed
    canonical sets) — so callers (the MANIFEST ``policy`` column, the loader's
    policy guard) treat an unstamped replay as the scripted FSM default rather
    than inventing an identity. A stamped replay returns its full five-field
    :class:`TacticalPolicyStamp`.
    """

    stamp: TacticalPolicyStamp | None = None
    for entry in read_all_entries(path):
        if isinstance(entry, GameEndReplayEntry) and entry.tactical_policy is not None:
            stamp = entry.tactical_policy
    return stamp


def read_crew_tactical_policy_stamp(path: Path) -> CrewTacticalPolicyStamp | None:
    """Return the stamped CREW tactical policy of a replay (Task 18.7).

    The crew twin of :func:`read_tactical_policy_stamp`: reads the
    ``crew_tactical_policy`` block off the game's ``game_over`` record (the last
    one wins, mirroring :func:`read_substrate_flags`). Returns ``None`` for a
    replay that carries no crew stamp — a legacy / scripted-crew-default recording
    (the committed canonical sets) — so callers treat an unstamped replay as the
    scripted :class:`agents.tactical.crewmate_policy.CrewmatePolicy` default rather
    than inventing an identity. A stamped replay returns its full five-field
    :class:`CrewTacticalPolicyStamp`.
    """

    stamp: CrewTacticalPolicyStamp | None = None
    for entry in read_all_entries(path):
        if (
            isinstance(entry, GameEndReplayEntry)
            and entry.crew_tactical_policy is not None
        ):
            stamp = entry.crew_tactical_policy
    return stamp


class PolicyStamps(NamedTuple):
    """The two-identity provenance pair read off one recording (Task 18.19).

    The dual-stamp read-back the 18.19 co-evo recordings need: an impostor
    :class:`TacticalPolicyStamp` and a crew :class:`CrewTacticalPolicyStamp`,
    returned in DISTINCT named slots of DISTINCT types so the two identities can
    NEVER be positionally conflated (the recorder-side conflation guard's
    read-side twin). Either slot is ``None`` when that side carries no stamp —
    the respective scripted default (:func:`read_tactical_policy_stamp` treats an
    absent impostor stamp as the scripted FSM; :func:`read_crew_tactical_policy_stamp`
    treats an absent crew stamp as the scripted
    :class:`agents.tactical.crewmate_policy.CrewmatePolicy`). A dual-stamp
    recording returns both non-``None``; a single-side recording returns exactly
    one; a legacy / FSM-default recording returns ``(None, None)``.
    """

    tactical: TacticalPolicyStamp | None
    crew: CrewTacticalPolicyStamp | None


def read_policy_stamps(path: Path) -> PolicyStamps:
    """Read BOTH policy stamps off a replay in one walk (Task 18.19).

    The dual-stamp read-back for the 18.19 co-evo recordings: reads the impostor
    ``tactical_policy`` block and the crew ``crew_tactical_policy`` block off the
    game's single ``game_over`` record in ONE pass over
    :func:`read_all_entries` (which already rejects a doubled-write file carrying
    more than one ``game_over`` row), last-``game_over``-wins for each block
    exactly as the two sibling readers do
    (:func:`read_tactical_policy_stamp` / :func:`read_crew_tactical_policy_stamp`).
    The two identities return in the DISTINCT named slots of :class:`PolicyStamps`
    so they can never be positionally conflated. A zero-stamp (legacy /
    FSM-default) game reads back ``PolicyStamps(tactical=None, crew=None)``; an
    impostor-only or crew-only game reads back exactly one populated slot; a
    dual-stamp co-evo recording reads back both — each the respective scripted
    default when absent.
    """

    tactical: TacticalPolicyStamp | None = None
    crew: CrewTacticalPolicyStamp | None = None
    for entry in read_all_entries(path):
        if isinstance(entry, GameEndReplayEntry):
            if entry.tactical_policy is not None:
                tactical = entry.tactical_policy
            if entry.crew_tactical_policy is not None:
                crew = entry.crew_tactical_policy
    return PolicyStamps(tactical=tactical, crew=crew)


def compute_cost_usd(path: Path) -> float:
    """Sum reported USD spend from resolved meetings, aborted meetings and failures.

    Each captured response contributes once, regardless of whether its meeting
    resolved. Separate failed-call rows contribute their own reported spend;
    zero-spend default markers add nothing. An unfinished run can have cost
    without a winner or any resolved meeting.
    """

    total = 0.0
    for entry in read_all_entries(path):
        if isinstance(entry, (MeetingReplayEntry, AbortedMeetingReplayEntry)):
            total += sum((call.cost_usd for call in entry.llm_calls), 0.0)
        elif isinstance(entry, FailedCallReplayEntry):
            total += entry.cost_usd
    return total


def read_all_entries(path: Path) -> tuple[ReplayLogEntry, ...]:
    """Read every replay record (tick + meeting) from the JSONL file.

    Walks the file once and fails loud on the doubled-file corruption
    pattern (DESIGN.md §11.4; Task 4.16): if two ``kind="tick"`` rows share
    a ``tick`` value, or more than one ``kind="game_over"`` row is present,
    raise :class:`ReplayLog.CorruptedFileError`. Both signatures mean two
    games' records were concatenated into one file — the silent doubled
    write that broke the loader in Phase 4 UX prep. The error names the file
    and the conflicting tick (or game_over count). Broader corruption
    hardening (mid-line partial writes, etc.) is deferred; Pydantic
    validation already rejects malformed rows.
    """

    if not path.exists():
        raise FileNotFoundError(path)

    entries: list[ReplayLogEntry] = []
    first_tick_line: dict[int, int] = {}
    game_over_count = 0
    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not raw_line:
            continue
        try:
            raw_entry = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid replay JSON at line {line_number}") from exc
        entry = _parse_entry(raw_entry)
        if isinstance(entry, ReplayEntry):
            if entry.tick in first_tick_line:
                raise ReplayLog.CorruptedFileError(
                    f"Duplicate tick {entry.tick} in {path} (first at line "
                    f"{first_tick_line[entry.tick]}, again at line "
                    f"{line_number}). The file is likely a doubled-write from "
                    "re-using a tournament --output-dir without --force; "
                    "truncate the file and re-run."
                )
            first_tick_line[entry.tick] = line_number
        elif isinstance(entry, GameEndReplayEntry):
            game_over_count += 1
            if game_over_count > 1:
                raise ReplayLog.CorruptedFileError(
                    f"Multiple game_over rows in {path} ({game_over_count} "
                    "found). The file is likely a doubled-write from re-using "
                    "a tournament --output-dir without --force; truncate the "
                    "file and re-run."
                )
        entries.append(entry)
    return tuple(entries)


def _parse_entry(raw_entry: Any) -> ReplayLogEntry:
    if not isinstance(raw_entry, dict):
        raise ValueError(
            f"replay entry must be a JSON object, got: {type(raw_entry).__name__}"
        )
    # Default the discriminator to "tick" so pre-Task-3.12 replay files
    # (which never wrote a ``kind`` field) keep validating against
    # :class:`ReplayEntry` without a migration step.
    kind = raw_entry.get("kind", "tick")
    if kind == "tick":
        return ReplayEntry.model_validate({**raw_entry, "kind": "tick"})
    if kind == "meeting":
        return MeetingReplayEntry.model_validate(raw_entry)
    if kind == "meeting_aborted":
        return AbortedMeetingReplayEntry.model_validate(raw_entry)
    if kind == "game_over":
        return GameEndReplayEntry.model_validate(raw_entry)
    if kind == "game_stopped":
        return GameStopReplayEntry.model_validate(raw_entry)
    if kind == "failed_call":
        return FailedCallReplayEntry.model_validate(raw_entry)
    raise ValueError(f"unknown replay entry kind: {kind!r}")


def _serialize_actions(actions: list[Action]) -> list[dict[str, Any]]:
    serialized_actions: list[dict[str, Any]] = []
    for action in actions:
        serialized = _to_jsonable(action)
        if not isinstance(serialized, dict):
            raise TypeError(
                f"action did not serialize to object: {type(action).__name__}"
            )
        serialized_actions.append(serialized)
    return serialized_actions


def _state_hash(state: WorldState) -> str:
    serialized_state = _stable_json(_serialize_world_state(state)).encode("utf-8")
    return hashlib.sha256(serialized_state).hexdigest()


def _serialize_world_state(state: WorldState) -> dict[str, Any]:
    serialized = _to_jsonable(state)
    if not isinstance(serialized, dict):
        raise TypeError("world state did not serialize to object")
    return serialized


def _to_jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, bytes):
        return value.hex()
    if isinstance(value, BaseModel):
        return _to_jsonable(value.model_dump(mode="json"))
    if is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: _to_jsonable(getattr(value, field.name))
            for field in fields(value)
        }
    if isinstance(value, Mapping):
        serialized_mapping: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError(f"unsupported mapping key type: {type(key).__name__}")
            serialized_mapping[key] = _to_jsonable(item)
        return serialized_mapping
    if isinstance(value, tuple):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_to_jsonable(item) for item in value]
    raise TypeError(f"unsupported replay serialization type: {type(value).__name__}")


def _stable_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


__all__ = [
    "FSM_DEFAULT_POLICY_ID",
    "SUBSTRATE_FLAG_KEYS",
    "TOGGLEABLE_SUBSTRATE_FLAG_KEYS",
    "ActionDisposition",
    "AbortedMeetingReplayEntry",
    "CrewTacticalPolicyStamp",
    "CompletionStatus",
    "FailedCallReplayEntry",
    "GameEndReplayEntry",
    "GameStopReplayEntry",
    "GameStopReason",
    "LLMCallRecord",
    "MeetingReplayEntry",
    "PolicyStamps",
    "ReplayEntry",
    "ReplayLog",
    "ReplayLogEntry",
    "SubstrateStampMismatch",
    "TacticalPolicyStamp",
    "WinnerSide",
    "classify_action_dispositions",
    "compute_cost_usd",
    "env_var_for_lever",
    "fold_meeting_outcome_into_memories",
    "fsm_default_tactical_policy_stamp",
    "read_all_entries",
    "recorded_temporal_observations",
    "require_legacy_observations",
    "read_crew_tactical_policy_stamp",
    "read_failed_call_entries",
    "read_game_outcome",
    "read_meeting_entries",
    "read_policy_stamps",
    "read_replay_entries",
    "read_substrate_flags",
    "read_tactical_policy_stamp",
    "recorded_completion_status",
    "substrate_flag_snapshot",
    "substrate_slate_mismatches",
    "substrate_stamp_mismatches",
]
