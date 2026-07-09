"""The surrogate MeetingRunner — the $0 inner-loop meeting path (Task 15.13).

:class:`SurrogateMeetingRunner` conforms to the runtime-checkable
:class:`orchestrator.game.MeetingRunner` protocol: on ``run_meeting`` it derives
the LIVING roster from the trigger-time ``state`` (dead voters cast nothing),
builds each living voter's live-parity feature view (the exact
:data:`training.surrogate.ballots.BALLOT_FEATURE_NAMES` layout the predictor was
fit on — belief suspicion/trust off the agent's own
``suspicion_graph_for_meeting()``, the witnessed-vent pin off its typed
``vent_witness_records_for_meeting()`` channel, reporter identity off the
trigger, meeting index off the orchestrator-formatted ``meeting_id``), predicts
one ballot per voter — with the §7.12 teammate-ballot firewall mirrored as
candidate-set exclusion (an impostor voter's fellow impostors, read off the
trigger-time state roles exactly as the orchestrator derives
``fellow_impostor_ids``, never enter its choice set — the real vote path's
``coerce_teammate_ballot_to_skip`` guarantee) — and lets the REAL
:func:`meetings.voting.tally_ballots` — at the explicit constants-home
:data:`meetings.constants.DEFAULT_SKIP_CONFIDENCE_THRESHOLD` — produce the
outcome. The returned :class:`~orchestrator.game.MeetingArtifacts` echoes
``meeting_id`` / ``triggered_by`` / ``trigger_tick`` (validated at
``orchestrator/game.py::_validate_runner_result``), carries the full-roster
ballot set (one :class:`~meetings.schemas.VoteBallot` per living voter — exactly
the roster the cross-meeting belief fold reads off ``result.ballots``), an empty
transcript, and empty LLM metadata (``llm_calls=()``, ``prompt_versions={}``).
The runner never mutates ``state``.

**The staleness cap is enforced here** (audits/post-phase-14-ML-training-signal.md
§5.6 — never train indefinitely against a frozen surrogate): every
``run_meeting`` call records ONE use against the
:class:`~training.surrogate.ballots.SurrogateStalenessCap` committed beside the
weights artifact, through a :class:`SurrogateUseCounter` the BAKE-OFF owns and
threads through every runner factory. The counter keys on the weights sha256 and
is CUMULATIVE across the run — constructing a fresh runner instance never resets
it, and exceeding the cap raises :class:`SurrogateStalenessExceededError` (the
re-grounding recipe lives in ``training/reports/report-ballot-surrogate.md``).

Public surface (stable — downstream tasks import these):
:class:`SurrogateMeetingRunner`, :class:`SurrogateUseCounter`,
:class:`SurrogateStalenessExceededError`, :func:`load_surrogate_runner_factory`.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Final

from agents.base import AgentInterface
from engine.entities import PlayerId
from engine.world import WorldState
from meetings.constants import DEFAULT_SKIP_CONFIDENCE_THRESHOLD
from meetings.manager import MeetingTrigger
from meetings.schemas import MeetingResult, MeetingTranscript, VoteBallot
from meetings.voting import tally_ballots
from orchestrator.game import MeetingArtifacts, MeetingAwareAgent
from training.surrogate.ballots import (
    BallotPredictor,
    SurrogateStalenessCap,
    VoterBallotView,
    load_ballot_predictor_artifact,
    load_staleness_cap,
)

# The orchestrator's meeting-id format (``orchestrator/game.py::_game_id`` +
# ``_run_and_apply_meeting``): ``"{game_id}:meeting-{meeting_index}"``. The
# runner reads the per-game meeting index off it rather than counting its own
# invocations, because a runner instance's lifetime is a wiring choice (fresh
# per game on the tournament path, potentially reused elsewhere) while the id
# is always stamped by the orchestrator per game.
_MEETING_ID_SEPARATOR: Final[str] = ":meeting-"

_SURROGATE_RATIONALE: Final[str] = (
    "surrogate-predicted ballot (no transcript; Task 15.13 ballot predictor)"
)


class SurrogateStalenessExceededError(RuntimeError):
    """The bake-off consumed the committed cap of surrogate-simulated meetings.

    Raised by :meth:`SurrogateUseCounter.record_use` when one more simulated
    meeting would exceed the committed ``max_uses``. Deliberately NOT silently
    recoverable: the §5.6 doctrine says a trainer at the cap must re-ground
    (record fresh real-LLM meetings, rebuild the table, re-fit, re-measure) —
    the step-by-step recipe is in ``training/reports/report-ballot-surrogate.md``.
    """


class SurrogateUseCounter:
    """The cumulative use-counter for one frozen weights artifact.

    An explicit object (never module state — AGENTS.md "no global state") the
    BAKE-OFF constructs ONCE per run from the committed cap and passes to every
    :class:`SurrogateMeetingRunner` it builds; because the counter outlives the
    runners, constructing a fresh runner never resets the count. ``record_use``
    keys every use on the weights sha256 so a counter can never be silently
    reused against different weights.
    """

    def __init__(self, cap: SurrogateStalenessCap) -> None:
        self._cap = cap
        self._uses = 0

    @property
    def cap(self) -> SurrogateStalenessCap:
        return self._cap

    @property
    def uses(self) -> int:
        """Surrogate-simulated meetings recorded so far (the cap's unit)."""

        return self._uses

    def record_use(self, *, weights_sha256: str) -> int:
        """Record one simulated meeting; raise once the committed cap is spent."""

        if weights_sha256 != self._cap.weights_sha256:
            raise ValueError(
                "SurrogateUseCounter is keyed on weights sha256 "
                f"{self._cap.weights_sha256!r} but was asked to record a use of "
                f"{weights_sha256!r} — one counter never meters two artifacts"
            )
        if self._uses >= self._cap.max_uses:
            raise SurrogateStalenessExceededError(
                f"the frozen ballot surrogate {weights_sha256[:12]}… has reached "
                f"its committed staleness cap of {self._cap.max_uses} simulated "
                "meetings for this run; re-ground before training further "
                "(record fresh real-LLM meetings, rebuild the table, re-fit, "
                "re-measure — training/reports/report-ballot-surrogate.md)"
            )
        self._uses += 1
        return self._uses


def _meeting_index_from_id(meeting_id: str) -> int:
    """Read the per-game meeting index off the orchestrator-formatted id."""

    _, separator, suffix = meeting_id.rpartition(_MEETING_ID_SEPARATOR)
    if not separator or not suffix.isdigit():
        raise ValueError(
            f"meeting_id {meeting_id!r} does not carry the orchestrator's "
            f"'{{game_id}}{_MEETING_ID_SEPARATOR}{{index}}' format; the surrogate "
            "cannot derive the meeting_index feature from it"
        )
    return int(suffix)


class SurrogateMeetingRunner:
    """The ballot-predictor MeetingRunner (Task 15.13 public type).

    Wraps a fitted (typically artifact-loaded) :class:`BallotPredictor`.
    ``weights_sha256`` identifies the exact frozen artifact so every simulated
    meeting is metered against it through ``use_counter`` (see the module
    docstring for the ownership rules). Construct via
    :func:`load_surrogate_runner_factory` to get the committed-artifact wiring
    for free.
    """

    def __init__(
        self,
        *,
        predictor: BallotPredictor,
        weights_sha256: str,
        use_counter: SurrogateUseCounter,
    ) -> None:
        self._predictor = predictor
        self._weights_sha256 = weights_sha256
        self._use_counter = use_counter

    @property
    def weights_sha256(self) -> str:
        return self._weights_sha256

    @property
    def use_counter(self) -> SurrogateUseCounter:
        return self._use_counter

    async def run_meeting(
        self,
        *,
        meeting_id: str,
        trigger: MeetingTrigger,
        state: WorldState,
        agents: Mapping[PlayerId, AgentInterface],
    ) -> MeetingArtifacts:
        """Simulate one meeting: predict every living voter's ballot, real tally.

        Reads ``state`` and the agents' meeting-input accessors only — never
        mutates either (the protocol contract; engine-state application happens
        through ``apply_meeting_result`` after this returns).
        """

        self._use_counter.record_use(weights_sha256=self._weights_sha256)
        living = tuple(
            sorted(
                player_id for player_id, player in state.players.items() if player.alive
            )
        )
        # The §7.12 teammate-ballot firewall (Codex review on PR #241): the real
        # vote path coerces a ballot naming a fellow impostor to SKIP BEFORE the
        # tally (``meetings.manager.coerce_teammate_ballot_to_skip``), so an
        # impostor can never supply the betrayal vote that ejects a teammate.
        # The surrogate mirrors it as candidate-set EXCLUSION: fellow impostors
        # are dropped from an impostor voter's choice set before prediction,
        # which (a) can never create the betrayal ballot the guard exists to
        # stop, and (b) matches the fit distribution — the recorded corpus
        # ballots the predictor learned from carry no teammate targets because
        # production's guard ran before recording. Roles are read off the
        # trigger-time engine state exactly as the orchestrator derives
        # ``fellow_impostor_ids`` for the real meeting (game.py:875-910); by
        # role, independent of alive state, mirroring that derivation.
        impostor_ids = frozenset(
            player_id
            for player_id, player in state.players.items()
            if player.role == "IMPOSTOR"
        )
        meeting_index = float(_meeting_index_from_id(meeting_id))
        alive_count = float(len(living))
        ballots: list[VoteBallot] = []
        for voter in living:
            agent = agents.get(voter)
            if agent is None:
                raise ValueError(
                    f"surrogate meeting {meeting_id!r} has no agent for living "
                    f"player {voter!r}; every alive player must have a "
                    "constructed agent"
                )
            if not isinstance(agent, MeetingAwareAgent):
                raise TypeError(
                    f"agent for {voter!r} does not implement MeetingAwareAgent; "
                    "the surrogate reads suspicion_graph_for_meeting() and "
                    "vent_witness_records_for_meeting() — the same inputs the "
                    "real meeting consumes"
                )
            suspicion = {
                entry.player_id: entry for entry in agent.suspicion_graph_for_meeting()
            }
            vent_subjects = frozenset(
                record.subject for record in agent.vent_witness_records_for_meeting()
            )
            # A crewmate (and a sole impostor) excludes only itself; an impostor
            # also excludes its living teammates (the §7.12 guard above). An
            # impostor whose every other living player is a teammate gets an
            # empty choice set and predicts SKIP — the same terminal shape the
            # production guard chain coerces to.
            teammates = impostor_ids - {voter} if voter in impostor_ids else frozenset()
            candidates = tuple(
                cand for cand in living if cand != voter and cand not in teammates
            )
            features: dict[PlayerId, dict[str, float]] = {}
            for cand in candidates:
                entry = suspicion.get(cand)
                features[cand] = {
                    # An absent graph row reads the neutral 0.5 prior — the same
                    # default the belief store's ``view()`` (and therefore the
                    # 15.11 table column) carries for an unseeded player.
                    "belief_suspicion": (
                        float(entry.suspicion) if entry is not None else 0.5
                    ),
                    "belief_trust": float(entry.trust) if entry is not None else 0.5,
                    "is_reporter": float(cand == trigger.triggered_by),
                    "witnessed_vent": float(cand in vent_subjects),
                    "meeting_index": meeting_index,
                    "alive_count": alive_count,
                }
            predicted = self._predictor.predict_ballot(
                VoterBallotView(voter=voter, candidates=candidates, features=features)
            )
            ballots.append(
                VoteBallot(
                    voter=voter,
                    target=predicted.target,
                    confidence=predicted.confidence,
                    primary_reason_id=None,
                    considered_alternatives=(),
                    rationale_text=_SURROGATE_RATIONALE,
                )
            )
        # The REAL deterministic tally at the explicit constants-home gate — the
        # structural fix: SKIP-vs-eject emerges from plurality + the confidence
        # gate, never from a tuned binary head (§5.2/§5.3).
        outcome, ejected = tally_ballots(
            ballots, skip_confidence_threshold=DEFAULT_SKIP_CONFIDENCE_THRESHOLD
        )
        result = MeetingResult(
            meeting_id=meeting_id,
            triggered_by=trigger.triggered_by,
            trigger_tick=trigger.trigger_tick,
            outcome=outcome,
            ejected_player_id=ejected,
            ballots=tuple(ballots),
            contradictions=(),
            transcript=MeetingTranscript(),
        )
        # Empty LLM metadata: MeetingArtifacts is the shape the orchestrator
        # dereferences — a bare MeetingResult fails (task contract hint).
        return MeetingArtifacts(result=result, llm_calls=(), prompt_versions={})


def load_surrogate_runner_factory(
    artifact_dir: Path,
    *,
    use_counter: SurrogateUseCounter | None = None,
) -> Callable[[], SurrogateMeetingRunner]:
    """Build a per-game runner factory over the COMMITTED weights artifact.

    Loads the weights (sha256 sidecar verified), loads the committed staleness
    cap, cross-checks the cap is keyed on exactly those weights, and returns a
    zero-arg factory suitable for
    :func:`eval.balance_eval.run_tournament_eval`'s
    ``meeting_runner_factory`` keyword and the training env's
    ``meeting_runner_factory`` seam. Every runner the factory constructs shares
    ONE :class:`SurrogateUseCounter` (pass ``use_counter`` to share it across
    multiple factories in a bake-off run), so the cap is cumulative across
    games — a fresh runner per game never resets it.

    A supplied ``use_counter`` is VALIDATED against the committed cap (Codex
    review on PR #241): it must be keyed on exactly these weights and its cap
    must be no LOOSER than the committed ``max_uses`` — a shared counter may
    tighten the committed cap (the cumulative-metering tests do), never loosen
    it, or the doctrine this factory enforces would be silently bypassable.
    """

    predictor, weights_sha256 = load_ballot_predictor_artifact(artifact_dir)
    cap = load_staleness_cap(artifact_dir)
    if cap.weights_sha256 != weights_sha256:
        raise ValueError(
            f"staleness cap under {artifact_dir} is keyed on weights "
            f"{cap.weights_sha256!r} but the committed weights hash to "
            f"{weights_sha256!r} — the cap and the artifact drifted apart"
        )
    if use_counter is not None:
        if use_counter.cap.weights_sha256 != weights_sha256:
            raise ValueError(
                "shared use_counter is keyed on weights "
                f"{use_counter.cap.weights_sha256!r} but {artifact_dir} commits "
                f"{weights_sha256!r} — one counter never meters two artifacts"
            )
        if use_counter.cap.max_uses > cap.max_uses:
            raise ValueError(
                f"shared use_counter allows {use_counter.cap.max_uses} uses but "
                f"the committed cap under {artifact_dir} is {cap.max_uses} — a "
                "shared counter may tighten the committed staleness cap, never "
                "loosen it"
            )
    counter = use_counter if use_counter is not None else SurrogateUseCounter(cap)

    def factory() -> SurrogateMeetingRunner:
        return SurrogateMeetingRunner(
            predictor=predictor,
            weights_sha256=weights_sha256,
            use_counter=counter,
        )

    return factory


__all__ = [
    "SurrogateMeetingRunner",
    "SurrogateStalenessExceededError",
    "SurrogateUseCounter",
    "load_surrogate_runner_factory",
]
