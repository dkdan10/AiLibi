"""Unit coverage for the replay-log records and fail-loud guards.

These exercise the additive replay records introduced by Task 3.19 and the
fail-loud / doubled-file guards added by Task 4.16 (DESIGN.md §11.4):

* ``record_game_end`` / ``read_game_outcome`` — persist and recover the
  decisive game outcome so win-rate is evaluable from any replay log,
  including a partial tournament that crashed mid-run (finding 3).
* ``record_failed_call`` — persist the cost + partial response of an LLM
  call that aborted a meeting on schema-validation failure, so per-meeting
  cost is auditable even for the crashed meeting (finding 2), and is folded
  into ``compute_cost_usd``.
* ``ReplayLog.__init__`` fail-loud on an existing path (write side) and
  ``read_all_entries`` doubled-file detection (read side) — Task 4.16
  guards against the silent run-over-run concatenation that broke the
  loader's dedup in Phase 4 UX prep.

Pure replay-layer tests: no full game loop, no LLM call.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agents.memory.beliefs import (
    ENV_EVIDENCE_QUALITY_LIFT,
    ENV_HARD_EVIDENCE_GATE,
    ENV_REPORTER_EXCULPATION,
    hard_evidence_gate_enabled,
)
from agents.memory.store import (
    ENV_OBSERVATION_ID_RENDERING,
    observation_id_rendering_enabled,
)
from orchestrator.replay import (
    SUBSTRATE_FLAG_KEYS,
    TOGGLEABLE_SUBSTRATE_FLAG_KEYS,
    _TOGGLEABLE_LEVER_RESOLVERS,
    FailedCallReplayEntry,
    GameEndReplayEntry,
    LLMCallRecord,
    ReplayEntry,
    ReplayLog,
    compute_cost_usd,
    read_all_entries,
    read_failed_call_entries,
    read_game_outcome,
    read_substrate_flags,
    substrate_flag_snapshot,
)
from tests._helpers.world_state import scripted_initial_world_state

# The Task-14.10 lever's snapshot key (retired to ``_RETIRED_ALWAYS_ON_LEVERS``
# at the 14.12 close); its env var is ``ENV_EVIDENCE_QUALITY_LIFT`` above.
ENV_EVIDENCE_QUALITY_LIFT_KEY = "evidence_quality_lift"

# The Task-15.5 reporter-exculpation lever's snapshot key — retired to
# ``_RETIRED_ALWAYS_ON_LEVERS`` at the Task-15.7 baseline-3 record; its env var is
# ``ENV_REPORTER_EXCULPATION`` above (retained but no longer read).
ENV_REPORTER_EXCULPATION_KEY = "reporter_exculpation"

# The Task-16.4 hard-evidence-gate (J1) lever's snapshot key — the FIRST LIVE
# ``_TOGGLEABLE_LEVER_RESOLVERS`` registration (the first live toggle re-entered
# into that table since the Task-15.7 graduation emptied it); its env var is
# ``ENV_HARD_EVIDENCE_GATE`` above, and its resolver is
# ``hard_evidence_gate_enabled``. DEFAULT-OFF.
ENV_HARD_EVIDENCE_GATE_KEY = "hard_evidence_gate"

# The Task-16.5 observation-id render lever's snapshot key — the SECOND LIVE
# ``_TOGGLEABLE_LEVER_RESOLVERS`` registration (behind 16.4's ``hard_evidence_gate``);
# its env var is ``ENV_OBSERVATION_ID_RENDERING`` above, and its resolver is
# ``observation_id_rendering_enabled``. DEFAULT-OFF.
ENV_OBSERVATION_ID_RENDERING_KEY = "observation_id_rendering"

# The committed 9p2i sample set the gp-4 audit measured; read-only here (the
# re-record itself is Task 9.11).
_COMMITTED_9P2I_REPLAYS = (
    Path(__file__).resolve().parents[2] / "replays" / "samples" / "9p2i"
)


class TestGameEndRecording:
    def test_record_game_end_round_trips_via_read_game_outcome(
        self, tmp_path: Path
    ) -> None:
        path = tmp_path / "outcome.jsonl"
        log = ReplayLog(path, game_id="g-1")

        log.record_game_end(winner="CREWMATES", reason="all_tasks_complete")

        assert read_game_outcome(path) == "CREWMATES"

    def test_game_end_entry_persists_winner_reason_and_tick(
        self, tmp_path: Path
    ) -> None:
        path = tmp_path / "outcome.jsonl"
        log = ReplayLog(path, game_id="g-1")

        log.record_game_end(winner="IMPOSTORS", reason="IMPOSTOR_PARITY", tick=412)

        entries = read_all_entries(path)
        assert len(entries) == 1
        entry = entries[0]
        assert isinstance(entry, GameEndReplayEntry)
        assert entry.kind == "game_over"
        assert entry.game_id == "g-1"
        assert entry.winner == "IMPOSTORS"
        assert entry.reason == "IMPOSTOR_PARITY"
        assert entry.tick == 412

    def test_read_game_outcome_returns_none_when_no_game_end_row(
        self, tmp_path: Path
    ) -> None:
        # A partial replay from a run that crashed mid-meeting: a failed-call
        # row is present but the game outcome was never decided.
        path = tmp_path / "partial.jsonl"
        log = ReplayLog(path, game_id="g-2")
        log.record_failed_call(
            meeting_id="g-2:meeting-0",
            tick=99,
            model="claude-sonnet-4-6",
            prompt_length=10,
            raw_response="I need to think...",
            input_tokens=1,
            output_tokens=1,
            cost_usd=0.0,
            error_type="ValidationError",
            error_message="boom",
        )

        assert read_game_outcome(path) is None

    def test_read_game_outcome_returns_none_for_empty_replay(
        self, tmp_path: Path
    ) -> None:
        path = tmp_path / "empty.jsonl"
        path.write_text("", encoding="utf-8")

        assert read_game_outcome(path) is None

    def test_read_game_outcome_raises_on_doubled_game_over(
        self, tmp_path: Path
    ) -> None:
        # A game writes exactly one game-end row. Two ``game_over`` rows mean
        # two games' records were concatenated into one file (the Phase 4
        # doubled-write). ``read_game_outcome`` routes through
        # ``read_all_entries``, so it now fails loud (Task 4.16) instead of
        # silently returning the last winner.
        path = tmp_path / "multi.jsonl"
        log = ReplayLog(path, game_id="g-3")
        log.record_game_end(winner="CREWMATES", reason="CREWMATE_TASKS")
        log.record_game_end(winner="IMPOSTORS", reason="IMPOSTOR_PARITY")

        with pytest.raises(ReplayLog.CorruptedFileError):
            read_game_outcome(path)

    def test_record_game_end_accepts_none_winner_as_undecided(
        self, tmp_path: Path
    ) -> None:
        # winner=None encodes a drawn / unfinished game; the engine never
        # produces one, but the field allows it and it reads back as None.
        path = tmp_path / "draw.jsonl"
        log = ReplayLog(path, game_id="g-4")
        log.record_game_end(winner=None, reason="unfinished")

        assert read_game_outcome(path) is None


class TestSubstrateFlagStamp:
    """The Task-14.7 substrate-flag stamp on the game_over record.

    A replay self-describes which substrate levers generated it. The SIX
    original levers are unconditionally ON with their env gates retired: the
    four 13.5 levers since Task 14.9, Task 14.10's ``evidence_quality_lift``
    since the Task-14.12 close, and Task 15.5's ``reporter_exculpation`` since
    the Task-15.7 baseline-3 record. Task 16.4 re-registers the one LIVE
    env-gated toggle, ``hard_evidence_gate`` (``_TOGGLEABLE_LEVER_RESOLVERS`` —
    the first entry back into that table since the 15.7 graduation emptied it),
    DEFAULT-OFF: a bare-environment recording stamps the six retired levers True
    and the new lever False — byte-identical to the committed baseline-3
    substrate, which predates the key (``_assert_substrate_matches`` reads a
    missing key as ``False`` on both sides, so the committed replays reconstruct
    under a bare env). An ambient ``AILIBI_HARD_EVIDENCE_GATE`` export flips the
    live toggle's stamp ON; the six retired levers never read env again.
    """

    def test_retired_levers_are_all_on_and_env_independent(self) -> None:
        # All six retired levers report True under ANY env — a bare mapping, an
        # explicit legacy "0", the (retired) AILIBI_EVIDENCE_QUALITY_LIFT export,
        # or a stray AILIBI_REPORTER_EXCULPATION export all read identically. The
        # levers that still read env are Task 16.4's default-OFF hard_evidence_gate
        # and Task 16.5's default-OFF observation_id_rendering (the two entries in
        # _TOGGLEABLE_LEVER_RESOLVERS), which are scoped out here so this pin stays
        # about the always-on set.
        retired = tuple(
            key
            for key in SUBSTRATE_FLAG_KEYS
            if key not in TOGGLEABLE_SUBSTRATE_FLAG_KEYS
        )
        for env in (
            {},
            {"AILIBI_TESTIMONY_AS_CONTENT": "0"},
            {ENV_EVIDENCE_QUALITY_LIFT: "0"},
            {ENV_EVIDENCE_QUALITY_LIFT: "1"},
            {ENV_REPORTER_EXCULPATION: "0"},
            {ENV_REPORTER_EXCULPATION: "1"},
        ):
            snapshot = substrate_flag_snapshot(env)
            assert all(snapshot[key] is True for key in retired)
        assert set(retired) == {
            "testimony_as_content",
            "witnessed_kill_evidence",
            "movement_perception",
            "unfreeze_memory",
            "evidence_quality_lift",
            "reporter_exculpation",
        }
        assert TOGGLEABLE_SUBSTRATE_FLAG_KEYS == (
            "hard_evidence_gate",
            "observation_id_rendering",
        )

    def test_reporter_exculpation_graduated_unconditional_on(self) -> None:
        # Graduated to unconditional-ON at the Task-15.7 baseline-3 record: the
        # snapshot reports it True under a bare mapping, an unrecognised value, an
        # explicit "0", or a truthy export alike — env is no longer consulted.
        for env in (
            {},
            {ENV_REPORTER_EXCULPATION: "nope"},
            {ENV_REPORTER_EXCULPATION: "0"},
        ):
            assert substrate_flag_snapshot(env)[ENV_REPORTER_EXCULPATION_KEY] is True
        assert (
            substrate_flag_snapshot({ENV_REPORTER_EXCULPATION: "1"})[
                ENV_REPORTER_EXCULPATION_KEY
            ]
            is True
        )

    def test_live_toggle_registrations(self) -> None:
        # Registration pin (Task 16.4 + 16.5 DoD "registered"): TWO live toggles in
        # ``_TOGGLEABLE_LEVER_RESOLVERS`` now — 16.4's ``hard_evidence_gate`` (the
        # first live toggle re-entered since the Task-15.7 graduation emptied the
        # table) followed by 16.5's ``observation_id_rendering``. Each key is bound
        # to its resolver BY IDENTITY, so the replay stamp and each lever's
        # read-site(s) share one source of truth: hard_evidence_gate ↔ the two
        # belief-render read-sites (store._build_belief_lines,
        # game.suspicion_graph_for_meeting), observation_id_rendering ↔ the §6.6
        # observation-line render (store.render_for_prompt).
        # ``SUBSTRATE_FLAG_KEYS`` appends the two live keys after the six retired
        # always-on keys; ``TOGGLEABLE_SUBSTRATE_FLAG_KEYS`` is exactly the
        # live-toggle subset the loader's mismatch-remediation hint branches on.
        assert len(_TOGGLEABLE_LEVER_RESOLVERS) == 2
        (gate_key, gate_resolver) = _TOGGLEABLE_LEVER_RESOLVERS[0]
        assert gate_key == ENV_HARD_EVIDENCE_GATE_KEY
        assert gate_resolver is hard_evidence_gate_enabled
        (obs_key, obs_resolver) = _TOGGLEABLE_LEVER_RESOLVERS[1]
        assert obs_key == ENV_OBSERVATION_ID_RENDERING_KEY
        assert obs_resolver is observation_id_rendering_enabled
        assert TOGGLEABLE_SUBSTRATE_FLAG_KEYS == (
            ENV_HARD_EVIDENCE_GATE_KEY,
            ENV_OBSERVATION_ID_RENDERING_KEY,
        )
        assert SUBSTRATE_FLAG_KEYS == (
            "testimony_as_content",
            "witnessed_kill_evidence",
            "movement_perception",
            "unfreeze_memory",
            "evidence_quality_lift",
            "reporter_exculpation",
            "hard_evidence_gate",
            "observation_id_rendering",
        )

    def test_hard_evidence_gate_resolver_is_a_pure_constant_function(self) -> None:
        # Resolver constant-ness at graduation readiness (the Task 16.4 DoD
        # phrase): the registered resolver IS
        # ``agents.memory.beliefs.hard_evidence_gate_enabled`` by identity, and it
        # is a deterministic PURE function of its env mapping — the same mapping in
        # yields the same bool out, repeatedly and independent of the object's
        # identity, and it never mutates the mapping. This is the seam the Task
        # 16.17 graduation flips exactly as ``reporter_exculpation`` did at 15.7:
        # retire the resolver, the table empties, and the stamp goes unconditional
        # — with no other read-site to reconcile because they all resolve here.
        (_key, resolver) = _TOGGLEABLE_LEVER_RESOLVERS[0]
        assert resolver is hard_evidence_gate_enabled
        for env in (
            {},
            {ENV_HARD_EVIDENCE_GATE: "1"},
            {ENV_HARD_EVIDENCE_GATE: "0"},
        ):
            before = dict(env)
            result = resolver(env)
            assert resolver(env) == result
            assert resolver(dict(env)) == result
            assert env == before
        assert resolver({}) is False
        assert resolver({ENV_HARD_EVIDENCE_GATE: "1"}) is True

    def test_hard_evidence_gate_toggle_reads_env_default_off(self) -> None:
        # The live toggle (Task 16.4 DoD "OFF/ON behavior"): OFF (unset / bare /
        # unrecognised) and ON (a truthy export), env-passed so no ``os.environ``
        # mutation. DEFAULT-OFF is the byte-identical baseline-3 substrate. Truthy
        # values mirror the retired 13.5 / 14.10 / 15.5 resolvers
        # (``1/true/yes/on``, case-insensitive).
        assert substrate_flag_snapshot({})[ENV_HARD_EVIDENCE_GATE_KEY] is False
        assert (
            substrate_flag_snapshot({ENV_HARD_EVIDENCE_GATE: "nope"})[
                ENV_HARD_EVIDENCE_GATE_KEY
            ]
            is False
        )
        assert (
            substrate_flag_snapshot({ENV_HARD_EVIDENCE_GATE: "1"})[
                ENV_HARD_EVIDENCE_GATE_KEY
            ]
            is True
        )
        assert (
            substrate_flag_snapshot({ENV_HARD_EVIDENCE_GATE: "true"})[
                ENV_HARD_EVIDENCE_GATE_KEY
            ]
            is True
        )

    def test_hard_evidence_gate_snapshot_env_none_honors_process_environment(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Unlike the six retired levers (which no longer read env), the LIVE
        # toggle resolves the process environment when ``env`` is None: an ambient
        # ``AILIBI_HARD_EVIDENCE_GATE`` export flips the default-OFF stamp ON, and
        # deleting it restores OFF. This is the seam the offline counterfactual and
        # the sweep configs drive the lever through without threading an explicit
        # mapping (Task 16.4).
        monkeypatch.delenv(ENV_HARD_EVIDENCE_GATE, raising=False)
        assert substrate_flag_snapshot()[ENV_HARD_EVIDENCE_GATE_KEY] is False
        monkeypatch.setenv(ENV_HARD_EVIDENCE_GATE, "1")
        assert substrate_flag_snapshot()[ENV_HARD_EVIDENCE_GATE_KEY] is True

    def test_observation_id_rendering_toggle_reads_env_default_off(self) -> None:
        # The second live toggle (Task 16.5 DoD "OFF/ON behavior"): OFF (unset /
        # bare / unrecognised) and ON (a truthy export), env-passed so no
        # ``os.environ`` mutation. DEFAULT-OFF is the byte-identical baseline-3
        # substrate. Truthy values mirror the 16.4 resolver it clones
        # (``1/true/yes/on``, case-insensitive).
        assert substrate_flag_snapshot({})[ENV_OBSERVATION_ID_RENDERING_KEY] is False
        assert (
            substrate_flag_snapshot({ENV_OBSERVATION_ID_RENDERING: "nope"})[
                ENV_OBSERVATION_ID_RENDERING_KEY
            ]
            is False
        )
        assert (
            substrate_flag_snapshot({ENV_OBSERVATION_ID_RENDERING: "1"})[
                ENV_OBSERVATION_ID_RENDERING_KEY
            ]
            is True
        )
        assert (
            substrate_flag_snapshot({ENV_OBSERVATION_ID_RENDERING: "on"})[
                ENV_OBSERVATION_ID_RENDERING_KEY
            ]
            is True
        )

    def test_observation_id_rendering_snapshot_env_none_honors_process_environment(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Like 16.4's live toggle, the 16.5 toggle resolves the process environment
        # when ``env`` is None: an ambient ``AILIBI_OBSERVATION_ID_RENDERING`` export
        # flips the default-OFF stamp ON, and deleting it restores OFF — the seam the
        # offline counterfactual and sweep configs drive without threading a mapping.
        monkeypatch.delenv(ENV_OBSERVATION_ID_RENDERING, raising=False)
        assert substrate_flag_snapshot()[ENV_OBSERVATION_ID_RENDERING_KEY] is False
        monkeypatch.setenv(ENV_OBSERVATION_ID_RENDERING, "1")
        assert substrate_flag_snapshot()[ENV_OBSERVATION_ID_RENDERING_KEY] is True

    def test_snapshot_retired_lever_independent_of_the_process_environment(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # The retired lever no longer reads any env (unconditional since the
        # 14.12 close): the process-environment snapshot is ON either way.
        monkeypatch.delenv(ENV_EVIDENCE_QUALITY_LIFT, raising=False)
        assert substrate_flag_snapshot()[ENV_EVIDENCE_QUALITY_LIFT_KEY] is True
        monkeypatch.setenv(ENV_EVIDENCE_QUALITY_LIFT, "0")
        assert substrate_flag_snapshot()[ENV_EVIDENCE_QUALITY_LIFT_KEY] is True

    def test_every_recording_stamps_the_full_snapshot(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Recording under a bare environment stamps all six retired levers ON
        # (byte-identical to the committed baseline-3 set — the graduated
        # reporter_exculpation lever needs no env export) and the TWO live
        # default-OFF toggles (Task 16.4's hard_evidence_gate, Task 16.5's
        # observation_id_rendering) OFF.
        monkeypatch.delenv(ENV_REPORTER_EXCULPATION, raising=False)
        monkeypatch.delenv(ENV_HARD_EVIDENCE_GATE, raising=False)
        monkeypatch.delenv(ENV_OBSERVATION_ID_RENDERING, raising=False)
        path = tmp_path / "on.jsonl"
        ReplayLog(path, game_id="g-on").record_game_end(
            winner="IMPOSTORS", reason="IMPOSTOR_PARITY", tick=41
        )
        entry = read_all_entries(path)[0]
        assert isinstance(entry, GameEndReplayEntry)
        assert entry.substrate_flags == {
            "testimony_as_content": True,
            "witnessed_kill_evidence": True,
            "movement_perception": True,
            "unfreeze_memory": True,
            "evidence_quality_lift": True,
            "reporter_exculpation": True,
            "hard_evidence_gate": False,
            "observation_id_rendering": False,
        }
        assert read_substrate_flags(path) == dict(entry.substrate_flags)

    def test_hard_evidence_gate_on_recording_round_trips_the_stamp(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # With the live toggle exported, ``record_game_end`` stamps it ON and the
        # file reader round-trips it — the recording self-describes the substrate
        # it ran under (the future adopting-baseline shape the Task 16.17
        # graduation would record; the MANIFEST ``flags`` cell renders from this
        # same ``read_substrate_flags`` value). The six retired levers stay ON
        # alongside it — a lever-ON recording is NOT byte-identical to the OFF
        # baseline-3 stamp, so it fails loud against a committed OFF stamp under
        # ``_assert_substrate_matches`` unless the loader opts into the mismatch.
        monkeypatch.setenv(ENV_HARD_EVIDENCE_GATE, "1")
        path = tmp_path / "gate-on.jsonl"
        ReplayLog(path, game_id="g-gate").record_game_end(
            winner="CREWMATES", reason="CREWMATE_EJECT", tick=17
        )
        flags = read_substrate_flags(path)
        assert flags is not None
        assert flags[ENV_HARD_EVIDENCE_GATE_KEY] is True
        # The retired always-on levers stay ON alongside the live toggle.
        assert all(
            flags[key]
            for key in SUBSTRATE_FLAG_KEYS
            if key not in TOGGLEABLE_SUBSTRATE_FLAG_KEYS
        )

    def test_retired_reporter_exculpation_export_still_stamps_on(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # The retired reporter_exculpation env export is a no-op stamp (the lever
        # is unconditional since the Task-15.7 baseline-3 record): exported or not
        # it records ON, and the reader round-trips it — the recording
        # self-describes the substrate it ran under (the baseline-3 shape; the
        # MANIFEST ``flags`` cell renders from this same read_substrate_flags
        # value). The other retired levers stay ON alongside it.
        monkeypatch.setenv(ENV_REPORTER_EXCULPATION, "1")
        path = tmp_path / "reporter-on.jsonl"
        ReplayLog(path, game_id="g-reporter").record_game_end(
            winner="CREWMATES", reason="CREWMATE_EJECT", tick=17
        )
        flags = read_substrate_flags(path)
        assert flags is not None
        assert flags[ENV_REPORTER_EXCULPATION_KEY] is True
        # The retired always-on levers stay ON; Task 16.4's live default-OFF
        # hard_evidence_gate is scoped out (it is not a retired lever).
        assert all(
            flags[key]
            for key in SUBSTRATE_FLAG_KEYS
            if key not in TOGGLEABLE_SUBSTRATE_FLAG_KEYS
        )

    def test_retired_evidence_quality_lift_export_still_stamps_on(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # The retired evidence_quality_lift env export is a no-op stamp (the
        # lever is unconditional since the 14.12 close): exported or not it
        # records ON, and the reader round-trips it. The other retired levers
        # stay ON alongside it.
        monkeypatch.setenv(ENV_EVIDENCE_QUALITY_LIFT, "1")
        path = tmp_path / "lever-on.jsonl"
        ReplayLog(path, game_id="g-lever").record_game_end(
            winner="CREWMATES", reason="CREWMATE_EJECT", tick=17
        )
        flags = read_substrate_flags(path)
        assert flags is not None
        assert flags[ENV_EVIDENCE_QUALITY_LIFT_KEY] is True
        # The retired always-on levers stay ON; Task 16.4's live default-OFF
        # hard_evidence_gate is scoped out (it is not a retired lever).
        assert all(
            flags[key]
            for key in SUBSTRATE_FLAG_KEYS
            if key not in TOGGLEABLE_SUBSTRATE_FLAG_KEYS
        )

    def test_legacy_game_over_without_stamp_deserializes(self) -> None:
        # A pre-14.7 game_over record (no substrate_flags key) still validates,
        # with the field defaulting to None — so committed replays reconstruct
        # unchanged.
        entry = GameEndReplayEntry.model_validate(
            {
                "kind": "game_over",
                "game_id": "legacy",
                "tick": 7,
                "winner": "CREWMATES",
                "reason": "TASKS",
            }
        )
        assert entry.substrate_flags is None


class TestFailedCallRecording:
    def test_record_failed_call_round_trips(self, tmp_path: Path) -> None:
        path = tmp_path / "failed.jsonl"
        log = ReplayLog(path, game_id="g-5")

        log.record_failed_call(
            meeting_id="g-5:meeting-0",
            tick=410,
            model="claude-sonnet-4-6",
            prompt_length=2048,
            raw_response='{"agent_id": "p-3"',
            input_tokens=1500,
            output_tokens=900,
            cost_usd=0.018,
            error_type="ValidationError",
            error_message="1 validation error for ReportDocument",
        )

        failed = read_failed_call_entries(path)
        assert len(failed) == 1
        entry = failed[0]
        assert isinstance(entry, FailedCallReplayEntry)
        assert entry.kind == "failed_call"
        assert entry.game_id == "g-5"
        assert entry.meeting_id == "g-5:meeting-0"
        assert entry.tick == 410
        assert entry.model == "claude-sonnet-4-6"
        assert entry.prompt_length == 2048
        assert entry.raw_response == '{"agent_id": "p-3"'
        assert entry.input_tokens == 1500
        assert entry.output_tokens == 900
        assert entry.cost_usd == 0.018
        assert entry.error_type == "ValidationError"
        assert entry.error_message == "1 validation error for ReportDocument"
        # A non-vote failed call carries no §4.6 verdict (Task 10.12).
        assert entry.rendered_vote_max is None

    def test_defaulted_vote_persists_rendered_max(self, tmp_path: Path) -> None:
        # Task 10.12 (audit H-H-2): a defaulted VOTE row carries the rendered
        # §4.6 max so the offline verdict reconstruction can classify it.
        path = tmp_path / "failed.jsonl"
        log = ReplayLog(path, game_id="g-5")

        log.record_failed_call(
            meeting_id="g-5:meeting-2",
            tick=80,
            model="(deadline_default)",
            prompt_length=0,
            raw_response="",
            input_tokens=0,
            output_tokens=0,
            cost_usd=0.0,
            error_type="deadline_default",
            error_message="vote defaulted (validation); p-1 submitted no ballot",
            rendered_vote_max=0.65,
        )

        entry = read_failed_call_entries(path)[0]
        assert entry.rendered_vote_max == 0.65

    def test_legacy_failed_call_without_field_tolerates_absence(self) -> None:
        # Backward-compat pin (Task 10.12): every committed single-era replay
        # predates ``rendered_vote_max``, so a row WITHOUT the key must still
        # load (default ``None``) -- the reader tolerates its absence and the
        # bytes reconstruct unchanged.
        legacy = {
            "kind": "failed_call",
            "game_id": "g-9",
            "meeting_id": "g-9:meeting-0",
            "tick": 40,
            "model": "(deadline_default)",
            "prompt_length": 0,
            "raw_response": "",
            "input_tokens": 0,
            "output_tokens": 0,
            "cost_usd": 0.0,
            "error_type": "deadline_default",
            "error_message": "vote defaulted (validation); p-1 submitted no ballot",
        }

        entry = FailedCallReplayEntry.model_validate(legacy)

        assert entry.rendered_vote_max is None

    def test_compute_cost_usd_folds_in_failed_call_cost(self, tmp_path: Path) -> None:
        # The crashing call's spend must not be silently dropped from the
        # canonical per-game cost reduction (Task 3.19 finding 2).
        path = tmp_path / "cost.jsonl"
        log = ReplayLog(path, game_id="g-6")
        log.record_failed_call(
            meeting_id="g-6:meeting-0",
            tick=200,
            model="claude-sonnet-4-6",
            prompt_length=1000,
            raw_response="...",
            input_tokens=500,
            output_tokens=300,
            cost_usd=0.0075,
            error_type="ValidationError",
            error_message="boom",
        )

        assert compute_cost_usd(path) == 0.0075

    def test_compute_cost_usd_is_zero_for_game_end_only_replay(
        self, tmp_path: Path
    ) -> None:
        path = tmp_path / "no-cost.jsonl"
        ReplayLog(path, game_id="g-7").record_game_end(
            winner="CREWMATES", reason="CREWMATE_TASKS"
        )

        assert compute_cost_usd(path) == 0.0


class TestFailedCallSingleWriteGuard:
    """Byte-identical failed-call rows write once (Task 9.10, audit gp-4).

    The lived incident (MECH-B-1): a deterministic provider (seeded local
    model, fixed prompt) regenerates the SAME failing response on the in-turn
    retry, so a single defaulted opening surfaced the same burned generation
    twice and seeds 8/36/39 each persisted a duplicate ``failed_call`` row —
    double-counting 5,969 input / 6,144 output tokens and inflating
    ``total_failed_calls`` 4→7. ``record_failed_call`` now drops a row that is
    byte-identical (the FULL frozen entry) to one this log already wrote.
    Distinct rows — including zero-spend ``deadline_default`` visibility
    markers that share the zero ``(model, raw_response, input_tokens,
    output_tokens)`` tuple but name different participants in
    ``error_message`` — still each record once.
    """

    @staticmethod
    def _record_seed_shape_row(
        log: ReplayLog,
        *,
        model: str = "Qwen/Qwen3-32B",
        raw_response: str = '{\n  "turn_id": "t",\n  "turn_index": 0,\n  "speaker": "p-2"',
        input_tokens: int = 1984,
        output_tokens: int = 2048,
        error_message: str = (
            "opening turn (turn 0) defaulted (validation); p-2 submitted no "
            "turn [ValidationError: EOF while parsing a string]"
        ),
    ) -> None:
        # Field values mirror the committed seed-8 duplicate (meeting-1,
        # tick 14) — the audited double-count shape.
        log.record_failed_call(
            meeting_id="headless-seed-8:meeting-1",
            tick=14,
            model=model,
            prompt_length=6627,
            raw_response=raw_response,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=0.0,
            error_type="deadline_default",
            error_message=error_message,
        )

    def test_byte_identical_retry_row_records_exactly_once(
        self, tmp_path: Path
    ) -> None:
        # The seed-8/36/39 shape: the opening's single retry burned a
        # byte-identical generation, so the defaulted turn issues the same
        # write twice; exactly one row may land.
        path = tmp_path / "dedup.jsonl"
        with ReplayLog(path, game_id="headless-seed-8") as log:
            self._record_seed_shape_row(log)
            self._record_seed_shape_row(log)

        failed = read_failed_call_entries(path)
        assert len(failed) == 1
        # The spend is counted once, not doubled.
        assert sum(f.input_tokens for f in failed) == 1984
        assert sum(f.output_tokens for f in failed) == 2048

    def test_distinct_failures_in_one_meeting_each_record_once(
        self, tmp_path: Path
    ) -> None:
        # Two genuinely different burned generations in the same meeting
        # (different raw response / spend) are NOT duplicates.
        path = tmp_path / "distinct.jsonl"
        with ReplayLog(path, game_id="headless-seed-8") as log:
            self._record_seed_shape_row(log)
            self._record_seed_shape_row(
                log,
                raw_response='{\n  "turn_id": "t",\n  "claims": [',
                output_tokens=903,
            )

        failed = read_failed_call_entries(path)
        assert len(failed) == 2
        assert sum(f.output_tokens for f in failed) == 2048 + 903

    def test_zero_spend_markers_for_different_defaults_each_record_once(
        self, tmp_path: Path
    ) -> None:
        # Two zero-spend visibility markers (a defaulted turn and a defaulted
        # vote) share the zero (model, raw_response, tokens) tuple and differ
        # only in error_message; deduping on the FULL row keeps both visible.
        path = tmp_path / "markers.jsonl"
        with ReplayLog(path, game_id="g-1") as log:
            for message in (
                "reply turn (turn 2) defaulted (deadline); p-2 submitted no turn",
                "vote defaulted (deadline); p-3 submitted no ballot",
            ):
                log.record_failed_call(
                    meeting_id="g-1:meeting-0",
                    tick=30,
                    model="(deadline_default)",
                    prompt_length=0,
                    raw_response="",
                    input_tokens=0,
                    output_tokens=0,
                    cost_usd=0.0,
                    error_type="deadline_default",
                    error_message=message,
                )

        assert len(read_failed_call_entries(path)) == 2

    def test_guard_is_per_log_not_per_process(self, tmp_path: Path) -> None:
        # The same failure shape in a DIFFERENT game's log is a different
        # burned call and must still record.
        with ReplayLog(tmp_path / "a.jsonl", game_id="g-a") as log:
            self._record_seed_shape_row(log)
        with ReplayLog(tmp_path / "b.jsonl", game_id="g-b") as log:
            self._record_seed_shape_row(log)

        assert len(read_failed_call_entries(tmp_path / "a.jsonl")) == 1
        assert len(read_failed_call_entries(tmp_path / "b.jsonl")) == 1

    def test_committed_9p2i_rows_rerecord_to_their_distinct_set(
        self, tmp_path: Path
    ) -> None:
        # Offline confirmation against the committed 9p2i set: re-recording
        # each replay's failed-call rows through the guarded chokepoint yields
        # exactly its distinct rows in order. On the Qwen/Qwen3-32B qwen3_32b.v3
        # re-record the committed bytes carry no duplicate failed-call shapes —
        # every seed's rows are already distinct, so clean bytes re-record to
        # themselves (including the rendered_vote_max carried on vote defaults,
        # e.g. seeds 21/34/36).
        sample_files = sorted(_COMMITTED_9P2I_REPLAYS.glob("replay-seed-*.jsonl"))
        assert sample_files, f"no committed replays under {_COMMITTED_9P2I_REPLAYS}"
        for sample in sample_files:
            originals = read_failed_call_entries(sample)
            if not originals:
                continue
            distinct = list(dict.fromkeys(originals))
            rerecord_path = tmp_path / sample.name
            with ReplayLog(rerecord_path, game_id=originals[0].game_id) as log:
                for entry in originals:
                    log.record_failed_call(
                        meeting_id=entry.meeting_id,
                        tick=entry.tick,
                        model=entry.model,
                        prompt_length=entry.prompt_length,
                        raw_response=entry.raw_response,
                        input_tokens=entry.input_tokens,
                        output_tokens=entry.output_tokens,
                        cost_usd=entry.cost_usd,
                        error_type=entry.error_type,
                        error_message=entry.error_message,
                        rendered_vote_max=entry.rendered_vote_max,
                    )
            assert list(read_failed_call_entries(rerecord_path)) == distinct


class TestLLMCallRecordAgentId:
    """``LLMCallRecord.agent_id`` per-call attribution (Task 4.7, §5, §11.4)."""

    def test_agent_id_round_trips_through_jsonl(self) -> None:
        record = LLMCallRecord(
            call_kind="meeting",
            model="claude-test",
            prompt="## Your role: CREWMATE",
            response_text='{"ok": true}',
            input_tokens=10,
            output_tokens=5,
            cost_usd=0.01,
            agent_id="p-2",
        )

        restored = LLMCallRecord.model_validate_json(record.model_dump_json())

        assert restored == record
        assert restored.agent_id == "p-2"

    def test_missing_agent_id_defaults_to_none(self) -> None:
        # A replay JSONL written before this field existed has no agent_id
        # key. ``extra="forbid"`` rejects unknown fields but still permits a
        # missing optional one, so old replays load with agent_id=None.
        legacy_line = (
            '{"call_kind": "meeting", "model": "claude-test", "prompt": "p", '
            '"response_text": "r", "input_tokens": 1, "output_tokens": 1, '
            '"cost_usd": 0.0}'
        )

        record = LLMCallRecord.model_validate_json(legacy_line)

        assert record.agent_id is None


class TestWriteSideFailLoud:
    """``ReplayLog.__init__`` refuses an existing path unless ``force=True``.

    Write-side guard for Task 4.16 (DESIGN.md §11.4): re-using a replay path
    used to silently append a second game's rows, doubling the file.
    """

    def test_constructing_against_existing_file_raises(self, tmp_path: Path) -> None:
        path = tmp_path / "replay.jsonl"
        state = scripted_initial_world_state(seed=1)
        ReplayLog(path, game_id="g-1").record_tick(0, [], state)

        with pytest.raises(ReplayLog.AlreadyExistsError) as excinfo:
            ReplayLog(path, game_id="g-1")

        assert str(path) in str(excinfo.value)

    def test_already_exists_error_is_a_file_exists_error(self, tmp_path: Path) -> None:
        # Subclassing FileExistsError lets callers that only catch the stdlib
        # type still intercept the fail-loud.
        path = tmp_path / "replay.jsonl"
        ReplayLog(path, game_id="g-1").record_game_end(
            winner="CREWMATES", reason="done"
        )

        with pytest.raises(FileExistsError):
            ReplayLog(path, game_id="g-1")

    def test_force_true_truncates_previous_content(self, tmp_path: Path) -> None:
        path = tmp_path / "replay.jsonl"
        state = scripted_initial_world_state(seed=1)
        ReplayLog(path, game_id="g-old").record_tick(0, [], state)

        # force=True deletes the old file before recording, so the previous
        # game's rows are gone and no doubled-write can happen. Nothing is on
        # disk until the next append.
        reopened = ReplayLog(path, game_id="g-new", force=True)
        assert not path.exists()

        reopened.record_tick(0, [], state)
        entries = read_all_entries(path)
        assert len(entries) == 1
        entry = entries[0]
        assert isinstance(entry, ReplayEntry)
        assert entry.game_id == "g-new"
        assert entry.tick == 0

    def test_constructing_against_fresh_path_succeeds(self, tmp_path: Path) -> None:
        # The common case: a brand-new path needs no force.
        path = tmp_path / "fresh.jsonl"
        ReplayLog(path, game_id="g-1").record_game_end(
            winner="CREWMATES", reason="done"
        )

        assert read_game_outcome(path) == "CREWMATES"


class TestReadSideDoubledFileDetection:
    """``read_all_entries`` fails loud on the doubled-file pattern (Task 4.16).

    The lived incident: two tournament runs against the same ``--output-dir``
    concatenated per-seed JSONLs. A doubled file has overlapping ``tick``
    values and/or two ``game_over`` rows.
    """

    def test_duplicate_tick_raises_naming_path_and_tick(self, tmp_path: Path) -> None:
        path = tmp_path / "doubled-ticks.jsonl"
        tick_row = (
            '{"kind":"tick","game_id":"g-1","tick":0,"actions":[],'
            '"state_hash":"deadbeef"}'
        )
        path.write_text(f"{tick_row}\n{tick_row}\n", encoding="utf-8")

        with pytest.raises(ReplayLog.CorruptedFileError) as excinfo:
            read_all_entries(path)

        message = str(excinfo.value)
        assert "Duplicate tick 0" in message
        assert str(path) in message

    def test_two_game_over_rows_raise_naming_path(self, tmp_path: Path) -> None:
        path = tmp_path / "doubled-overs.jsonl"
        over_row = (
            '{"kind":"game_over","game_id":"g-1","winner":"CREWMATES","reason":"done"}'
        )
        path.write_text(f"{over_row}\n{over_row}\n", encoding="utf-8")

        with pytest.raises(ReplayLog.CorruptedFileError) as excinfo:
            read_all_entries(path)

        message = str(excinfo.value)
        assert "game_over" in message
        assert str(path) in message

    def test_clean_single_game_reads_without_raising(self, tmp_path: Path) -> None:
        # A normal game — strictly increasing ticks, exactly one game_over —
        # is unaffected by the doubled-file detection.
        path = tmp_path / "clean.jsonl"
        state = scripted_initial_world_state(seed=1)
        log = ReplayLog(path, game_id="g-1")
        log.record_tick(0, [], state)
        log.record_tick(1, [], state)
        log.record_game_end(winner="CREWMATES", reason="done")

        entries = read_all_entries(path)

        assert len(entries) == 3
