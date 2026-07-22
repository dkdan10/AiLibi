"""The composed meeting-outcome runner — conviction WHETHER × surrogate WHO (Task 18.29).

Training rollouts run fake meetings that convict nobody, while 65.2% of real
baseline-6 meetings convict — so rosters never shrink, parity never arises, an
impostor never loses a teammate, and crew never wins by ejection inside training.
This module composes the two committed instruments into a
:class:`~orchestrator.game.MeetingRunner` that closes that gap WITHOUT a single
learned parameter of its own:

* the committed **conviction model** decides WHETHER the meeting convicts —
  ``predict(features).conversion_prob >=
  CONVICTION_CONVERSION_DECISION_THRESHOLD`` (the pinned 0.5 fidelity operating
  point, imported never re-stated), over the live 12-feature vector the 18.30
  serving assembler (:func:`training.conviction.serving.
  assemble_live_conviction_features`) reconstructs from the run_meeting inputs;
* the committed **ballot surrogate's ranking channel** decides WHO — candidates
  ranked by expected vote share (mean per-voter ``PredictedBallot.target_probs``
  over the non-self voters, ties to smallest id — the exact
  :meth:`training.surrogate.ballots.BallotSurrogateModel.predict` Form-B recipe,
  computed live);
* the ballots are synthesized coherently with that outcome THROUGH the real
  :func:`meetings.voting.tally_ballots` at
  :data:`meetings.constants.DEFAULT_SKIP_CONFIDENCE_THRESHOLD` — the outcome is
  NEVER hand-set. Under a convict decision the surrogate's predicted ballots are
  re-anchored (minimal, deterministic) so the plurality lands on the ranked
  target through the real tally; under skip they pass through unchanged.

**The two fences, inherited untouched.** The §7.12 teammate firewall survives as
candidate-set exclusion (an impostor voter's fellow impostors never enter its
choice set, including after re-anchoring — the same guarantee
:class:`training.surrogate.runner.SurrogateMeetingRunner` mirrors from the real
``coerce_teammate_ballot_to_skip``). Both components load through their committed
loaders and fail loud before any use: the surrogate side is loaded through
:func:`training.surrogate.runner.load_surrogate_runner_factory` (the committed
fence — weights-sha verification, cap cross-check, fit-corpus cross-check,
optional corpus fingerprint, supplied-counter validation), and the predictor is
read back off the SAME sha-verified artifact
(:func:`training.surrogate.ballots.load_ballot_predictor_artifact`) because the
composed runner needs the per-voter ``target_probs`` the runner class keeps
private. The conviction side is the sha-verified model plus its committed cap and
its committed **GO** verdict — a NO-GO conviction verdict means the composed
runner is structurally unbuildable (the diagnostic-only doctrine). Both component
staleness counters meter every composed meeting (surrogate at entry — one
run_meeting is one use; conviction on DELIVERY — a failed assembly/predict never
burns quota).

**The pre-registered GO bar** (stated before measurement, on the held-out corpus
test split — 96 meetings / 60 ejections): (1) meeting-level decision accuracy
STRICTLY greater than the always-eject baseline (60/96); (2) among convicting
meetings, ejected-target top-1 at least ``GO_TOP1_CEILING_RATIO`` × the honest
ceiling (the standing axis-1 form); (3) exact-outcome match reported beside the
verdict, informational never gating. GO ⇒ the runner is an OPTIONAL campaign
configuration through 18.21's runner-factory seam; NO-GO ⇒ diagnostic-only. The
composed artifact carries NO weights — it is a manifest pinning both component
shas plus the bar verdict.

Public surface (stable signatures — downstream tasks import these):
the loaders/fence (:func:`load_composed_components`,
:func:`load_composed_runner_factory`, :class:`ComposedComponents`), the runner
(:class:`ComposedMeetingRunner`, :class:`ComposedBallotSynthesisError`), the
offline fidelity + verdict (:func:`run_composed_fidelity`,
:class:`ComposedFidelityReport`, :func:`decide_composed_go`,
:class:`ComposedGoVerdict`, :class:`ComposedManifest` and their
writers/loaders), and the composed-path Goodhart leg
(:func:`run_composed_goodhart_leg`, :class:`ComposedGoodhartLeg`).
"""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Literal

import numpy as np
from pydantic import BaseModel, ConfigDict, Field

from agents.base import AgentInterface
from engine.entities import PlayerId
from engine.world import WorldState
from meetings.constants import DEFAULT_SKIP_CONFIDENCE_THRESHOLD
from meetings.manager import MeetingTrigger
from meetings.schemas import MeetingResult, MeetingTranscript, VoteBallot
from meetings.voting import SKIP_TARGET, tally_ballots
from orchestrator.game import MeetingArtifacts, MeetingAwareAgent
from training.bakeoff.es import ESConfig
from training.bakeoff.goodhart import (
    ConvictionPathProbeReport,
    run_conviction_path_probe,
)
from training.conviction.dataset import (
    build_conviction_table,
    validate_conviction_split,
)
from training.conviction.fidelity import (
    CONVICTION_CONVERSION_DECISION_THRESHOLD,
    ConvictionGoVerdict,
    load_conviction_verdict,
)
from training.conviction.model import (
    ConvictionEconomyModel,
    ConvictionUseCounter,
    load_conviction_model_artifact,
    load_conviction_staleness_cap,
)
from training.conviction.serving import assemble_live_conviction_features
from training.surrogate.ballots import (
    BallotPredictor,
    BallotSurrogateModel,
    PredictedBallot,
    VoterBallotView,
    load_ballot_predictor_artifact,
    load_staleness_cap,
)
from training.surrogate.dataset import build_meeting_table
from training.surrogate.fidelity import (
    GO_TOP1_CEILING_RATIO,
    build_meeting_views,
    compute_honest_ceiling,
)
from training.surrogate.runner import (
    SurrogateUseCounter,
    load_surrogate_runner_factory,
)

# The committed-artifact directories the composed runner reads through. Path
# literals (not imported from ``training.bakeoff.harness``, which 18.29's scope
# leaves untouched) — the same two dirs the component loaders default to.
_CONVICTION_ARTIFACT_DIR: Final[Path] = Path("training/artifacts/conviction")
_SURROGATE_ARTIFACT_DIR: Final[Path] = Path("training/artifacts/surrogate")

# The committed composed-artifact sidecars under ``training/artifacts/composed/``.
COMPOSED_MANIFEST_FILENAME: Final[str] = "manifest.json"
COMPOSED_VERDICT_FILENAME: Final[str] = "verdict.json"

# The orchestrator's meeting-id format (``orchestrator/game.py`` ``_game_id`` +
# ``_run_and_apply_meeting``): ``"{game_id}:meeting-{meeting_index}"`` — parsed
# for the surrogate leg's ``meeting_index`` feature exactly as
# ``training/surrogate/runner.py`` does.
_MEETING_ID_SEPARATOR: Final[str] = ":meeting-"

# The neutral belief prior an absent graph row reads (the surrogate-runner
# precedent) — one voter/candidate cell the surrogate was never seeded on.
_NEUTRAL_PRIOR: Final[float] = 0.5

# Distinct audit-marker rationales. A pass-through ballot is the surrogate's own
# prediction, carried unchanged; a re-anchored ballot is one the composition
# rewrote to land the conviction decision through the real tally (a distinct
# string so the fold and any auditor can tell them apart). The gate's DECISION
# is recorded by the outcome, never by the rationale: a convicting meeting whose
# pass-through ballots already eject the ranked target re-anchors nothing, so
# its ballots honestly stay pass-through-stamped.
_COMPOSED_RATIONALE: Final[str] = (
    "composed-runner pass-through ballot (surrogate-predicted, not re-anchored; "
    "Task 18.29)"
)
_REANCHOR_RATIONALE: Final[str] = (
    "composed-runner re-anchored ballot (conviction convicts; surrogate-ranked "
    "target; synthesized through the real tally; Task 18.29)"
)

# The committed corpus set the composition is grounded on.
_CORPUS_SET: Final[str] = "9p2i"


class ComposedBallotSynthesisError(RuntimeError):
    """Re-anchoring could not land the conviction ejection through the real tally.

    Raised by :meth:`ComposedMeetingRunner.run_meeting` when the conviction gate
    convicts but no deterministic re-anchoring of the surrogate's predicted
    ballots makes :func:`meetings.voting.tally_ballots` return
    ``("EJECTED", target)`` — a structurally unreachable state on any roster the
    REAL vote path could itself eject the target on (e.g. an impostor target
    with no living crew to name it). Deliberately NOT silently recoverable
    (AGENTS.md "no silent fallbacks"): silently downgrading a convict decision to
    a SKIP would launder a component disagreement into the training substrate
    invisibly.
    """


def _meeting_index_from_id(meeting_id: str) -> int:
    """Read the per-game meeting index off the orchestrator-formatted id."""

    _, separator, suffix = meeting_id.rpartition(_MEETING_ID_SEPARATOR)
    if not separator or not suffix.isdigit():
        raise ValueError(
            f"meeting_id {meeting_id!r} does not carry the orchestrator's "
            f"'{{game_id}}{_MEETING_ID_SEPARATOR}{{index}}' format; the composed "
            "runner cannot derive the meeting_index feature from it"
        )
    return int(suffix)


# --------------------------------------------------------------------------- #
# Loaders / fence semantics                                                    #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class ComposedComponents:
    """The two committed instruments the runner composes, loaded + fenced.

    Holds the sha-verified conviction model and ballot predictor, the two
    weights digests (each the key of its own use-counter and cap), the two
    cumulative use-counters (both metered per composed meeting), and the
    committed **GO** conviction verdict the composition is built under. Built by
    :func:`load_composed_components`; never carries a learned parameter of its
    own.
    """

    conviction_model: ConvictionEconomyModel
    conviction_weights_sha256: str
    conviction_use_counter: ConvictionUseCounter
    conviction_verdict: ConvictionGoVerdict
    ballot_predictor: BallotPredictor
    surrogate_weights_sha256: str
    surrogate_use_counter: SurrogateUseCounter


def load_composed_components(
    *,
    conviction_artifact_dir: Path = _CONVICTION_ARTIFACT_DIR,
    surrogate_artifact_dir: Path = _SURROGATE_ARTIFACT_DIR,
    conviction_use_counter: ConvictionUseCounter | None = None,
    surrogate_use_counter: SurrogateUseCounter | None = None,
    corpus_dir: Path | None = None,
) -> ComposedComponents:
    """Load + fence both committed components (fail loud before any use).

    **Surrogate side.** The committed fence is enforced by CALLING
    :func:`training.surrogate.runner.load_surrogate_runner_factory` — it verifies
    the weights sha256 sidecar, cross-checks the staleness cap and the
    fit-corpus provenance against those weights, optionally fingerprints the live
    ``corpus_dir``, and validates a supplied ``surrogate_use_counter`` (same
    sha; no looser than the committed cap). The shared counter is constructed
    first when the caller supplied none (so the same validation still runs), and
    the predictor is read back off the SAME sha-verified artifact via
    :func:`~training.surrogate.ballots.load_ballot_predictor_artifact` — the
    runner class the factory returns keeps its predictor private, and the
    composed runner needs the per-voter ``target_probs`` for the ranking channel.

    **Conviction side.** The sha-verified model
    (:func:`~training.conviction.model.load_conviction_model_artifact`), its
    committed cap (cross-checked keyed on those weights), and its committed
    verdict (cross-checked keyed on those weights AND asserted **GO** — a NO-GO
    conviction verdict means the composed runner is structurally unbuildable, the
    diagnostic-only doctrine, so it fails loud rather than compose around an
    absent term). A supplied ``conviction_use_counter`` is validated like the
    surrogate factory validates its own: same sha, and no looser than the
    committed cap (tighten, never loosen).
    """

    # -- Surrogate side: the committed factory loader IS the fence. -------------
    surrogate_cap = load_staleness_cap(surrogate_artifact_dir)
    surrogate_counter = (
        surrogate_use_counter
        if surrogate_use_counter is not None
        else SurrogateUseCounter(surrogate_cap)
    )
    # Weights-sha verification, cap cross-check, fit-corpus cross-check, optional
    # corpus fingerprint, and supplied-counter validation all run here (the
    # returned factory is discarded — the composed runner holds the predictor
    # itself, read back below off the same sha-verified artifact).
    load_surrogate_runner_factory(
        surrogate_artifact_dir,
        use_counter=surrogate_counter,
        corpus_dir=corpus_dir,
    )
    ballot_predictor, surrogate_sha = load_ballot_predictor_artifact(
        surrogate_artifact_dir
    )

    # -- Conviction side: sha-verified model + cap + GO verdict. ----------------
    conviction_model, conviction_sha = load_conviction_model_artifact(
        conviction_artifact_dir
    )
    conviction_cap = load_conviction_staleness_cap(conviction_artifact_dir)
    if conviction_cap.weights_sha256 != conviction_sha:
        raise ValueError(
            f"conviction staleness cap under {conviction_artifact_dir} is keyed "
            f"on weights {conviction_cap.weights_sha256!r} but the committed "
            f"weights hash to {conviction_sha!r} — the cap and the artifact "
            "drifted apart"
        )
    conviction_verdict = load_conviction_verdict(conviction_artifact_dir)
    if conviction_verdict.weights_sha256 != conviction_sha:
        raise ValueError(
            f"conviction verdict under {conviction_artifact_dir} is keyed on "
            f"weights {conviction_verdict.weights_sha256!r} but the committed "
            f"weights hash to {conviction_sha!r} — the verdict and the artifact "
            "drifted apart"
        )
    if conviction_verdict.verdict != "GO":
        raise ValueError(
            f"the committed conviction verdict under {conviction_artifact_dir} "
            f"is {conviction_verdict.verdict!r} (model_role="
            f"{conviction_verdict.model_role!r}) — a NO-GO conviction model is "
            "DIAGNOSTIC-ONLY, so the composed runner is structurally unbuildable "
            "(the WHETHER gate would compose around an absent term); nothing to "
            "compose (no silent fallbacks)"
        )
    if conviction_use_counter is not None:
        if conviction_use_counter.cap.weights_sha256 != conviction_sha:
            raise ValueError(
                "shared conviction use_counter is keyed on weights "
                f"{conviction_use_counter.cap.weights_sha256!r} but "
                f"{conviction_artifact_dir} commits {conviction_sha!r} — one "
                "counter never meters two artifacts"
            )
        if conviction_use_counter.cap.max_uses > conviction_cap.max_uses:
            raise ValueError(
                f"shared conviction use_counter allows "
                f"{conviction_use_counter.cap.max_uses} uses but the committed "
                f"cap under {conviction_artifact_dir} is {conviction_cap.max_uses}"
                " — a shared counter may tighten the committed staleness cap, "
                "never loosen it"
            )
        conviction_counter = conviction_use_counter
    else:
        conviction_counter = ConvictionUseCounter(conviction_cap)

    return ComposedComponents(
        conviction_model=conviction_model,
        conviction_weights_sha256=conviction_sha,
        conviction_use_counter=conviction_counter,
        conviction_verdict=conviction_verdict,
        ballot_predictor=ballot_predictor,
        surrogate_weights_sha256=surrogate_sha,
        surrogate_use_counter=surrogate_counter,
    )


def load_composed_runner_factory(
    *,
    conviction_artifact_dir: Path = _CONVICTION_ARTIFACT_DIR,
    surrogate_artifact_dir: Path = _SURROGATE_ARTIFACT_DIR,
    conviction_use_counter: ConvictionUseCounter | None = None,
    surrogate_use_counter: SurrogateUseCounter | None = None,
    corpus_dir: Path | None = None,
) -> Callable[[], ComposedMeetingRunner]:
    """Build a per-game composed-runner factory (18.21's ``Callable[[], MeetingRunner]``).

    Loads + fences both components ONCE (:func:`load_composed_components`) and
    returns a zero-arg factory. Every runner the factory constructs shares the
    SAME :class:`ComposedComponents` and therefore BOTH use-counters — cumulative
    across games (a fresh runner per game never resets them), the surrogate-factory
    ownership doctrine. This is the slot 18.21's runner-factory seam plugs a
    GO-verdict composed runner into without ever editing the frozen driver.
    """

    components = load_composed_components(
        conviction_artifact_dir=conviction_artifact_dir,
        surrogate_artifact_dir=surrogate_artifact_dir,
        conviction_use_counter=conviction_use_counter,
        surrogate_use_counter=surrogate_use_counter,
        corpus_dir=corpus_dir,
    )

    def factory() -> ComposedMeetingRunner:
        return ComposedMeetingRunner(components=components)

    return factory


# --------------------------------------------------------------------------- #
# The composed MeetingRunner                                                   #
# --------------------------------------------------------------------------- #


def _expected_vote_shares(
    living: tuple[PlayerId, ...],
    by_voter: Mapping[PlayerId, PredictedBallot],
) -> dict[PlayerId, float]:
    """The surrogate's Form-B expected vote share per candidate, computed live.

    ``share[cand] = mean over the candidate's eligible (non-self) voters of that
    voter's predicted ``target_probs`` for the candidate`` — the exact
    :meth:`training.surrogate.ballots.BallotSurrogateModel.predict` recipe
    (ballots.py:867-878), voters iterated in sorted id order. An absent mass
    (a candidate outside a voter's teammate-excluded choice set) reads 0.0; a
    candidate no eligible voter can name reads 0.0.
    """

    sorted_voters = sorted(by_voter)
    shares: dict[PlayerId, float] = {}
    for cand in living:
        masses = [
            by_voter[voter].target_probs.get(cand, 0.0)
            for voter in sorted_voters
            if voter != cand
        ]
        shares[cand] = float(np.mean(masses)) if masses else 0.0
    return shares


def _can_name_target(
    voter: PlayerId, target: PlayerId, impostor_ids: frozenset[PlayerId]
) -> bool:
    """Whether ``voter`` may validly name ``target`` (the §7.12 firewall rule).

    A voter may name the target iff it is not the target itself and not (the
    voter is an impostor and the target is a fellow impostor) — the same
    candidate-set exclusion the surrogate leg uses, so the firewall survives
    re-anchoring by construction.
    """

    if voter == target:
        return False
    return not (voter in impostor_ids and target in impostor_ids)


def _rewrite_ballot(
    ballot: VoteBallot, *, target: PlayerId | str, confidence: float
) -> VoteBallot:
    """A re-anchored ballot: new target/confidence, the audit-marker rationale."""

    return ballot.model_copy(
        update={
            "target": target,
            "confidence": confidence,
            "primary_reason_id": None,
            "considered_alternatives": (),
            "rationale_text": _REANCHOR_RATIONALE,
        }
    )


def _reanchor_ballots(
    *,
    ballots: dict[PlayerId, VoteBallot],
    by_voter: Mapping[PlayerId, PredictedBallot],
    predicted_confidence: Mapping[PlayerId, float],
    living: tuple[PlayerId, ...],
    impostor_ids: frozenset[PlayerId],
    target: PlayerId,
    meeting_id: str,
) -> None:
    """Re-anchor the predicted ballots onto ``target`` through the REAL tally.

    Deterministic, minimal-perturbation. Mutates ``ballots`` in place until
    :func:`meetings.voting.tally_ballots` returns ``("EJECTED", target)`` — the
    tally is recomputed at EVERY step (never a re-implemented count). Raises
    :class:`ComposedBallotSynthesisError` when the ejection is structurally
    unreachable (a roster the real path could not eject the target on either).
    """

    threshold = DEFAULT_SKIP_CONFIDENCE_THRESHOLD

    def mass_key(voter: PlayerId) -> tuple[float, PlayerId]:
        return (-by_voter[voter].target_probs.get(target, 0.0), voter)

    def real_tally_outcome() -> tuple[str, PlayerId | None]:
        return tally_ballots(
            [ballots[voter] for voter in living],
            skip_confidence_threshold=threshold,
        )

    def try_confidence_anchor() -> bool:
        # When the target holds strict plurality but the tally still skips because
        # no target-ballot reaches the gate, raise the single best-mass
        # target-ballot's confidence to exactly the gate and re-tally (inclusive
        # at cutoff). Applied ONLY when it completes the ejection — reverted
        # otherwise, so it never fires on a still-tied plurality. The bumped
        # ballot is RE-STAMPED with the re-anchor marker (Codex review on PR
        # #310): the composition changed it to land the ejection, so the audit
        # trail must never claim it is the surrogate's untouched prediction.
        target_voters = [v for v in living if ballots[v].target == target]
        if not target_voters:
            return False
        best = min(target_voters, key=mass_key)
        saved = ballots[best]
        if saved.confidence >= threshold:
            return False
        ballots[best] = _rewrite_ballot(
            saved, target=saved.target, confidence=threshold
        )
        if real_tally_outcome() == ("EJECTED", target):
            return True
        ballots[best] = saved
        return False

    if real_tally_outcome() == ("EJECTED", target):
        return

    # Phase 1 — flip eligible voters not already on the target, in descending
    # target-mass order (re-anchor where the surrogate's mass already points).
    eligible = sorted(
        (v for v in living if _can_name_target(v, target, impostor_ids)),
        key=mass_key,
    )
    for voter in eligible:
        if ballots[voter].target == target:
            continue
        ballots[voter] = _rewrite_ballot(
            ballots[voter], target=target, confidence=predicted_confidence[voter]
        )
        if real_tally_outcome() == ("EJECTED", target):
            return
        if try_confidence_anchor():
            return

    # Phase 2 — flipping every eligible voter still does not eject the target:
    # spread the competing ballots (the target + its fellow impostors, which
    # cannot name it) onto distinct valid candidates so none ties the target.
    non_namers = sorted(
        v for v in living if not _can_name_target(v, target, impostor_ids)
    )
    for index, voter in enumerate(non_namers):
        teammates = impostor_ids - {voter} if voter in impostor_ids else frozenset()
        valid = sorted(
            cand
            for cand in living
            if cand != voter and cand not in teammates and cand != target
        )
        pick: PlayerId | str = valid[index % len(valid)] if valid else SKIP_TARGET
        ballots[voter] = _rewrite_ballot(
            ballots[voter], target=pick, confidence=predicted_confidence[voter]
        )
    if real_tally_outcome() == ("EJECTED", target):
        return
    if try_confidence_anchor():
        return

    raise ComposedBallotSynthesisError(
        f"composed meeting {meeting_id!r} convicts on ranked target {target!r} "
        f"but re-anchoring could not land ('EJECTED', {target!r}) through the "
        f"real tally over living roster {living} (impostors "
        f"{sorted(impostor_ids)}); this is structurally unreachable on a roster "
        "the real vote path could itself eject the target on — refusing to "
        "silently downgrade the conviction decision"
    )


class ComposedMeetingRunner:
    """The composed :class:`~orchestrator.game.MeetingRunner` (Task 18.29 public type).

    Conviction decides WHETHER, the surrogate ranking channel decides WHO, and
    the ballots are synthesized coherently with the outcome through the real
    :func:`meetings.voting.tally_ballots`. Construct via
    :func:`load_composed_runner_factory` for the committed-artifact wiring. Never
    mutates ``state``; echoes ``meeting_id`` / ``triggered_by`` / ``trigger_tick``
    (the ``_validate_runner_result`` invariants); returns one ballot per living
    voter (the belief fold reads the voter roster).
    """

    def __init__(self, *, components: ComposedComponents) -> None:
        self._components = components

    @property
    def conviction_weights_sha256(self) -> str:
        return self._components.conviction_weights_sha256

    @property
    def surrogate_weights_sha256(self) -> str:
        return self._components.surrogate_weights_sha256

    @property
    def conviction_use_counter(self) -> ConvictionUseCounter:
        return self._components.conviction_use_counter

    @property
    def surrogate_use_counter(self) -> SurrogateUseCounter:
        return self._components.surrogate_use_counter

    async def run_meeting(
        self,
        *,
        meeting_id: str,
        trigger: MeetingTrigger,
        state: WorldState,
        agents: Mapping[PlayerId, AgentInterface],
    ) -> MeetingArtifacts:
        """Compose one meeting: surrogate leg → ranking → conviction gate → tally.

        Reads ``state`` and the agents' meeting-input accessors only — never
        mutates either (the protocol contract; engine-state application happens
        through ``apply_meeting_result`` after this returns).
        """

        components = self._components
        surrogate_sha = components.surrogate_weights_sha256
        conviction_sha = components.conviction_weights_sha256

        # 1. Meter the SURROGATE counter at meeting entry (one run_meeting = one
        #    use — the surrogate runner's own doctrine).
        components.surrogate_use_counter.record_use(weights_sha256=surrogate_sha)

        # 2. Build the surrogate leg EXACTLY as SurrogateMeetingRunner does.
        living = tuple(
            sorted(pid for pid, player in state.players.items() if player.alive)
        )
        impostor_ids = frozenset(
            pid for pid, player in state.players.items() if player.role == "IMPOSTOR"
        )
        meeting_index = float(_meeting_index_from_id(meeting_id))
        alive_count = float(len(living))
        by_voter: dict[PlayerId, PredictedBallot] = {}
        predicted_confidence: dict[PlayerId, float] = {}
        ballots: dict[PlayerId, VoteBallot] = {}
        for voter in living:
            agent = agents.get(voter)
            if agent is None:
                raise ValueError(
                    f"composed meeting {meeting_id!r} has no agent for living "
                    f"player {voter!r}; every alive player must have a "
                    "constructed agent"
                )
            if not isinstance(agent, MeetingAwareAgent):
                raise TypeError(
                    f"agent for {voter!r} does not implement MeetingAwareAgent; "
                    "the composed runner reads suspicion_graph_for_meeting() and "
                    "vent_witness_records_for_meeting() — the same inputs the "
                    "real meeting consumes"
                )
            suspicion = {
                entry.player_id: entry for entry in agent.suspicion_graph_for_meeting()
            }
            vent_subjects = frozenset(
                record.subject for record in agent.vent_witness_records_for_meeting()
            )
            teammates = impostor_ids - {voter} if voter in impostor_ids else frozenset()
            candidates = tuple(
                cand for cand in living if cand != voter and cand not in teammates
            )
            features: dict[PlayerId, dict[str, float]] = {}
            for cand in candidates:
                entry = suspicion.get(cand)
                features[cand] = {
                    "belief_suspicion": (
                        float(entry.suspicion) if entry is not None else _NEUTRAL_PRIOR
                    ),
                    "belief_trust": (
                        float(entry.trust) if entry is not None else _NEUTRAL_PRIOR
                    ),
                    "is_reporter": float(cand == trigger.triggered_by),
                    "witnessed_vent": float(cand in vent_subjects),
                    "meeting_index": meeting_index,
                    "alive_count": alive_count,
                }
            predicted = components.ballot_predictor.predict_ballot(
                VoterBallotView(voter=voter, candidates=candidates, features=features)
            )
            by_voter[voter] = predicted
            predicted_confidence[voter] = predicted.confidence
            ballots[voter] = VoteBallot(
                voter=voter,
                target=predicted.target,
                confidence=predicted.confidence,
                primary_reason_id=None,
                considered_alternatives=(),
                rationale_text=_COMPOSED_RATIONALE,
            )

        # 3. Ranking channel — the committed Form-B recipe, computed live.
        shares = _expected_vote_shares(living, by_voter)
        ranking = tuple(sorted(living, key=lambda cand: (-shares[cand], cand)))

        # 4. Conviction gate — assemble live features, predict, THEN meter (on
        #    DELIVERY: a failed assembly/predict never burns quota).
        conviction_features = assemble_live_conviction_features(
            meeting_id=meeting_id, state=state, agents=agents
        )
        prediction = components.conviction_model.predict(conviction_features)
        components.conviction_use_counter.record_use(weights_sha256=conviction_sha)
        convict = prediction.conversion_prob >= CONVICTION_CONVERSION_DECISION_THRESHOLD

        # 5. Convict → re-anchor onto ranking[0]; skip → ballots pass through.
        if convict and ranking:
            _reanchor_ballots(
                ballots=ballots,
                by_voter=by_voter,
                predicted_confidence=predicted_confidence,
                living=living,
                impostor_ids=impostor_ids,
                target=ranking[0],
                meeting_id=meeting_id,
            )

        final_ballots = tuple(ballots[voter] for voter in living)

        # 6. The REAL tally is the ONLY source of the outcome.
        outcome, ejected = tally_ballots(
            final_ballots, skip_confidence_threshold=DEFAULT_SKIP_CONFIDENCE_THRESHOLD
        )
        if convict and ranking and (outcome, ejected) != ("EJECTED", ranking[0]):
            raise ComposedBallotSynthesisError(
                f"composed meeting {meeting_id!r} convicts on target "
                f"{ranking[0]!r} but the real tally returned {(outcome, ejected)!r}"
                " after re-anchoring — never silently downgrade a convict decision"
            )

        # 7. One ballot per living voter, always (the belief fold roster).
        result = MeetingResult(
            meeting_id=meeting_id,
            triggered_by=trigger.triggered_by,
            trigger_tick=trigger.trigger_tick,
            outcome=outcome,
            ejected_player_id=ejected,
            ballots=final_ballots,
            contradictions=(),
            transcript=MeetingTranscript(),
        )
        return MeetingArtifacts(result=result, llm_calls=(), prompt_versions={})


# --------------------------------------------------------------------------- #
# Offline fidelity — the pre-registered bar's measurement                      #
# --------------------------------------------------------------------------- #


class ComposedFidelityReport(BaseModel):
    """Held-out composed fidelity — pure measurement (the bars live in the verdict).

    Every cell is measured on the SAME held-out population (the committed
    ``splits.json`` test side: 96 meetings / 60 ejections). ``decision_accuracy``
    and ``convicting_top1`` are the two gating channels; ``exact_outcome_match``
    is informational. The honest-diagnosis fields (gate confusion vs the ejection
    label, the predicted-convict count, the surrogate tally's decision census —
    its all-SKIP degeneracy is the NO-GO fact this composes around, and the
    conditioned ``convicting_top1_gated``) are reported beside, never gating.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    replay_set_dir: str
    conviction_weights_sha256: str = Field(min_length=64, max_length=64)
    surrogate_weights_sha256: str = Field(min_length=64, max_length=64)
    test_meetings: int
    test_ejections: int
    always_eject_baseline: float
    # The two gating channels + the informational one.
    decision_accuracy: float
    convicting_top1: float
    top1_ceiling: float
    exact_outcome_match: float
    # Honest diagnosis (reported beside, never gating).
    predicted_convictions: int
    gate_true_positives: int
    gate_false_positives: int
    gate_false_negatives: int
    gate_true_negatives: int
    surrogate_tally_ejections: int
    surrogate_tally_skips: int
    convicting_top1_gated: float


def run_composed_fidelity(
    corpus_dir: Path,
    *,
    conviction_artifact_dir: Path = _CONVICTION_ARTIFACT_DIR,
    surrogate_artifact_dir: Path = _SURROGATE_ARTIFACT_DIR,
) -> ComposedFidelityReport:
    """Score the composition on the held-out split (mirrors run_surrogate_fidelity).

    Split discipline: the committed ``splits.json`` is honored, the fit side is
    NEVER scored, and the verdict is taken on the FIRST held-out evaluation. Both
    tables' test seed sets are cross-checked identical; every test meeting joins
    the surrogate :class:`~training.surrogate.fidelity.MeetingView` to its
    conviction row on ``(seed, meeting_id)`` exactly once. Per meeting the
    composed prediction mirrors the runner semantics: convict ⇒
    ``("EJECTED", ranking[0])``; else the surrogate tally's own pass-through
    output. Both committed artifacts are loaded sha-verified and evaluated FROZEN
    (no refit).
    """

    table = build_meeting_table(corpus_dir)
    if table.splits is None:
        raise ValueError(
            f"{corpus_dir} ships no committed splits.json; the composed verdict "
            "is a single pre-registered held-out evaluation — use the corpus"
        )
    test_seeds = frozenset(table.splits.test)
    views = build_meeting_views(table)

    ctable = build_conviction_table(corpus_dir)
    _, conviction_test_seeds = validate_conviction_split(ctable)
    if conviction_test_seeds != test_seeds:
        raise ValueError(
            "the surrogate and conviction tables disagree on the held-out test "
            f"seeds: surrogate {sorted(test_seeds)} vs conviction "
            f"{sorted(conviction_test_seeds)} — the composition scores ONE "
            "population"
        )

    ballot_predictor, surrogate_sha = load_ballot_predictor_artifact(
        surrogate_artifact_dir
    )
    conviction_model, conviction_sha = load_conviction_model_artifact(
        conviction_artifact_dir
    )
    surrogate_model = BallotSurrogateModel(table, predictor=ballot_predictor)

    test_views = sorted(
        (view for view in views if view.seed in test_seeds),
        key=lambda view: (view.seed, view.meeting_id),
    )
    conviction_rows = {
        (row.seed, row.meeting_id): row for row in ctable.rows if row.seed in test_seeds
    }
    if len(conviction_rows) != len(test_views):
        raise ValueError(
            f"held-out join mismatch: {len(test_views)} surrogate test meetings "
            f"vs {len(conviction_rows)} conviction test rows — every test meeting "
            "must join exactly once"
        )

    decision_correct = 0
    exact_matches = 0
    ejection_meetings = 0
    top1_hits = 0
    gated_ejection_meetings = 0
    top1_gated_hits = 0
    predicted_convictions = 0
    tp = fp = fn = tn = 0
    surrogate_tally_ejections = 0
    surrogate_tally_skips = 0

    for view in test_views:
        row = conviction_rows.get((view.seed, view.meeting_id))
        if row is None:
            raise ValueError(
                f"held-out test meeting {view.seed}:{view.meeting_id} has no "
                "conviction row to join — the two tables must cover the same "
                "meetings"
            )
        meeting_prediction = surrogate_model.predict(view)
        convict = (
            conviction_model.predict(row.features).conversion_prob
            >= CONVICTION_CONVERSION_DECISION_THRESHOLD
        )
        if convict:
            predicted_convictions += 1
        if meeting_prediction.ejected is not None:
            surrogate_tally_ejections += 1
        else:
            surrogate_tally_skips += 1

        # The composed predicted outcome — the exact runner semantics.
        if convict:
            composed_ejected: PlayerId | None = meeting_prediction.ranking[0]
        else:
            composed_ejected = meeting_prediction.ejected
        composed_is_ejection = composed_ejected is not None
        actual_is_ejection = view.ejected is not None

        if composed_is_ejection == actual_is_ejection:
            decision_correct += 1
        if composed_ejected == view.ejected:
            exact_matches += 1

        if convict and actual_is_ejection:
            tp += 1
        elif convict and not actual_is_ejection:
            fp += 1
        elif not convict and actual_is_ejection:
            fn += 1
        else:
            tn += 1

        if actual_is_ejection:
            ejection_meetings += 1
            hit = bool(
                meeting_prediction.ranking
                and meeting_prediction.ranking[0] == view.ejected
            )
            if hit:
                top1_hits += 1
            if convict:
                gated_ejection_meetings += 1
                if hit:
                    top1_gated_hits += 1

    test_meetings = len(test_views)
    if test_meetings == 0 or ejection_meetings == 0:
        raise ValueError(
            "the held-out split has no scoreable meetings or no ejections — the "
            "composed decision/top-1 axes would be undefined"
        )
    honest_ceiling = compute_honest_ceiling(test_views)
    return ComposedFidelityReport(
        replay_set_dir=table.replay_set_dir,
        conviction_weights_sha256=conviction_sha,
        surrogate_weights_sha256=surrogate_sha,
        test_meetings=test_meetings,
        test_ejections=ejection_meetings,
        always_eject_baseline=ejection_meetings / test_meetings,
        decision_accuracy=decision_correct / test_meetings,
        convicting_top1=top1_hits / ejection_meetings,
        top1_ceiling=honest_ceiling.max_achievable_top1,
        exact_outcome_match=exact_matches / test_meetings,
        predicted_convictions=predicted_convictions,
        gate_true_positives=tp,
        gate_false_positives=fp,
        gate_false_negatives=fn,
        gate_true_negatives=tn,
        surrogate_tally_ejections=surrogate_tally_ejections,
        surrogate_tally_skips=surrogate_tally_skips,
        convicting_top1_gated=(
            top1_gated_hits / gated_ejection_meetings
            if gated_ejection_meetings
            else 0.0
        ),
    )


# --------------------------------------------------------------------------- #
# The verdict + manifest + their writers/loaders                              #
# --------------------------------------------------------------------------- #


class ComposedGoVerdict(BaseModel):
    """The pre-stated GO/NO-GO verdict for the composition (frozen).

    GO ⇔ ``decision_accuracy > always_eject_baseline`` (strict — a channel worse
    than the strictest trivial constant never ships) AND ``convicting_top1 >=
    GO_TOP1_CEILING_RATIO × honest_ceiling`` (inclusive at the standing axis-1
    bar). Exact-outcome match NEVER gates. Pre-committed consequence: GO ⇒ the
    runner is an OPTIONAL campaign configuration; NO-GO ⇒ diagnostic-only. Keyed
    to BOTH component shas.

    ``adoption_constraints`` carries the composed-path Goodhart leg's NAMED
    adoption constraints machine-readably (Codex review on PR #310): a driver
    that branches on this verdict alone must still see them, never only the
    report's prose. They ride WITH the pre-committed consequence — they never
    flip the GO/NO-GO mapping (that would re-tune the pre-registered bar after
    measurement) — and an adopting campaign carries every one in its meters.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    replay_set_dir: str
    test_meetings: int
    test_ejections: int
    # Axis 1 — meeting-level decision accuracy vs the always-eject baseline.
    decision_accuracy: float
    decision_accuracy_bar: float
    meets_decision_bar: bool
    # Axis 2 — convicting-meeting top-1 vs the honest-ceiling-relative bar.
    convicting_top1: float
    top1_bar: float
    top1_ceiling: float
    top1_ceiling_ratio: float
    meets_top1_bar: bool
    # Informational (never gating).
    exact_outcome_match: float
    verdict: Literal["GO", "NO-GO"]
    composed_role: Literal["optional-campaign-configuration", "diagnostic-only"]
    # The Goodhart leg's named adoption constraints, machine-readable beside the
    # consequence (never flipping it).
    adoption_constraints: tuple[str, ...] = ()
    conviction_weights_sha256: str = Field(min_length=64, max_length=64)
    surrogate_weights_sha256: str = Field(min_length=64, max_length=64)


def decide_composed_go(
    report: ComposedFidelityReport,
    *,
    conviction_weights_sha256: str,
    surrogate_weights_sha256: str,
    adoption_constraints: tuple[str, ...] = (),
) -> ComposedGoVerdict:
    """Apply the pre-registered bar to a held-out composed fidelity report.

    The two component shas are cross-checked against the report's (fail loud on
    drift) so the verdict is keyed to exactly the artifacts the numbers were
    produced by. GO ⇔ the decision channel strictly beats always-eject AND the
    convicting top-1 clears the standing axis-1 bar; exact-outcome match never
    flips the verdict. ``adoption_constraints`` (additive keyword) carries the
    Goodhart leg's named adoption constraints into the machine-readable verdict
    — they ride beside the consequence and never move the GO/NO-GO decision.
    """

    if conviction_weights_sha256 != report.conviction_weights_sha256:
        raise ValueError(
            f"conviction sha {conviction_weights_sha256!r} != the report's "
            f"{report.conviction_weights_sha256!r} — the verdict must key to the "
            "artifact the numbers were produced by"
        )
    if surrogate_weights_sha256 != report.surrogate_weights_sha256:
        raise ValueError(
            f"surrogate sha {surrogate_weights_sha256!r} != the report's "
            f"{report.surrogate_weights_sha256!r} — the verdict must key to the "
            "artifact the numbers were produced by"
        )

    decision_bar = report.always_eject_baseline
    meets_decision = report.decision_accuracy > decision_bar
    top1_bar = GO_TOP1_CEILING_RATIO * report.top1_ceiling
    meets_top1 = report.convicting_top1 >= top1_bar
    is_go = meets_decision and meets_top1
    return ComposedGoVerdict(
        replay_set_dir=report.replay_set_dir,
        test_meetings=report.test_meetings,
        test_ejections=report.test_ejections,
        decision_accuracy=report.decision_accuracy,
        decision_accuracy_bar=decision_bar,
        meets_decision_bar=meets_decision,
        convicting_top1=report.convicting_top1,
        top1_bar=top1_bar,
        top1_ceiling=report.top1_ceiling,
        top1_ceiling_ratio=GO_TOP1_CEILING_RATIO,
        meets_top1_bar=meets_top1,
        exact_outcome_match=report.exact_outcome_match,
        verdict="GO" if is_go else "NO-GO",
        composed_role=(
            "optional-campaign-configuration" if is_go else "diagnostic-only"
        ),
        adoption_constraints=adoption_constraints,
        conviction_weights_sha256=conviction_weights_sha256,
        surrogate_weights_sha256=surrogate_weights_sha256,
    )


class ComposedManifest(BaseModel):
    """The component-sha manifest — the composed artifact carries NO weights (frozen).

    Pins both committed component shas, the component conviction verdict the
    composition was built under (**GO**), the corpus set, the two pinned
    thresholds (the conviction decision gate and the tally's skip-confidence
    gate, quoted from the imported constants — never re-stated literals), and the
    bar verdict the manifest commits.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    conviction_weights_sha256: str = Field(min_length=64, max_length=64)
    surrogate_weights_sha256: str = Field(min_length=64, max_length=64)
    conviction_verdict: Literal["GO"]
    corpus_set: str
    replay_set_dir: str
    decision_threshold: float
    skip_confidence_threshold: float
    composed_verdict: Literal["GO", "NO-GO"]


def build_composed_manifest(
    verdict: ComposedGoVerdict,
    *,
    conviction_verdict: ConvictionGoVerdict,
) -> ComposedManifest:
    """Assemble the component-sha manifest from the bar verdict + the component one."""

    if conviction_verdict.verdict != "GO":
        raise ValueError(
            f"the component conviction verdict is {conviction_verdict.verdict!r}"
            " — the composed runner is only buildable under a GO conviction model"
        )
    if conviction_verdict.weights_sha256 != verdict.conviction_weights_sha256:
        raise ValueError(
            "the component conviction verdict's weights sha "
            f"{conviction_verdict.weights_sha256!r} != the composed verdict's "
            f"{verdict.conviction_weights_sha256!r}"
        )
    return ComposedManifest(
        conviction_weights_sha256=verdict.conviction_weights_sha256,
        surrogate_weights_sha256=verdict.surrogate_weights_sha256,
        conviction_verdict="GO",
        corpus_set=_CORPUS_SET,
        replay_set_dir=verdict.replay_set_dir,
        decision_threshold=CONVICTION_CONVERSION_DECISION_THRESHOLD,
        skip_confidence_threshold=DEFAULT_SKIP_CONFIDENCE_THRESHOLD,
        composed_verdict=verdict.verdict,
    )


def write_composed_verdict_artifact(
    verdict: ComposedGoVerdict, artifact_dir: Path
) -> None:
    """Commit the machine-readable composed verdict (sorted keys + trailing newline)."""

    artifact_dir.mkdir(parents=True, exist_ok=True)
    (artifact_dir / COMPOSED_VERDICT_FILENAME).write_text(
        json.dumps(verdict.model_dump(), indent=2, sort_keys=True) + "\n"
    )


def write_composed_manifest_artifact(
    manifest: ComposedManifest, artifact_dir: Path
) -> None:
    """Commit the component-sha manifest (sorted keys + trailing newline)."""

    artifact_dir.mkdir(parents=True, exist_ok=True)
    (artifact_dir / COMPOSED_MANIFEST_FILENAME).write_text(
        json.dumps(manifest.model_dump(), indent=2, sort_keys=True) + "\n"
    )


def load_composed_verdict(artifact_dir: Path) -> ComposedGoVerdict:
    """Read the committed composed verdict beside the manifest (fail loud)."""

    path = artifact_dir / COMPOSED_VERDICT_FILENAME
    if not path.is_file():
        raise FileNotFoundError(
            f"no committed composed verdict at {path}; a campaign consumes the "
            "machine-readable verdict, never a prose reading of the report"
        )
    return ComposedGoVerdict.model_validate_json(path.read_text())


def load_composed_manifest(artifact_dir: Path) -> ComposedManifest:
    """Read the committed composed component-sha manifest (fail loud)."""

    path = artifact_dir / COMPOSED_MANIFEST_FILENAME
    if not path.is_file():
        raise FileNotFoundError(
            f"no committed composed manifest at {path}; the composed artifact is "
            "the component-sha manifest + verdict, never learned weights"
        )
    return ComposedManifest.model_validate_json(path.read_text())


# --------------------------------------------------------------------------- #
# The composed-path Goodhart leg                                              #
# --------------------------------------------------------------------------- #


class ComposedGoodhartLeg(BaseModel):
    """The composed-path Goodhart leg — 18.18's machinery over the composed runner.

    Embeds the whole :class:`~training.bakeoff.goodhart.ConvictionPathProbeReport`
    (which itself embeds the standing probe), records the composed-path meeting
    stats, and re-quotes the component consumption on the ONE shared sha-keyed
    conviction counter + the surrogate counter. ``blockers`` / ``verdict`` mirror
    the probe's — any above-bar finding is a NAMED campaign-adoption blocker,
    never a silent caveat.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    roster_key: str
    baseline_id: str
    substrate_note: str
    conviction_weights_sha256: str = Field(min_length=64, max_length=64)
    surrogate_weights_sha256: str = Field(min_length=64, max_length=64)
    materiality_bar: float
    probe: ConvictionPathProbeReport
    composed_meetings: int
    surrogate_uses: int
    conviction_uses_runner: int
    conviction_uses_probe: int
    conviction_uses_total: int
    conviction_max_uses: int
    surrogate_uses_total: int
    surrogate_max_uses: int
    consumption_note: str
    blockers: tuple[str, ...]
    verdict: Literal["HELD", "EXPLOITS_FOUND"]

    def to_json(self) -> str:
        return json.dumps(self.model_dump(mode="json"), sort_keys=True, indent=2)


def run_composed_goodhart_leg(
    *,
    config: ESConfig,
    num_players: int = 9,
    num_impostors: int = 2,
    tasks_per_crewmate: int = 2,
    baseline_id: str = "baseline-6",
    materiality_bar: float = 0.25,
    conviction_artifact_dir: Path = _CONVICTION_ARTIFACT_DIR,
    surrogate_artifact_dir: Path = _SURROGATE_ARTIFACT_DIR,
) -> ComposedGoodhartLeg:
    """Run 18.18's conviction-path probe over the composed runner as the meeting path.

    Builds ONE shared :class:`~training.conviction.model.ConvictionUseCounter`
    and ONE shared :class:`~training.surrogate.runner.SurrogateUseCounter`,
    threads both through a composed runner factory, and drives
    :func:`~training.bakeoff.goodhart.run_conviction_path_probe` with that factory
    plus the shared conviction counter. The ONE-shared-counter discipline: the
    probe's fitness-term + prescreen reads AND the composed runner's own
    per-meeting gate all meter the same conviction counter, and every composed
    meeting also meters the surrogate counter. ``composed_meetings`` is the
    surrogate-counter delta (one surrogate use per composed meeting);
    ``conviction_uses_runner`` is that same count (the composed runner meters the
    conviction counter once per meeting); ``conviction_uses_probe`` is the
    probe's own reads (its total minus the composed runner's share).
    """

    conviction_counter = ConvictionUseCounter(
        load_conviction_staleness_cap(conviction_artifact_dir)
    )
    surrogate_counter = SurrogateUseCounter(load_staleness_cap(surrogate_artifact_dir))
    factory = load_composed_runner_factory(
        conviction_artifact_dir=conviction_artifact_dir,
        surrogate_artifact_dir=surrogate_artifact_dir,
        conviction_use_counter=conviction_counter,
        surrogate_use_counter=surrogate_counter,
    )

    surrogate_before = surrogate_counter.uses
    probe = run_conviction_path_probe(
        config=config,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        baseline_id=baseline_id,
        materiality_bar=materiality_bar,
        conviction_artifact_dir=conviction_artifact_dir,
        use_counter=conviction_counter,
        meeting_runner_factory=factory,
    )

    # One surrogate use per composed meeting; the composed runner meters the
    # shared conviction counter exactly once per meeting too, so the probe's own
    # reads are its total minus that share (the 2× per recorded meeting invariant).
    composed_meetings = surrogate_counter.uses - surrogate_before
    conviction_uses_runner = composed_meetings
    conviction_uses_probe = probe.conviction_uses - composed_meetings

    substrate_note = (
        "Substrate: the COMPOSED meeting path (conviction decides WHETHER, the "
        "ballot surrogate's ranking channel decides WHO, ballots synthesized "
        "through the real tally) — the embedded probe's prose says 'surrogate "
        "meeting path' for any non-fake factory; this leg owns the composed "
        "framing. The recorded-bytes pairing rule (report-goodhart-probe.md §7) "
        "holds: the probe pairs every predicted (pre-screen) floor read with a "
        "recorded floor read on the SAME replay bytes, so a composed-path "
        "'prescreen-substrate-divergence' blocker (if present) means a "
        "pre-screen PASS is real-path spend advice ONLY on the composed "
        "substrate — never a recorded-floor read on a substrate whose meetings "
        "mint no flags in bytes."
    )
    consumption_note = (
        "Component consumption on the composed path: "
        f"{composed_meetings} composed meetings ran (surrogate uses "
        f"{surrogate_counter.uses} of the committed cap "
        f"{surrogate_counter.cap.max_uses}); the shared sha-keyed conviction "
        f"counter charged {conviction_uses_runner} composed-runner gate reads + "
        f"{conviction_uses_probe} probe reads (2× per recorded meeting: the "
        "fitness-term read and the composed-gate pre-screen read), total "
        f"{conviction_counter.uses} of the committed cap "
        f"{conviction_counter.cap.max_uses}. No prediction ran unmetered."
    )

    return ComposedGoodhartLeg(
        roster_key=probe.roster_key,
        baseline_id=baseline_id,
        substrate_note=substrate_note,
        conviction_weights_sha256=conviction_counter.cap.weights_sha256,
        surrogate_weights_sha256=surrogate_counter.cap.weights_sha256,
        materiality_bar=materiality_bar,
        probe=probe,
        composed_meetings=composed_meetings,
        surrogate_uses=composed_meetings,
        conviction_uses_runner=conviction_uses_runner,
        conviction_uses_probe=conviction_uses_probe,
        conviction_uses_total=conviction_counter.uses,
        conviction_max_uses=conviction_counter.cap.max_uses,
        surrogate_uses_total=surrogate_counter.uses,
        surrogate_max_uses=surrogate_counter.cap.max_uses,
        consumption_note=consumption_note,
        blockers=probe.blockers,
        verdict=probe.verdict,
    )


__all__ = [
    "COMPOSED_MANIFEST_FILENAME",
    "COMPOSED_VERDICT_FILENAME",
    "ComposedBallotSynthesisError",
    "ComposedComponents",
    "ComposedFidelityReport",
    "ComposedGoVerdict",
    "ComposedGoodhartLeg",
    "ComposedManifest",
    "ComposedMeetingRunner",
    "build_composed_manifest",
    "decide_composed_go",
    "load_composed_components",
    "load_composed_manifest",
    "load_composed_runner_factory",
    "load_composed_verdict",
    "run_composed_fidelity",
    "run_composed_goodhart_leg",
    "write_composed_manifest_artifact",
    "write_composed_verdict_artifact",
]
