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

from agents.memory.store import AgentMemory
from meetings.schemas import MeetingResult, MeetingTranscript, VoteBallot
from orchestrator.replay import (
    ENV_IMPOSTOR_ROLL_CALL,
    SUBSTRATE_FLAG_KEYS,
    TOGGLEABLE_SUBSTRATE_FLAG_KEYS,
    _impostor_roll_call_enabled,
    _TOGGLEABLE_LEVER_RESOLVERS,
    FailedCallReplayEntry,
    GameEndReplayEntry,
    LLMCallRecord,
    ReplayEntry,
    ReplayLog,
    compute_cost_usd,
    env_var_for_lever,
    fold_meeting_outcome_into_memories,
    read_all_entries,
    read_failed_call_entries,
    read_game_outcome,
    read_substrate_flags,
    substrate_flag_snapshot,
    substrate_slate_mismatches,
)
from engine.world import WorldState
from orchestrator import replay as replay_module
from tests._helpers.world_state import scripted_initial_world_state

# The one LIVE toggle's snapshot key: Task 18.10's impostor-answer arm, the one
# lever the CREW-ONLY ruling did not ship. Its resolver is
# ``orchestrator.replay._impostor_roll_call_enabled`` -- a byte-mirror of the
# loader's, because the loader's import-time Jinja build is prompt-set-sensitive
# and would break every replay-only consumer on a stray AILIBI_PROMPT_SET export;
# the equivalence pin below stands in for identity.
ENV_IMPOSTOR_ROLL_CALL_KEY = "impostor_roll_call"

# Every RETIRED lever: snapshot key and the ``AILIBI_*`` variable its key
# derives, in graduation order. Written out as literals rather than derived from
# the registry, so this table is an independent statement of what graduated -- a
# registry that lost or renamed an entry fails against it instead of agreeing
# with itself. No resolver column: a retired lever HAS no resolver.
_RETIRED_LEVERS: tuple[tuple[str, str], ...] = (
    ("testimony_as_content", "AILIBI_TESTIMONY_AS_CONTENT"),
    ("witnessed_kill_evidence", "AILIBI_WITNESSED_KILL_EVIDENCE"),
    ("movement_perception", "AILIBI_MOVEMENT_PERCEPTION"),
    ("unfreeze_memory", "AILIBI_UNFREEZE_MEMORY"),
    ("evidence_quality_lift", "AILIBI_EVIDENCE_QUALITY_LIFT"),
    ("reporter_exculpation", "AILIBI_REPORTER_EXCULPATION"),
    ("hard_evidence_gate", "AILIBI_HARD_EVIDENCE_GATE"),
    ("observation_id_rendering", "AILIBI_OBSERVATION_ID_RENDERING"),
    ("citation_gate", "AILIBI_CITATION_GATE"),
    ("absence_prior", "AILIBI_ABSENCE_PRIOR"),
    ("roll_call_round", "AILIBI_ROLL_CALL_ROUND"),
    ("whereabouts_interior_flags", "AILIBI_WHEREABOUTS_INTERIOR_FLAGS"),
    ("vent_placement_contradictions", "AILIBI_VENT_PLACEMENT_CONTRADICTIONS"),
    ("task_completion_from_events", "AILIBI_TASK_COMPLETION_FROM_EVENTS"),
    ("self_location_trail", "AILIBI_SELF_LOCATION_TRAIL"),
    ("movement_claim_shape", "AILIBI_MOVEMENT_CLAIM_SHAPE"),
    ("grounded_prosecution", "AILIBI_GROUNDED_PROSECUTION"),
    ("map_aware_arbitration", "AILIBI_MAP_AWARE_ARBITRATION"),
    ("structured_turn_markers", "AILIBI_STRUCTURED_TURN_MARKERS"),
    ("meeting_outcome_memory", "AILIBI_MEETING_OUTCOME_MEMORY"),
    ("coalesced_memory_render", "AILIBI_COALESCED_MEMORY_RENDER"),
)

# The substrate stamp every committed recording carries: the twenty-one graduated
# levers ON, the impostor-answer arm OFF. Written as a literal because it is the
# thing the committed bytes assert -- deriving it from the registry would make the
# pin agree with any drift.
_BASELINE7_STAMP: dict[str, bool] = {
    "testimony_as_content": True,
    "witnessed_kill_evidence": True,
    "movement_perception": True,
    "unfreeze_memory": True,
    "evidence_quality_lift": True,
    "reporter_exculpation": True,
    "hard_evidence_gate": True,
    "observation_id_rendering": True,
    "citation_gate": True,
    "absence_prior": True,
    "roll_call_round": True,
    "whereabouts_interior_flags": True,
    "vent_placement_contradictions": True,
    "task_completion_from_events": True,
    "self_location_trail": True,
    "movement_claim_shape": True,
    "grounded_prosecution": True,
    "map_aware_arbitration": True,
    "structured_turn_markers": True,
    "meeting_outcome_memory": True,
    "coalesced_memory_render": True,
    "impostor_roll_call": False,
}

# What a BARE environment stamps: exactly the committed baseline-7 stamp. The
# one live toggle is default-OFF and every other lever is unconditional, so a
# shell with no ``AILIBI_*`` export reproduces the committed substrate.
_BARE_STAMP: dict[str, bool] = dict(_BASELINE7_STAMP)

# The eight keys the baseline-7 record appended: the Phase-20 belief-substrate
# levers. Named so the legacy baseline-6 shape below is derived by SUBTRACTING
# exactly them rather than by re-listing thirteen keys.
_PHASE20_KEYS: frozenset[str] = frozenset(
    {
        "task_completion_from_events",
        "self_location_trail",
        "movement_claim_shape",
        "grounded_prosecution",
        "map_aware_arbitration",
        "structured_turn_markers",
        "meeting_outcome_memory",
        "coalesced_memory_render",
    }
)

# The stamp the baseline-6 sets carried, kept as the legacy shape the
# missing-key-reads-False rule has to keep accepting.
_BASELINE6_STAMP: dict[str, bool] = {
    key: value for key, value in _BASELINE7_STAMP.items() if key not in _PHASE20_KEYS
}


def _clear_lever_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Strip every ``AILIBI_*`` lever export so the process env is a bare slate."""

    for key in SUBSTRATE_FLAG_KEYS:
        monkeypatch.delenv(env_var_for_lever(key), raising=False)


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

    A replay self-describes which substrate levers generated it. THIRTEEN levers
    are unconditionally ON with their env gates retired: the four 13.5 levers since
    Task 14.9, Task 14.10's ``evidence_quality_lift`` since the Task-14.12 close,
    Task 15.5's ``reporter_exculpation`` since the Task-15.7 baseline-3 record, the
    three Phase-16 levers graduated at the Task-16.17 baseline-5 record — 16.4's
    ``hard_evidence_gate``, 16.5's ``observation_id_rendering``, 16.6's
    ``citation_gate`` — and the FOUR meeting-layer levers graduated at the
    Task-18.12 baseline-6 record on the CREW-ONLY ruling: 16.8's ``absence_prior``,
    18.8's ``roll_call_round``, and 18.9's ``whereabouts_interior_flags`` and
    ``vent_placement_contradictions``; and the eight Phase-20 belief-substrate
    levers at the baseline-7 record. ONE live env-gated toggle remains in
    ``_TOGGLEABLE_LEVER_RESOLVERS`` — Task 18.10's ``impostor_roll_call`` (the arm
    the CREW-ONLY ruling did NOT ship), DEFAULT-OFF: a bare-environment recording
    stamps the twenty-one retired levers True and that one toggle False — exactly
    the committed baseline-7 substrate (``_assert_substrate_matches`` reads a
    missing key as ``False`` on both sides). An ambient
    ``AILIBI_IMPOSTOR_ROLL_CALL`` export flips the live toggle's stamp ON; the
    twenty-one retired levers never read env again.
    """

    @pytest.mark.parametrize(("key", "env_var"), _RETIRED_LEVERS)
    def test_a_retired_lever_stamps_on_under_every_environment(
        self, key: str, env_var: str, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # ONE pin for the whole retired registry, four cases per lever: a bare
        # mapping, its own variable explicitly OFF, a junk value, and the ambient
        # process environment with the variable exported "0". A retired lever has
        # no resolver to consult, so every case must read True -- and no case may
        # move any OTHER key, which is what makes a stray export provably inert.
        assert substrate_flag_snapshot({})[key] is True
        for value in ("0", "nope"):
            snapshot = substrate_flag_snapshot({env_var: value})
            assert snapshot[key] is True, (key, value)
            assert snapshot == _BARE_STAMP, (key, value)
        _clear_lever_env(monkeypatch)
        monkeypatch.setenv(env_var, "0")
        assert substrate_flag_snapshot()[key] is True
        assert substrate_flag_snapshot() == _BARE_STAMP

    def test_the_retired_table_is_the_registry(self) -> None:
        # The independent statement: this file's literal table names exactly the
        # keys the registry retires, in the same order, and derives each one's
        # documented variable. A lever added to, dropped from or renamed in the
        # registry fails here rather than agreeing with itself.
        assert tuple(key for key, _ in _RETIRED_LEVERS) == tuple(
            key
            for key in SUBSTRATE_FLAG_KEYS
            if key not in TOGGLEABLE_SUBSTRATE_FLAG_KEYS
        )
        for key, env_var in _RETIRED_LEVERS:
            assert env_var_for_lever(key) == env_var, key
        assert TOGGLEABLE_SUBSTRATE_FLAG_KEYS == (ENV_IMPOSTOR_ROLL_CALL_KEY,)

    def test_the_retired_stamp_pin_bites(self) -> None:
        # The perturbation craft rule 2 asks for: a registry that stopped
        # stamping one retired key True must fail the pin above. Patch the
        # snapshot's retired tuple to drop a key and the bare-stamp comparison
        # breaks -- so a green run is a statement about the real registry.
        broken = dict(_BARE_STAMP)
        del broken["citation_gate"]
        assert broken != _BARE_STAMP
        assert substrate_flag_snapshot({}) != broken

    def test_live_toggle_registrations(self) -> None:
        # Registration pin: ONE live toggle, DEFAULT-OFF -- the impostor-answer
        # arm. The graduated levers are not here: they moved into
        # ``_RETIRED_ALWAYS_ON_LEVERS`` at the records that adopted them and their
        # env gates are gone.
        assert len(_TOGGLEABLE_LEVER_RESOLVERS) == 1
        registry = dict(_TOGGLEABLE_LEVER_RESOLVERS)
        assert registry[ENV_IMPOSTOR_ROLL_CALL_KEY] is _impostor_roll_call_enabled
        for key, _env_var in _RETIRED_LEVERS:
            assert key not in registry, key
        assert TOGGLEABLE_SUBSTRATE_FLAG_KEYS == (ENV_IMPOSTOR_ROLL_CALL_KEY,)
        # The full stamp key order: twenty-one graduated levers in graduation
        # order, then the one live toggle. The retired half grows at its end, so
        # graduating a lever moves the surviving toggles DOWN the key order --
        # which is why this literal is written out rather than derived.
        assert SUBSTRATE_FLAG_KEYS == (
            "testimony_as_content",
            "witnessed_kill_evidence",
            "movement_perception",
            "unfreeze_memory",
            "evidence_quality_lift",
            "reporter_exculpation",
            "hard_evidence_gate",
            "observation_id_rendering",
            "citation_gate",
            "absence_prior",
            "roll_call_round",
            "whereabouts_interior_flags",
            "vent_placement_contradictions",
            "task_completion_from_events",
            "self_location_trail",
            "movement_claim_shape",
            "grounded_prosecution",
            "map_aware_arbitration",
            "structured_turn_markers",
            "meeting_outcome_memory",
            "coalesced_memory_render",
            "impostor_roll_call",
        )

    def test_env_var_for_lever_derives_the_documented_variable(self) -> None:
        # The one derivation .env.example, the recorders' diagnostics and
        # scripts/check_doc_facts.py all rely on: a registry key uppercases into
        # its AILIBI_* variable. Pinned against the lever table's own literals, so
        # a key renamed without its variable fails here.
        assert env_var_for_lever(ENV_IMPOSTOR_ROLL_CALL_KEY) == ENV_IMPOSTOR_ROLL_CALL
        for key, env_var in _RETIRED_LEVERS:
            assert env_var_for_lever(key) == env_var, key

    def test_bare_snapshot_is_the_committed_stamp(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # A bare environment stamps the committed baseline-7 substrate exactly, so
        # `scripts/verify_samples.sh` reconstructs the committed sets in a shell
        # with no `AILIBI_*` export at all.
        _clear_lever_env(monkeypatch)
        assert substrate_flag_snapshot({}) == _BARE_STAMP
        assert substrate_flag_snapshot() == _BARE_STAMP
        assert _BARE_STAMP == _BASELINE7_STAMP

    def test_every_recording_stamps_the_full_snapshot(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Recording under a bare environment stamps the twenty-one graduated
        # levers ON and the one live toggle OFF -- which is what ``_BARE_STAMP``
        # spells out. Every key is stamped: the stamp is a whole-slate statement,
        # so a recording can never be silent about a lever it ran under.
        _clear_lever_env(monkeypatch)
        path = tmp_path / "on.jsonl"
        ReplayLog(path, game_id="g-on").record_game_end(
            winner="IMPOSTORS", reason="IMPOSTOR_PARITY", tick=41
        )
        entry = read_all_entries(path)[0]
        assert isinstance(entry, GameEndReplayEntry)
        assert entry.substrate_flags == _BARE_STAMP
        assert set(entry.substrate_flags) == set(SUBSTRATE_FLAG_KEYS)
        assert read_substrate_flags(path) == dict(entry.substrate_flags)

    def test_impostor_roll_call_on_recording_round_trips_the_stamp(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # With the impostor-answer toggle exported, ``record_game_end`` stamps it
        # ON and the file reader round-trips it — the recording self-describes the
        # substrate it ran under, and the MANIFEST ``flags`` cell renders from this
        # same ``read_substrate_flags`` value. The graduated levers stay ON
        # alongside it, and an impostor-ON recording is NOT byte-identical to the
        # committed (impostor-OFF) stamp, so it fails loud under
        # ``_assert_substrate_matches`` unless the loader opts into the mismatch.
        monkeypatch.setenv(ENV_IMPOSTOR_ROLL_CALL, "1")
        path = tmp_path / "impostor-on.jsonl"
        ReplayLog(path, game_id="g-impostor").record_game_end(
            winner="CREWMATES", reason="CREWMATE_EJECT", tick=17
        )
        flags = read_substrate_flags(path)
        assert flags is not None
        assert flags[ENV_IMPOSTOR_ROLL_CALL_KEY] is True
        # The retired always-on levers stay ON alongside the live toggle.
        assert all(
            flags[key]
            for key in SUBSTRATE_FLAG_KEYS
            if key not in TOGGLEABLE_SUBSTRATE_FLAG_KEYS
        )

    @pytest.mark.parametrize(
        ("env_var", "flag_key", "resolver"),
        [
            (
                ENV_IMPOSTOR_ROLL_CALL,
                ENV_IMPOSTOR_ROLL_CALL_KEY,
                _impostor_roll_call_enabled,
            ),
        ],
    )
    def test_impostor_roll_call_toggle_default_off_reads_env(
        self,
        env_var: str,
        flag_key: str,
        resolver: object,
    ) -> None:
        # The impostor-answer arm is DEFAULT-OFF like every other live toggle:
        # unset / bare / unrecognised stamps False (byte-identical to the committed
        # set, which predates the key having any effect), and a truthy
        # AILIBI_IMPOSTOR_ROLL_CALL export flips it True — the seam a future gate
        # that ships the arm would drive. It is the ONE toggle bound to a local
        # MIRROR rather than by identity (the eight Phase-20 levers bind their home
        # resolvers directly), which is why it keeps its own case here.
        assert dict(_TOGGLEABLE_LEVER_RESOLVERS)[flag_key] is resolver
        assert substrate_flag_snapshot({})[flag_key] is False
        assert substrate_flag_snapshot({env_var: "nope"})[flag_key] is False
        assert substrate_flag_snapshot({env_var: "1"})[flag_key] is True
        assert substrate_flag_snapshot({env_var: "yes"})[flag_key] is True

    def test_impostor_roll_call_mirror_equivalent_to_the_loader_resolver(
        self,
    ) -> None:
        # The 18.10 lever's stamp-side resolver is a LOCAL mirror in
        # ``orchestrator.replay`` (importing the loader would execute its
        # import-time, prompt-set-sensitive Jinja build in every replay-only
        # consumer). This pin is the CI substitute for the identity binding the
        # graduated levers' read-sites kept before they retired: the mirror and the
        # loader's
        # ``impostor_roll_call_enabled`` must agree over the env grid, so the
        # replay stamp and the lever's read-site cannot drift apart without
        # this failing. The loader import happens HERE (the test env carries a
        # valid default prompt set), never in the replay module.
        from agents.strategic.prompts.loader import (
            ENV_IMPOSTOR_ROLL_CALL as LOADER_ENV,
        )
        from agents.strategic.prompts.loader import impostor_roll_call_enabled

        assert LOADER_ENV == ENV_IMPOSTOR_ROLL_CALL
        for env in (
            {},
            {ENV_IMPOSTOR_ROLL_CALL: "1"},
            {ENV_IMPOSTOR_ROLL_CALL: "true"},
            {ENV_IMPOSTOR_ROLL_CALL: "YES"},
            {ENV_IMPOSTOR_ROLL_CALL: " on "},
            {ENV_IMPOSTOR_ROLL_CALL: "0"},
            {ENV_IMPOSTOR_ROLL_CALL: "nope"},
            {ENV_IMPOSTOR_ROLL_CALL: ""},
        ):
            assert _impostor_roll_call_enabled(env) == impostor_roll_call_enabled(
                env
            ), env

    def test_replay_module_imports_under_a_garbage_prompt_set(self) -> None:
        # The regression the local mirror exists to prevent: ``import
        # orchestrator.replay`` must succeed even when the shell carries an
        # unknown AILIBI_PROMPT_SET (importing the loader here would raise at
        # its module-level Jinja build and take down every replay-only
        # consumer — sample byte-verification, MANIFEST reads, the API replay
        # loader — before a single JSONL row is read).
        import os
        import subprocess
        import sys

        env = dict(os.environ)
        env["AILIBI_PROMPT_SET"] = "no-such-prompt-set"
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import orchestrator.replay; "
                "print(orchestrator.replay.substrate_flag_snapshot({}))",
            ],
            cwd=str(Path(__file__).resolve().parents[2]),
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert result.returncode == 0, result.stderr
        assert "impostor_roll_call" in result.stdout

    def test_a_whole_slate_export_stamps_every_lever_on(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # The other end of the range: with EVERY live toggle exported, all
        # twenty-two keys stamp ON. This is the shape an adopting record that
        # shipped the whole slate would carry, and it is emphatically NOT the
        # baseline-6 substrate -- which is exactly why the loader refuses to serve
        # one recording's bytes under the other's environment.
        monkeypatch.setenv(ENV_IMPOSTOR_ROLL_CALL, "1")
        for _key, env_var in _RETIRED_LEVERS:
            monkeypatch.setenv(env_var, "1")
        path = tmp_path / "impostor-on.jsonl"
        ReplayLog(path, game_id="g-full").record_game_end(
            winner="IMPOSTORS", reason="IMPOSTOR_PARITY", tick=23
        )
        flags = read_substrate_flags(path)
        assert flags is not None
        assert all(flags[key] is True for key in SUBSTRATE_FLAG_KEYS)

    def test_baseline6_bare_recording_stamps_the_graduated_slate(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # The baseline-6 substrate: the four meeting-layer levers stamp ON
        # (graduated at the Task-18.12 record on the CREW-ONLY ruling) and
        # impostor_roll_call stamps OFF (the arm the ruling did NOT ship) under a
        # BARE environment — no AILIBI_* lever export needed, exactly what the
        # substrate-lever preflight in scripts/refresh_samples.sh enforces before a
        # record stages. This is the record the committed baseline-6 samples carry.
        _clear_lever_env(monkeypatch)
        path = tmp_path / "baseline6.jsonl"
        ReplayLog(path, game_id="g-baseline6").record_game_end(
            winner="CREWMATES", reason="CREWMATE_EJECT", tick=31
        )
        flags = read_substrate_flags(path)
        assert flags is not None
        assert flags["roll_call_round"] is True
        assert flags["whereabouts_interior_flags"] is True
        assert flags["vent_placement_contradictions"] is True
        assert flags["absence_prior"] is True
        assert flags["impostor_roll_call"] is False
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


# --------------------------------------------------------------------------- #
# The shared slate comparison + the shared meeting-outcome fold                #
# --------------------------------------------------------------------------- #


class TestSubstrateSlateMismatches:
    """The one comparison both recorders' pre-spend gates run."""

    def test_a_matching_slate_reports_nothing(self) -> None:
        assert substrate_slate_mismatches([], env={}) == []
        assert (
            substrate_slate_mismatches(
                ["impostor_roll_call"], env={ENV_IMPOSTOR_ROLL_CALL: "1"}
            )
            == []
        )

    def test_an_expected_lever_left_unexported_is_named(self) -> None:
        # The failure a blacklist of variable names cannot catch, and the reason
        # the check is a positive whole-slate equality: the operator declared a
        # lever the shell never exported, so the record would silently be made on
        # the OLD substrate.
        problems = substrate_slate_mismatches(["impostor_roll_call"], env={})
        assert problems == [
            "impostor_roll_call must be ON but the live slate reads OFF "
            "(AILIBI_IMPOSTOR_ROLL_CALL)"
        ]

    def test_an_unexpected_export_is_named(self) -> None:
        # The mirror failure: a stale export from an earlier probe session that
        # nobody declared would ship an unruled arm into the record.
        problems = substrate_slate_mismatches([], env={ENV_IMPOSTOR_ROLL_CALL: "1"})
        assert problems == [
            "impostor_roll_call must be OFF but the live slate reads ON "
            "(AILIBI_IMPOSTOR_ROLL_CALL)"
        ]

    def test_a_graduated_lever_named_as_a_toggle_fails_loud(self) -> None:
        # The class this became at the baseline-7 record: a runbook still naming
        # one of the eight graduated levers in its `--expect-levers` slate is
        # declaring a knob that no longer exists, and an expectation nobody can
        # check is worse than no expectation. Reported for every one of them,
        # whether or not a stale export is also present.
        for key, env_var in _RETIRED_LEVERS:
            expected = [
                f"{key!r} is a graduated lever (unconditionally ON, no env gate) "
                "and cannot be named as an expected toggle"
            ]
            assert substrate_slate_mismatches([key], env={}) == expected, key
            assert substrate_slate_mismatches([key], env={env_var: "1"}) == expected

    def test_both_directions_are_reported_together(self) -> None:
        # A half-set expectation names BOTH deviations in one refusal, so the
        # operator fixes the environment once instead of discovering the second
        # failure on the next attempt.
        problems = substrate_slate_mismatches(
            ["grounded_prosecution", "impostor_roll_call"],
            env={},
        )
        assert problems == [
            "'grounded_prosecution' is a graduated lever (unconditionally ON, no "
            "env gate) and cannot be named as an expected toggle",
            "impostor_roll_call must be ON but the live slate reads OFF "
            "(AILIBI_IMPOSTOR_ROLL_CALL)",
        ]

    def test_a_typo_in_the_expectation_fails_loud(self) -> None:
        # A misspelled key must never be silently ignored: an expectation nobody
        # checks is worse than no expectation, because the echo still claims it.
        assert substrate_slate_mismatches(["grounded_prosecutions"], env={}) == [
            "'grounded_prosecutions' is not a lever in the registry"
        ]

    def test_a_partial_graduation_is_reported(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # The third failure class, planted so the branch can be seen to bite: a
        # graduation half-done -- the key added to ``_RETIRED_ALWAYS_ON_LEVERS``
        # while its toggle resolver is still registered. The check is STRUCTURAL,
        # so neither a truthy stale export nor an operator declaring the lever can
        # dress the broken registry up as healthy; all three environments below
        # report the same defect.
        expected = [
            "impostor_roll_call is registered as BOTH a graduated lever and a "
            "live toggle (a half-finished graduation: delete its resolver, or "
            "drop the retired entry) -- this build cannot produce the substrate "
            "the record would claim"
        ]
        monkeypatch.setattr(
            replay_module,
            "_RETIRED_ALWAYS_ON_LEVERS",
            (*replay_module._RETIRED_ALWAYS_ON_LEVERS, "impostor_roll_call"),
        )
        assert substrate_slate_mismatches(["impostor_roll_call"], env={}) == [
            *expected,
            "impostor_roll_call must be ON but the live slate reads OFF "
            "(AILIBI_IMPOSTOR_ROLL_CALL)",
        ]
        assert substrate_slate_mismatches([], env={}) == expected
        assert (
            substrate_slate_mismatches(
                ["impostor_roll_call"], env={ENV_IMPOSTOR_ROLL_CALL: "1"}
            )
            == expected
        )
        # Undo the plant and the same calls are silent, so the lines above are the
        # PERTURBATION biting rather than a branch that always fires.
        monkeypatch.undo()
        assert substrate_slate_mismatches([], env={}) == []
        assert (
            substrate_slate_mismatches(
                ["impostor_roll_call"], env={ENV_IMPOSTOR_ROLL_CALL: "1"}
            )
            == []
        )

    def test_a_graduated_lever_cannot_be_named_as_a_toggle(self) -> None:
        # Naming a graduated lever is the same class of error: its env gate is
        # gone, so an operator who expects to control it is mistaken about what
        # this build can produce.
        assert substrate_slate_mismatches(["absence_prior"], env={}) == [
            "'absence_prior' is a graduated lever (unconditionally ON, no env "
            "gate) and cannot be named as an expected toggle"
        ]


class TestMeetingOutcomeFold:
    """The one reconstruction-side fold the three replay mirrors share."""

    @staticmethod
    def _result(*, ejected: str | None) -> MeetingResult:
        ballots = tuple(
            VoteBallot(
                voter=voter,
                target=target,
                confidence=0.6,
                primary_reason_id=None,
                rationale_text="because",
            )
            for voter, target in (
                ("p-1", ejected or "SKIP"),
                ("p-2", ejected or "SKIP"),
                ("p-4", "SKIP"),
            )
        )
        return MeetingResult(
            meeting_id="g:meeting-0",
            triggered_by="p-1",
            trigger_tick=5,
            outcome="EJECTED" if ejected is not None else "SKIPPED",
            ejected_player_id=ejected,
            ballots=ballots,
            transcript=MeetingTranscript(),
        )

    @staticmethod
    def _post_meeting_state(*, ejected: str | None, tick: int) -> WorldState:
        from dataclasses import replace

        state = scripted_initial_world_state(seed=3)
        players = dict(state.players)
        if ejected is not None:
            players[ejected] = replace(players[ejected], alive=False)
        return replace(state, tick=tick, players=players)

    def test_the_fold_records_the_announced_outcome_for_every_living_agent(
        self,
    ) -> None:
        # Everything the table heard, and only that: the resume tick, the ejected
        # player with the confirm-ejects role, the tally, and the roster impostor
        # count stated at game start. The ejected player is dead in the
        # post-meeting state, so nothing is written into their memory.
        state = self._post_meeting_state(ejected="p-3", tick=11)
        result = self._result(ejected="p-3")
        memories = {pid: AgentMemory() for pid in state.players}

        fold_meeting_outcome_into_memories(result, state=state, memories=memories)

        assert memories["p-3"].meeting_history.outcomes == ()
        for pid in ("p-1", "p-2", "p-4"):
            outcomes = memories[pid].meeting_history.outcomes
            assert len(outcomes) == 1, pid
            recorded = outcomes[0]
            assert recorded.end_tick == 11
            assert recorded.ejected_id == "p-3"
            assert recorded.revealed_role == "IMPOSTOR"
            assert recorded.votes_for_ejected == 2
            assert recorded.skip_votes == 1
            assert recorded.roster_impostor_count == 1

    def test_a_skipped_meeting_reveals_no_role(self) -> None:
        # A skip discloses nothing about anyone, so the role field stays empty --
        # the same rule that keeps a KILLED player's role out of memory.
        state = self._post_meeting_state(ejected=None, tick=7)
        result = self._result(ejected=None)
        memories = {pid: AgentMemory() for pid in state.players}

        fold_meeting_outcome_into_memories(result, state=state, memories=memories)

        recorded = memories["p-1"].meeting_history.outcomes[0]
        assert recorded.ejected_id is None
        assert recorded.revealed_role is None
        assert recorded.votes_for_ejected == 0
        assert recorded.skip_votes == 3

    def test_the_fold_equals_the_live_post_meeting_notification(self) -> None:
        # The parity claim the three reconstruction mirrors rest on: folding a
        # recorded meeting through the shared helper produces the SAME
        # meeting-history rows the live orchestrator wrote while recording it.
        # Drive both against one state/result pair and compare -- if the helper
        # ever derived a field differently (a tick, a tally, the role), the two
        # sides would diverge here.
        from orchestrator.game import TacticalAgent, _notify_meeting_concluded
        from meetings.manager import derive_meeting_outcome_summary
        from agents.tactical.crewmate_policy import CrewmatePolicy
        from agents.tactical.impostor_policy import ImpostorPolicy

        state = self._post_meeting_state(ejected="p-3", tick=13)
        result = self._result(ejected="p-3")
        agents = {
            pid: TacticalAgent(
                agent_id=pid,
                policy=(
                    ImpostorPolicy(agent_id=pid)
                    if state.players[pid].role == "IMPOSTOR"
                    else CrewmatePolicy(agent_id=pid)
                ),
                role=state.players[pid].role,
                memory=None,
            )
            for pid in state.players
        }
        _notify_meeting_concluded(
            state=state,
            agents=agents,
            emergency_caller_id=None,
            outcome=derive_meeting_outcome_summary(result),
            roster_impostor_count=1,
        )

        memories = {pid: AgentMemory() for pid in state.players}
        fold_meeting_outcome_into_memories(result, state=state, memories=memories)

        for pid in state.players:
            assert (
                memories[pid].meeting_history.outcomes
                == agents[pid].memory.meeting_history.outcomes
            ), pid
        assert memories["p-1"].meeting_history.outcomes != ()

    def test_a_missing_memory_fails_loud(self) -> None:
        # No silent fallback: a living player with no memory in the mapping is a
        # wiring bug in the walk, not a player to skip.
        state = self._post_meeting_state(ejected=None, tick=4)
        result = self._result(ejected=None)
        memories = {pid: AgentMemory() for pid in state.players if pid != "p-2"}

        with pytest.raises(KeyError):
            fold_meeting_outcome_into_memories(result, state=state, memories=memories)


class TestSubstrateMismatchOnAPhase20Lever:
    def test_a_stamped_off_lever_is_refused_after_the_graduation(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # The guard the graduation arms: a recording whose stamp says a Phase-20
        # lever was OFF can no longer be reconstructed at all -- this build has no
        # OFF derivation to re-render its memory from. The remediation hint must
        # name the key under the RETIRED branch, never the toggleable one (there
        # is no environment that would match the stamp).
        from api.replay_loader import (
            ReplaySubstrateMismatchError,
            _assert_substrate_matches,
        )

        _clear_lever_env(monkeypatch)
        stamped_off = GameEndReplayEntry(
            game_id="g-stamped-off",
            tick=21,
            winner="CREWMATES",
            reason="TASKS",
            substrate_flags={**_BARE_STAMP, "grounded_prosecution": False},
        )
        with pytest.raises(ReplaySubstrateMismatchError) as excinfo:
            _assert_substrate_matches("g-stamped-off", [stamped_off])
        message = str(excinfo.value)
        assert "grounded_prosecution" in message
        assert "unconditionally ON" in message

    def test_the_committed_stamp_reconstructs_in_a_bare_shell(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # The other half of the gate (a guard that always raised would be prose):
        # the stamp every committed baseline-7 replay carries passes in a shell
        # with no lever export at all.
        from api.replay_loader import _assert_substrate_matches

        _clear_lever_env(monkeypatch)
        recorded = GameEndReplayEntry(
            game_id="g-baseline-7",
            tick=21,
            winner="CREWMATES",
            reason="TASKS",
            substrate_flags=dict(_BASELINE7_STAMP),
        )
        _assert_substrate_matches("g-baseline-7", [recorded])

    def test_a_baseline6_stamp_no_longer_reconstructs(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # The cost of the graduation, asserted rather than assumed: a stamp that
        # OMITS the eight keys reads them False under the missing-key rule, which
        # this build cannot reproduce. Nothing in the repository carries that
        # stamp any more -- the record re-recorded all four sets -- and a replay
        # that did must be refused rather than silently re-rendered.
        from api.replay_loader import (
            ReplaySubstrateMismatchError,
            _assert_substrate_matches,
        )

        _clear_lever_env(monkeypatch)
        legacy = GameEndReplayEntry(
            game_id="g-legacy",
            tick=30,
            winner="CREWMATES",
            reason="TASKS",
            substrate_flags=dict(_BASELINE6_STAMP),
        )
        with pytest.raises(ReplaySubstrateMismatchError):
            _assert_substrate_matches("g-legacy", [legacy])
