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

Phase 19 tier map (training/README.md §2a), the standalone-vs-dependency
boundary: the surrogate RANKING channel is KEPT (46/60 top-1); the standalone
DECISION arm is the NO-GO in ``training/reports/report-ballot-surrogate.md`` §5
(all-SKIP census). The factory, the class, and the counter STAY:
``training/composed_runner.py``'s verification fence and
``training/bakeoff/harness.py`` consume them.

Task 19.19's retire item — a surrogate-ONLY runner exposure proven CONSUMER-FREE
— resolved as a RECORDED NO-OP. A surrogate-only exposure does exist; what does
not exist is a consumer-free one, and consumer-free was the retire condition.
Every site that installs this runner as the sole meeting runner has a live
consumer:

* ``training/bakeoff/harness.py:2072`` — ``run_goodhart_surrogate_rerun`` hands
  the factory straight to ``run_goodhart_probe``, so the probe's games run on
  this runner ALONE. That IS a surrogate-only exposure, and it is driven by a
  live CLI: the ``goodhart-surrogate`` subcommand of that module's own ``main``
  (:2208/:2244). It is also pinned by
  ``tests/training/test_bakeoff_harness.py:546``. Consumed, so it stays;
* ``training/bakeoff/harness.py:1763`` — ``evaluate_candidate``'s surrogate-path
  DIAGNOSTIC column, likewise surrogate-only for that pass, feeding
  ``inner_fitness_surrogate`` / ``surrogate_real_divergence`` on the bake-off row;
* ``training/composed_runner.py:278`` — the sha/staleness verification fence
  (calls the factory, discards the result);
* ``eval/balance_eval.py``'s ``meeting_runner_factory`` is a GENERIC seam that
  accepts any :class:`~orchestrator.game.MeetingRunner` factory (the composed
  runner included) — not a surrogate-only arm at all.

Both surrogate-only exposures are DIAGNOSTIC, but they are not diagnostic in the
same way, and the difference matters for the NO-GO:

* the ``:1763`` column SCORES an already-chosen candidate
  (``_score_eval_pass(candidate.policy, ...)``) — it selects nothing;
* the ``:2072`` Goodhart arm DOES select. ``run_goodhart_probe`` runs a full
  :func:`~training.bakeoff.es.evolve` against the referee score and evaluates
  ``result.champion`` (``training/bakeoff/goodhart.py:879-884`` / ``:913``), so a
  PROBE champion is selected on the surrogate path. That is the point of the
  probe — it is the adversarial attack that asks whether the referee is gameable,
  and it has to optimize to answer.

What the surrogate never does is select an ADOPTED entrant: a probe champion is
an artifact of the attack, and the bake-off's adopted numbers are rescored on a
real meeting path (``eval/balance_eval.py``'s reporting rule). That narrower
statement — not "the surrogate never selects a champion" — is what squares these
arms with the standalone-DECISION NO-GO in
``training/reports/report-ballot-surrogate.md`` §5.

Nothing here was force-deleted.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Final, Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field

from agents.base import AgentInterface
from engine.entities import PlayerId
from engine.world import WorldState
from meetings.constants import DEFAULT_SKIP_CONFIDENCE_THRESHOLD
from meetings.manager import MeetingTrigger
from meetings.schemas import MeetingResult, MeetingTranscript, VoteBallot
from meetings.voting import tally_ballots
from orchestrator.game import MeetingArtifacts, MeetingAwareAgent
from training.surrogate.ballots import (
    MASKED_IS_REPORTER,
    BallotPredictor,
    SurrogateStalenessCap,
    VoterBallotView,
    load_ballot_predictor_artifact,
    load_staleness_cap,
)
from training.surrogate.fidelity import GoNoGoVerdict

#: What a caller is installing the loaded surrogate AS. ``"diagnostic"`` covers
#: every path a NO-GO surrogate may still serve (fidelity replays, probes, the
#: composed runner's verification fence); ``"training-time-runner"`` is the role
#: the pre-committed consequence mapping grants only to a GO verdict.
SurrogateInstallRole: TypeAlias = Literal["diagnostic", "training-time-runner"]

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

# The committed fit-corpus provenance sidecar (Task 18.14). ``SurrogateStalenessCap``
# keys only on ``weights_sha256``, so the load path fails loud on WEIGHTS drift but
# is BLIND to SUBSTRATE drift — a bake-off could load weights fitted on one corpus
# against a re-recorded (baseline-N+1) corpus while nothing raised. This sidecar
# records the fit corpus's identity beside the weights so the loader can catch it.
FIT_CORPUS_FILENAME: Final[str] = "fit-corpus.json"

# The committed GO/NO-GO verdict beside the weights artifact, mirroring the
# conviction model's own ``verdict.json``. ``load_surrogate_runner_factory``
# reads it when a caller asks to install the surrogate as a TRAINING-TIME
# runner, so the pre-committed fallback mapping is enforced by the load path
# rather than by convention.
SURROGATE_VERDICT_FILENAME: Final[str] = "verdict.json"

# The repo-relative root under which the canonical corpora live (``9p2i`` / ``4p1i``).
# ``load_surrogate_runner_factory`` uses ``_DEFAULT_CORPUS_ROOT / corpus_set`` only as
# the documentation of where the fit corpus lives; the corpus-identity check itself is
# opt-in via the ``corpus_dir`` argument (recomputing the fingerprint reads every
# replay byte, too costly to run on every per-candidate load).
_DEFAULT_CORPUS_ROOT: Final[Path] = Path("replays/ml_corpus")


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
                    # Masked identically to the fit side, so the frozen weights
                    # multiply the same column here as they were fitted on.
                    "is_reporter": MASKED_IS_REPORTER,
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


class SurrogateFitCorpus(BaseModel):
    """The committed fit-corpus provenance beside the weights (Task 18.14).

    Records the identity of the corpus the surrogate weights were FIT on so the
    load path can catch SUBSTRATE drift, the blind spot
    :class:`~training.surrogate.ballots.SurrogateStalenessCap` leaves: the cap
    keys only on ``weights_sha256``, so a bake-off that loaded these weights
    against a re-recorded (baseline-N+1) corpus would raise on WEIGHTS drift but
    silently optimize a policy against a model fitted on different games. The
    §8 re-grounding recipe re-records the corpus and re-fits the weights
    TOGETHER, so this record is written in the same commit; ``weights_sha256``
    keys it to those exact weights (the loader refuses a record that drifted
    from the artifact).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    corpus_set: str = Field(min_length=1)
    corpus_sha256: str = Field(min_length=64, max_length=64)
    fit_side_meetings: int = Field(gt=0)
    weights_sha256: str = Field(min_length=64, max_length=64)


def fit_corpus_fingerprint(corpus_dir: Path) -> str:
    """One digest of a fit corpus's identity (replay bytes + split + provenance).

    Folds the per-replay sha256 digests (in sorted-filename order), then the
    committed ``splits.json`` and ``MANIFEST.md`` bytes, into a single sha256 —
    the same "hash the recorded bytes, not just the metadata" idiom
    :func:`training.anchor_study._corpus_replays_sha256` uses, so the
    fingerprint moves when ANY recorded game byte, the by-game split, or the
    recording provenance moves. This is the corpus-identity the committed
    :class:`SurrogateFitCorpus` records; recomputing it reads every replay, so
    the loader verifies it only when a caller opts in (``corpus_dir``).
    """

    digest = hashlib.sha256()
    for path in sorted(corpus_dir.glob("replay-seed-*.jsonl")):
        digest.update(path.name.encode("utf-8"))
        digest.update(b"\x00")
        digest.update(hashlib.sha256(path.read_bytes()).hexdigest().encode("utf-8"))
        digest.update(b"\n")
    for meta_name in ("splits.json", "MANIFEST.md"):
        meta_path = corpus_dir / meta_name
        digest.update(meta_name.encode("utf-8"))
        digest.update(b"\x00")
        digest.update(
            hashlib.sha256(meta_path.read_bytes()).hexdigest().encode("utf-8")
        )
        digest.update(b"\n")
    return digest.hexdigest()


def load_fit_corpus_record(artifact_dir: Path) -> SurrogateFitCorpus:
    """Read the committed fit-corpus provenance beside the weights (fail loud).

    Generic over the artifact directory — the surrogate and the conviction model
    both record their fit corpus in this shape — so the message names the
    directory that was asked for rather than one instrument.
    """

    path = artifact_dir / FIT_CORPUS_FILENAME
    if not path.is_file():
        raise FileNotFoundError(
            f"no committed fit-corpus provenance at {path}; an instrument must "
            f"record the corpus it was fitted on so a load against {artifact_dir}"
            " can catch substrate drift (training/reports/"
            "report-ballot-surrogate.md §7)"
        )
    return SurrogateFitCorpus.model_validate_json(path.read_text())


def write_surrogate_verdict_artifact(
    verdict: GoNoGoVerdict, artifact_dir: Path
) -> None:
    """Commit the machine-readable verdict beside the weights artifact.

    Sorted keys + one trailing newline (byte-stable re-serialization), the same
    shape ``write_conviction_verdict_artifact`` commits. A verdict that names no
    weights is refused: ``weights_sha256`` is what the install gate cross-checks
    against the artifact it is about to seat, so an unkeyed verdict would guard
    nothing in particular. It names the weights this verdict AUTHORIZES — the
    bar's own harness re-fits per fold, so no surrogate verdict has ever been a
    measurement OF a frozen artifact.
    """

    if verdict.weights_sha256 is None:
        raise ValueError(
            "a committed surrogate verdict must be keyed on the weights it "
            "judged; pass weights_sha256= to decide_go_no_go"
        )
    artifact_dir.mkdir(parents=True, exist_ok=True)
    (artifact_dir / SURROGATE_VERDICT_FILENAME).write_text(
        json.dumps(verdict.model_dump(), indent=2, sort_keys=True) + "\n"
    )


def load_surrogate_verdict(artifact_dir: Path) -> GoNoGoVerdict:
    """Read the committed surrogate verdict beside the weights (fail loud)."""

    path = artifact_dir / SURROGATE_VERDICT_FILENAME
    if not path.is_file():
        raise FileNotFoundError(
            f"no committed surrogate verdict at {path}; installing the "
            "surrogate as a training-time runner consumes the machine-readable "
            "verdict, never a prose reading of the report"
        )
    return GoNoGoVerdict.model_validate_json(path.read_text())


def load_surrogate_runner_factory(
    artifact_dir: Path,
    *,
    use_counter: SurrogateUseCounter | None = None,
    corpus_dir: Path | None = None,
    install_role: SurrogateInstallRole = "diagnostic",
) -> Callable[[], SurrogateMeetingRunner]:
    """Build a per-game runner factory over the COMMITTED weights artifact.

    Loads the weights (sha256 sidecar verified), loads the committed staleness
    cap, cross-checks the cap is keyed on exactly those weights, loads the
    committed fit-corpus provenance and cross-checks IT is keyed on those
    weights too, and returns a zero-arg factory suitable for
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

    **The substrate fence (Task 18.14).** ``SurrogateStalenessCap`` is blind to
    substrate drift — it keys on the weights, not the corpus they were fitted
    on — so the load path caught WEIGHTS drift but not a re-recorded corpus
    (the §8 hazard: optimizing against a model fitted on different games). The
    committed :class:`SurrogateFitCorpus` closes that gap: its ``weights_sha256``
    is cross-checked here UNCONDITIONALLY (a botched re-fit that moved the
    weights but not the corpus record fails loud). Pass ``corpus_dir`` to verify
    the fit-corpus fingerprint against a live corpus as well — recomputing it
    reads every replay byte (too costly to run on every per-candidate load, so
    it is opt-in); ``replays/ml_corpus/<corpus_set>`` is where the recorded
    ``corpus_set`` lives. A mismatch fails loud rather than scoring a bake-off
    against a stale surrogate.

    **The install gate.** ``install_role="training-time-runner"`` asks for the
    role only a GO verdict grants — the surrogate driving the bake-off's
    meetings — so the committed verdict is loaded, its ``weights_sha256`` must
    name THESE weights, and its COMPOSED ``verdict`` field must read ``GO``. The
    sha cross-check comes first and is what stops a stale or copied GO verdict
    authorizing weights nobody judged; the composed field is the one the
    consequence mapping is defined on, so the reporting split's
    ``ranking_verdict`` / ``decision_verdict`` halves are neither read here nor
    re-conjoined. The default ``"diagnostic"`` is the role every current caller
    holds — the fidelity and probe paths a NO-GO surrogate is explicitly still
    allowed to serve — and loads no verdict at all.
    """

    predictor, weights_sha256 = load_ballot_predictor_artifact(artifact_dir)
    cap = load_staleness_cap(artifact_dir)
    if cap.weights_sha256 != weights_sha256:
        raise ValueError(
            f"staleness cap under {artifact_dir} is keyed on weights "
            f"{cap.weights_sha256!r} but the committed weights hash to "
            f"{weights_sha256!r} — the cap and the artifact drifted apart"
        )
    fit_corpus = load_fit_corpus_record(artifact_dir)
    if fit_corpus.weights_sha256 != weights_sha256:
        raise ValueError(
            f"fit-corpus provenance under {artifact_dir} is keyed on weights "
            f"{fit_corpus.weights_sha256!r} but the committed weights hash to "
            f"{weights_sha256!r} — the fit-corpus record and the artifact "
            "drifted apart (a re-fit must re-write both together, §8)"
        )
    if corpus_dir is not None:
        live_fingerprint = fit_corpus_fingerprint(corpus_dir)
        if live_fingerprint != fit_corpus.corpus_sha256:
            raise ValueError(
                f"the surrogate under {artifact_dir} was fitted on corpus "
                f"{fit_corpus.corpus_set!r} (fingerprint "
                f"{fit_corpus.corpus_sha256[:12]}…) but {corpus_dir} fingerprints "
                f"to {live_fingerprint[:12]}… — the substrate drifted; re-ground "
                "before scoring against this corpus "
                "(training/reports/report-ballot-surrogate.md §8)"
            )
    if install_role == "training-time-runner":
        verdict = load_surrogate_verdict(artifact_dir)
        if verdict.weights_sha256 != weights_sha256:
            raise ValueError(
                f"the committed surrogate verdict under {artifact_dir} is keyed "
                f"on weights {verdict.weights_sha256!r} but the committed "
                f"weights hash to {weights_sha256!r} — a verdict that judged "
                "other weights authorizes nothing here (a re-fit must re-write "
                "both together)"
            )
        if verdict.verdict != "GO":
            raise ValueError(
                f"the committed surrogate verdict under {artifact_dir} is "
                f"{verdict.verdict!r} (surrogate_role={verdict.surrogate_role!r})"
                " — a NO-GO surrogate is DIAGNOSTIC-ONLY and never the "
                "training-time meeting runner; the fake-provider MeetingManager "
                "is the pre-committed fallback (no silent fallbacks)"
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
    "FIT_CORPUS_FILENAME",
    "SURROGATE_VERDICT_FILENAME",
    "SurrogateFitCorpus",
    "SurrogateInstallRole",
    "SurrogateMeetingRunner",
    "SurrogateStalenessExceededError",
    "SurrogateUseCounter",
    "fit_corpus_fingerprint",
    "load_fit_corpus_record",
    "load_surrogate_runner_factory",
    "load_surrogate_verdict",
    "write_surrogate_verdict_artifact",
]
