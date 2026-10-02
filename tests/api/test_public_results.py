"""Public outcomes are reconstructed; editorial prose binds to exact recordings."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import threading
from collections.abc import Callable
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

import api.public_results as public
from api.main import ENV_REPLAY_DIR, create_app
from api.replay_loader import ReplayLoader
from api.schemas import (
    AccusationClaimView,
    AgentMemoryView,
    MeetingView,
    PublicCaseView,
    PublicResultsView,
    ReplayView,
)
from orchestrator.recording_fingerprint import recording_fingerprint
from tests.orchestrator.test_replay_integrity import (
    completed_recording as completed_recording,
)

SAMPLES = Path(__file__).resolve().parents[2] / "replays/samples"


@pytest.fixture(scope="module")
def canonical_summary() -> PublicResultsView:
    return public.build_public_results(ReplayLoader(SAMPLES / "9p2i"))


def test_current_summary_is_bounded_and_source_checked(
    canonical_summary: PublicResultsView,
) -> None:
    r = canonical_summary
    # The promoted set (candidate round 2, since 2026-10-02). Was (50, 50, 39, 11,
    # 1) / (145, 90, 81, 9) / (70, 70, 20, 11) on the baseline-9 bytes, and
    # (50, 50, 35, 15, 0) / (151, 95, 82, 13) / (68, 68, 27, 14) on baseline 8.
    assert (r.games, r.completed, r.crew_wins, r.impostor_wins, r.task_wins) == (
        50,
        50,
        26,
        24,
        13,
    )
    assert (r.meetings, r.ejections, r.impostor_ejections, r.innocent_ejections) == (
        117,
        66,
        44,
        22,
    )
    assert (
        r.proof_backed_ejections,
        r.proof_backed_correct,
        r.proof_free_ejections,
        r.proof_free_correct,
    ) == (24, 24, 42, 20)
    # The two kept cases sit on the featured head, seed 19, and the set links the
    # commit that landed its bytes. (The holding edit published no case and no
    # link; the baseline-9 bytes carried three cases on seeds 23, 29 and 0.)
    assert [case.case_id for case in r.cases] == ["witnessed-vent", "weak-evidence"]
    assert (r.recorded_from, r.recorded_until) == ("2026-10-01", "2026-10-01")
    assert r.source_url == _ROOT_9P2I
    assert len(r.model_dump_json().encode()) < public.MAX_PUBLIC_RESULTS_BYTES
    assert r.reported_cost_usd == 0 and r.input_tokens > 0


@pytest.mark.parametrize("mutation", ["winner", "tick", "order"])
def test_corrupt_recording_cannot_publish_results(
    completed_recording: Path,
    tmp_path: Path,
    mutation: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    rows = [json.loads(line) for line in completed_recording.read_text().splitlines()]
    if mutation == "winner":
        rows[-1]["winner"] = "IMPOSTORS"
    elif mutation == "tick":
        rows[0]["tick"] = 9000
    else:
        rows[0], rows[1] = rows[1], rows[0]
    destination = tmp_path / completed_recording.name
    destination.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    with pytest.raises(ValueError):
        public.build_public_results(ReplayLoader(tmp_path))
    monkeypatch.setenv(ENV_REPLAY_DIR, str(tmp_path))
    with TestClient(create_app(), raise_server_exceptions=False) as client:
        assert client.get("/eval/summary").status_code >= 400


def test_analysis_override_never_certifies_public_results(
    completed_recording: Path,
) -> None:
    with pytest.raises(ValueError, match="strict substrate"):
        public.build_public_results(
            ReplayLoader(completed_recording.parent, allow_substrate_mismatch=True)
        )


def test_changed_source_suppresses_editorial_prose_and_pinned_set_url(
    tmp_path: Path,
) -> None:
    destination = tmp_path / "9p2i"
    destination.mkdir()
    shutil.copyfile(SAMPLES / "9p2i/roster.json", destination / "roster.json")
    source = SAMPLES / "9p2i/replay-seed-19.jsonl"
    shutil.copyfile(source, destination / source.name)
    # The case's own game, copied unchanged, keeps both cases (their sha256
    # matches); a one-set fingerprint is not a published one, so no set link.
    unchanged = public.build_public_results(ReplayLoader(destination))
    assert [case.case_id for case in unchanged.cases] == [
        "witnessed-vent",
        "weak-evidence",
    ]
    assert unchanged.source_url is None
    # Valid JSON/replay with a different byte identity cannot keep the old prose.
    with (destination / source.name).open("a") as stream:
        stream.write("\n")
    r = public.build_public_results(ReplayLoader(destination))
    assert r.games == r.completed == 1
    assert not r.cases and r.source_url is None
    assert r.recorded_from is None


def test_summary_budget_gate_bites(
    completed_recording: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(public, "MAX_PUBLIC_RESULTS_BYTES", 1)
    with pytest.raises(ValueError, match="50 KiB"):
        public.build_public_results(ReplayLoader(completed_recording.parent))


def test_partial_recording_retains_reported_spend_without_a_win(
    completed_recording: Path, tmp_path: Path
) -> None:
    rows = [json.loads(line) for line in completed_recording.read_text().splitlines()]
    end = next(
        i for i, row in enumerate(rows) if "llm_calls" in row and "ballots" in row
    )
    rows = rows[: end + 1]
    assert rows[-1]["llm_calls"]
    rows[-1]["llm_calls"][0]["cost_usd"] = 0.25
    destination = tmp_path / completed_recording.name
    destination.write_text("\n".join(json.dumps(row) for row in rows) + "\n")
    result = public.build_public_results(ReplayLoader(tmp_path))
    assert (result.games, result.completed, result.unfinished) == (1, 0, 1)
    assert result.crew_wins == result.impostor_wins == 0
    assert result.reported_cost_usd == 0.25


def test_the_kept_cases_sit_on_the_featured_head_and_pin_its_bytes() -> None:
    # Two cases are kept, both re-written on the featured 9-player head (seed 19,
    # the promoted set since 2026-10-02): its first meeting is the supported
    # case, its second the unresolved one. The disputed-route case is withdrawn:
    # its game (seed 29 meeting 1 on the baseline-9 bytes) has no promoted
    # counterpart on the strip, and no featured meeting ejects an innocent
    # player on a disputed account. Each kept case names its file's sha256.
    cases = public._curated_cases()  # noqa: SLF001
    assert [(c.case_id, c.classification, c.meeting_id) for c in cases] == [
        ("witnessed-vent", "supported", "headless-seed-19:meeting-0"),
        ("weak-evidence", "unresolved", "headless-seed-19:meeting-1"),
    ]
    recorded = (SAMPLES / "9p2i" / "replay-seed-19.jsonl").read_bytes()
    for case in cases:
        assert case.source_sha256 == hashlib.sha256(recorded).hexdigest()
        assert case.source_url == _ROOT_9P2I + "replay-seed-19.jsonl"


def test_each_case_names_the_facts_its_check_holds() -> None:
    # `_check_case` holds facts to the recording; this holds each sentence to
    # name exactly those facts, so prose rewritten to say something else fails
    # here even where the check still passes.
    vent, weak = public._curated_cases()  # noqa: SLF001
    assert vent.title == "A sighting the table can check"
    assert vent.setup == (
        "A body report opens the meeting, and another player then describes "
        "seeing someone use a vent. Follow that observation into the ballots."
    )
    assert vent.explanation == (
        "p-1's observation records p-6 venting in Engineering at tick 12, and "
        "p-1's ballot cites it. Four other voters cite p-1's turn and vote for "
        "p-6. The meeting carries role proof and ejects p-6. This is a supported "
        "use of a certified observation; it does not demonstrate general social "
        "deduction."
    )
    assert (vent.meeting_tick, vent.observer_id, vent.observation_id) == (
        12,
        "p-1",
        "p-1:12:1",
    )
    assert vent.turn_id == "headless-seed-19:meeting-0:turn-2"
    assert weak.title == "When accounts do not settle the question"
    assert weak.setup == (
        "A body reporter is accused, and the meeting raises no flag at all. Read "
        "the accusations, the reporter's reply, and how the table handles "
        "uncertainty."
    )
    assert weak.explanation == (
        "Four speakers accuse the reporter, crewmate p-1, and no flag names "
        "anyone. p-1 replies with an account of its own route. Four voters skip, "
        "each saying it held nothing, and one votes for p-1, so no one is "
        "ejected. Withholding a conviction is defensible on this evidence; this "
        "example does not establish that skipping was the optimal game strategy."
    )
    assert (weak.meeting_tick, weak.observer_id, weak.observation_id) == (
        31,
        "p-1",
        None,
    )
    assert weak.turn_id == "headless-seed-19:meeting-1:turn-5"


# The two roots, typed here rather than imported, so a moved constant cannot
# move its own check. The 9-player set's bytes landed in 148fa211 (the
# promotion); the 4-player replays are unchanged since 9bae2b03.
_ROOT_9P2I = (
    "https://github.com/dkdan10/AiLibi/blob/"
    "148fa211a5851c288eeaf1a9591197f8ba13bdcc/replays/samples/9p2i/"
)
_ROOT_4P1I = (
    "https://github.com/dkdan10/AiLibi/blob/"
    "9bae2b03032cede6a180c0888fde3b4e47f9a5f1/replays/samples/4p1i/"
)


def _assert_split_roots(nine: str | None, four: str | None) -> None:
    assert nine == _ROOT_9P2I, ("9p2i", nine)
    assert four == _ROOT_4P1I, ("4p1i", four)


def test_each_set_links_the_commit_that_holds_its_bytes() -> None:
    nine = public._source_url(recording_fingerprint(SAMPLES / "9p2i"))  # noqa: SLF001
    four = public._source_url(recording_fingerprint(SAMPLES / "4p1i"))  # noqa: SLF001
    _assert_split_roots(nine, four)
    four_summary = public.build_public_results(ReplayLoader(SAMPLES / "4p1i"))
    assert four_summary.source_url == _ROOT_4P1I
    # Planted: the d41c9006 rule, the 4p1i link built from the one 9p2i root,
    # would name the promotion commit for bytes it does not cover, and would
    # move data/4p1i/eval/summary.json in the bundle.
    with pytest.raises(AssertionError, match="4p1i"):
        _assert_split_roots(nine, _ROOT_9P2I.replace("9p2i/", "4p1i/"))
    # A fingerprint no published set carries has no pinned source.
    assert public._source_url("sha256:" + "0" * 64) is None  # noqa: SLF001


@pytest.fixture(scope="module")
def head_loader() -> ReplayLoader:
    return ReplayLoader(SAMPLES / "9p2i")


@pytest.fixture(scope="module")
def head_replay(head_loader: ReplayLoader) -> ReplayView:
    return head_loader.load_replay("headless-seed-19")


def _case(case_id: str) -> PublicCaseView:
    (case,) = [c for c in public._curated_cases() if c.case_id == case_id]  # noqa: SLF001
    return case


def _meeting(replay: ReplayView, meeting_id: str) -> MeetingView:
    return next(m for m in replay.meetings if m.meeting_id == meeting_id)


def _edit_meeting(replay: ReplayView, meeting_id: str, **update: Any) -> ReplayView:
    meetings = tuple(
        m.model_copy(update=update) if m.meeting_id == meeting_id else m
        for m in replay.meetings
    )
    return replay.model_copy(update={"meetings": meetings})


def _edit_turn(
    replay: ReplayView, meeting_id: str, turn_id: str, **update: Any
) -> ReplayView:
    meeting = _meeting(replay, meeting_id)
    turns = tuple(
        t.model_copy(update=update) if t.turn_id == turn_id else t
        for t in meeting.turns
    )
    return _edit_meeting(replay, meeting_id, turns=turns)


def _edit_ballot(
    replay: ReplayView, meeting_id: str, voter: str, **update: Any
) -> ReplayView:
    meeting = _meeting(replay, meeting_id)
    ballots = tuple(
        b.model_copy(update=update) if b.voter == voter else b for b in meeting.ballots
    )
    return _edit_meeting(replay, meeting_id, ballots=ballots)


def _role(replay: ReplayView, agent_id: str, role: str) -> ReplayView:
    players = tuple(
        p.model_copy(update={"role": role}) if p.agent_id == agent_id else p
        for p in replay.players
    )
    return replay.model_copy(update={"players": players})


_VENT = "headless-seed-19:meeting-0"
_VENT_TURN = "headless-seed-19:meeting-0:turn-2"
_WEAK = "headless-seed-19:meeting-1"
_WEAK_TURN = "headless-seed-19:meeting-1:turn-5"


def _sighting_moved(replay: ReplayView) -> ReplayView:
    turn = next(t for t in _meeting(replay, _VENT).turns if t.turn_id == _VENT_TURN)
    observations = tuple(
        o.model_copy(update={"room": "STORAGE"}) if o.type == "saw_vent" else o
        for o in turn.observations
    )
    return _edit_turn(replay, _VENT, _VENT_TURN, observations=observations)


def _one_voter_cites_elsewhere(replay: ReplayView) -> ReplayView:
    return _edit_ballot(
        replay, _VENT, "p-3", primary_reason_id="headless-seed-19:meeting-0:turn-0"
    )


def _role_proof_recategorised(replay: ReplayView) -> ReplayView:
    flags = tuple(
        c.model_copy(update={"category": "cross_statement"})
        for c in _meeting(replay, _VENT).contradictions
    )
    return _edit_meeting(replay, _VENT, contradictions=flags)


def _an_accusation_withdrawn(replay: ReplayView) -> ReplayView:
    # p-7's opt-in turn keeps every other claim and loses its accusation.
    turn_id = "headless-seed-19:meeting-1:turn-3"
    turn = next(t for t in _meeting(replay, _WEAK).turns if t.turn_id == turn_id)
    assert turn.speaker == "p-7"
    claims = tuple(c for c in turn.claims if c.type != "accusation")
    return _edit_turn(replay, _WEAK, turn_id, claims=claims)


def _an_accusation_turned(replay: ReplayView) -> ReplayView:
    # p-7 still accuses, but names p-9 instead of the reporter.
    turn_id = "headless-seed-19:meeting-1:turn-3"
    turn = next(t for t in _meeting(replay, _WEAK).turns if t.turn_id == turn_id)
    claims = tuple(
        c.model_copy(update={"against": "p-9"}) if c.type == "accusation" else c
        for c in turn.claims
    )
    return _edit_turn(replay, _WEAK, turn_id, claims=claims)


def _a_flag_raised(replay: ReplayView) -> ReplayView:
    flag = _meeting(replay, _VENT).contradictions[0]
    return _edit_meeting(replay, _WEAK, contradictions=(flag,))


def _the_reply_states_no_route(replay: ReplayView) -> ReplayView:
    turn = next(t for t in _meeting(replay, _WEAK).turns if t.turn_id == _WEAK_TURN)
    claims = tuple(c for c in turn.claims if c.type != "alibi")
    return _edit_turn(replay, _WEAK, _WEAK_TURN, claims=claims)


def _another_voter_cites_it(replay: ReplayView) -> ReplayView:
    """The witness's citation moved onto another voter's ballot for p-6."""

    moved = _edit_ballot(replay, _VENT, "p-3", primary_reason_observation_id="p-1:12:1")
    return _edit_ballot(moved, _VENT, "p-1", primary_reason_observation_id=None)


def _the_flag_names_another(replay: ReplayView) -> ReplayView:
    flags = tuple(
        c.model_copy(update={"subjects": ("p-9",)})
        for c in _meeting(replay, _VENT).contradictions
    )
    return _edit_meeting(replay, _VENT, contradictions=flags)


def _the_route_is_about(replay: ReplayView, subject: str | None) -> ReplayView:
    """The reply's stated route about ``subject``, or with no legs for ``None``."""

    turn = next(t for t in _meeting(replay, _WEAK).turns if t.turn_id == _WEAK_TURN)
    claims = tuple(
        (
            c.model_copy(update={"subject": subject})
            if subject is not None
            else c.model_copy(update={"route": ()})
        )
        if c.type == "alibi"
        else c
        for c in turn.claims
    )
    return _edit_turn(replay, _WEAK, _WEAK_TURN, claims=claims)


def _a_sixth_ballot(replay: ReplayView) -> ReplayView:
    meeting = _meeting(replay, _WEAK)
    extra = meeting.ballots[0].model_copy(
        update={"voter": "p-5", "target": "p-3", "grounding_label": "supported"}
    )
    return _edit_meeting(replay, _WEAK, ballots=(*meeting.ballots, extra))


_PERTURBATIONS: dict[str, tuple[str, Callable[[ReplayView], ReplayView]]] = {
    # The supported case, sentence by sentence.
    "body-report-opens": (
        "witnessed-vent",
        lambda r: _edit_meeting(r, _VENT, trigger_kind="emergency"),
    ),
    "another-player-describes": (
        "witnessed-vent",
        lambda r: _edit_meeting(r, _VENT, triggered_by="p-1"),
    ),
    "the-turn-is-not-the-opening": (
        "witnessed-vent",
        lambda r: _edit_turn(r, _VENT, _VENT_TURN, turn_kind="opening"),
    ),
    "venting-in-engineering": ("witnessed-vent", _sighting_moved),
    "the-witness-ballot-cites-it": (
        "witnessed-vent",
        lambda r: _edit_ballot(r, _VENT, "p-1", primary_reason_observation_id=None),
    ),
    "four-other-voters-cite-the-turn": (
        "witnessed-vent",
        _one_voter_cites_elsewhere,
    ),
    "role-proof": ("witnessed-vent", _role_proof_recategorised),
    "ejects-p-6": (
        "witnessed-vent",
        lambda r: _edit_meeting(r, _VENT, ejected_player_id="p-5"),
    ),
    "a-supported-use": ("witnessed-vent", lambda r: _role(r, "p-6", "CREWMATE")),
    # The unresolved case, sentence by sentence.
    "a-body-reporter": (
        "weak-evidence",
        lambda r: _edit_meeting(r, _WEAK, trigger_kind="emergency"),
    ),
    "crewmate-p-1": ("weak-evidence", lambda r: _role(r, "p-1", "IMPOSTOR")),
    "four-speakers-accuse": ("weak-evidence", _an_accusation_withdrawn),
    "four-speakers-accuse-p-1": ("weak-evidence", _an_accusation_turned),
    "no-flag-names-anyone": ("weak-evidence", _a_flag_raised),
    "p-1-replies": (
        "weak-evidence",
        lambda r: _edit_turn(r, _WEAK, _WEAK_TURN, turn_kind="opt_in"),
    ),
    "an-account-of-its-route": ("weak-evidence", _the_reply_states_no_route),
    "each-held-nothing": (
        "weak-evidence",
        lambda r: _edit_ballot(r, _WEAK, "p-4", grounding_label="uncited"),
    ),
    "one-votes-for-p-1": (
        "weak-evidence",
        lambda r: _edit_ballot(r, _WEAK, "p-7", target="p-1"),
    ),
    "no-one-is-ejected": (
        "weak-evidence",
        lambda r: _edit_meeting(r, _WEAK, outcome="EJECTED", ejected_player_id="p-1"),
    ),
    "voters-choose-to-skip": (
        "weak-evidence",
        lambda r: _edit_ballot(r, _WEAK, "p-3", rewrite_reasons=("invalid_target",)),
    ),
    # Each conjunct alone, where the sentence families above change two facts.
    "the-sighting-is-p-1s": (
        "witnessed-vent",
        lambda r: _edit_turn(r, _VENT, _VENT_TURN, speaker="p-3"),
    ),
    "role-proof-names-p-6": ("witnessed-vent", _the_flag_names_another),
    "the-ballot-citing-it-is-p-1s": ("witnessed-vent", _another_voter_cites_it),
    "p-1s-ballot-names-p-6": (
        "witnessed-vent",
        lambda r: _edit_ballot(r, _VENT, "p-1", target="p-9"),
    ),
    "reported-by-p-1": (
        "weak-evidence",
        lambda r: _edit_meeting(r, _WEAK, triggered_by="p-3"),
    ),
    "the-reply-is-p-1s": (
        "weak-evidence",
        lambda r: _edit_turn(r, _WEAK, _WEAK_TURN, speaker="p-3"),
    ),
    "after-an-accusation": (
        "weak-evidence",
        lambda r: _edit_turn(r, _WEAK, _WEAK_TURN, turn_index=0),
    ),
    "about-its-own-route": (
        "weak-evidence",
        lambda r: _the_route_is_about(r, "p-3"),
    ),
    "a-route-with-legs": ("weak-evidence", lambda r: _the_route_is_about(r, None)),
    "the-meeting-skips": (
        "weak-evidence",
        lambda r: _edit_meeting(r, _WEAK, outcome="EJECTED"),
    ),
    "nobody-is-named-ejected": (
        "weak-evidence",
        lambda r: _edit_meeting(r, _WEAK, ejected_player_id="p-9"),
    ),
    "five-ballots": ("weak-evidence", _a_sixth_ballot),
    "four-skips": (
        "weak-evidence",
        lambda r: _edit_ballot(r, _WEAK, "p-4", target="p-3"),
    ),
    "exactly-one-vote-for-p-1": (
        "weak-evidence",
        lambda r: _edit_ballot(r, _WEAK, "p-9", target="p-3"),
    ),
}

# Facts the prose does not state, each changed alone: the check must still
# pass, which is what shows a clause reads exactly its sentence.
_CONTROLS: dict[str, tuple[str, Callable[[ReplayView], ReplayView]]] = {
    # "Four OTHER voters": the witness's own ballot citing its own turn too.
    "the-witness-also-cites-its-turn": (
        "witnessed-vent",
        lambda r: _edit_ballot(r, _VENT, "p-1", primary_reason_id=_VENT_TURN),
    ),
    # "replies": after the first accusation, even before the last one.
    "the-reply-between-accusations": (
        "weak-evidence",
        lambda r: _edit_turn(r, _WEAK, _WEAK_TURN, turn_index=2),
    ),
    # "Four speakers accuse the reporter": the reporter naming itself is not one.
    "the-reporter-names-itself": (
        "weak-evidence",
        lambda r: _edit_turn(
            r,
            _WEAK,
            "headless-seed-19:meeting-1:turn-0",
            claims=(
                AccusationClaimView(
                    type="accusation", against="p-1", confidence=0.5, reason=""
                ),
            ),
        ),
    ),
}


def test_both_kept_cases_pass_their_own_prose_check(
    head_loader: ReplayLoader, head_replay: ReplayView
) -> None:
    for case in public._curated_cases():  # noqa: SLF001
        public._check_case(case, head_replay, head_loader)  # noqa: SLF001


@pytest.mark.parametrize("sentence", sorted(_PERTURBATIONS))
def test_a_case_sentence_the_recording_no_longer_shows_withholds_publication(
    head_loader: ReplayLoader, head_replay: ReplayView, sentence: str
) -> None:
    # One planted defect per sentence family of each kept case: the served
    # replay with exactly that fact changed, every other fact as recorded. The
    # unperturbed replay passes the same check (the test above), so each refusal
    # is the perturbation's.
    case_id, perturb = _PERTURBATIONS[sentence]
    with pytest.raises(
        ValueError, match=f"^Curated case no longer describes its source: {case_id}$"
    ):
        public._check_case(_case(case_id), perturb(head_replay), head_loader)  # noqa: SLF001


@pytest.mark.parametrize("fact", sorted(_CONTROLS))
def test_a_case_holds_through_a_fact_its_prose_does_not_state(
    head_loader: ReplayLoader, head_replay: ReplayView, fact: str
) -> None:
    case_id, perturb = _CONTROLS[fact]
    public._check_case(_case(case_id), perturb(head_replay), head_loader)  # noqa: SLF001


def test_the_cited_observation_must_resolve_to_what_the_case_says(
    head_loader: ReplayLoader, head_replay: ReplayView, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The witness's memory projection is a source of the supported case too: its
    # cited reference resolving to another room, or not at all, withholds it.
    original = head_loader.get_meeting_memory
    case = _case("witnessed-vent")

    def moved(game_id: str, meeting_id: str, agent_id: str) -> AgentMemoryView:
        memory = original(game_id, meeting_id, agent_id)
        return memory.model_copy(
            update={
                "observation_references": tuple(
                    r.model_copy(update={"room": "STORAGE"})
                    if r.observation_id == case.observation_id
                    else r
                    for r in memory.observation_references
                )
            }
        )

    for projection in (
        moved,
        lambda *_args: original(*_args).model_copy(
            update={"observation_references": ()}
        ),
    ):
        monkeypatch.setattr(head_loader, "get_meeting_memory", projection)
        with pytest.raises(ValueError, match="witnessed-vent"):
            public._check_case(case, head_replay, head_loader)  # noqa: SLF001
    monkeypatch.setattr(head_loader, "get_meeting_memory", original)
    public._check_case(case, head_replay, head_loader)  # noqa: SLF001


@pytest.mark.parametrize(
    "sentence", ["four-other-voters-cite-the-turn", "four-speakers-accuse"]
)
def test_a_stale_case_refuses_publication_end_to_end(
    monkeypatch: pytest.MonkeyPatch, sentence: str
) -> None:
    # The same refusal through the publication path, once per case: the build
    # raises by name rather than shipping prose about a different game.
    case_id, perturb = _PERTURBATIONS[sentence]
    loader = ReplayLoader(SAMPLES / "9p2i")
    original = loader.load_replay

    def load(requested: str, *, include_llm_bodies: bool = True) -> ReplayView:
        replay = original(requested, include_llm_bodies=include_llm_bodies)
        return perturb(replay) if requested == "headless-seed-19" else replay

    monkeypatch.setattr(loader, "load_replay", load)
    with pytest.raises(
        ValueError, match=f"^Curated case no longer describes its source: {case_id}$"
    ):
        public.build_public_results(loader)


@pytest.fixture
def summary_recording(completed_recording: Path, tmp_path: Path) -> Path:
    destination = tmp_path / completed_recording.name
    shutil.copyfile(completed_recording, destination)
    roster = completed_recording.parent / "roster.json"
    if roster.exists():
        shutil.copyfile(roster, tmp_path / roster.name)
    return destination


def test_public_summary_reuses_walks_and_clear_cache_revalidates() -> None:
    # The real set exceeds the loader's sixteen-entry playback cache.
    loader = ReplayLoader(SAMPLES / "9p2i")
    with patch.object(loader, "_walk", wraps=loader._walk) as walk:
        first = public.build_public_results(loader)
        initial_walks = walk.call_count
        assert initial_walks > 0
        assert public.build_public_results(loader) == first
        assert walk.call_count == initial_walks
        loader.clear_cache()
        assert public.build_public_results(loader) == first
        assert walk.call_count > initial_walks


def test_warm_summary_refuses_same_mtime_corruption_and_recovers(
    summary_recording: Path,
) -> None:
    completed_recording = summary_recording
    loader = ReplayLoader(completed_recording.parent)
    first = public.build_public_results(loader)
    original = completed_recording.read_bytes()
    stamp = completed_recording.stat()
    rows = [json.loads(line) for line in original.splitlines()]
    rows[-1]["winner"] = (
        "IMPOSTORS" if rows[-1]["winner"] == "CREWMATES" else "CREWMATES"
    )
    completed_recording.write_text("\n".join(json.dumps(row) for row in rows) + "\n")
    os.utime(completed_recording, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
    with pytest.raises(ValueError, match="invalid or unverified"):
        public.build_public_results(loader)
    completed_recording.write_bytes(original)
    os.utime(completed_recording, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
    assert public.build_public_results(loader) == first


def test_a_peer_walk_landing_during_a_clear_cannot_install_pre_flip_bytes(
    summary_recording: Path,
) -> None:
    """CONC-6: the controlled interleaving that produced a silent stale install.

    A same-mtime replacement is invisible to the mtime-keyed caches, so the
    builder clears them on a fingerprint miss. Clearing does not cancel walks
    another thread already started: their PRE-flip results land in the freshly
    cleared caches, and the builder then reads them back while its own
    fingerprint is already the POST-flip one -- publishing a summary derived
    from bytes the fingerprint does not cover.

    Two peers are held mid-walk, one per cache the builder reads, so both land
    after the clear and before the builder looks. The replacement makes the
    recording invalid, so consuming those stale walks publishes an outcome the
    bytes no longer support, while reading the disk refuses.
    """

    loader = ReplayLoader(summary_recording.parent)
    original = summary_recording.read_bytes()
    stamp = summary_recording.stat()
    rows = [json.loads(line) for line in original.splitlines()]
    assert rows[-1]["winner"] == "CREWMATES"
    rows[-1]["winner"] = "IMPOSTORS"
    flipped = "\n".join(json.dumps(row) for row in rows) + "\n"

    parsed = threading.Barrier(3, timeout=30)
    caches_cleared = threading.Event()
    landed = threading.Barrier(3, timeout=30)
    walk = loader._walk
    peer_names = ("peer-metadata", "peer-replay")

    def held_walk(*args: Any, **kwargs: Any) -> Any:
        """Hold a peer's parsed result until the builder has cleared."""

        result = walk(*args, **kwargs)
        if threading.current_thread().name in peer_names:
            parsed.wait()
            assert caches_cleared.wait(timeout=30)
        return result

    def read_metadata() -> None:
        loader.list_replays()
        landed.wait()

    def read_replay() -> None:
        loader.load_replay("headless-seed-1")
        landed.wait()

    def release_peers_on_clear() -> None:
        clear_cache()
        caches_cleared.set()
        landed.wait()

    clear_cache = loader.clear_cache
    threads = [
        threading.Thread(target=read_metadata, name=peer_names[0]),
        threading.Thread(target=read_replay, name=peer_names[1]),
    ]
    with patch.object(loader, "_walk", held_walk):
        for thread in threads:
            thread.start()
        try:
            # Both peers have parsed the pre-flip bytes and are holding them.
            parsed.wait()
            summary_recording.write_text(flipped)
            os.utime(summary_recording, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
            with patch.object(loader, "clear_cache", release_peers_on_clear):
                with pytest.raises(ValueError, match="invalid or unverified"):
                    public.build_public_results(loader)
        finally:
            caches_cleared.set()
            parsed.abort()
            landed.abort()
            for thread in threads:
                thread.join(timeout=30)
    assert loader._public_results_cache is None
    summary_recording.write_bytes(original)
    os.utime(summary_recording, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
    assert public.build_public_results(loader).games == 1


def test_warm_summary_refuses_after_a_negative_seed_recording_appears(
    summary_recording: Path,
) -> None:
    """A recording the loader would serve cannot stay invisible to the cache key."""

    loader = ReplayLoader(summary_recording.parent)
    first = public.build_public_results(loader)
    appeared = summary_recording.parent / "replay-seed--1.jsonl"
    appeared.write_bytes(b"not a recording\n")
    with pytest.raises(ValueError, match="invalid or unverified"):
        public.build_public_results(loader)
    with pytest.raises(ValueError, match="invalid or unverified"):
        public.build_public_results(ReplayLoader(summary_recording.parent))
    appeared.unlink()
    assert public.build_public_results(loader) == first


def test_warm_summary_refreshes_manifest_provenance(summary_recording: Path) -> None:
    completed_recording = summary_recording
    loader = ReplayLoader(completed_recording.parent)
    first = public.build_public_results(loader)
    manifest = completed_recording.parent / "MANIFEST.md"
    seed = int(completed_recording.stem.removeprefix("replay-seed-"))
    manifest.write_text(
        f"| seed | refreshed_at |\n| --- | --- |\n| {seed} | 2026-09-06 |\n"
    )
    refreshed = public.build_public_results(loader)
    assert refreshed.source_fingerprint != first.source_fingerprint
    assert refreshed.recorded_from == refreshed.recorded_until == "2026-09-06"
    assert refreshed.games == first.games


def test_warm_summary_rechecks_ambient_substrate(
    summary_recording: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    loader = ReplayLoader(summary_recording.parent)
    public.build_public_results(loader)
    monkeypatch.setenv("AILIBI_TEMPORAL_OBSERVATIONS", "1")
    with pytest.raises(ValueError, match="invalid or unverified"):
        public.build_public_results(loader)


def test_warm_summary_rechecks_same_mtime_roster(summary_recording: Path) -> None:
    roster = summary_recording.parent / "roster.json"
    roster.write_text(
        json.dumps({"num_players": 7, "num_impostors": 1, "tasks_per_crewmate": 1})
    )
    loader = ReplayLoader(summary_recording.parent)
    public.build_public_results(loader)
    stamp = roster.stat()
    roster.write_text(
        json.dumps({"num_players": 7, "num_impostors": 2, "tasks_per_crewmate": 1})
    )
    os.utime(roster, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
    with pytest.raises(ValueError, match="invalid or unverified"):
        public.build_public_results(loader)


@pytest.mark.parametrize("changed", ["source", "substrate"])
def test_generation_drift_is_refused_and_not_cached(
    summary_recording: Path, monkeypatch: pytest.MonkeyPatch, changed: str
) -> None:
    loader = ReplayLoader(summary_recording.parent)
    original = loader.load_replay
    altered = False

    def load(game_id: str, *, include_llm_bodies: bool = True) -> ReplayView:
        nonlocal altered
        result = original(game_id, include_llm_bodies=include_llm_bodies)
        if not altered:
            altered = True
            if changed == "source":
                with summary_recording.open("ab") as stream:
                    stream.write(b"\n")
            else:
                monkeypatch.setenv("AILIBI_TEMPORAL_OBSERVATIONS", "1")
        return result

    monkeypatch.setattr(loader, "load_replay", load)
    with pytest.raises(ValueError, match="changed during public-results"):
        public.build_public_results(loader)
    assert loader._public_results_cache is None


def test_public_results_cache_is_scoped_to_its_loader(summary_recording: Path) -> None:
    first_loader = ReplayLoader(summary_recording.parent)
    first = public.build_public_results(first_loader)
    second_loader = ReplayLoader(summary_recording.parent)
    with patch.object(second_loader, "_walk", wraps=second_loader._walk) as walk:
        assert public.build_public_results(second_loader) == first
        assert walk.call_count > 0


def test_public_summary_keeps_actual_candidate_identity(tmp_path: Path) -> None:
    from experiments.deduction_scenarios import run_case
    from orchestrator.experiment_config import RecordedExperimentConfig

    config = RecordedExperimentConfig(
        format_version=2,
        evidence_reasoning_version=2,
        public_account_version=1,
        attributed_testimony_version=1,
    )
    run_case(tmp_path, case="honest", experiment_config=config)
    (tmp_path / "roster.json").write_text(
        json.dumps({"num_players": 4, "num_impostors": 1, "tasks_per_crewmate": 1})
    )
    result = public.build_public_results(ReplayLoader(tmp_path))
    assert result.provenance_groups is not None
    assert len(result.provenance_groups) == 1
    identity = result.provenance_groups[0]
    assert identity.agent_factory_kind == "custom"
    assert identity.experiment_config is not None
    assert identity.experiment_config.public_account_version == 1
    assert identity.experiment_config.attributed_testimony_version == 1
    assert identity.tactical_policy is None
    # The clock the recording ran under, so a v1 and a v2 arm cannot pool.
    assert identity.temporal_observation_version == 2
    assert identity.game_ids == ("headless-seed-1",)


def test_historical_summary_never_invents_a_default_factory(
    canonical_summary: PublicResultsView, tmp_path: Path
) -> None:
    # The committed set records its factory (the experimental factory its era's
    # declared config ran, since 2026-10-02; scripted on the baseline-9 bytes),
    # and the summary reports exactly that recorded identity with the config
    # beside it; it still predates the clock stamp, and reading it does not
    # relabel it as v1.
    assert canonical_summary.provenance_groups
    assert all(
        group.agent_factory_kind == "experimental"
        and group.experiment_config is not None
        and group.experiment_config.kill_cooldown_ticks == 6
        and group.temporal_observation_version is None
        for group in canonical_summary.provenance_groups
    )
    assert (
        sum(len(group.game_ids) for group in canonical_summary.provenance_groups)
        == canonical_summary.games
    )

    # The historical shape is a committed recording with its factory stamp
    # removed: absent is unknown, and reading it must not invent the default.
    destination = tmp_path / "9p2i"
    destination.mkdir()
    shutil.copyfile(SAMPLES / "9p2i/roster.json", destination / "roster.json")
    source = SAMPLES / "9p2i/replay-seed-0.jsonl"
    rows = [json.loads(line) for line in source.read_text().splitlines() if line]
    assert any("agent_factory_kind" in row for row in rows)
    for row in rows:
        row.pop("agent_factory_kind", None)
    (destination / source.name).write_text(
        "\n".join(
            json.dumps(row, sort_keys=True, separators=(",", ":")) for row in rows
        )
        + "\n"
    )
    historical = public.build_public_results(ReplayLoader(destination))
    assert historical.provenance_groups
    assert all(
        group.agent_factory_kind is None and group.temporal_observation_version is None
        for group in historical.provenance_groups
    )
    assert (
        sum(len(group.game_ids) for group in historical.provenance_groups)
        == historical.games
        == 1
    )
