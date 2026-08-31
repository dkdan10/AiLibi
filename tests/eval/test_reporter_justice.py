"""The reporter-justice instrument, pinned over the corpus at THIS head.

Every number below is a fresh walk over the four committed sets -- the bytes the
baseline-8 combined re-record wrote -- and NOT a copy of the Wave-0 register's
figures, which were measured on the sets that record replaced. Where the two are
comparable the register's cell is named beside the pin as a REFERENCE, so a
reader can see which way the class moved without either number pretending to be
the other.

Three independent cross-checks make the walk more than self-consistent: the
pooled ejection ledger reproduces the record's own published 429 total and 46
innocent (audits/audit-phase-21-rerecord.md §5.1) without reading that document,
and the reporter role census reproduces the premise the whole class rests on --
the reporter is a crewmate in every body-report meeting, so exculpating them
launders nobody.

Every cell ships with a planted perturbation proving it bites: the fold is
re-run over a doctored copy of one committed game and the cell is asserted to
MOVE, so a pin that agreed with any corpus would fail here.
"""

from __future__ import annotations

import json
import math
import shutil
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from eval.validity import resolve_roster_knobs, roles_by_seed

from eval.reporter_justice import (
    EXCULPATORY_HINGE_TERMS,
    ReporterJusticeCells,
    ReporterJusticeError,
    compute_reporter_justice,
    pool_reporter_justice,
    render_reporter_justice,
)

_Rows = list[dict[str, object]]
_Mutate = Callable[[_Rows], _Rows]

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SETS: tuple[Path, ...] = (
    _REPO_ROOT / "replays" / "samples" / "9p2i",
    _REPO_ROOT / "replays" / "samples" / "4p1i",
    _REPO_ROOT / "replays" / "ml_corpus" / "9p2i",
    _REPO_ROOT / "replays" / "ml_corpus" / "4p1i",
)


@pytest.fixture(scope="module")
def pooled() -> ReporterJusticeCells:
    return pool_reporter_justice(compute_reporter_justice(path) for path in _SETS)


class TestCorpusShape:
    def test_the_meeting_census(self, pooled: ReporterJusticeCells) -> None:
        # baseline-7 REFERENCE: 618 body report + 50 emergency over 668.
        assert pooled.games == 300
        assert pooled.meetings == 672
        assert pooled.body_report_meetings == 620
        assert pooled.emergency_meetings == 52
        assert (
            pooled.body_report_meetings + pooled.emergency_meetings == pooled.meetings
        )

    def test_the_reporter_is_a_crewmate_in_every_body_report(
        self, pooled: ReporterJusticeCells
    ) -> None:
        # The premise the whole class rests on, re-derived rather than assumed:
        # an impostor that reported its own kill would turn the exculpation into
        # a laundering channel. baseline-7 REFERENCE: 618/618 CREWMATE.
        assert pooled.reporter_impostor_meetings == 0
        assert pooled.reporter_crewmate_meetings == pooled.body_report_meetings == 620

    def test_the_ejection_ledger_reproduces_the_records_published_totals(
        self, pooled: ReporterJusticeCells
    ) -> None:
        # An independent arrival at the two cells the baseline-8 record published
        # (audits/audit-phase-21-rerecord.md §5.1): 429 ejections of which 46 are
        # innocent. Read off the recorded bytes here, never off that document.
        assert pooled.ejections == 429
        assert pooled.innocent_ejections == 46
        assert pooled.impostor_ejections == 383
        assert pooled.ejections == pooled.innocent_ejections + pooled.impostor_ejections


class TestReporterExposure:
    def test_the_reporters_share_of_the_innocent_ejections(
        self, pooled: ReporterJusticeCells
    ) -> None:
        # The cell the record did NOT re-derive, and the reason this module
        # exists. baseline-7 REFERENCE: 30 of 42 = 71.4%.
        assert pooled.reporter_ejections == 34
        assert pooled.reporter_share_of_innocent_ejections == pytest.approx(
            34 / 46, abs=1e-9
        )

    def test_the_per_slot_rates_and_the_relative_risk(
        self, pooled: ReporterJusticeCells
    ) -> None:
        # baseline-7 REFERENCE: reporter 30/618 = 4.85%, innocent non-reporter
        # 12/1844 = 0.65%, relative risk 7.46x.
        assert (pooled.reporter_ejections, pooled.reporter_slots) == (34, 620)
        assert (
            pooled.innocent_non_reporter_ejections,
            pooled.innocent_non_reporter_slots,
        ) == (12, 1859)
        assert (pooled.impostor_slot_ejections, pooled.impostor_slots) == (331, 856)
        assert pooled.reporter_ejection_rate == pytest.approx(34 / 620, abs=1e-9)
        assert pooled.innocent_non_reporter_ejection_rate == pytest.approx(
            12 / 1859, abs=1e-9
        )
        assert pooled.reporter_relative_risk == pytest.approx(
            (34 / 620) / (12 / 1859), abs=1e-9
        )
        assert pooled.reporter_relative_risk == pytest.approx(8.495, abs=5e-3)

    def test_an_undefined_relative_risk_is_never_reported_as_zero(self) -> None:
        # replays/samples/4p1i ejects 4 reporters and 0 innocent non-reporters.
        # A ratio over a zero baseline is UNBOUNDED, not zero, and printing 0.00x
        # would reverse the reading of the one shape this class is about.
        cells = compute_reporter_justice(_SETS[1])
        assert cells.reporter_ejections == 4
        assert cells.innocent_non_reporter_ejections == 0
        assert math.isinf(cells.reporter_relative_risk)
        assert "unbounded" in render_reporter_justice(cells)
        assert "0.00x" not in render_reporter_justice(cells)

    def test_no_innocent_ejection_of_either_kind_reads_as_undefined(self) -> None:
        # replays/ml_corpus/4p1i ejects no innocent at all: there is no evidence
        # either way, which is a third state and not a zero.
        cells = compute_reporter_justice(_SETS[3])
        assert cells.reporter_ejections == 0
        assert cells.innocent_non_reporter_ejections == 0
        assert math.isnan(cells.reporter_relative_risk)
        assert "undefined" in render_reporter_justice(cells)

    def test_the_slot_classes_partition_the_living_roster(
        self, pooled: ReporterJusticeCells
    ) -> None:
        # Every living participant of a body-report meeting is exactly one of
        # reporter / innocent non-reporter / impostor, so the slot total is the
        # ballot total. A double-counted seat would deflate every rate above.
        assert (
            pooled.reporter_slots
            + pooled.innocent_non_reporter_slots
            + pooled.impostor_slots
            == pooled.crew_ballots + pooled.impostor_ballots
        )


class TestAimAtTheReporter:
    def test_speech_shares(self, pooled: ReporterJusticeCells) -> None:
        # baseline-7 REFERENCE: impostor 521/737 = 70.7%, crew 540/1513 = 35.7%.
        # The impostor half is flat; the crew half fell well outside its interval.
        assert (
            pooled.impostor_accusations_at_reporter,
            pooled.impostor_accusations,
        ) == (520, 739)
        assert (pooled.crew_accusations_at_reporter, pooled.crew_accusations) == (
            521,
            2129,
        )
        assert pooled.impostor_accusation_at_reporter_share == pytest.approx(
            520 / 739, abs=1e-9
        )
        assert pooled.crew_accusation_at_reporter_share == pytest.approx(
            521 / 2129, abs=1e-9
        )

    def test_ballot_shares(self, pooled: ReporterJusticeCells) -> None:
        # The follow-through half: what the table SAYS about the reporter and
        # what it VOTES are different numbers, and only the second convicts.
        assert (pooled.crew_ballots_at_reporter, pooled.crew_ballots) == (160, 2479)
        assert (pooled.impostor_ballots_at_reporter, pooled.impostor_ballots) == (
            103,
            856,
        )
        assert pooled.crew_ballot_at_reporter_share == pytest.approx(
            160 / 2479, abs=1e-9
        )
        assert pooled.impostor_ballot_at_reporter_share == pytest.approx(
            103 / 856, abs=1e-9
        )


class TestInvocation:
    def test_the_exculpation_is_rendered_far_more_often_than_it_is_used(
        self, pooled: ReporterJusticeCells
    ) -> None:
        # Every one of the 3,335 body-report ballots CARRIES the exculpation.
        # baseline-7 REFERENCE (a different, implicit hinge list -- NOT
        # like-for-like): 113/3312 = 3.41% mentioning, 28 = 0.85% with a hinge,
        # 8 = 0.24% speech turns and 0 by the reporter.
        assert pooled.ballot_rationales == 3335
        assert pooled.ballot_rationales_mentioning_report == 82
        assert pooled.ballot_rationales_with_hinge == 13
        assert pooled.speech_turns == 3335
        assert pooled.speech_turns_mentioning_report == 309
        assert pooled.speech_turns_with_hinge == 5
        assert pooled.speech_turns_with_hinge_by_reporter == 1

    def test_the_hinge_list_is_stated_data_and_a_hinge_is_a_ceiling(self) -> None:
        # The register's own filing was off fourfold because its hinge list was
        # implicit. This one is a module constant, so the count is reproducible,
        # and every hinge is lowercase because the match lowercases its input.
        assert EXCULPATORY_HINGE_TERMS
        assert all(term == term.lower() for term in EXCULPATORY_HINGE_TERMS)
        assert len(set(EXCULPATORY_HINGE_TERMS)) == len(EXCULPATORY_HINGE_TERMS)

    def test_a_hinge_is_only_counted_alongside_a_report_mention(
        self, pooled: ReporterJusticeCells
    ) -> None:
        # The co-mention is the link that makes a generic exculpatory phrase a
        # probable base-rate invocation, so the hinge count can never exceed the
        # mention count.
        assert (
            pooled.ballot_rationales_with_hinge
            <= pooled.ballot_rationales_mentioning_report
        )
        assert pooled.speech_turns_with_hinge <= pooled.speech_turns_mentioning_report


class TestCoDiscovery:
    def test_the_split_by_role(self, pooled: ReporterJusticeCells) -> None:
        # The measurement that REJECTED the filed fix. baseline-7 REFERENCE:
        # 121/618 meetings, 89 CREWMATE / 51 IMPOSTOR = 36.4% impostor. The
        # meeting count sits inside its interval; the impostor SHARE is well
        # above it, so exculpatory framing over the discoverer set would defend
        # an impostor in nearly half the meetings it fired in and the rejection
        # holds a fortiori.
        #
        # A co-discoverer is matched on THIS meeting's corpse, not on any corpse
        # near the trigger tick: the tick-only predicate counted a speaker who
        # found a different body a tick earlier and inflated this class by
        # roughly a third (173 meetings / 223 slots).
        assert pooled.meetings_with_co_discoverer == 118
        assert pooled.co_discoverer_slots_crewmate == 74
        assert pooled.co_discoverer_slots_impostor == 71
        assert pooled.co_discoverer_slots == 145
        assert pooled.co_discoverer_impostor_share == pytest.approx(71 / 145, abs=1e-9)
        assert pooled.co_discoverer_impostor_share > 0.45


class TestPerSetShape:
    def test_each_set_reports_its_own_name_and_games(self) -> None:
        rows = {
            path: compute_reporter_justice(path)
            for path in (_SETS[0], _SETS[1], _SETS[3])
        }
        assert [cells.games for cells in rows.values()] == [50, 50, 50]
        assert {cells.set_name for cells in rows.values()} == {"9p2i", "4p1i"}

    def test_the_render_names_every_headline_cell(
        self, pooled: ReporterJusticeCells
    ) -> None:
        text = render_reporter_justice(pooled)
        for fragment in (
            "body report 620",
            "34 reporter (73.9% of innocent)",
            "34/620",
            "12/1859",
            "71 IMPOSTOR",
        ):
            assert fragment in text, fragment

    def test_pooling_an_empty_input_fails_loud(self) -> None:
        with pytest.raises(ReporterJusticeError, match="no sets to pool"):
            pool_reporter_justice([])

    def test_a_directory_with_no_replays_fails_loud(self, tmp_path: Path) -> None:
        with pytest.raises(ReporterJusticeError, match="no replay-seed"):
            compute_reporter_justice(tmp_path)


# --------------------------------------------------------------------------- #
# The perturbations: every cell above is asserted to MOVE on doctored bytes    #
# --------------------------------------------------------------------------- #


def _first_replay_with_a_meeting(source: Path) -> tuple[Path, _Rows]:
    """The set's first committed game that actually resolved a meeting.

    A game whose crew finished its tasks without a meeting exercises no cell, so
    a perturbation planted in one would prove nothing.
    """

    for replay in sorted(source.glob("replay-seed-*.jsonl")):
        rows = [json.loads(line) for line in replay.read_text().splitlines() if line]
        if any(row.get("kind") == "meeting" for row in rows):
            return replay, rows
    raise AssertionError(f"{source}: no committed game carries a meeting")


def _doctored_set(tmp_path: Path, *, mutate: _Mutate) -> Path:
    """A one-game copy of the 4p1i sample set with ``mutate`` applied to its rows.

    Small on purpose: one seed is enough to prove a cell bites, and the fold is
    identical whatever the set's size.
    """

    source = _SETS[1]
    target = tmp_path / "doctored"
    target.mkdir(parents=True)
    for name in ("roster.json",):
        candidate = source / name
        if candidate.exists():
            shutil.copy(candidate, target / name)
    replay, rows = _first_replay_with_a_meeting(source)
    mutated = mutate(rows)
    (target / replay.name).write_text(
        "".join(json.dumps(row) + "\n" for row in mutated)
    )
    return target


def _items(row: dict[str, object], key: str) -> list[Any]:
    """A recorded row's list-valued field, or [] -- the JSONL is untyped here."""

    value = row.get(key)
    return value if isinstance(value, list) else []


def _baseline(tmp_path: Path) -> ReporterJusticeCells:
    return compute_reporter_justice(_doctored_set(tmp_path, mutate=lambda rows: rows))


def test_the_meeting_kind_cell_bites(tmp_path: Path) -> None:
    # Rewrite the applied report action into an emergency one and the meeting
    # re-bins, which moves every reporter cell that depends on the split.
    def mutate(rows: _Rows) -> _Rows:
        for row in rows:
            for action in _items(row, "actions"):
                if isinstance(action, dict) and action.get("type") == "report":
                    action["type"] = "emergency"
                    action["payload"] = {"reason": "planted"}
        return rows

    base = _baseline(tmp_path / "base")
    doctored = compute_reporter_justice(_doctored_set(tmp_path / "flip", mutate=mutate))
    assert base.body_report_meetings > 0
    assert doctored.body_report_meetings < base.body_report_meetings
    assert doctored.emergency_meetings > base.emergency_meetings


def test_an_unexplained_meeting_fails_loud(tmp_path: Path) -> None:
    # Drop the trigger action entirely: the meeting kind is then unreadable from
    # the recorded bytes, and a half-read measurement must raise rather than bin
    # the meeting as "other".
    def mutate(rows: _Rows) -> _Rows:
        for row in rows:
            actions = row.get("actions")
            if not isinstance(actions, list):
                continue
            keep = [
                index
                for index, action in enumerate(actions)
                if not (
                    isinstance(action, dict)
                    and action.get("type") in ("report", "emergency")
                )
            ]
            dispositions = row.get("action_dispositions")
            row["actions"] = [actions[index] for index in keep]
            if isinstance(dispositions, list):
                row["action_dispositions"] = [dispositions[index] for index in keep]
        return rows

    with pytest.raises(ReporterJusticeError, match="no applied report or emergency"):
        compute_reporter_justice(_doctored_set(tmp_path, mutate=mutate))


def test_the_ejection_and_share_cells_bite(tmp_path: Path) -> None:
    # Re-point every ejection at the meeting's own reporter: the reporter
    # ejection count and its share of the innocent total must both move.
    def mutate(rows: _Rows) -> _Rows:
        for row in rows:
            if row.get("kind") == "meeting" and row.get("ejected_player_id"):
                row["ejected_player_id"] = row["triggered_by"]
        return rows

    base = _baseline(tmp_path / "base")
    doctored = compute_reporter_justice(
        _doctored_set(tmp_path / "eject", mutate=mutate)
    )
    assert doctored.reporter_ejections > base.reporter_ejections
    assert (
        doctored.reporter_share_of_innocent_ejections
        != base.reporter_share_of_innocent_ejections
    )


def test_the_aim_at_reporter_cells_bite(tmp_path: Path) -> None:
    # Re-point every ballot at the reporter; the at-reporter shares must move and
    # the denominators must not.
    def mutate(rows: _Rows) -> _Rows:
        for row in rows:
            if row.get("kind") != "meeting":
                continue
            for ballot in _items(row, "ballots"):
                if isinstance(ballot, dict) and ballot.get("voter") != row.get(
                    "triggered_by"
                ):
                    ballot["target"] = row["triggered_by"]
        return rows

    base = _baseline(tmp_path / "base")
    doctored = compute_reporter_justice(_doctored_set(tmp_path / "aim", mutate=mutate))
    assert doctored.crew_ballots == base.crew_ballots
    assert doctored.impostor_ballots == base.impostor_ballots
    assert doctored.crew_ballots_at_reporter > base.crew_ballots_at_reporter
    assert doctored.impostor_ballots_at_reporter >= base.impostor_ballots_at_reporter


def test_the_speech_accusation_cells_bite(tmp_path: Path) -> None:
    # The BALLOT perturbation above leaves the speech half untouched, so it gets
    # its own: rewrite every accusation claim in the transcript to name the
    # reporter and the at-reporter numerators must rise to their denominators;
    # then DROP every accusation claim and both denominators must fall to zero.
    # Without this the speech cells rest on corpus pins alone.
    def aim(rows: _Rows) -> _Rows:
        for row in rows:
            if row.get("kind") != "meeting":
                continue
            transcript = row.get("transcript")
            if not isinstance(transcript, dict):
                continue
            for turn in _items(transcript, "turns"):
                for claim in _items(turn, "claims"):
                    if isinstance(claim, dict) and claim.get("type") == "accusation":
                        claim["against"] = row["triggered_by"]
        return rows

    def strip(rows: _Rows) -> _Rows:
        for row in rows:
            if row.get("kind") != "meeting":
                continue
            transcript = row.get("transcript")
            if not isinstance(transcript, dict):
                continue
            for turn in _items(transcript, "turns"):
                if isinstance(turn, dict):
                    turn["claims"] = [
                        claim
                        for claim in _items(turn, "claims")
                        if not (
                            isinstance(claim, dict)
                            and claim.get("type") == "accusation"
                        )
                    ]
        return rows

    base = _baseline(tmp_path / "base")
    assert base.crew_accusations + base.impostor_accusations > 0
    assert (
        base.crew_accusations_at_reporter + base.impostor_accusations_at_reporter
        < base.crew_accusations + base.impostor_accusations
    )

    aimed = compute_reporter_justice(_doctored_set(tmp_path / "aimed", mutate=aim))
    # Denominators hold, numerators saturate: the split is by the SPEAKER's role
    # and the target is what moved.
    assert aimed.crew_accusations == base.crew_accusations
    assert aimed.impostor_accusations == base.impostor_accusations
    assert aimed.crew_accusations_at_reporter == aimed.crew_accusations
    assert aimed.impostor_accusations_at_reporter == aimed.impostor_accusations

    stripped = compute_reporter_justice(
        _doctored_set(tmp_path / "stripped", mutate=strip)
    )
    assert stripped.crew_accusations == 0
    assert stripped.impostor_accusations == 0
    assert stripped.crew_accusations_at_reporter == 0
    assert stripped.impostor_accusations_at_reporter == 0
    # The BALLOT cells are untouched by a transcript mutation, so the two halves
    # are shown to be independent rather than one counter read twice.
    assert stripped.crew_ballots == base.crew_ballots
    assert stripped.impostor_ballots == base.impostor_ballots


def test_the_reporter_slot_class_survives_an_impostor_reporter(tmp_path: Path) -> None:
    # The laundering case the role census exists to catch, planted because the
    # corpus has none of it: make an IMPOSTOR the reporter and the slot classes
    # must still partition the roster -- that seat belongs to the reporter class,
    # not to both -- and its ejection must count as a reporter ejection without
    # ever becoming an innocent one.
    source = _SETS[1]
    replay, rows = _first_replay_with_a_meeting(source)
    seed = int(replay.stem.rsplit("-", 1)[1])
    num_players, num_impostors, tasks_per_crewmate = resolve_roster_knobs(source)
    roles = roles_by_seed(
        source,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
    )[seed]
    impostor = next(pid for pid, role in sorted(roles.items()) if role == "IMPOSTOR")

    def impostor_reports(mutated: _Rows) -> _Rows:
        for row in mutated:
            if row.get("kind") == "meeting":
                # The ejection too, so the reporter-first ejection branch is
                # exercised and not only the slot loop.
                if row.get("ejected_player_id") is not None:
                    row["ejected_player_id"] = impostor
                row["triggered_by"] = impostor
            for action in _items(row, "actions"):
                if isinstance(action, dict) and action.get("type") in (
                    "report",
                    "emergency",
                ):
                    action["actor"] = impostor
        return mutated

    cells = compute_reporter_justice(_doctored_set(tmp_path, mutate=impostor_reports))
    assert cells.reporter_impostor_meetings > 0
    assert cells.reporter_crewmate_meetings == 0
    # The partition holds: the impostor reporter occupies the reporter slot and
    # NOT the impostor slot, so the three classes still sum to the ballot count.
    assert (
        cells.reporter_slots + cells.innocent_non_reporter_slots + cells.impostor_slots
        == cells.crew_ballots + cells.impostor_ballots
    )
    assert cells.reporter_slots == cells.body_report_meetings
    # And an ejected impostor reporter is a reporter ejection that is NOT an
    # innocent one -- the whole-set ledger keeps it on the impostor side.
    assert cells.reporter_ejections > 0
    assert cells.innocent_ejections == 0
    assert cells.impostor_ejections >= cells.reporter_ejections


def test_the_invocation_cells_bite(tmp_path: Path) -> None:
    # Plant the base-rate reasoning into every rationale; the mention and hinge
    # counts must both rise to the whole ballot population.
    def mutate(rows: _Rows) -> _Rows:
        for row in rows:
            if row.get("kind") != "meeting":
                continue
            for ballot in _items(row, "ballots"):
                if isinstance(ballot, dict):
                    ballot["rationale_text"] = (
                        "They reported the body, which is weakly exculpatory."
                    )
        return rows

    base = _baseline(tmp_path / "base")
    doctored = compute_reporter_justice(
        _doctored_set(tmp_path / "hinge", mutate=mutate)
    )
    assert base.ballot_rationales_with_hinge < doctored.ballot_rationales_with_hinge
    assert doctored.ballot_rationales_mentioning_report == doctored.ballot_rationales
    assert doctored.ballot_rationales_with_hinge == doctored.ballot_rationales


def test_the_speech_cells_bite(tmp_path: Path) -> None:
    def mutate(rows: _Rows) -> _Rows:
        for row in rows:
            if row.get("kind") != "meeting":
                continue
            transcript = row.get("transcript")
            if not isinstance(transcript, dict):
                continue
            for turn in _items(transcript, "turns"):
                if isinstance(turn, dict):
                    turn["free_text"] = (
                        "They reported it, and that is not proof of anything."
                    )
        return rows

    base = _baseline(tmp_path / "base")
    doctored = compute_reporter_justice(
        _doctored_set(tmp_path / "speech", mutate=mutate)
    )
    assert doctored.speech_turns == base.speech_turns
    assert doctored.speech_turns_with_hinge > base.speech_turns_with_hinge
    assert doctored.speech_turns_with_hinge == doctored.speech_turns


def _reported_victims(rows: _Rows) -> dict[int, str]:
    """``{meeting tick: reported victim}`` off the applied report actions."""

    victims: dict[int, str] = {}
    for row in rows:
        for action in _items(row, "actions"):
            if not isinstance(action, dict) or action.get("type") != "report":
                continue
            payload = action.get("payload")
            body_id = payload.get("body_id") if isinstance(payload, dict) else None
            if isinstance(body_id, str):
                victims[int(str(row["tick"]))] = body_id.rsplit("-", 1)[0][
                    len("body-") :
                ]
    return victims


def test_the_co_discovery_cells_bite(tmp_path: Path) -> None:
    # Plant a discovery of THIS MEETING'S corpse at the trigger tick into every
    # recorded prompt: each non-reporter speaker then reads as a co-discoverer,
    # so the meeting count and the role slots must move off zero.
    def mutate(rows: _Rows) -> _Rows:
        victims = _reported_victims(rows)
        for row in rows:
            if row.get("kind") != "meeting":
                continue
            tick = int(str(row["tick"]))
            victim = victims.get(tick)
            if victim is None:
                continue
            for call in _items(row, "llm_calls"):
                if isinstance(call, dict) and call.get("agent_id"):
                    call["prompt"] = (
                        f"[tick {tick}] You discovered {victim}'s body in MEDBAY.\n"
                        + str(call.get("prompt", ""))
                    )
        return rows

    base = _baseline(tmp_path / "base")
    doctored = compute_reporter_justice(
        _doctored_set(tmp_path / "codisc", mutate=mutate)
    )
    assert base.meetings_with_co_discoverer == 0
    assert doctored.meetings_with_co_discoverer > 0
    assert doctored.co_discoverer_slots > 0


def test_a_discovery_of_a_different_corpse_is_not_a_co_discovery(
    tmp_path: Path,
) -> None:
    # The discrimination half, and the reason the reported victim is threaded at
    # all: the SAME planted line naming a corpse this meeting was NOT opened on
    # must count nobody. A tick-only predicate calls that speaker a co-discoverer
    # and inflates the class -- it did, by about a third, before the victim match.
    def mutate(rows: _Rows) -> _Rows:
        victims = _reported_victims(rows)
        for row in rows:
            if row.get("kind") != "meeting":
                continue
            tick = int(str(row["tick"]))
            reported = victims.get(tick)
            if reported is None:
                continue
            other = next(
                pid
                for pid in ("p-1", "p-2", "p-3", "p-4")
                if pid != reported and pid != row["triggered_by"]
            )
            for call in _items(row, "llm_calls"):
                if isinstance(call, dict) and call.get("agent_id"):
                    call["prompt"] = (
                        f"[tick {tick}] You discovered {other}'s body in MEDBAY.\n"
                        + str(call.get("prompt", ""))
                    )
        return rows

    base = _baseline(tmp_path / "base")
    doctored = compute_reporter_justice(
        _doctored_set(tmp_path / "wrong-corpse", mutate=mutate)
    )
    assert doctored.meetings_with_co_discoverer == base.meetings_with_co_discoverer == 0
    assert doctored.co_discoverer_slots == 0


def test_the_discovery_window_excludes_an_older_row(tmp_path: Path) -> None:
    # The window is a decision, not an accident: a discovery stamped well before
    # the trigger is NOT "at the body when the meeting opened", so the same
    # planted line outside the window changes nothing.
    def mutate(rows: _Rows) -> _Rows:
        for row in rows:
            if row.get("kind") != "meeting":
                continue
            for call in _items(row, "llm_calls"):
                if isinstance(call, dict) and call.get("agent_id"):
                    call["prompt"] = (
                        "[tick 0] You discovered p-9's body in MEDBAY.\n"
                        + str(call.get("prompt", ""))
                    )
        return rows

    base = _baseline(tmp_path / "base")
    doctored = compute_reporter_justice(
        _doctored_set(tmp_path / "stale", mutate=mutate)
    )
    assert doctored.meetings_with_co_discoverer == base.meetings_with_co_discoverer
    assert doctored.co_discoverer_slots == base.co_discoverer_slots
