"""Append-only JSONL replay log (DESIGN.md §11.4).

Each game produces a single replay file. Records are JSON objects, one
per line. The replay log has two kinds of records, discriminated by the
``kind`` field:

* ``"tick"`` — a :class:`ReplayEntry` written each tick by
  :meth:`ReplayLog.record_tick`. Carries the input actions and a state
  hash. This shape pre-dates Task 3.12 and is preserved for the
  existing engine-determinism tests (Task 2.8 byte-identity gate).
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
:class:`api.replay_loader.ReplayPolicyMismatchError`.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import fields, is_dataclass
import hashlib
import json
from pathlib import Path
from typing import Annotated, Any, Final, Literal, TextIO, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, field_validator

from engine.actions import Action
from engine.world import WorldState
from meetings.schemas import (
    ContradictionRef,
    MeetingOutcome,
    MeetingResult,
    MeetingTranscript,
    PlayerId,
    VoteBallot,
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


class ReplayEntry(BaseModel):
    """One per-tick replay record written by :meth:`ReplayLog.record_tick`."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: Literal["tick"] = "tick"
    game_id: str
    tick: int
    actions: tuple[dict[str, Any], ...]
    state_hash: str


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


WinnerSide: TypeAlias = Literal["CREWMATES", "IMPOSTORS"]


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
        non-blank, pipe-free token, so nothing valid is rejected.
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


class FailedCallReplayEntry(BaseModel):
    """One failed-LLM-call replay record (DESIGN.md §11.4; Task 3.19 finding 2).

    Written by :meth:`ReplayLog.record_failed_call` when a meeting aborts
    because a structured-output response failed schema validation. The
    ``ValidationError`` fires inside the provider before an
    :class:`~llm.client.LLMResponse` exists, so the tokens the model
    already burned would otherwise be invisible to both the budget layer
    and :meth:`ReplayLog.record_meeting` (which never runs for the crashed
    meeting). This row captures that spend — plus enough of the raw
    response and the error to reconstruct what broke — so per-meeting cost
    is auditable even for the meeting that crashed the run.
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


ReplayLogEntry: TypeAlias = Annotated[
    ReplayEntry | MeetingReplayEntry | GameEndReplayEntry | FailedCallReplayEntry,
    Field(discriminator="kind"),
]


# The canonical key order for a substrate-flag snapshot (Task 14.7). Mirrors
# ``experiments.lab.probe_backends.active_substrate_flags`` exactly so the
# recorded MANIFEST ``flags`` column, the sweep result rows, and the replay
# stamp all describe the same substrate levers with identical keys. The four
# merged Phase-13.5 levers (Task 14.9), the Task-14.10 ``evidence_quality_lift``
# lever (retired to unconditional at the Task-14.12 close, once baseline 2 adopted
# it), AND Task 15.5's ``reporter_exculpation`` (graduated to unconditional at the
# Task-15.7 baseline-3 record, once baseline 3 adopted it) are ALL RETIRED as
# toggles — unconditionally ON, env gates deleted — but stay in the snapshot as
# provenance. ``_TOGGLEABLE_LEVER_RESOLVERS`` below is now empty; a future live
# toggleable lever would register its key + resolver there.
_RETIRED_ALWAYS_ON_LEVERS: Final[tuple[str, ...]] = (
    "testimony_as_content",
    "witnessed_kill_evidence",
    "movement_perception",
    "unfreeze_memory",
    "evidence_quality_lift",
    "reporter_exculpation",
)

# (key, resolver) pairs for levers that still consult an ``AILIBI_*`` env var.
# Added HERE in source, never mutated at runtime (an immutable ``Final`` tuple,
# per AGENTS.md "no module-level mutable state", so nothing can silently change
# replay stamps or the loader's mismatch check mid-process). Each resolver takes
# the optional ``env`` mapping and returns the lever's active state (the 13.5
# ``*_enabled()`` signature). This table is currently EMPTY: every substrate lever
# has graduated to unconditional-ON. Task 15.5's ``reporter_exculpation`` was the
# last live toggle; it joined ``_RETIRED_ALWAYS_ON_LEVERS`` at the Task-15.7
# baseline-3 record (``evidence_quality_lift`` graduated the same way at the 14.12
# close). The typed-empty form is retained so a future live lever registers here
# with no structural change, and so ``substrate_flag_snapshot`` keeps one uniform
# snapshot path.
_TOGGLEABLE_LEVER_RESOLVERS: Final[
    tuple[tuple[str, Callable[[Mapping[str, str] | None], bool]], ...]
] = ()

# The still-toggleable subset of ``SUBSTRATE_FLAG_KEYS`` (Task 14.10):
# levers whose active state is an ``AILIBI_*`` env read, so a stamp/ambient
# mismatch on one of THESE is remediable by matching the environment to the
# stamp — unlike the retired four, whose OFF derivation no longer exists.
# The loader's substrate-mismatch error branches its remediation hint on
# this split.
TOGGLEABLE_SUBSTRATE_FLAG_KEYS: Final[tuple[str, ...]] = tuple(
    key for key, _ in _TOGGLEABLE_LEVER_RESOLVERS
)

SUBSTRATE_FLAG_KEYS: Final[tuple[str, ...]] = (
    *_RETIRED_ALWAYS_ON_LEVERS,
    *TOGGLEABLE_SUBSTRATE_FLAG_KEYS,
)


def substrate_flag_snapshot(
    env: Mapping[str, str] | None = None,
) -> dict[str, bool]:
    """Snapshot the active substrate-lever config (Task 14.7).

    Every substrate lever now reports unconditionally ``True``. The four merged
    Phase-13.5 levers (Task 14.9), Task 14.10's ``evidence_quality_lift`` (retired
    at the Task-14.12 close once baseline 2 adopted it), and Task 15.5's
    ``reporter_exculpation`` (graduated at the Task-15.7 baseline-3 record once
    baseline 3 adopted it) all had their ``*_enabled()`` env gates retired, so the
    unconditional derivation is the only substrate this build can produce. They
    stay in the snapshot so the MANIFEST ``flags`` column and the replay stamp keep
    self-describing recordings (and so the loader's substrate-mismatch guard can
    still validate legacy stamped replays — a baseline-2 stamp recording
    ``reporter_exculpation`` OFF now fails loud, no cross-substrate replay). ``env``
    is still threaded to the (currently empty) ``_TOGGLEABLE_LEVER_RESOLVERS`` loop
    so a future live lever can resolve a specific mapping without a signature churn.
    """

    snapshot = dict.fromkeys(_RETIRED_ALWAYS_ON_LEVERS, True)
    for key, resolver in _TOGGLEABLE_LEVER_RESOLVERS:
        snapshot[key] = resolver(env)
    return snapshot


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
    ) -> None:
        # ``tactical_policy_stamp`` is the recorder-supplied provenance stamp
        # (Task 15.9) written onto the ``game_over`` record by
        # :meth:`record_game_end`. Default ``None`` = absent = scripted FSM
        # default, byte-identical to the pre-15.9 writer. The stamp rides the
        # WRITER (not ``record_game_end``'s signature) so the many direct
        # ``record_game_end`` callers (unit tests, eval/determinism_test.py) stay
        # untouched and record the FSM default.
        self._tactical_policy_stamp = tactical_policy_stamp
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

    def record_tick(self, tick: int, actions: list[Action], state: WorldState) -> None:
        entry = {
            "kind": "tick",
            "game_id": self._game_id,
            "tick": tick,
            "actions": _serialize_actions(actions),
            "state_hash": _state_hash(state),
        }
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
            substrate_flags=substrate_flag_snapshot(),
            tactical_policy=self._tactical_policy_stamp,
        )
        payload = entry.model_dump(mode="json")
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
        self._append(payload)

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
    ) -> None:
        """Persist a meeting-aborting failed LLM call (DESIGN.md §11.4; Task 3.19).

        Called by the orchestrator on the meeting-failure path when a
        structured-output response failed schema validation (the metadata
        rides the propagating ``ValidationError`` and is recovered via
        :func:`llm.provider.extract_parse_failure`). Captures the spend
        and partial response for the rejected call so per-meeting cost is
        reconstructable even though the meeting crashed and
        :meth:`record_meeting` never ran.

        Single-write guard (Task 9.10, audit gp-4 / MECH-B-1): a row that is
        byte-identical to one already written by this log is dropped instead
        of appended. A deterministic provider (seeded local model, fixed
        prompt) regenerates the SAME failing response on the in-turn retry,
        so a single defaulted opening surfaced the same burned generation
        twice — seeds 8/36/39 each persisted a duplicate ``failed_call`` row,
        double-counting 5,969 input / 6,144 output tokens. De-duplication is
        on the FULL frozen entry — the audit's byte-identity tuple
        ``(model, raw_response, input_tokens, output_tokens)`` scoped by
        ``meeting_id`` / ``tick`` / error fields — so two zero-spend
        ``deadline_default`` visibility markers from DIFFERENT participants
        (which share the zero tuple but differ in ``error_message``) and any
        genuinely distinct failures in one meeting still each record once.
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
        )
        if entry in self._recorded_failed_calls:
            return
        self._recorded_failed_calls.add(entry)
        self._append(entry.model_dump(mode="json"))

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


def compute_cost_usd(path: Path) -> float:
    """Sum LLM cost (USD) across a replay log (DESIGN.md §11.4; Task 3.19).

    Reads every record once and sums :attr:`LLMCallRecord.cost_usd` over
    each ``kind == "meeting"`` record's captured calls *plus* each
    ``kind == "failed_call"`` record's cost. This is the canonical
    per-game cost reduction: future eval code (including the real-provider
    50-game eval that checks the ``<= $0.30`` merge criterion) consumes it
    rather than re-deriving the sum inline. Folding in the failed-call
    rows means a meeting that aborted on a rejected response still
    contributes the tokens the model already burned, so a crashed run's
    spend is not silently undercounted (Task 3.19 finding 2).

    Returns ``0.0`` for replay logs with no meeting or failed-call entries
    (e.g. games that ended before any meeting fired) and for meetings
    whose ``llm_calls`` list is empty. The sum is seeded with a float so
    the return value is always a finite, non-negative float (fake-provider
    runs report ``cost_usd == 0.0`` per call).
    """

    total = 0.0
    for entry in read_all_entries(path):
        if isinstance(entry, MeetingReplayEntry):
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
    if kind == "game_over":
        return GameEndReplayEntry.model_validate(raw_entry)
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
    "FailedCallReplayEntry",
    "GameEndReplayEntry",
    "LLMCallRecord",
    "MeetingReplayEntry",
    "ReplayEntry",
    "ReplayLog",
    "ReplayLogEntry",
    "TacticalPolicyStamp",
    "WinnerSide",
    "compute_cost_usd",
    "fsm_default_tactical_policy_stamp",
    "read_all_entries",
    "read_failed_call_entries",
    "read_game_outcome",
    "read_meeting_entries",
    "read_replay_entries",
    "read_substrate_flags",
    "read_tactical_policy_stamp",
    "substrate_flag_snapshot",
]
