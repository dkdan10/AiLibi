"""FROZEN (Phase 19 tier map, training/README.md): Phase-9 probe harness, concluded.
Bug fixes and evidence readers only; no new search.

Reconstruct real vote-ballot decision contexts from committed replays.

The harness's foundation. For every recorded vote in a committed replay set it
rebuilds the *exact* context the voter's prompt was rendered from — reusing the
production seams so the reconstruction is faithful, not approximate:

- ground-truth roles via :func:`orchestrator.seeder.seed_initial_state` (roles
  are firewalled out of the replays);
- each voter's rendered memory + belief suspicion via the loader's public
  :meth:`api.replay_loader.ReplayLoader.get_meeting_memory` (a full
  perception+memory re-walk, cached per game);
- the vote-time suspicion graph via the production
  :func:`meetings.manager._suspicion_graph_with_contradictions` (belief Rule 2
  + the 7.12/9.3 teammate firewall) over the *recorded* contradictions;
- the transcript / contradictions / recorded ballots straight from the raw
  :class:`orchestrator.replay.MeetingReplayEntry`.

``trust`` is never mutated in the live pipeline (only suspicion moves via belief
rules 1-4), so it is the constant ``_DEFAULT_TRUST`` (0.5) for every belief — the
one field the public view drops, reconstructed exactly as the default.

Each item is tagged with ground truth (was a living true impostor visible at
suspicion >= the skip threshold?) and the recorded decision, so the grader can
score conversion / inversion deterministically.

Usage::

    python -m experiments.model_probe.corpus [--sample-dir DIR] [--seeds 0,1,2]
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from agents.strategic.prompts.loader import vote_ballot_prompt
from api.replay_loader import ReplayLoader
from engine.world import load_canonical_map
from meetings.manager import SuspicionEntry, _suspicion_graph_with_contradictions
from meetings.schemas import ContradictionRef, MeetingTranscript
from orchestrator.replay import MeetingReplayEntry, read_all_entries
from orchestrator.seeder import seed_initial_state

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SAMPLE_DIR = REPO_ROOT / "replays" / "samples" / "9p2i"
# DESIGN.md §4.6 / MeetingConfig default; the value the prompt is rendered with.
SKIP_THRESHOLD = 0.6
# trust is never adjusted in the live perception/belief pipeline (only suspicion
# moves), so every belief carries agents.memory.beliefs._DEFAULT_TRUST.
DEFAULT_TRUST = 0.5


@dataclass(frozen=True)
class VoteContext:
    """Everything needed to (re-)render one voter's vote-ballot prompt.

    The exact kwargs of :func:`agents.strategic.prompts.loader.vote_ballot_prompt`,
    held as live objects so a variant template can re-render the same context.
    """

    voter_id: str
    rendered_memory: str
    transcript: MeetingTranscript
    contradiction_flags: tuple[ContradictionRef, ...]
    suspicion_graph: tuple[SuspicionEntry, ...]
    candidate_targets: tuple[str, ...]
    skip_confidence_threshold: float
    fellow_impostor_ids: tuple[str, ...]


@dataclass(frozen=True)
class CorpusItem:
    """One reconstructed vote decision + its ground truth and recorded outcome."""

    seed: int
    game_id: str
    meeting_id: str
    voter_id: str
    voter_role: str
    context: VoteContext
    recorded_target: str
    recorded_confidence: float
    recorded_rationale: str
    # Ground truth, computed from the lifted graph the prompt actually shows:
    max_impostor_suspicion: float
    available_impostor_ids: tuple[str, ...]
    recorded_voted_impostor: bool
    # A crewmate who, with a living true impostor visible at >= threshold, did
    # NOT vote that impostor (skipped or voted an innocent) — the F1 set.
    is_inversion: bool

    @property
    def item_id(self) -> str:
        return f"{self.seed}:{self.meeting_id}:{self.voter_id}"


def _roster(sample_dir: Path) -> dict[str, int]:
    raw = json.loads((sample_dir / "roster.json").read_text(encoding="utf-8"))
    return {
        "num_players": int(raw["num_players"]),
        "num_impostors": int(raw["num_impostors"]),
        "tasks_per_crewmate": int(raw["tasks_per_crewmate"]),
    }


def _roles_for_seed(
    seed: int, game_map: object, roster: dict[str, int]
) -> dict[str, str]:
    state = seed_initial_state(
        seed=seed,
        game_map=game_map,  # type: ignore[arg-type]
        num_players=roster["num_players"],
        num_impostors=roster["num_impostors"],
        tasks_per_crewmate=roster["tasks_per_crewmate"],
    )
    return {pid: player.role for pid, player in state.players.items()}


def render_prompt(context: VoteContext) -> str:
    """Render the BASELINE vote-ballot prompt for a context (production template)."""

    return vote_ballot_prompt(
        voter_id=context.voter_id,
        rendered_memory=context.rendered_memory,
        transcript=context.transcript,
        contradiction_flags=context.contradiction_flags,
        suspicion_graph=context.suspicion_graph,
        candidate_targets=context.candidate_targets,
        skip_confidence_threshold=context.skip_confidence_threshold,
        fellow_impostor_ids=context.fellow_impostor_ids,
    )


def build_corpus(
    sample_dir: Path = DEFAULT_SAMPLE_DIR,
    *,
    seeds: set[int] | None = None,
) -> list[CorpusItem]:
    """Reconstruct every recorded vote in ``sample_dir`` into a CorpusItem list."""

    game_map = load_canonical_map()
    roster = _roster(sample_dir)
    loader = ReplayLoader(sample_dir, game_map=game_map)

    paths = sorted(
        sample_dir.glob("replay-seed-*.jsonl"),
        key=lambda p: int(p.stem.rsplit("-", 1)[1]),
    )
    items: list[CorpusItem] = []
    for path in paths:
        seed = int(path.stem.rsplit("-", 1)[1])
        if seeds is not None and seed not in seeds:
            continue
        game_id = f"headless-seed-{seed}"
        roles = _roles_for_seed(seed, game_map, roster)
        impostors = {pid for pid, role in roles.items() if role == "IMPOSTOR"}

        meetings = [
            entry
            for entry in read_all_entries(path)
            if isinstance(entry, MeetingReplayEntry)
        ]
        for meeting in meetings:
            if not meeting.ballots:
                continue
            living = tuple(sorted({ballot.voter for ballot in meeting.ballots}))
            living_set = set(living)
            living_impostors = tuple(sorted(impostors & living_set))

            for ballot in meeting.ballots:
                voter = ballot.voter
                role = roles.get(voter, "UNKNOWN")
                try:
                    view = loader.get_meeting_memory(game_id, meeting.meeting_id, voter)
                except KeyError:
                    continue

                raw_graph = tuple(
                    SuspicionEntry(
                        player_id=belief.subject,
                        suspicion=belief.suspicion,
                        trust=DEFAULT_TRUST,
                    )
                    for belief in view.beliefs
                )
                fellow = (
                    tuple(pid for pid in living_impostors if pid != voter)
                    if role == "IMPOSTOR"
                    else ()
                )
                lifted = _suspicion_graph_with_contradictions(
                    voter_id=voter,
                    suspicion_graph=raw_graph,
                    contradictions=meeting.contradictions,
                    fellow_impostor_ids=fellow,
                    # Task 14.10 (PR #217 review): the recorded transcript
                    # carries the self-refuted-alibi signal, so a lever-ON
                    # corpus rebuild folds the same evidence-quality
                    # downgrade the production ballot fold applied — without
                    # it the reconstruction would silently diverge from the
                    # substrate the replay's stamp names (the helper fails
                    # loud on that shape).
                    transcript=meeting.transcript,
                )
                candidate_targets = tuple(pid for pid in living if pid != voter)
                context = VoteContext(
                    voter_id=voter,
                    rendered_memory=view.rendered_memory_text,
                    transcript=meeting.transcript,
                    contradiction_flags=meeting.contradictions,
                    suspicion_graph=lifted,
                    candidate_targets=candidate_targets,
                    skip_confidence_threshold=SKIP_THRESHOLD,
                    fellow_impostor_ids=fellow,
                )

                # Ground truth from the lifted graph (exactly what the prompt shows).
                impostor_suspicion = {
                    entry.player_id: entry.suspicion
                    for entry in lifted
                    if roles.get(entry.player_id) == "IMPOSTOR"
                    and entry.player_id in living_set
                }
                available = tuple(
                    sorted(
                        pid
                        for pid, susp in impostor_suspicion.items()
                        if susp >= SKIP_THRESHOLD
                    )
                )
                max_impostor = max(impostor_suspicion.values(), default=0.0)
                voted_impostor = ballot.target in living_impostors
                is_inversion = (
                    role == "CREWMATE" and bool(available) and not voted_impostor
                )

                items.append(
                    CorpusItem(
                        seed=seed,
                        game_id=game_id,
                        meeting_id=meeting.meeting_id,
                        voter_id=voter,
                        voter_role=role,
                        context=context,
                        recorded_target=ballot.target,
                        recorded_confidence=ballot.confidence,
                        recorded_rationale=ballot.rationale_text,
                        max_impostor_suspicion=max_impostor,
                        available_impostor_ids=available,
                        recorded_voted_impostor=voted_impostor,
                        is_inversion=is_inversion,
                    )
                )
    return items


def _digest(item: CorpusItem) -> dict[str, object]:
    return {
        "item_id": item.item_id,
        "seed": item.seed,
        "meeting_id": item.meeting_id,
        "voter_id": item.voter_id,
        "voter_role": item.voter_role,
        "recorded_target": item.recorded_target,
        "recorded_confidence": item.recorded_confidence,
        "max_impostor_suspicion": round(item.max_impostor_suspicion, 4),
        "available_impostor_ids": list(item.available_impostor_ids),
        "recorded_voted_impostor": item.recorded_voted_impostor,
        "is_inversion": item.is_inversion,
        "recorded_rationale": item.recorded_rationale[:240],
    }


def _parse_seeds(raw: str | None) -> set[int] | None:
    if not raw:
        return None
    return {int(token) for token in raw.split(",") if token.strip()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample-dir", type=Path, default=DEFAULT_SAMPLE_DIR)
    parser.add_argument("--seeds", type=str, default=None, help="e.g. 0,1,2")
    parser.add_argument(
        "--dump-sample",
        action="store_true",
        help="Write one reconstructed inversion prompt to results/ for eyeballing.",
    )
    args = parser.parse_args()

    items = build_corpus(args.sample_dir, seeds=_parse_seeds(args.seeds))
    crew = [i for i in items if i.voter_role == "CREWMATE"]
    inversions = [i for i in items if i.is_inversion]
    crew_with_available = [i for i in crew if i.available_impostor_ids]

    print(
        f"corpus: {len(items)} votes ({len(crew)} crew, "
        f"{len(items) - len(crew)} impostor)"
    )
    print(
        f"crew votes with a living impostor visible >= {SKIP_THRESHOLD}: "
        f"{len(crew_with_available)}"
    )
    print(f"inversions (crew, impostor available, did NOT vote it): {len(inversions)}")
    if crew_with_available:
        converted = sum(1 for i in crew_with_available if i.recorded_voted_impostor)
        print(
            f"  of those, recorded conversion: {converted}/{len(crew_with_available)} "
            f"({converted / len(crew_with_available):.1%})"
        )
    skips = sum(1 for i in inversions if i.recorded_target == "SKIP")
    print(f"  inversions that SKIPPED: {skips}/{len(inversions)}")

    results_dir = Path(__file__).resolve().parent / "results"
    results_dir.mkdir(exist_ok=True)
    digest_path = results_dir / "corpus-digest.json"
    digest_path.write_text(
        json.dumps([_digest(i) for i in items], indent=2), encoding="utf-8"
    )
    print(f"digest -> {digest_path}")

    if args.dump_sample and inversions:
        sample = inversions[0]
        sample_path = results_dir / "sample-inversion-prompt.txt"
        sample_path.write_text(
            f"# {sample.item_id} (role={sample.voter_role}, "
            f"recorded={sample.recorded_target}, "
            f"max_impostor_suspicion={sample.max_impostor_suspicion:.2f}, "
            f"available={sample.available_impostor_ids})\n\n"
            + render_prompt(sample.context),
            encoding="utf-8",
        )
        print(f"sample inversion prompt -> {sample_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
