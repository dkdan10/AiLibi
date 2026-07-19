"""Unit + production-seam coverage for the tactical-policy provenance stamp.

Task 15.9 (DESIGN.md §11.4; audit post-phase-14-ML-planning.md §7.2-7.3). The
stamp answers "which tactical policy produced these bytes" the same way
``substrate_flags`` answers "which substrate levers": a five-string block on the
``game_over`` record. These tests pin:

* the :class:`TacticalPolicyStamp` schema (five required strings, extra
  forbidden, frozen) and the canonical FSM-default factory;
* the writer round-trip (:class:`ReplayLog` → :func:`read_tactical_policy_stamp`)
  with all five fields intact, beside ``substrate_flags``;
* the byte-identity carve-out — an ABSENT stamp omits the JSON key entirely, so
  an unstamped re-record stays byte-identical to the pre-15.9 game_over row;
* the PRODUCTION seam — a game recorded through
  ``HeadlessGame(tactical_policy_stamp=…)`` and one through
  ``run_tournament_eval(…, tactical_policy_stamp=…)`` land stamped ON DISK, and
  omitting the kwarg records the absent = FSM default.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from engine.world import load_canonical_map
from eval.balance_eval import run_tournament_eval
from orchestrator.game import (
    HeadlessGame,
    build_default_agent_factory,
)
from orchestrator.replay import (
    FSM_DEFAULT_POLICY_ID,
    CrewTacticalPolicyStamp,
    GameEndReplayEntry,
    ReplayLog,
    TacticalPolicyStamp,
    fsm_default_tactical_policy_stamp,
    read_all_entries,
    read_crew_tactical_policy_stamp,
    read_substrate_flags,
    read_tactical_policy_stamp,
)
from orchestrator.scheduler import TickScheduler

# The committed canonical sets, read-only here — they predate BOTH policy stamps
# (15.9 impostor + 18.7 crew), so both read back absent = scripted default.
_COMMITTED_9P2I_DIR = (
    Path(__file__).resolve().parents[2] / "replays" / "samples" / "9p2i"
)
_COMMITTED_4P1I_DIR = (
    Path(__file__).resolve().parents[2] / "replays" / "samples" / "4p1i"
)

# A distinct learned-policy stamp (all five fields non-default) used to prove
# every field round-trips and that the stamp is disjoint from the FSM default.
_CHAMPION = TacticalPolicyStamp(
    policy_id="wave2-champion-7",
    method="neuroevolution",
    encoder_version="encoder.v3",
    weights_sha256="a" * 64,
    anchor_policy="fsm-default",
)

# A seed that reaches a decisive GAME_OVER under the default agents with no
# meeting runner within a generous tick budget, so a game_over row (carrying the
# stamp) is written. Probed at HEAD: seed 0 -> IMPOSTORS.
_DECISIVE_SEED = 0
_DECISIVE_MAX_TICKS = 200


class TestTacticalPolicyStampSchema:
    def test_five_fields_round_trip_through_json(self) -> None:
        raw = _CHAMPION.model_dump_json()
        assert TacticalPolicyStamp.model_validate_json(raw) == _CHAMPION

    def test_is_frozen(self) -> None:
        with pytest.raises(ValidationError):
            _CHAMPION.policy_id = "mutated"

    def test_extra_fields_are_forbidden(self) -> None:
        with pytest.raises(ValidationError):
            TacticalPolicyStamp.model_validate(
                {
                    "policy_id": "p",
                    "method": "m",
                    "encoder_version": "e",
                    "weights_sha256": "h",
                    "anchor_policy": "a",
                    "unexpected": "x",
                }
            )

    @pytest.mark.parametrize(
        "missing",
        ["policy_id", "method", "encoder_version", "weights_sha256", "anchor_policy"],
    )
    def test_every_field_is_required(self, missing: str) -> None:
        fields = {
            "policy_id": "p",
            "method": "m",
            "encoder_version": "e",
            "weights_sha256": "h",
            "anchor_policy": "a",
        }
        del fields[missing]
        with pytest.raises(ValidationError):
            TacticalPolicyStamp.model_validate(fields)

    @pytest.mark.parametrize(
        "bad_value",
        ["champ|x", "champ\nx", "champ\rx"],
    )
    def test_table_breaking_chars_are_rejected(self, bad_value: str) -> None:
        # A pipe or newline in a stamp field would corrupt the JSONL replay line
        # or the Markdown MANIFEST policy cell (silently dropping the row on the
        # next manifest merge). It must fail loud at the stamp boundary instead.
        with pytest.raises(ValidationError):
            TacticalPolicyStamp.model_validate(
                {
                    "policy_id": bad_value,
                    "method": "m",
                    "encoder_version": "e",
                    "weights_sha256": "h",
                    "anchor_policy": "a",
                }
            )

    def test_table_breaking_chars_rejected_in_any_field(self) -> None:
        # The guard covers every field, not just policy_id.
        with pytest.raises(ValidationError):
            TacticalPolicyStamp.model_validate(
                {
                    "policy_id": "p",
                    "method": "m",
                    "encoder_version": "e",
                    "weights_sha256": "abc|def",
                    "anchor_policy": "a",
                }
            )

    @pytest.mark.parametrize("blank", ["", "   ", "\t"])
    def test_blank_fields_are_rejected(self, blank: str) -> None:
        # An empty policy_id is indistinguishable from an ABSENT stamp at the
        # MANIFEST renderer, so it would misattribute a stamped recording as the
        # FSM default. A well-formed stamp field is always a non-blank token, so
        # blanks fail loud at the stamp boundary.
        with pytest.raises(ValidationError):
            TacticalPolicyStamp.model_validate(
                {
                    "policy_id": blank,
                    "method": "m",
                    "encoder_version": "e",
                    "weights_sha256": "h",
                    "anchor_policy": "a",
                }
            )

    def test_fsm_default_factory_shape(self) -> None:
        stamp = fsm_default_tactical_policy_stamp()
        assert stamp.policy_id == FSM_DEFAULT_POLICY_ID == "fsm-default"
        assert stamp.method == "scripted-fsm"
        # The FSM has no encoder and no weights; it is its own piKL anchor.
        assert stamp.encoder_version == "none"
        assert stamp.weights_sha256 == "none"
        assert stamp.anchor_policy == FSM_DEFAULT_POLICY_ID


class TestWriterRoundTrip:
    def test_stamped_game_end_round_trips_all_five_fields(self, tmp_path: Path) -> None:
        path = tmp_path / "replay-seed-1.jsonl"
        log = ReplayLog(
            path, game_id="headless-seed-1", tactical_policy_stamp=_CHAMPION
        )
        log.record_game_end(winner="CREWMATES", reason="CREWMATE_TASKS", tick=10)
        log.close()

        assert read_tactical_policy_stamp(path) == _CHAMPION

    def test_stamp_sits_beside_substrate_flags_on_the_game_over_entry(
        self, tmp_path: Path
    ) -> None:
        path = tmp_path / "replay-seed-2.jsonl"
        log = ReplayLog(
            path, game_id="headless-seed-2", tactical_policy_stamp=_CHAMPION
        )
        log.record_game_end(winner="IMPOSTORS", reason="IMPOSTOR_PARITY", tick=9)
        log.close()

        (entry,) = [
            e for e in read_all_entries(path) if isinstance(e, GameEndReplayEntry)
        ]
        assert entry.tactical_policy == _CHAMPION
        assert entry.substrate_flags is not None  # the sibling stamp still present

    def test_fsm_default_stamp_round_trips(self, tmp_path: Path) -> None:
        path = tmp_path / "replay-seed-3.jsonl"
        log = ReplayLog(
            path,
            game_id="headless-seed-3",
            tactical_policy_stamp=fsm_default_tactical_policy_stamp(),
        )
        log.record_game_end(winner="CREWMATES", reason="CREWMATE_TASKS", tick=4)
        log.close()

        assert read_tactical_policy_stamp(path) == fsm_default_tactical_policy_stamp()


class TestAbsentStampByteIdentity:
    def test_absent_stamp_omits_the_json_key(self, tmp_path: Path) -> None:
        # An absent stamp is the FSM default and MUST record byte-identically to
        # the pre-15.9 game_over row: the optional field is OMITTED from the JSON
        # entirely, never written as ``"tactical_policy": null``.
        path = tmp_path / "replay-seed-4.jsonl"
        log = ReplayLog(path, game_id="headless-seed-4")
        log.record_game_end(winner="CREWMATES", reason="CREWMATE_TASKS", tick=5)
        log.close()

        row = json.loads(path.read_text(encoding="utf-8").strip())
        assert "tactical_policy" not in row
        assert read_tactical_policy_stamp(path) is None

    def test_unstamped_recording_is_byte_identical_to_the_default_writer(
        self, tmp_path: Path
    ) -> None:
        # Explicitly passing ``tactical_policy_stamp=None`` records the exact same
        # bytes as omitting the kwarg (today's path).
        default_path = tmp_path / "default.jsonl"
        ReplayLog(default_path, game_id="headless-seed-9").record_game_end(
            winner="IMPOSTORS", reason="IMPOSTOR_PARITY", tick=7
        )
        none_path = tmp_path / "none.jsonl"
        ReplayLog(
            none_path, game_id="headless-seed-9", tactical_policy_stamp=None
        ).record_game_end(winner="IMPOSTORS", reason="IMPOSTOR_PARITY", tick=7)

        assert default_path.read_bytes() == none_path.read_bytes()

    def test_legacy_game_over_without_stamp_deserializes(self) -> None:
        # A pre-15.9 game_over record (no ``tactical_policy`` key) still validates
        # and reads as absent = FSM default.
        entry = GameEndReplayEntry.model_validate(
            {
                "kind": "game_over",
                "game_id": "headless-seed-1",
                "tick": 5,
                "winner": "CREWMATES",
                "reason": "CREWMATE_TASKS",
            }
        )
        assert entry.tactical_policy is None


class TestProductionSeam:
    def test_headless_game_stamps_the_replay_on_disk(self, tmp_path: Path) -> None:
        path = tmp_path / "replay-seed-0.jsonl"
        result = HeadlessGame(
            seed=_DECISIVE_SEED,
            game_map=load_canonical_map(),
            agent_factory=build_default_agent_factory(),
            replay_path=path,
            scheduler=TickScheduler(max_ticks=_DECISIVE_MAX_TICKS),
            tactical_policy_stamp=_CHAMPION,
        ).run()

        assert result.outcome in {"CREWMATES", "IMPOSTORS"}  # reached game_over
        assert read_tactical_policy_stamp(path) == _CHAMPION

    def test_headless_game_without_stamp_records_absent(self, tmp_path: Path) -> None:
        path = tmp_path / "replay-seed-0.jsonl"
        HeadlessGame(
            seed=_DECISIVE_SEED,
            game_map=load_canonical_map(),
            agent_factory=build_default_agent_factory(),
            replay_path=path,
            scheduler=TickScheduler(max_ticks=_DECISIVE_MAX_TICKS),
        ).run()

        assert read_tactical_policy_stamp(path) is None
        (entry,) = [
            e for e in read_all_entries(path) if isinstance(e, GameEndReplayEntry)
        ]
        # Absent stamp, but the substrate stamp still fires — proving the omission
        # is scoped to the tactical stamp, not a broken game_over row.
        assert entry.tactical_policy is None
        assert entry.substrate_flags is not None

    def test_run_tournament_eval_stamps_every_replay(self, tmp_path: Path) -> None:
        run_tournament_eval(
            seeds=[0, 2],
            output_dir=tmp_path,
            max_ticks=_DECISIVE_MAX_TICKS,
            tactical_policy_stamp=_CHAMPION,
        )
        for seed in (0, 2):
            path = tmp_path / f"replay-seed-{seed}.jsonl"
            assert read_tactical_policy_stamp(path) == _CHAMPION

    def test_run_tournament_eval_without_stamp_is_absent(self, tmp_path: Path) -> None:
        run_tournament_eval(
            seeds=[0], output_dir=tmp_path, max_ticks=_DECISIVE_MAX_TICKS
        )
        path = tmp_path / "replay-seed-0.jsonl"
        assert read_tactical_policy_stamp(path) is None
        # The unstamped tournament replay carries no tactical_policy key on disk —
        # byte-compatible with the committed samples.
        row = next(
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line and json.loads(line).get("kind") == "game_over"
        )
        assert "tactical_policy" not in row
        assert read_substrate_flags(path) is not None


class TestCrewStampCommittedSetRoundTrip:
    """The 18.7 crew stamp reads back absent on every committed replay (Task 18.11).

    The 18.7 verifier pinned the crew-stamp writer round-trip and the absent-stamp
    byte-identity carve-out against a FRESH ``ReplayLog``, but left one soft spot:
    a dedicated round-trip pin over the COMMITTED canonical sets — the exact bytes
    the meeting-gate probe and every downstream record are byte-compared against.
    18.11 closes it while in ``orchestrator/replay.py`` for the substrate-flag
    registry. The committed 9p2i + 4p1i sets predate BOTH policy stamps, so every
    ``game_over`` row must (a) carry NO ``crew_tactical_policy`` key on disk and
    (b) read back ``None`` = the scripted ``CrewmatePolicy`` default through
    :func:`read_crew_tactical_policy_stamp`. A regression that made the crew reader
    invent an identity, or the schema reject the unstamped committed shape, would
    surface here rather than silently mis-attributing a canonical recording.
    """

    def _committed_replays(self, directory: Path) -> list[Path]:
        paths = sorted(directory.glob("replay-seed-*.jsonl"))
        assert paths, f"no committed replays under {directory}"
        return paths

    @pytest.mark.parametrize("set_name", ["9p2i", "4p1i"])
    def test_committed_game_over_carries_no_crew_stamp_key(self, set_name: str) -> None:
        directory = _COMMITTED_9P2I_DIR if set_name == "9p2i" else _COMMITTED_4P1I_DIR
        for path in self._committed_replays(directory):
            game_over_rows = [
                json.loads(line)
                for line in path.read_text(encoding="utf-8").splitlines()
                if line and json.loads(line).get("kind") == "game_over"
            ]
            assert len(game_over_rows) == 1, path
            row = game_over_rows[0]
            # The absent-stamp byte-identity carve-out: the optional crew key is
            # OMITTED from the JSON entirely, never written as null, so the
            # committed bytes are byte-identical to the pre-18.7 game_over row.
            assert "crew_tactical_policy" not in row, path
            # And the impostor stamp is likewise absent (FSM-default recordings).
            assert "tactical_policy" not in row, path

    @pytest.mark.parametrize("set_name", ["9p2i", "4p1i"])
    def test_committed_crew_stamp_reads_back_absent(self, set_name: str) -> None:
        directory = _COMMITTED_9P2I_DIR if set_name == "9p2i" else _COMMITTED_4P1I_DIR
        for path in self._committed_replays(directory):
            # read_crew_tactical_policy_stamp returns None = scripted crew default,
            # and the entry parses (the schema tolerates the unstamped shape).
            assert read_crew_tactical_policy_stamp(path) is None, path
            (entry,) = [
                e for e in read_all_entries(path) if isinstance(e, GameEndReplayEntry)
            ]
            assert entry.crew_tactical_policy is None, path

    def test_committed_crew_stamp_survives_a_crew_stamp_round_trip(
        self, tmp_path: Path
    ) -> None:
        # A learned-crew recording DOES stamp the crew block, and the reader
        # round-trips all five fields — proving the committed-set None read is a
        # genuine absence, not a reader that always returns None.
        crew = CrewTacticalPolicyStamp(
            policy_id="crew-owned-tasks-es-1",
            method="neuroevolution",
            encoder_version="crew.encoder.v1",
            weights_sha256="b" * 64,
            anchor_policy="crewmate-policy",
        )
        path = tmp_path / "crew-stamped.jsonl"
        ReplayLog(
            path, game_id="crew-1", crew_tactical_policy_stamp=crew
        ).record_game_end(winner="CREWMATES", reason="CREWMATE_TASKS", tick=9)
        assert read_crew_tactical_policy_stamp(path) == crew
        # The impostor stamp stays absent beside a present crew stamp.
        assert read_tactical_policy_stamp(path) is None
