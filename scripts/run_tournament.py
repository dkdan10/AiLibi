"""CLI: headless tournament harness (DESIGN.md §11.3).

Runs many headless games and emits a single typed
:class:`~eval.meeting_quality.TournamentEvalReport` as JSON — the
:class:`~eval.report_schema.TournamentReport` plus all four Phase 5 metrics
(vote correctness, accusation calibration, alibi-fabrication rate, cost
dashboard). The single-game loop comes from
:class:`orchestrator.game.HeadlessGame` (Task 2.8); this script only wires CLI
flags, builds the seed range, calls
:func:`eval.balance_eval.run_tournament_eval` +
:func:`eval.meeting_quality.build_tournament_eval_report`, writes the JSON, and
prints a short summary.

The JSON report supersedes the old ``BalanceReport`` text summary as the
tournament artifact (Task 5.6 / Task 5.1 ``## Decisions``); the crew / impostor
/ tick-budget buckets remain derivable from it and are still printed for the
operator.

The learned champion is OPT-IN via ``--agent-factory learned-champion`` beside
the untouched ``fsm-default`` scripted-FSM default
(audits/audit-phase-15-pause.md decision 2, branch A): the committed
``replays/samples/`` corpus stays byte-identical because an unflagged run
threads neither factory nor stamp, exactly as before Task 15.21 — and an
explicit ``--tactical-policy-stamp`` must match the SELECTED factory's stamp
field-for-field in either direction, so no recording can carry the other
policy's label (the owner-ratified PR-#248 amendment to the 15.21 contract;
it retires the Task-15.9 champion-JSON surface on the FSM path, which the
auto-stamp obsoleted). A
``learned-champion`` run AUTO-STAMPS each recording with the champion's
:class:`~orchestrator.replay.TacticalPolicyStamp`, so the Task-15.18
finalist-eval proof (``stamp.weights_sha256`` equals the committed sidecar
digest) can never be forgotten on a learned run. Flipping the scripted default
to the champion is deliberately NOT this task's call — the Q3 corollary recorded
with decision 2 re-evaluates it at phase close / Phase 17, behind the
Task-15.19-hardened referee plus a corpus-scale companion record.

The multi-finalist recorder (Task 17.14; audits/audit-phase-15-pause.md:145-184)
productizes the pause's uncommitted per-finalist driver as a thin loader
parameter beside the committed champion: ``--candidate-artifact
training/artifacts/impostor/<entrant>`` records with an ARBITRARY committed
candidate artifact loaded by path — the genome is sha-verified against the
artifact's ``weights.json.sha256`` sidecar (a mismatch fails loud BEFORE any
spend, reusing ``training.bakeoff.harness.load_candidate_weights`` rather than a
second loader), rebuilt through the committed policy builder its
``encoder_version`` selects (``utility_es.build_utility_scorer_policy`` for the
``impostor-option-features-v1`` family, ``policy_es.build_masked_mlp_policy`` for
the ``v2`` masked-MLP family), wrapped by
``training.bakeoff.harness.build_candidate_factory``, and AUTO-STAMPED from the
artifact's OWN ``stamp.json`` — never the committed champion's constants (the
17.14 conflation guard: one candidate per invocation, the stamp names it, and
``stamp.weights_sha256`` must equal the sidecar digest). The committed champion
surface (``agents/tactical/learned/``) is never touched. This is the recording
seam for the 50-seed real-LLM finalist eval; measurement is assembled by the
committed scoring CLIs (``scripts/validity_gate.py``, ``scripts/measure_baseline.py``)
and the stamp read back from every recording via
``orchestrator.replay.read_tactical_policy_stamp`` (see
``training/reports/report-finalist-eval.md``).

The opt-in learned CREW surface is a THIRD ``--agent-factory`` arm beside the
scripted default (Task 18.7; audits/audit-phase-18-planning.md §4 #7) — the
missing half of co-evolution, the 15.20/15.21 pattern on the crew side.
``--agent-factory learned-crew`` wraps every crewmate with the committed
``crew-owned-tasks-es`` scorer (``agents.tactical.learned`` again) while
impostors stay the scripted FSM, and AUTO-STAMPS each recording with the crew
:class:`~orchestrator.replay.CrewTacticalPolicyStamp` beside an ABSENT impostor
tactical stamp — so a crew recording carries its own provenance in a DISTINCT
schema slot and can never be re-read as an impostor-champion game. Adoption
stays GATED exactly as the impostor champion's: this ships a SURFACE, not a
champion, and the scripted crew default (``agents.tactical.crewmate_policy``) is
untouched — an unflagged run threads neither factory nor crew stamp,
byte-identical to before Task 18.7. The 18.7 conflation guard is enforced in the
arm itself: the crew stamp's ``policy_id`` / ``weights_sha256`` are asserted
disjoint from the impostor champion's, so the two learned surfaces can never
share one recording's label.

The dual-role co-evolution recorder is the ``--crew-artifact`` arm (Task 18.19;
audits/audit-phase-18-planning.md §4 #7) — the crew analog of
``--candidate-artifact`` and the seam that stamps BOTH identities on one game.
``--crew-artifact training/artifacts/crew/<entrant>`` records with an ARBITRARY
committed CREW artifact loaded by path: the genome is sha-verified against the
artifact's ``weights.json.sha256`` sidecar (a mismatch fails loud BEFORE any
spend, REUSING ``training.bakeoff.harness.load_candidate_weights`` — the SAME
shared loader the impostor arm uses, since crew artifacts share the
``weights.json`` + sidecar layout — rather than a second loader), rebuilt through
``training.crew.scorer.build_crew_scorer`` (with an ``OwnedTaskOptionBasis`` for
the ``crew-option-features-v2`` 27-weight owned-task family, bare for the
``crew-option-features-v1`` 22-weight family) selected by its ``stamp.json``
``encoder_version``, wrapped by ``training.coevo.factory.build_coevo_factory``
(the dual-role ROLE BRANCH: crew agents score against the loaded crew policy,
impostors stay the scripted FSM unless a ``--candidate-artifact`` supplies the
impostor side too), and AUTO-STAMPED from the artifact's OWN five-field
``stamp.json`` into a :class:`~orchestrator.replay.CrewTacticalPolicyStamp`.
Combined with ``--candidate-artifact`` it produces a DUAL-stamp co-evo recording
carrying an impostor :class:`~orchestrator.replay.TacticalPolicyStamp` AND a crew
stamp in DISTINCT schema slots; a CROSS-STAMP conflation guard rejects a
recording whose two identities share a ``policy_id`` or ``weights_sha256`` (the
two movers on one recording must be distinct). ``--crew-artifact`` is mutually
exclusive with the two single-side ``--agent-factory`` arms
(``learned-champion`` / ``learned-crew``), and an impostor artifact handed to
``--crew-artifact`` — or a crew artifact handed to ``--candidate-artifact`` —
fails loud on the encoder NAMESPACE (``crew-`` vs impostor) BEFORE any game runs.
NOTE: the committed ``training/artifacts/crew`` dirs do NOT yet carry a
``stamp.json`` (the 18.25 crew campaign's recording legs (the first dual-stamped crew recordings) writes them), so the arm fails loud on
them until one is added; the tests build fixture dirs. An unflagged run threads
neither factory nor stamp, byte-identical to before Task 18.19.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Final

# Allow `uv run python scripts/run_tournament.py ...` to find top-level packages.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from agents.tactical.crewmate_policy import CrewmatePolicy  # noqa: E402
from agents.tactical.impostor_policy import ImpostorPolicy  # noqa: E402
from agents.tactical.learned.factory import (  # noqa: E402
    LearnedAgentFactory,
    LearnedCrewAgentFactory,
    build_learned_agent_factory,
    build_learned_crew_factory,
)
from eval.balance_eval import run_tournament_eval  # noqa: E402
from eval.meeting_quality import (  # noqa: E402
    TournamentEvalReport,
    build_tournament_eval_report,
)
from observation.packet import PlayerId, Role  # noqa: E402
from orchestrator.game import (  # noqa: E402
    AgentFactory,
    DEFAULT_MAX_TICKS,
    DEFAULT_NUM_IMPOSTORS,
    DEFAULT_NUM_PLAYERS,
    DEFAULT_TASKS_PER_CREWMATE,
    ROSTER_PRESETS,
    TacticalAgent,
)
from orchestrator.replay import (  # noqa: E402
    FSM_DEFAULT_POLICY_ID,
    CrewTacticalPolicyStamp,
    TacticalPolicyStamp,
    fsm_default_tactical_policy_stamp,
)

if TYPE_CHECKING:
    # Type-only imports for the artifact-arm resolvers' policy annotations. Kept
    # under TYPE_CHECKING so the default ``fsm-default`` path's runtime module
    # graph stays byte-identical (the two policy Protocols live in training/ and
    # are imported lazily inside the arm resolvers, mirroring
    # ``_resolve_candidate_artifact``); mypy resolves the names at check time.
    from training.bakeoff.harness import BakeoffPolicy
    from training.crew.scorer import CrewTrackPolicy

_DEFAULT_REPORT_FILENAME = "tournament-eval-report.json"

# ``--agent-factory`` choices (Task 15.21; audits/audit-phase-15-pause.md
# decision 2, branch A): the scripted FSM stays the default; the learned
# champion is opt-in. Reusing ``FSM_DEFAULT_POLICY_ID`` as the default value
# keeps an unflagged run byte-identical to the pre-15.21 CLI.
LEARNED_CHAMPION_FACTORY_ID: Final[str] = "learned-champion"
# The opt-in crew surface arm (Task 18.7; audits/audit-phase-18-planning.md §4
# #7): a third choice beside the untouched scripted default and the impostor
# champion. Adoption stays gated — this selects a SURFACE, not a champion.
LEARNED_CREW_FACTORY_ID: Final[str] = "learned-crew"
_AGENT_FACTORY_CHOICES: Final[tuple[str, ...]] = (
    FSM_DEFAULT_POLICY_ID,
    LEARNED_CHAMPION_FACTORY_ID,
    LEARNED_CREW_FACTORY_ID,
)


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a headless AiLibi tournament and emit a JSON eval report.",
    )
    parser.add_argument(
        "--num-games",
        type=int,
        default=100,
        help="number of games to run (default: 100)",
    )
    parser.add_argument(
        "--start-seed",
        type=int,
        default=0,
        help="first seed in the tournament; seeds are start..start+num_games-1",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="directory for per-seed replay and audit logs",
    )
    parser.add_argument(
        "--report-output",
        type=Path,
        default=None,
        help=(
            "path for the JSON TournamentEvalReport "
            f"(default: <output-dir>/{_DEFAULT_REPORT_FILENAME})"
        ),
    )
    # The roster flags default to None (not their constants) so main() can tell
    # an explicitly-passed value from an omitted one and reject combining any of
    # them with --roster-preset. Omitted flags resolve to the shared defaults in
    # _resolve_roster.
    parser.add_argument(
        "--num-players",
        type=int,
        default=None,
        help=f"total players per game (default: {DEFAULT_NUM_PLAYERS})",
    )
    parser.add_argument(
        "--num-impostors",
        type=int,
        default=None,
        help=f"impostors per game (default: {DEFAULT_NUM_IMPOSTORS})",
    )
    parser.add_argument(
        "--tasks-per-crewmate",
        type=int,
        default=None,
        help=(
            "distinct map tasks assigned to each crewmate "
            f"(default: {DEFAULT_TASKS_PER_CREWMATE}). Raising this lengthens "
            "games so bodies can outlive the win condition (Phase 7 W0.1)."
        ),
    )
    parser.add_argument(
        "--roster-preset",
        choices=sorted(ROSTER_PRESETS),
        default=None,
        help=(
            "named roster config supplying num-players, num-impostors, and "
            "tasks-per-crewmate together; mutually exclusive with passing any of "
            "those flags explicitly. Choices: " + ", ".join(sorted(ROSTER_PRESETS))
        ),
    )
    parser.add_argument(
        "--max-ticks",
        type=int,
        default=DEFAULT_MAX_TICKS,
        help=f"per-game tick budget (default: {DEFAULT_MAX_TICKS})",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "overwrite existing per-seed replay files in --output-dir. "
            "Without it, re-using an --output-dir whose replay files already "
            "exist raises ReplayLog.AlreadyExistsError and exits non-zero, "
            "guarding against the silent doubled-file corruption that broke "
            "replay reads in Phase 4 (DESIGN.md §11.4)."
        ),
    )
    parser.add_argument(
        "--tactical-policy-stamp",
        default=None,
        metavar="fsm-default|PATH.json",
        help=(
            "stamp a tactical-policy provenance block onto every game's "
            "game_over record (Task 15.9). Accepts the literal 'fsm-default' for "
            "the canonical scripted-FSM stamp, or a path to a JSON file with the "
            "five TacticalPolicyStamp fields (policy_id, method, encoder_version, "
            "weights_sha256, anchor_policy). Since Task 15.21 the stamp must "
            "match the factory selected by --agent-factory field-for-field (the "
            "champion stamp is auto-wired by 'learned-champion', so an explicit "
            "stamp is only ever a re-statement); a contradiction exits non-zero. "
            "Omitted records the absent = FSM-default stamp, byte-identical to "
            "today."
        ),
    )
    parser.add_argument(
        "--agent-factory",
        choices=_AGENT_FACTORY_CHOICES,
        default=FSM_DEFAULT_POLICY_ID,
        help=(
            "tactical agent factory for every game (Task 15.21; audit decision 2, "
            "branch A). 'fsm-default' (the default) keeps the scripted-FSM factory, "
            "byte-identical to omitting the flag; 'learned-champion' wraps every "
            "impostor with the committed utility-es champion scorer "
            "(agents.tactical.learned) and auto-stamps each recording with the "
            "champion's TacticalPolicyStamp — combining it with a contradicting "
            "--tactical-policy-stamp is rejected loudly. 'learned-crew' (opt-in, "
            "Task 18.7) wraps every crewmate with the committed crew-owned-tasks-es "
            "scorer while impostors stay the scripted FSM, and auto-stamps each "
            "recording with the crew stamp (CrewTacticalPolicyStamp) beside an "
            "absent impostor stamp."
        ),
    )
    parser.add_argument(
        "--candidate-artifact",
        type=Path,
        default=None,
        metavar="ARTIFACT_DIR",
        help=(
            "record with an arbitrary committed impostor candidate artifact "
            "loaded by path (Task 17.14, the multi-finalist recorder). "
            "ARTIFACT_DIR is a training/artifacts/impostor/<entrant> dir carrying "
            "weights.json + its .sha256 sidecar + stamp.json + config.json. The "
            "genome is sha-verified against the sidecar (a mismatch fails loud "
            "BEFORE any spend), rebuilt through the committed policy builder its "
            "encoder_version selects, wrapped by the bake-off candidate factory, "
            "and AUTO-STAMPED from the artifact's own stamp.json — never the "
            "committed champion's constants. Mutually exclusive with "
            "--agent-factory learned-champion; an explicit --tactical-policy-stamp "
            "must match the artifact stamp field-for-field."
        ),
    )
    parser.add_argument(
        "--crew-artifact",
        type=Path,
        default=None,
        metavar="ARTIFACT_DIR",
        help=(
            "record with an arbitrary committed CREW artifact loaded by path "
            "(Task 18.19, the dual-role co-evo recorder's crew arm, mirroring "
            "--candidate-artifact). ARTIFACT_DIR is a training/artifacts/crew/"
            "<entrant> dir carrying weights.json + its .sha256 sidecar + a "
            "five-field stamp.json (CrewTacticalPolicyStamp). The genome is "
            "sha-verified against the sidecar (a mismatch fails loud BEFORE any "
            "spend), rebuilt through the committed crew builder its encoder_version "
            "selects (build_crew_scorer, with an OwnedTaskOptionBasis for the "
            "crew-option-features-v2 family), wrapped by "
            "training.coevo.factory.build_coevo_factory, and AUTO-STAMPED from the "
            "artifact's own stamp.json. Combinable with --candidate-artifact for a "
            "DUAL-stamp co-evo recording (a cross-stamp guard rejects colliding "
            "identities); mutually exclusive with --agent-factory learned-champion "
            "/ learned-crew. NOTE: the committed crew dirs do not yet carry "
            "stamp.json, so the arm fails loud on them until one is added."
        ),
    )
    return parser.parse_args(argv)


def _resolve_tactical_policy_stamp(value: str | None) -> TacticalPolicyStamp | None:
    """Parse ``--tactical-policy-stamp`` into a stamp (Task 15.9).

    ``None`` (the flag omitted) yields ``None`` — the absent = scripted-FSM
    default, byte-identical to the pre-15.9 recorder. The literal
    ``fsm-default`` yields :func:`fsm_default_tactical_policy_stamp`, so the
    Task-15.12 corpus wrapper can stamp the FSM default explicitly. Any other
    value is a path to a JSON file carrying exactly the five
    :class:`TacticalPolicyStamp` fields (a Wave-2 champion stamp); a missing file,
    unreadable JSON, or a schema mismatch is fail-loud
    (``SystemExit``) rather than silently recording an FSM default (AGENTS.md "no
    silent fallbacks").
    """

    if value is None:
        return None
    if value == FSM_DEFAULT_POLICY_ID:
        return fsm_default_tactical_policy_stamp()
    path = Path(value)
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SystemExit(
            f"--tactical-policy-stamp: cannot read stamp file {path!r}: {exc}. "
            f"Pass the literal {FSM_DEFAULT_POLICY_ID!r} or a readable JSON file."
        ) from exc
    try:
        return TacticalPolicyStamp.model_validate_json(raw)
    except ValueError as exc:
        raise SystemExit(
            f"--tactical-policy-stamp: {path} is not a valid TacticalPolicyStamp "
            f"(need the five string fields policy_id/method/encoder_version/"
            f"weights_sha256/anchor_policy): {exc}"
        ) from exc


def _build_learned_champion_factory() -> LearnedAgentFactory:
    """Build the Task-15.20 champion factory around the production inner agent.

    The injected inner constructor is exactly the per-player construction
    :func:`orchestrator.game.build_default_agent_factory` performs — the
    orchestrator-owned :class:`~orchestrator.game.TacticalAgent` wrapping the
    role-appropriate scripted FSM policy. It is injected rather than imported by
    ``agents/tactical/learned/`` because that package may not import the
    orchestrator (the ``agents → orchestrator → engine`` chain would breach the
    observation firewall) while this CLI may (Task 15.21); this closes the seam
    Task 15.20 deliberately left injected.
    """

    def inner(agent_id: PlayerId, role: Role) -> TacticalAgent:
        policy: CrewmatePolicy | ImpostorPolicy
        if role == "IMPOSTOR":
            policy = ImpostorPolicy(agent_id=agent_id)
        else:
            policy = CrewmatePolicy(agent_id=agent_id)
        return TacticalAgent(agent_id=agent_id, policy=policy, role=role)

    return build_learned_agent_factory(inner)


def _build_learned_crew_factory() -> LearnedCrewAgentFactory:
    """Build the Task-18.7 crew factory around the production inner agent.

    The injected inner constructor is exactly the per-player construction
    :func:`orchestrator.game.build_default_agent_factory` performs — the
    orchestrator-owned :class:`~orchestrator.game.TacticalAgent` wrapping the
    role-appropriate scripted FSM policy — the same one-liner
    :func:`_build_learned_champion_factory` injects. It is injected rather than
    imported by ``agents/tactical/learned/`` because that package may not import
    the orchestrator (``agents → orchestrator → engine`` breaches the observation
    firewall) while this CLI may.

    The crew factory additionally needs two SCALARS off the engine map that the
    submission-mask re-validation and emergency bookkeeping read but the
    observation surface does not expose — the sabotage kinds and the per-player
    emergency-use budget. ``engine.world.load_canonical_map`` is imported INSIDE
    this function (the :func:`_resolve_candidate_artifact` lazy-import idiom) so
    the default ``fsm-default`` path's module graph stays byte-identical, and the
    two scalars are read off the real map (``game_map.sabotages`` /
    ``game_map.emergency.uses_per_player``) and INJECTED — closing the seam
    Task 18.7 deliberately leaves injected because ``agents/`` may not read the
    engine map.
    """

    def inner(agent_id: PlayerId, role: Role) -> TacticalAgent:
        policy: CrewmatePolicy | ImpostorPolicy
        if role == "IMPOSTOR":
            policy = ImpostorPolicy(agent_id=agent_id)
        else:
            policy = CrewmatePolicy(agent_id=agent_id)
        return TacticalAgent(agent_id=agent_id, policy=policy, role=role)

    from engine.world import load_canonical_map

    game_map = load_canonical_map()
    return build_learned_crew_factory(
        inner,
        sabotage_kinds=tuple(sorted(game_map.sabotages)),
        emergency_uses_per_player=game_map.emergency.uses_per_player,
    )


def _resolve_learned_crew_factory() -> tuple[AgentFactory, CrewTacticalPolicyStamp]:
    """Resolve ``--agent-factory learned-crew`` into a factory + crew auto-stamp (18.7).

    Builds the opt-in Task-18.7 crew factory (its committed
    ``crew-owned-tasks-es`` weights sha-verified on load, fail loud) and
    constructs the real :class:`~orchestrator.replay.CrewTacticalPolicyStamp` here
    in ``scripts/`` from the factory's five plain-string stamp fields — the
    factory itself stays engine-free per Task 18.7 — so the crew auto-stamp always
    carries the digest of the crew artifact actually loaded, never a hard-coded
    sha.

    Then enforces the 18.7 CONFLATION GUARD (the task's integration-risk clause):
    a crew recording must NEVER wear the impostor champion's stamp, so the crew
    stamp's ``policy_id`` / ``weights_sha256`` are asserted DISJOINT from the
    committed impostor champion's namespaces (``CHAMPION_POLICY_ID`` /
    :func:`agents.tactical.learned.weights.committed_weights_sha256`). A collision
    on either — which would let the two learned surfaces share one recording's
    label — is fail-loud (``SystemExit``), never a silent record.
    """

    factory = _build_learned_crew_factory()
    fields = factory.stamp
    stamp = CrewTacticalPolicyStamp(
        policy_id=fields.policy_id,
        method=fields.method,
        encoder_version=fields.encoder_version,
        weights_sha256=fields.weights_sha256,
        anchor_policy=fields.anchor_policy,
    )

    from agents.tactical.learned.factory import CHAMPION_POLICY_ID
    from agents.tactical.learned.weights import committed_weights_sha256

    if (
        stamp.policy_id == CHAMPION_POLICY_ID
        or stamp.weights_sha256 == committed_weights_sha256()
    ):
        raise SystemExit(
            "the learned-crew recorder produced a crew stamp that collides with "
            f"the impostor champion's (policy_id={stamp.policy_id!r}, "
            f"weights_sha256={stamp.weights_sha256!r}); a crew recording must "
            "never wear the impostor champion's stamp — the 18.7 conflation guard "
            "requires distinct policy_id/weights_sha256 namespaces across the crew "
            "and impostor stamps."
        )
    return factory, stamp


_CANDIDATE_STAMP_FILENAME: Final[str] = "stamp.json"
_CANDIDATE_CONFIG_FILENAME: Final[str] = "config.json"
_CANDIDATE_SIDECAR_FILENAME: Final[str] = "weights.json.sha256"


def _read_candidate_stamp(artifact_dir: Path) -> TacticalPolicyStamp:
    """Load a candidate's five-field 15.9 stamp from its ``stamp.json`` (Task 17.14).

    The stamp fields come from the candidate's OWN artifact — never the committed
    champion's constants (the implementation-hint contract). A missing file,
    unreadable JSON, or a schema mismatch (including a blank / pipe-bearing field
    the :class:`TacticalPolicyStamp` validator rejects) is fail-loud
    (``SystemExit``) rather than a silent fallback (AGENTS.md "no silent
    fallbacks").
    """

    stamp_path = artifact_dir / _CANDIDATE_STAMP_FILENAME
    try:
        raw = stamp_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SystemExit(
            f"--candidate-artifact: cannot read {str(stamp_path)!r}: {exc}. The "
            "artifact dir must carry a five-field stamp.json (policy_id, method, "
            "encoder_version, weights_sha256, anchor_policy)."
        ) from exc
    try:
        return TacticalPolicyStamp.model_validate_json(raw)
    except ValueError as exc:
        raise SystemExit(
            f"--candidate-artifact: {stamp_path} is not a valid TacticalPolicyStamp "
            f"(need the five string fields policy_id/method/encoder_version/"
            f"weights_sha256/anchor_policy): {exc}"
        ) from exc


def _read_candidate_hidden(artifact_dir: Path) -> int:
    """Read the masked-MLP ``hidden`` width from a candidate's ``config.json``.

    The masked-MLP policy families (``v2`` — policy-es / bc-dagger / map-elites —
    and the Task-18.22 ``v3``) rebuild through
    :func:`training.bakeoff.policy_es.build_masked_mlp_policy`, whose ``hidden``
    width is a committed artifact parameter, not a hard-coded champion constant.
    A missing / non-integer ``hidden`` is fail-loud.
    """

    config_path = artifact_dir / _CANDIDATE_CONFIG_FILENAME
    try:
        raw = config_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SystemExit(
            f"--candidate-artifact: cannot read {str(config_path)!r}: {exc}. The "
            "masked-MLP policy family needs an integer 'hidden' in config.json."
        ) from exc
    try:
        config = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(
            f"--candidate-artifact: {config_path} is not valid JSON: {exc}"
        ) from exc
    hidden = config.get("hidden") if isinstance(config, dict) else None
    if not isinstance(hidden, int) or isinstance(hidden, bool):
        raise SystemExit(
            f"--candidate-artifact: {config_path} must carry an integer 'hidden' "
            f"for the masked-MLP policy family (got {hidden!r})."
        )
    return hidden


def _load_candidate_policy(
    artifact_dir: Path,
) -> tuple[BakeoffPolicy, TacticalPolicyStamp]:
    """Load a finalist artifact by path into an inference policy + stamp (Task 17.14).

    The policy-building core of :func:`_resolve_candidate_artifact`, extracted
    (Task 18.19) so the dual-role co-evo arm (:func:`_resolve_crew_artifact_arm`)
    can reuse the IMPOSTOR side without the single-side
    :func:`training.bakeoff.harness.build_candidate_factory` wrap. REUSES the
    committed loaders rather than writing a second one (the 17.14 hint): the genome
    is read + sha-verified against the artifact's sidecar via
    :func:`training.bakeoff.harness.load_candidate_weights` (fail loud on drift,
    BEFORE any spend), the inference policy is rebuilt through the committed builder
    its ``encoder_version`` selects, and the stamp comes from the candidate's OWN
    ``stamp.json`` — its ``weights_sha256`` MUST equal the sidecar digest (the 17.14
    conflation guard: one candidate per invocation, the stamp names it, no ambient
    state leaks between runs). A CREW artifact (``encoder_version`` in the
    ``crew-`` namespace) handed to the impostor slot fails loud HERE (the 18.19
    vice-versa guard) — the impostor slot rebuilds through the bake-off impostor
    builders, never the crew scorer; the operator is pointed at ``--crew-artifact``.
    Imports live inside this function so the default ``fsm-default`` path's module
    graph stays byte-identical.
    """

    from engine.world import load_canonical_map
    from training.bakeoff import policy_es, utility_es
    from training.bakeoff.harness import load_candidate_weights
    from training.coevo.factory import CREW_ENCODER_NAMESPACE_PREFIX

    if not artifact_dir.is_dir():
        raise SystemExit(
            f"--candidate-artifact: {str(artifact_dir)!r} is not a directory; pass "
            "a committed impostor artifact dir (e.g. "
            "training/artifacts/impostor/utility-es)."
        )

    stamp = _read_candidate_stamp(artifact_dir)

    # Vice-versa conflation guard (Task 18.19): a crew artifact (its encoder tag in
    # the ``crew-`` namespace) in the impostor slot fails loud BEFORE any spend —
    # the impostor slot rebuilds through the bake-off impostor builders, not the
    # crew scorer. CREW_ENCODER_NAMESPACE_PREFIX is training.coevo.factory's single
    # source of truth for the crew-tag convention (imported here, not re-literaled).
    if stamp.encoder_version.startswith(CREW_ENCODER_NAMESPACE_PREFIX):
        raise SystemExit(
            f"--candidate-artifact: {artifact_dir}'s stamp names a CREW policy "
            f"(encoder_version={stamp.encoder_version!r}, in the "
            f"{CREW_ENCODER_NAMESPACE_PREFIX!r} namespace); the impostor slot "
            "rebuilds through the bake-off impostor builders, not the crew scorer. "
            "Pass it as --crew-artifact instead (the 18.19 conflation guard)."
        )

    # sha verification against the artifact sidecar — fail loud BEFORE any spend.
    try:
        weights = load_candidate_weights(artifact_dir)
    except (OSError, ValueError) as exc:
        raise SystemExit(
            f"--candidate-artifact: weights load/verify failed for "
            f"{artifact_dir}: {exc}"
        ) from exc

    sidecar_digest = (
        (artifact_dir / _CANDIDATE_SIDECAR_FILENAME)
        .read_text(encoding="utf-8")
        .split()[0]
    )
    if stamp.weights_sha256 != sidecar_digest:
        raise SystemExit(
            f"--candidate-artifact: stamp.json weights_sha256 "
            f"{stamp.weights_sha256!r} != sidecar digest {sidecar_digest!r} for "
            f"{artifact_dir}; the stamp must name THIS artifact (the 17.14 "
            "conflation guard — two learned movers must never share one recording)."
        )

    # Dispatch the reload seam on the stamp's encoder_version so an arbitrary
    # finalist rebuilds through the SAME committed builder the bake-off froze it
    # with — never a hard-coded champion assumption.
    game_map = load_canonical_map()
    policy: BakeoffPolicy
    if stamp.encoder_version == utility_es.ENCODER_VERSION:
        policy = utility_es.build_utility_scorer_policy(weights, game_map=game_map)
    else:
        hidden = _read_candidate_hidden(artifact_dir)
        try:
            # The encoder_version seam (Task 18.22): the stamp selects the v2 or
            # v3 masked-MLP family, so a v3 artifact rebuilds with its own wider
            # encoder + per-target head instead of failing the v2 genome-length
            # check; an unknown stamp version raises here (no silent fallback).
            policy = policy_es.build_masked_mlp_policy(
                weights,
                game_map=game_map,
                hidden=hidden,
                encoder_version=stamp.encoder_version,
            )
        except ValueError as exc:
            raise SystemExit(
                f"--candidate-artifact: could not rebuild the masked-MLP policy "
                f"for {artifact_dir}: {exc}"
            ) from exc
    if policy.encoder_version != stamp.encoder_version:
        raise SystemExit(
            f"--candidate-artifact: rebuilt policy encoder "
            f"{policy.encoder_version!r} != stamp encoder_version "
            f"{stamp.encoder_version!r} for {artifact_dir} (unknown encoder / "
            "artifact-stamp mismatch)."
        )
    return policy, stamp


def _resolve_candidate_artifact(
    artifact_dir: Path,
) -> tuple[AgentFactory, TacticalPolicyStamp]:
    """Load an arbitrary finalist artifact by path into a factory + stamp (Task 17.14).

    Productizes the pause's uncommitted per-finalist driver
    (audits/audit-phase-15-pause.md:145-184): the policy + stamp come from the
    extracted :func:`_load_candidate_policy` (Task 18.19), then the factory is
    :func:`training.bakeoff.harness.build_candidate_factory` — the exact reload seam
    the bake-off froze the artifact with. Behavior is byte-identical to the Task
    17.14 single-side ``--candidate-artifact`` recorder. Imports live inside this
    function so the default ``fsm-default`` path's module graph stays byte-identical.
    """

    from engine.world import load_canonical_map
    from training.bakeoff.harness import build_candidate_factory

    policy, stamp = _load_candidate_policy(artifact_dir)
    factory = build_candidate_factory(policy, game_map=load_canonical_map())
    return factory, stamp


def _resolve_agent_factory(
    choice: str,
    *,
    candidate_artifact: Path | None = None,
) -> tuple[AgentFactory | None, TacticalPolicyStamp | None]:
    """Resolve ``--agent-factory`` into a factory + auto-stamp pair (Task 15.21).

    ``fsm-default`` resolves to ``(None, None)`` — :func:`main` then passes NO
    ``agent_factory`` kwarg to :func:`run_tournament_eval` (whose omitted-kwarg
    default already is :func:`orchestrator.game.build_default_agent_factory`),
    keeping the default path byte-identical to the pre-15.21 CLI (the decision-2
    posture, audit branch A). ``learned-champion`` builds the opt-in Task-15.20
    factory (its committed weights sha-verified on load, fail loud) and
    constructs the real :class:`~orchestrator.replay.TacticalPolicyStamp` here in
    ``scripts/`` from the factory's five plain-string stamp fields — the factory
    itself stays engine-free per Task 15.20 — so the auto-stamp always carries
    the digest of the artifact actually loaded, never a hard-coded sha.

    ``candidate_artifact`` (Task 17.14, the multi-finalist recorder) takes
    precedence when set: it loads an arbitrary committed candidate artifact by
    path (:func:`_resolve_candidate_artifact`) and auto-stamps from the artifact's
    own ``stamp.json``. It is mutually exclusive with a non-default
    ``--agent-factory`` — the artifact, not the flag, selects the impostor policy
    — so combining the two is rejected loudly.
    """

    if candidate_artifact is not None:
        if choice != FSM_DEFAULT_POLICY_ID:
            raise SystemExit(
                f"--candidate-artifact is mutually exclusive with --agent-factory "
                f"{choice!r}: the artifact selects the impostor policy and "
                "auto-stamps from its own stamp.json. Drop --agent-factory (it "
                f"defaults to {FSM_DEFAULT_POLICY_ID!r})."
            )
        return _resolve_candidate_artifact(candidate_artifact)
    if choice == FSM_DEFAULT_POLICY_ID:
        return None, None
    factory = _build_learned_champion_factory()
    fields = factory.stamp
    stamp = TacticalPolicyStamp(
        policy_id=fields.policy_id,
        method=fields.method,
        encoder_version=fields.encoder_version,
        weights_sha256=fields.weights_sha256,
        anchor_policy=fields.anchor_policy,
    )
    return factory, stamp


def _read_crew_artifact_stamp(artifact_dir: Path) -> CrewTacticalPolicyStamp:
    """Load a crew artifact's five-field crew stamp from its ``stamp.json`` (Task 18.19).

    The crew twin of :func:`_read_candidate_stamp`: the stamp fields come from the
    crew artifact's OWN ``stamp.json`` (a
    :class:`~orchestrator.replay.CrewTacticalPolicyStamp`), never the committed crew
    surface's constants. A missing file, unreadable JSON, or a schema mismatch
    (including a blank / pipe-bearing field the validator rejects) is fail-loud
    (``SystemExit``) rather than a silent fallback (AGENTS.md "no silent
    fallbacks"). NOTE: the committed ``training/artifacts/crew`` dirs do NOT yet
    carry a ``stamp.json`` (the 18.25 crew campaign's recording legs (the first dual-stamped crew recordings) writes them), so the arm
    fails loud on them until one is added; the tests build fixture dirs.
    """

    stamp_path = artifact_dir / _CANDIDATE_STAMP_FILENAME
    try:
        raw = stamp_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SystemExit(
            f"--crew-artifact: cannot read {str(stamp_path)!r}: {exc}. The crew "
            "artifact dir must carry a five-field stamp.json (policy_id, method, "
            "encoder_version, weights_sha256, anchor_policy)."
        ) from exc
    try:
        return CrewTacticalPolicyStamp.model_validate_json(raw)
    except ValueError as exc:
        raise SystemExit(
            f"--crew-artifact: {stamp_path} is not a valid CrewTacticalPolicyStamp "
            f"(need the five string fields policy_id/method/encoder_version/"
            f"weights_sha256/anchor_policy): {exc}"
        ) from exc


def _load_crew_artifact_policy(
    artifact_dir: Path,
) -> tuple[CrewTrackPolicy, CrewTacticalPolicyStamp]:
    """Load a crew artifact by path into a crew policy + crew stamp (Task 18.19).

    The crew twin of :func:`_load_candidate_policy`, mirroring its steps
    field-for-field: verify the dir; read the crew ``stamp.json`` via
    :func:`_read_crew_artifact_stamp`; sha-verify the genome against the sidecar via
    the SAME shared :func:`training.bakeoff.harness.load_candidate_weights` (crew
    artifacts share the ``weights.json`` + sidecar layout) — fail loud on drift,
    BEFORE any spend; assert the stamp's ``weights_sha256`` equals the sidecar
    digest (the 18.19 conflation guard: the stamp must name THIS artifact); then
    DISPATCH on the stamp's ``encoder_version`` through the committed crew builder
    :func:`training.crew.scorer.build_crew_scorer` — the ``crew-option-features-v1``
    22-weight menu (no basis) or the ``crew-option-features-v2`` 27-weight
    owned-task menu (:class:`~training.crew.options.OwnedTaskOptionBasis`). ANY
    other ``encoder_version`` names no rebuildable crew family and fails loud — an
    IMPOSTOR artifact (``impostor-option-features-*``) in the crew slot fails HERE,
    before any game runs. A genome-length drift raises ``ValueError`` from the
    builder, re-raised as ``SystemExit``; a rebuilt policy whose ``encoder_version``
    disagrees with the stamp is a fail-loud artifact-stamp mismatch (mirrors 17.14).
    Imports live inside this function so the default path's module graph stays
    byte-identical.
    """

    from engine.world import load_canonical_map
    from training.bakeoff.harness import load_candidate_weights
    from training.crew.options import OwnedTaskOptionBasis
    from training.crew.scorer import (
        ENCODER_VERSION as CREW_V1_ENCODER_VERSION,
    )
    from training.crew.scorer import (
        OWNED_TASK_ENCODER_VERSION,
        build_crew_scorer,
    )

    if not artifact_dir.is_dir():
        raise SystemExit(
            f"--crew-artifact: {str(artifact_dir)!r} is not a directory; pass a "
            "committed crew artifact dir (e.g. "
            "training/artifacts/crew/crew-owned-tasks-es) carrying weights.json + "
            "its .sha256 sidecar + a five-field stamp.json."
        )

    stamp = _read_crew_artifact_stamp(artifact_dir)

    # sha verification against the artifact sidecar — fail loud BEFORE any spend.
    try:
        weights = load_candidate_weights(artifact_dir)
    except (OSError, ValueError) as exc:
        raise SystemExit(
            f"--crew-artifact: weights load/verify failed for {artifact_dir}: {exc}"
        ) from exc

    sidecar_digest = (
        (artifact_dir / _CANDIDATE_SIDECAR_FILENAME)
        .read_text(encoding="utf-8")
        .split()[0]
    )
    if stamp.weights_sha256 != sidecar_digest:
        raise SystemExit(
            f"--crew-artifact: stamp.json weights_sha256 {stamp.weights_sha256!r} "
            f"!= sidecar digest {sidecar_digest!r} for {artifact_dir}; the stamp "
            "must name THIS artifact (the 18.19 conflation guard — a crew recording "
            "must carry the provenance of the bytes it produced)."
        )

    # Dispatch the crew reload seam on the stamp's encoder_version. An impostor
    # artifact (impostor-option-features-*) in the crew slot names no rebuildable
    # crew family and fails HERE, before any game runs.
    game_map = load_canonical_map()
    policy: CrewTrackPolicy
    try:
        if stamp.encoder_version == CREW_V1_ENCODER_VERSION:
            policy = build_crew_scorer(weights, game_map=game_map)
        elif stamp.encoder_version == OWNED_TASK_ENCODER_VERSION:
            policy = build_crew_scorer(
                weights, game_map=game_map, basis=OwnedTaskOptionBasis()
            )
        else:
            raise SystemExit(
                f"--crew-artifact: stamp encoder_version {stamp.encoder_version!r} "
                f"for {artifact_dir} names no rebuildable crew family — only "
                f"{CREW_V1_ENCODER_VERSION!r} (build_crew_scorer, the 22-weight v1 "
                f"menu) and {OWNED_TASK_ENCODER_VERSION!r} (build_crew_scorer with "
                "an OwnedTaskOptionBasis, the 27-weight owned-task menu) rebuild "
                "here. An impostor artifact (impostor-option-features-*) in the "
                "crew slot fails HERE — pass it as --candidate-artifact."
            )
    except ValueError as exc:
        raise SystemExit(
            f"--crew-artifact: could not rebuild the crew scorer for "
            f"{artifact_dir}: {exc}"
        ) from exc
    if policy.encoder_version != stamp.encoder_version:
        raise SystemExit(
            f"--crew-artifact: rebuilt crew policy encoder "
            f"{policy.encoder_version!r} != stamp encoder_version "
            f"{stamp.encoder_version!r} for {artifact_dir} (artifact-stamp "
            "mismatch)."
        )
    return policy, stamp


def _resolve_crew_artifact_arm(
    *,
    crew_artifact: Path,
    candidate_artifact: Path | None,
) -> tuple[AgentFactory, TacticalPolicyStamp | None, CrewTacticalPolicyStamp]:
    """Resolve ``--crew-artifact`` into a co-evo factory + BOTH auto-stamps (Task 18.19).

    The dual-role co-evo recorder's resolver (the crew analog of
    :func:`_resolve_candidate_artifact`, composing the impostor side when
    ``--candidate-artifact`` rides along). Loads the crew policy + its own
    ``stamp.json`` :class:`~orchestrator.replay.CrewTacticalPolicyStamp` via
    :func:`_load_crew_artifact_policy` (sha-verified, fail loud BEFORE any spend).
    When ``candidate_artifact`` is given the IMPOSTOR side loads through the EXISTING
    :func:`_load_candidate_policy` and both identities ride one recording — a
    CROSS-STAMP conflation guard then rejects a recording whose two identities share
    a ``policy_id`` or ``weights_sha256`` (the two movers on one recording MUST be
    distinct, so neither side's provenance can be re-read as the other's). Crew-only,
    the impostor side is ``None`` (the scripted FSM) and its auto-stamp is ``None``.
    The factory is :func:`training.coevo.factory.build_coevo_factory` — the ROLE
    BRANCH wrapping crew agents with the loaded crew scorer and impostor agents with
    the loaded impostor policy (or the frozen FSM when absent). Imports live inside
    this function so the default path's module graph stays byte-identical.
    """

    from engine.world import load_canonical_map
    from training.coevo.factory import build_coevo_factory

    crew_policy, crew_stamp = _load_crew_artifact_policy(crew_artifact)

    impostor_policy: BakeoffPolicy | None
    impostor_stamp: TacticalPolicyStamp | None
    if candidate_artifact is not None:
        impostor_policy, impostor_stamp = _load_candidate_policy(candidate_artifact)
        if (
            crew_stamp.policy_id == impostor_stamp.policy_id
            or crew_stamp.weights_sha256 == impostor_stamp.weights_sha256
        ):
            raise SystemExit(
                "the dual-role co-evo recorder produced a crew stamp and an "
                "impostor stamp that collide (the 18.19 cross-stamp conflation "
                f"guard): crew (policy_id={crew_stamp.policy_id!r}, "
                f"weights_sha256={crew_stamp.weights_sha256!r}) vs impostor "
                f"(policy_id={impostor_stamp.policy_id!r}, "
                f"weights_sha256={impostor_stamp.weights_sha256!r}). The two "
                "identities on one recording must be DISTINCT so neither side's "
                "provenance can be re-read as the other's."
            )
    else:
        impostor_policy = None
        impostor_stamp = None

    factory = build_coevo_factory(
        impostor_policy, crew_policy, game_map=load_canonical_map()
    )
    return factory, impostor_stamp, crew_stamp


def _resolve_recorded_stamp(
    *,
    auto_stamp: TacticalPolicyStamp | None,
    explicit_stamp: TacticalPolicyStamp | None,
) -> TacticalPolicyStamp | None:
    """Reconcile the running factory's stamp with any explicit stamp (Task 15.21).

    The Task-15.21 mis-stamp guard, in BOTH directions (the owner-ratified
    PR-#248 amendment to the 15.21 contract), now shared by the champion path and
    the Task-17.14 candidate-artifact path. The stamp of the factory actually
    running is authoritative — the champion auto-stamp on ``learned-champion``,
    the candidate's own ``stamp.json`` on ``--candidate-artifact``, or ``None``
    (the absent = FSM default) on ``fsm-default``. An explicit
    ``--tactical-policy-stamp`` is accepted only when it matches that stamp
    field-for-field (an idempotent re-statement), and any contradiction exits
    non-zero naming the differing field — a learned recording can never carry an
    FSM label, an FSM recording can never carry a learned one, and the Task-15.18
    finalist-eval proof (``stamp.weights_sha256`` equals the committed sidecar)
    becomes impossible to forget AND impossible to counterfeit from this CLI.
    What is RECORDED is unchanged from Task 15.9 for every accepted combination,
    so an unflagged, unstamped run stays byte-identical to the pre-15.9 recorder.
    """

    reference = (
        auto_stamp if auto_stamp is not None else fsm_default_tactical_policy_stamp()
    )
    if explicit_stamp is not None:
        for field_name in (
            "policy_id",
            "method",
            "encoder_version",
            "weights_sha256",
            "anchor_policy",
        ):
            reference_value = getattr(reference, field_name)
            explicit_value = getattr(explicit_stamp, field_name)
            if reference_value != explicit_value:
                descriptor = (
                    "auto-stamps every recording from the loaded policy artifact "
                    f"(policy_id={reference.policy_id!r})"
                    if auto_stamp is not None
                    else "records the scripted FSM default"
                )
                raise SystemExit(
                    f"the running recorder {descriptor}; the explicit "
                    "--tactical-policy-stamp contradicts it on "
                    f"{field_name!r} (explicit {explicit_value!r} != recorder "
                    f"{reference_value!r}). Drop the explicit stamp (the selected "
                    "factory auto-wires its own stamp; the FSM default needs at "
                    f"most the literal {FSM_DEFAULT_POLICY_ID!r}) or pass one "
                    "matching the running factory field-for-field."
                )
    if auto_stamp is not None:
        return auto_stamp
    return explicit_stamp


def _format_summary(eval_report: TournamentEvalReport) -> str:
    """Human-readable balance + meeting-rate + cost summary from the eval report.

    The crew / impostor / tick-budget buckets reduce out of
    ``GameReport.winner`` (``winner is None`` is the non-decisive tick-budget
    bucket); the meeting numbers come from the Phase 7 W0.3
    :class:`~eval.meeting_quality.MeetingRateReport` (``meeting_rate`` is
    rendered as a percentage and guards the ``None``/no-games case the way
    ``decisive_split`` guards the no-decisive-games case); the cost numbers come
    from the bundled cost dashboard.
    """

    report = eval_report.report
    games = len(report.games)
    crew_wins = sum(1 for game in report.games if game.winner == "CREWMATES")
    impostor_wins = sum(1 for game in report.games if game.winner == "IMPOSTORS")
    tick_budget_reached = sum(1 for game in report.games if game.winner is None)
    meeting = eval_report.meeting_rate
    dashboard = eval_report.cost_dashboard

    lines = [
        f"games:                {games}",
        f"crew_wins:            {crew_wins}",
        f"impostor_wins:        {impostor_wins}",
        f"tick_budget_reached:  {tick_budget_reached}",
    ]
    decisive = crew_wins + impostor_wins
    if decisive > 0:
        lines.append(
            "decisive_split:       "
            f"CREWMATES={crew_wins / decisive:.2%} "
            f"IMPOSTORS={impostor_wins / decisive:.2%} of {decisive} decisive"
        )
    else:
        lines.append("decisive_split:       (no decisive games)")
    lines.append(f"meetings_total:       {meeting.meetings_total}")
    if meeting.meeting_rate is not None:
        lines.append(
            "meeting_rate:         "
            f"{meeting.meeting_rate:.2%} "
            f"({meeting.games_with_meeting}/{meeting.games_total} games)"
        )
    else:
        lines.append("meeting_rate:         (no games)")
    lines.append(
        "meeting_triggers:     "
        f"body={meeting.body_report_meetings} "
        f"emergency={meeting.emergency_meetings}"
    )
    lines.append(f"total_cost_usd:       {dashboard.total_cost_usd:.4f}")
    lines.append(f"mean_cost_per_game:   {dashboard.mean_cost_per_game:.4f}")
    return "\n".join(lines)


def _resolve_roster(args: argparse.Namespace) -> tuple[int, int, int]:
    """Resolve ``(num_players, num_impostors, tasks_per_crewmate)`` from CLI args.

    A ``--roster-preset`` supplies all three values at once and is mutually
    exclusive with passing ``--num-players`` / ``--num-impostors`` /
    ``--tasks-per-crewmate`` explicitly — combining them raises ``SystemExit``
    rather than silently letting one win (AGENTS.md "no silent fallbacks"). When
    no preset is given, each omitted roster flag falls back to its shared default
    constant, so an unflagged run uses the 4p/1i roster at the locked default of
    2 tasks/crewmate (``DEFAULT_TASKS_PER_CREWMATE``).
    """

    explicit = [
        flag
        for flag, value in (
            ("--num-players", args.num_players),
            ("--num-impostors", args.num_impostors),
            ("--tasks-per-crewmate", args.tasks_per_crewmate),
        )
        if value is not None
    ]
    if args.roster_preset is not None:
        if explicit:
            raise SystemExit(
                f"--roster-preset {args.roster_preset!r} is mutually exclusive "
                f"with explicit roster flags ({', '.join(explicit)}); pass a "
                "named preset or explicit roster flags, not both"
            )
        preset = ROSTER_PRESETS[args.roster_preset]
        return preset.num_players, preset.num_impostors, preset.tasks_per_crewmate

    num_players = (
        args.num_players if args.num_players is not None else DEFAULT_NUM_PLAYERS
    )
    num_impostors = (
        args.num_impostors if args.num_impostors is not None else DEFAULT_NUM_IMPOSTORS
    )
    tasks_per_crewmate = (
        args.tasks_per_crewmate
        if args.tasks_per_crewmate is not None
        else DEFAULT_TASKS_PER_CREWMATE
    )
    return num_players, num_impostors, tasks_per_crewmate


def _emit_report_json(eval_report: TournamentEvalReport, report_output: Path) -> None:
    """Serialize the eval report to JSON, validating the round-trip first.

    A report that cannot be read back is not a report: ``model_validate_json``
    re-parses the dumped JSON and raises on any drift before it is persisted
    (the DoD's ``model_validate_json(model_dump_json(...))`` gate).
    """

    json_text = eval_report.model_dump_json(indent=2)
    TournamentEvalReport.model_validate_json(json_text)
    report_output.parent.mkdir(parents=True, exist_ok=True)
    report_output.write_text(json_text + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.num_games < 1:
        raise SystemExit(f"--num-games must be at least 1, got {args.num_games}")
    num_players, num_impostors, tasks_per_crewmate = _resolve_roster(args)
    explicit_stamp = _resolve_tactical_policy_stamp(args.tactical_policy_stamp)
    # Arm selection (Task 18.19 puts the dual-role co-evo arm FIRST, leaving the
    # two Task-18.7/15.21 branches verbatim). --crew-artifact records with an
    # arbitrary committed CREW artifact and, combined with --candidate-artifact,
    # produces a DUAL-stamp co-evo recording (both a crew AND an impostor stamp on
    # one game); it is mutually exclusive with the two single-side --agent-factory
    # arms (learned-champion / learned-crew), which each select a single mover.
    # The learned-crew arm (Task 18.7) resolves its own factory + CREW auto-stamp
    # and leaves the impostor tactical auto_stamp ABSENT (impostors stay the
    # scripted FSM); it still rejects a combined --candidate-artifact (an impostor
    # mover) because it is single-side. Every other arm keeps crew_auto_stamp None.
    # The three resolution outputs are declared up front so the crew branches
    # (which alone yield a non-None factory here) do not narrow ``agent_factory``
    # below the ``| None`` the ``fsm-default`` path needs.
    agent_factory: AgentFactory | None
    auto_stamp: TacticalPolicyStamp | None
    crew_auto_stamp: CrewTacticalPolicyStamp | None
    if args.crew_artifact is not None:
        if args.agent_factory != FSM_DEFAULT_POLICY_ID:
            raise SystemExit(
                f"--crew-artifact is mutually exclusive with --agent-factory "
                f"{args.agent_factory!r}: the crew artifact selects the crew policy "
                "(and --candidate-artifact the impostor side) for a dual-role "
                "co-evo recording, while the single-side --agent-factory arms each "
                f"select one mover. Drop --agent-factory (it defaults to "
                f"{FSM_DEFAULT_POLICY_ID!r})."
            )
        agent_factory, auto_stamp, crew_auto_stamp = _resolve_crew_artifact_arm(
            crew_artifact=args.crew_artifact,
            candidate_artifact=args.candidate_artifact,
        )
    elif args.agent_factory == LEARNED_CREW_FACTORY_ID:
        if args.candidate_artifact is not None:
            raise SystemExit(
                f"--candidate-artifact is mutually exclusive with --agent-factory "
                f"{LEARNED_CREW_FACTORY_ID!r}: the crew arm wraps every crewmate "
                "with the committed crew scorer and auto-stamps the crew stamp, "
                "while the artifact records an impostor policy. Drop --agent-factory "
                f"(it defaults to {FSM_DEFAULT_POLICY_ID!r})."
            )
        agent_factory, crew_auto_stamp = _resolve_learned_crew_factory()
        auto_stamp = None
    else:
        agent_factory, auto_stamp = _resolve_agent_factory(
            args.agent_factory, candidate_artifact=args.candidate_artifact
        )
        crew_auto_stamp = None
    # The IMPOSTOR-side stamp reconciliation is unchanged (Task 15.21): on the
    # learned-crew arm and the crew-only --crew-artifact arm auto_stamp is None, so
    # the reference is the FSM default and an explicit champion
    # --tactical-policy-stamp contradicts it and exits here; on a dual-role
    # --crew-artifact + --candidate-artifact recording auto_stamp is the impostor
    # artifact's OWN stamp, so an explicit stamp must restate it field-for-field
    # (the same two-direction guard the single-side candidate arm uses).
    tactical_policy_stamp = _resolve_recorded_stamp(
        auto_stamp=auto_stamp,
        explicit_stamp=explicit_stamp,
    )
    seeds = range(args.start_seed, args.start_seed + args.num_games)
    # ``force`` is threaded into each per-seed ReplayLog construction inside
    # run_tournament_eval, so a conflicting replay-seed-{seed}.jsonl is truncated
    # immediately before that game writes it. A crash partway through a re-run
    # therefore never deletes a later seed's replay that was never reached;
    # without --force, the first existing file raises and exits non-zero
    # (DESIGN.md §11.4; Task 4.16).
    #
    # Three-branch call (Task 18.7, extending the Task-15.21 two-branch seam;
    # Task 18.19 reuses the crew_auto_stamp branch for dual-role recordings):
    # the two pre-18.7 call sites stay BYTE-IDENTICAL for their spies — the
    # fsm-default path passes NO agent_factory kwarg (run_tournament_eval's
    # omitted-kwarg default already is build_default_agent_factory(), so any
    # 15.9/15.21/17.14-era caller/spy of this seam keeps pinning it) and the
    # learned-champion / candidate path threads the opt-in factory unchanged.
    # The crew_auto_stamp branch threads the additive crew_policy_stamp beside the
    # impostor tactical stamp — absent (scripted FSM) on the learned-crew and
    # crew-only --crew-artifact arms, present on a dual-role co-evo recording;
    # crew_auto_stamp is None on every other path, so they fall through to the
    # unchanged branches.
    if crew_auto_stamp is not None:
        report = run_tournament_eval(
            seeds=seeds,
            output_dir=args.output_dir,
            agent_factory=agent_factory,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
            max_ticks=args.max_ticks,
            force=args.force,
            tactical_policy_stamp=tactical_policy_stamp,
            crew_policy_stamp=crew_auto_stamp,
        )
    elif agent_factory is None:
        report = run_tournament_eval(
            seeds=seeds,
            output_dir=args.output_dir,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
            max_ticks=args.max_ticks,
            force=args.force,
            tactical_policy_stamp=tactical_policy_stamp,
        )
    else:
        report = run_tournament_eval(
            seeds=seeds,
            output_dir=args.output_dir,
            agent_factory=agent_factory,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
            max_ticks=args.max_ticks,
            force=args.force,
            tactical_policy_stamp=tactical_policy_stamp,
        )
    eval_report = build_tournament_eval_report(report)

    report_output: Path = (
        args.report_output
        if args.report_output is not None
        else args.output_dir / _DEFAULT_REPORT_FILENAME
    )
    _emit_report_json(eval_report, report_output)

    print(_format_summary(eval_report))
    print(f"report:               {report_output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
