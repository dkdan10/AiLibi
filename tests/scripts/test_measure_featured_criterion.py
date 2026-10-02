"""The featured-criterion instrument, over the committed bytes it reads.

``scripts/measure_featured_criterion.py`` prints the counts the spectator's
featured order rests on. Two of its claims are load-bearing enough to pin here:

* ``alternatives_shape`` — the spectator's ballot card ANNOTATES a recorded
  alternative that duplicates the card's own header (the voter itself, or the
  target the vote applied to). That render is a statement about the recordings,
  so the committed games that carry each shape are named here rather than left
  to a reviewer's trust — and where no committed game carries one, that is
  said here too;
* ``_parse_games`` — a malformed selector raises instead of quietly measuring
  fewer games than the caller asked for, which would print a number nobody
  could reproduce;
* ``--list`` — the seeds the strip draws its cards from are printed, not
  asserted: the eligible openers, the non-vent openers and the first meetings
  that eject a crewmate who did not open them. Each list is pinned on the
  promoted bytes, and each predicate is perturbed on a served replay so that a
  moved vent, a flipped role or a planted flag visibly moves a game off it.

The ejection bands themselves are pinned on the other side of the fence, in
``tests/api/test_sets.py``, which re-implements the predicate deliberately.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any

import pytest

from api.replay_loader import SetLoaderRegistry
from api.schemas import ContradictionView, ReplayView

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PARENT = _REPO_ROOT / "replays" / "samples"

# `scripts/` is not a package; import the module the way the other script tests
# in this directory do.
_SCRIPTS = _REPO_ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
_criterion: Any = importlib.import_module("measure_featured_criterion")


@pytest.mark.parametrize(
    "seed,shape,why",
    [
        # (ballots, recorded entries, ballots naming the voter, naming the target)
        (2, (7, 10, 2, 0), "two voters list THEMSELVES in the only meeting"),
        (13, (13, 22, 1, 0), "one voter lists itself; none lists its own target"),
        (3, (19, 26, 1, 0), "the tour's landing game: one voter lists itself"),
        (23, (12, 24, 0, 0), "the old landing game carries neither shape"),
    ],
)
def test_alternatives_shape_reads_the_committed_duplicates(
    seed: int, shape: tuple[int, int, int, int], why: str
) -> None:
    # The annotation in `frontend/src/components/BallotCard.tsx` exists because
    # these bytes exist. Seed 2 is the case in the flesh: a voter records ITSELF
    # among the players it weighed, which without a note renders as a second
    # identical pill beside the one in the ballot's header.
    #
    # The TARGET shape is recorded by no committed ballot — 0 of the promoted
    # 9p2i set's 691 ballots (candidate round 2, since 2026-10-02) and 0 in each
    # of the three baseline-9 sets
    # (`scripts/measure_featured_criterion.py --alternatives`, and the same count
    # over `--parent replays/ml_corpus`) — so no game here can name it, and the
    # "(the vote cast)" note is proved only by its constructed case in
    # `frontend/src/components/PrivateReasoning.test.tsx`.
    # (Was 2: (7, 9, 1, 0); 13: (7, 10, 1, 0); 23: (26, 29, 0, 0) on the
    # baseline-9 bytes, and 2: (7, 13, 2, 0); 13: (18, 35, 1, 2);
    # 23: (26, 36, 0, 0) on baseline 8.)
    replay = SetLoaderRegistry(_PARENT).get("9p2i").load_replay(f"headless-seed-{seed}")
    assert _criterion.alternatives_shape(replay) == shape


def test_parse_games_rejects_a_malformed_selector() -> None:
    assert _criterion._parse_games(["9p2i:23", "9p2i:13", "4p1i:2"]) == {
        "9p2i": frozenset({23, 13}),
        "4p1i": frozenset({2}),
    }
    for bad in ("9p2i", "9p2i:", ":23", "9p2i:head", ""):
        with pytest.raises(ValueError):
            _criterion._parse_games([bad])


# ── --list: the candidates, named ────────────────────────────────────────────

_NINE = SetLoaderRegistry(_PARENT).get("9p2i")


def _replay(seed: int) -> ReplayView:
    return _NINE.load_replay(f"headless-seed-{seed}")


def test_the_list_names_the_candidates_on_the_promoted_bytes(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # The seeds the strip is drawn from, re-measured on the set the spectator
    # serves since 2026-10-02. The head is one of the eligible openers, the
    # second 9p2i card one of the non-vent openers; the third list is what a
    # card about a crewmate ejected on believable evidence would come from.
    assert _criterion.main(["--set", "9p2i", "--list"]) == 0
    lines = capsys.readouterr().out.splitlines()
    for expected in (
        "    role_proof flag   24 ejections  24 role-correct",
        "    other flag         2 ejections   0 role-correct",
        "    no flag           40 ejections  20 role-correct",
        "  first meeting ejects on a role_proof flag: 11 of 50 games",
        "  the games behind each count (seed:meeting)",
        "  first meeting ejects on a role_proof flag: seeds "
        "[3, 5, 6, 7, 10, 11, 19, 20, 27, 42, 49]",
        "  first meeting ejects an impostor, no flag anywhere and no vent at or "
        "before it: seeds [14, 44]",
        "  first meeting ejects a crewmate who did not open it: seeds "
        "[2, 12, 13, 22, 25]",
        "    other flag ejections: 2:0 8:1",
        "    other flag role-correct: none",
    ):
        assert expected in lines, expected
    # The games behind the band counts: one seed:meeting per ejection, so the
    # listed tokens count to the printed number.
    by_label = {
        line.split(":", 1)[0].strip(): line.split(":", 1)[1].split()
        for line in lines
        if line.startswith("    ") and ("ejections:" in line or "role-correct:" in line)
    }
    assert len(by_label["role_proof flag ejections"]) == 24
    assert (
        by_label["role_proof flag role-correct"]
        == by_label["role_proof flag ejections"]
    )
    assert len(by_label["no flag ejections"]) == 40
    assert len(by_label["no flag role-correct"]) == 20
    assert "19:0" in by_label["role_proof flag ejections"]
    assert "14:0" in by_label["no flag role-correct"]
    # Without --list the counts print alone.
    assert _criterion.main(["--set", "9p2i"]) == 0
    plain = capsys.readouterr().out
    assert "seeds [14, 44]" not in plain
    assert "(seed:meeting)" not in plain


def test_the_list_flag_is_documented(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        _criterion.main(["--help"])
    usage = " ".join(capsys.readouterr().out.split())  # argparse wraps its lines
    assert "[--alternatives] [--list]" in usage
    assert "also name the games behind each count and the two candidate lists" in usage
    assert "the featured strip's five" in usage


def test_the_list_follows_a_game_selection_and_the_other_set(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # --games with --list names only the selected games: the strip's two 9p2i
    # cards land on one list each. The 4p1i set, whose games end in one meeting
    # or none, has nobody on either new list (a game with no meeting is on no
    # list, rather than an error).
    assert _criterion.main(["--games", "9p2i:19", "9p2i:14", "--list"]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert "  first meeting ejects on a role_proof flag: seeds [19]" in lines
    assert (
        "  first meeting ejects an impostor, no flag anywhere and no vent at or "
        "before it: seeds [14]"
    ) in lines
    assert "  first meeting ejects a crewmate who did not open it: seeds []" in lines
    assert _criterion.main(["--set", "4p1i", "--list"]) == 0
    four = capsys.readouterr().out.splitlines()
    assert (
        "  first meeting ejects an impostor, no flag anywhere and no vent at or "
        "before it: seeds []"
    ) in four
    assert "  first meeting ejects a crewmate who did not open it: seeds []" in four
    assert "    other flag ejections: none" in four


def _with_vent_at(replay: ReplayView, tick: int) -> ReplayView:
    """The served replay with its first vent event moved onto ``tick``'s frame."""

    event = next(e for frame in replay.ticks for e in frame.events if e.type == "vent")
    moved = event.model_copy(update={"tick": tick})
    frames = tuple(
        frame.model_copy(
            update={
                "events": tuple(e for e in frame.events if e is not event)
                + ((moved,) if frame.tick == tick else ())
            }
        )
        for frame in replay.ticks
    )
    return replay.model_copy(update={"ticks": frames})


def _with_role(replay: ReplayView, agent_id: str, role: str) -> ReplayView:
    players = tuple(
        p.model_copy(update={"role": role}) if p.agent_id == agent_id else p
        for p in replay.players
    )
    return replay.model_copy(update={"players": players})


def test_a_vent_moved_to_or_before_the_first_meeting_leaves_the_non_vent_list() -> None:
    # Seed 44's only vent trip starts at tick 20, ten ticks after its one
    # meeting, so the game is on the list. Moved onto the meeting's own tick, or
    # before it, the same event takes it off; moved to the tick after, it stays.
    replay = _replay(44)
    opened = replay.meetings[0].tick
    assert opened == 10
    assert _criterion.opens_on_non_vent_impostor_ejection(replay)
    for tick in (opened, opened - 1, 0):
        assert not _criterion.opens_on_non_vent_impostor_ejection(
            _with_vent_at(replay, tick)
        ), tick
    assert _criterion.opens_on_non_vent_impostor_ejection(
        _with_vent_at(replay, opened + 1)
    )


def test_a_flipped_role_or_a_planted_flag_leaves_the_non_vent_list() -> None:
    # Seed 14 records no vent event at all. Its ejected player read as a
    # crewmate leaves the non-vent list and joins the crewmate list (the opener
    # is someone else); one flag anywhere leaves it too.
    replay = _replay(14)
    first = replay.meetings[0]
    ejected = first.ejected_player_id
    assert ejected == "p-1" and first.triggered_by == "p-3"
    assert _criterion.opens_on_non_vent_impostor_ejection(replay)
    assert not _criterion.first_meeting_ejects_a_crewmate_not_the_opener(replay)

    flipped = _with_role(replay, ejected, "CREWMATE")
    assert not _criterion.opens_on_non_vent_impostor_ejection(flipped)
    assert _criterion.first_meeting_ejects_a_crewmate_not_the_opener(flipped)

    flag = _replay(2).meetings[0].contradictions[0]
    assert isinstance(flag, ContradictionView)
    flagged = replay.model_copy(
        update={"meetings": (first.model_copy(update={"contradictions": (flag,)}),)}
    )
    assert not _criterion.opens_on_non_vent_impostor_ejection(flagged)


def test_the_crewmate_list_reads_the_role_and_the_opener() -> None:
    # Seed 2's first meeting, which p-1 opened, ejects crewmate p-5. Read as an
    # impostor, or as the opener, p-5 leaves the list.
    replay = _replay(2)
    first = replay.meetings[0]
    assert (first.triggered_by, first.ejected_player_id) == ("p-1", "p-5")
    assert _criterion.first_meeting_ejects_a_crewmate_not_the_opener(replay)
    assert not _criterion.first_meeting_ejects_a_crewmate_not_the_opener(
        _with_role(replay, "p-5", "IMPOSTOR")
    )
    opened_by_ejected = replay.model_copy(
        update={"meetings": (first.model_copy(update={"triggered_by": "p-5"}),)}
    )
    assert not _criterion.first_meeting_ejects_a_crewmate_not_the_opener(
        opened_by_ejected
    )
    # A game whose first meeting skips is on neither list.
    skipped = _replay(0)
    assert skipped.meetings[0].ejected_player_id is None
    assert not _criterion.first_meeting_ejects_a_crewmate_not_the_opener(skipped)
    assert not _criterion.opens_on_non_vent_impostor_ejection(skipped)
