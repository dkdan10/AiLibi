"""Unit tests for scripts/_manifest_writer.py (Task 4.17).

Provenance extraction, manifest render/parse round-trips, the row-update merge
path (and its idempotency), and the argparse-driven CLI. Hermetic: reads the
committed samples but only ever writes into ``tmp_path``.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import pytest

import _manifest_writer as mw
from orchestrator.replay import ReplayLog

_REPO_ROOT = Path(__file__).resolve().parents[2]
# The flat 4p1i baseline now lives under replays/samples/4p1i/ (Task 12.12).
_REAL_SAMPLES = _REPO_ROOT / "replays" / "samples" / "4p1i"
# Task 13.12 redistribute + Wave-E re-record: the new 4p/1i recording is far more
# meeting-dense (39/50 seeds carry a meeting), so the old _NO_MEETING_SEED 0 now
# HAS a meeting — re-anchored to seed 12 (still meeting-free). seed 22 stays
# meeting-bearing. The recorded prompt versions bumped with the merged Wave-E:
# accusation_round.v9 / crewmate_report.v8 / impostor_report_v6 / vote_ballot/v7
# (was v8/v7/v5/v5; the 13.13 de-imperative bumped vote_ballot v6->v7).
_MEETING_SEED = 22
_NO_MEETING_SEED = 12


@pytest.fixture
def small_samples(tmp_path: Path) -> Path:
    """A tmp sample dir holding one meeting-bearing and one meeting-free replay."""

    dst = tmp_path / "samples"
    dst.mkdir()
    for seed in (_NO_MEETING_SEED, _MEETING_SEED):
        src = _REAL_SAMPLES / f"replay-seed-{seed}.jsonl"
        (dst / src.name).write_bytes(src.read_bytes())
    return dst


def test_parse_seed_csv_accepts_ints_and_spaces() -> None:
    assert mw._parse_seed_csv("22,24,26") == [22, 24, 26]
    assert mw._parse_seed_csv("7, 13 , 40") == [7, 13, 40]


def test_parse_seed_csv_dedupes_preserving_order() -> None:
    # sum-cost must not double-count a seed repeated by a typo.
    assert mw._parse_seed_csv("22,22,24,22") == [22, 24]


@pytest.mark.parametrize("bad", ["3,x", "", "   ", "-5", "1.5", "abc", ","])
def test_parse_seed_csv_rejects_bad(bad: str) -> None:
    with pytest.raises(argparse.ArgumentTypeError):
        mw._parse_seed_csv(bad)


def test_discover_seeds_sorted(small_samples: Path) -> None:
    assert mw.discover_seeds(small_samples) == [_NO_MEETING_SEED, _MEETING_SEED]


def test_provenance_meeting_seed(small_samples: Path) -> None:
    fallback = mw.fallback_model(small_samples)
    model, prompt_versions, flags, cost, winner = mw.sample_provenance(
        small_samples, _MEETING_SEED, fallback
    )
    assert model == "qwen3.5:9b"
    # The union of the recorded prompt-version *values*, sorted — using the
    # actual recorded values (e.g. "vote_ballot/v5"), not the idealized hint.
    assert "accusation_round.v9" in prompt_versions
    assert "vote_ballot/v7" in prompt_versions
    parts = prompt_versions.split(", ")
    assert parts == sorted(parts)
    # The committed final-9B baseline predates the Task-14.7 substrate stamp and
    # was recorded with every lever OFF, so it carries no stamp -> the flags
    # column reads the legacy sentinel.
    assert flags == mw._NO_FLAGS
    # The committed re-records (Task 8.12 / Task 8.18) run on the local Ollama
    # provider: real LLM calls, zero spend, so the recorded per-seed cost is
    # exactly 0.
    assert float(cost) == 0.0
    # This test pins provenance *extraction*, not the game outcome: the meeting
    # seed's winner is a live-recorded result that can land either way (after the
    # Task 6.3 CREWMATE_EJECT change, seed 22's re-record resolves IMPOSTORS), so
    # assert membership rather than a specific side — matching the no-meeting case.
    assert winner in {"CREWMATES", "IMPOSTORS"}


def test_provenance_no_meeting_seed(small_samples: Path) -> None:
    fallback = mw.fallback_model(small_samples)
    model, prompt_versions, flags, cost, winner = mw.sample_provenance(
        small_samples, _NO_MEETING_SEED, fallback
    )
    assert prompt_versions == mw._NO_MEETINGS
    assert flags == mw._NO_FLAGS
    assert cost == "0.0000"
    # No LLM call recorded -> attributed to the directory's meeting model.
    assert model == fallback == "qwen3.5:9b"
    assert winner in {"CREWMATES", "IMPOSTORS", "null"}


def test_provenance_reads_stamped_substrate_flags(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # A flag-ON re-record (the Task-14.7 baseline) stamps its substrate config
    # onto the replay's game_over record; the MANIFEST flags column reports the
    # ON levers, sorted. This is the stamp -> manifest provenance path.
    for var in (
        "AILIBI_TESTIMONY_AS_CONTENT",
        "AILIBI_WITNESSED_KILL_EVIDENCE",
        "AILIBI_MOVEMENT_PERCEPTION",
        "AILIBI_UNFREEZE_MEMORY",
    ):
        monkeypatch.setenv(var, "1")
    samples = tmp_path / "samples"
    samples.mkdir()
    log = ReplayLog(samples / "replay-seed-5.jsonl", game_id="headless-seed-5")
    log.record_game_end(winner="CREWMATES", reason="TASKS_COMPLETE", tick=10)
    log.close()

    model, prompt_versions, flags, cost, winner = mw.sample_provenance(
        samples, 5, "Qwen/Qwen3-32B"
    )
    assert flags == (
        "movement_perception, testimony_as_content, "
        "unfreeze_memory, witnessed_kill_evidence"
    )
    assert winner == "CREWMATES"
    # No meeting recorded -> attributed to the active model, no prompt versions.
    assert model == "Qwen/Qwen3-32B"
    assert prompt_versions == mw._NO_MEETINGS


def test_rebuild_writes_sorted_rows(small_samples: Path, tmp_path: Path) -> None:
    manifest = tmp_path / "MANIFEST.md"
    written = mw.rebuild_manifest(manifest, small_samples)
    assert written == 2
    text = manifest.read_text()
    assert mw._COLUMNS in text
    assert mw._SEPARATOR in text
    rows = mw.parse_manifest(text)
    assert list(rows) == [
        _NO_MEETING_SEED,
        _MEETING_SEED,
    ]  # parsed in file order -> ascending
    assert rows[22].prompt_versions.startswith("accusation_round.v9")
    assert rows[_NO_MEETING_SEED].prompt_versions == mw._NO_MEETINGS


def test_rebuild_real_samples_have_50_rows(tmp_path: Path) -> None:
    manifest = tmp_path / "MANIFEST.md"
    written = mw.rebuild_manifest(manifest, _REAL_SAMPLES)
    assert written == 50
    rows = mw.parse_manifest(manifest.read_text())
    assert set(rows) == set(range(50))
    # Meeting-bearing seeds in the Task 13.12 redistribute + Wave-E flat 4p/1i
    # re-record (39/50 seeds carry a meeting now; 22/24/26/39 are all meeting-
    # bearing, recording the bumped Wave-E prompt versions).
    for seed in (22, 24, 26, 39):
        assert "accusation_round.v9" in rows[seed].prompt_versions
        assert rows[seed].git_sha  # non-empty provenance
    assert rows[_NO_MEETING_SEED].prompt_versions == mw._NO_MEETINGS


def test_header_uses_contracted_snake_case_column_names() -> None:
    # Phase 5 may read this schema programmatically (Task 4.17), so the header
    # must carry the exact contracted column names, not title-cased display text.
    for column in (
        "seed",
        "model",
        "prompt_versions",
        "flags",
        "refreshed_at",
        "git_sha",
        "cost_usd",
        "winner",
    ):
        assert f"| {column} |" in mw._COLUMNS or f" {column} |" in mw._COLUMNS
    assert "Prompt Versions" not in mw._COLUMNS
    assert "Cost (USD)" not in mw._COLUMNS


def test_parse_manifest_ignores_prose_and_separators() -> None:
    text = (
        "# Title\n\nsome prose | with a pipe\n"
        f"{mw._COLUMNS}\n{mw._SEPARATOR}\n"
        "| 3 | m | (none — no meetings) | testimony_as_content | d | sha "
        "| 0.0000 | CREWMATES |\n"
    )
    rows = mw.parse_manifest(text)
    assert set(rows) == {3}
    assert rows[3].winner == "CREWMATES"
    assert rows[3].flags == "testimony_as_content"


def test_parse_manifest_tolerates_legacy_7_column_rows() -> None:
    # A pre-Task-14.7 MANIFEST.md (the committed final-9B baseline) has no
    # ``flags`` column. The parser must still read those rows so a legacy manifest
    # merges/updates without a re-record; the missing column reads the sentinel.
    legacy = (
        "| seed | model | prompt_versions | refreshed_at | git_sha "
        "| cost_usd | winner |\n"
        "|---|---|---|---|---|---|---|\n"
        "| 7 | qwen3.5:9b | crewmate_report.v8 | 2026-06-23 | 4289051 "
        "| 0.0000 | IMPOSTORS |\n"
    )
    rows = mw.parse_manifest(legacy)
    assert set(rows) == {7}
    assert rows[7].model == "qwen3.5:9b"
    assert rows[7].winner == "IMPOSTORS"
    assert rows[7].flags == mw._NO_FLAGS


def test_render_parse_round_trip(small_samples: Path) -> None:
    fallback = mw.fallback_model(small_samples)
    original = {
        seed: mw.build_row(small_samples, seed, fallback, "abc1234", "2026-05-28")
        for seed in (_NO_MEETING_SEED, _MEETING_SEED)
    }
    reparsed = mw.parse_manifest(mw.render_manifest(original.values()))
    assert reparsed == original


def test_update_merges_without_touching_other_rows(
    small_samples: Path, tmp_path: Path
) -> None:
    manifest = tmp_path / "MANIFEST.md"
    mw.rebuild_manifest(manifest, small_samples)
    before = mw.parse_manifest(manifest.read_text())
    mw.update_manifest(
        manifest, small_samples, [22], git_sha="abc1234", refreshed_at="2026-05-28"
    )
    after = mw.parse_manifest(manifest.read_text())
    assert after[22].git_sha == "abc1234"
    assert after[22].refreshed_at == "2026-05-28"
    assert after[_NO_MEETING_SEED] == before[_NO_MEETING_SEED]  # untouched
    assert set(after) == set(before)


def test_update_is_idempotent(small_samples: Path, tmp_path: Path) -> None:
    manifest = tmp_path / "MANIFEST.md"
    mw.rebuild_manifest(manifest, small_samples)
    mw.update_manifest(
        manifest,
        small_samples,
        [_NO_MEETING_SEED, _MEETING_SEED],
        git_sha="cafe123",
        refreshed_at="2026-05-28",
    )
    first = manifest.read_text()
    mw.update_manifest(
        manifest,
        small_samples,
        [_NO_MEETING_SEED, _MEETING_SEED],
        git_sha="cafe123",
        refreshed_at="2026-05-28",
    )
    assert manifest.read_text() == first


def test_update_creates_manifest_when_absent(
    small_samples: Path, tmp_path: Path
) -> None:
    manifest = tmp_path / "sub" / "MANIFEST.md"  # parent dir does not exist yet
    mw.update_manifest(
        manifest, small_samples, [22], git_sha="x", refreshed_at="2026-05-28"
    )
    assert set(mw.parse_manifest(manifest.read_text())) == {22}


def test_update_uses_atomic_temp_then_replace(
    small_samples: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # H-H-3: the manifest is written to a sibling temp file and os.replace-d into
    # place, never written through a truncating in-place write.
    manifest = tmp_path / "MANIFEST.md"
    mw.rebuild_manifest(manifest, small_samples)

    calls: list[tuple[Path, Path]] = []
    real_replace = os.replace

    def spy_replace(src: Path, dst: Path) -> None:
        calls.append((Path(src), Path(dst)))
        real_replace(src, dst)

    # os is a singleton module, so patching os.replace also patches the
    # reference _manifest_writer calls through.
    monkeypatch.setattr(os, "replace", spy_replace)
    mw.update_manifest(
        manifest, small_samples, [22], git_sha="abc1234", refreshed_at="2026-05-28"
    )

    assert len(calls) == 1
    src, dst = calls[0]
    assert dst == manifest
    assert src != manifest
    assert src.suffix == ".tmp"
    assert src.parent == manifest.parent  # same filesystem -> atomic rename
    assert not src.exists()  # consumed by the replace; no temp left behind
    assert mw.parse_manifest(manifest.read_text())[22].git_sha == "abc1234"


def test_update_does_not_truncate_manifest_on_crash(
    small_samples: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # H-H-3: a crash at the replace step leaves the live MANIFEST fully intact
    # (the truncating-write failure mode this fix removes).
    manifest = tmp_path / "MANIFEST.md"
    mw.rebuild_manifest(manifest, small_samples)
    original = manifest.read_text()

    def boom(src: Path, dst: Path) -> None:
        raise OSError("simulated crash during replace")

    monkeypatch.setattr(os, "replace", boom)
    with pytest.raises(OSError):
        mw.update_manifest(
            manifest, small_samples, [22], git_sha="x", refreshed_at="2026-05-28"
        )

    # The live manifest is byte-for-byte unchanged...
    assert manifest.read_text() == original
    # ...and the temp file was cleaned up rather than orphaned.
    leftover = [p for p in tmp_path.iterdir() if p.name.endswith(".tmp")]
    assert leftover == []


def test_sum_cost(small_samples: Path) -> None:
    # The committed re-records (Task 8.12 / Task 8.18) run on the local Ollama
    # provider ($0/call), so the meeting-bearing seed's recorded spend is
    # exactly 0 too — the sum is still exercised over a seed WITH recorded
    # calls (22) and one without (0).
    assert mw.sum_cost(small_samples, [_NO_MEETING_SEED]) == 0.0
    assert mw.sum_cost(small_samples, [_NO_MEETING_SEED, _MEETING_SEED]) == 0.0


def test_main_rebuild(
    small_samples: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    manifest = tmp_path / "MANIFEST.md"
    rc = mw.main(
        ["rebuild", "--sample-dir", str(small_samples), "--manifest", str(manifest)]
    )
    assert rc == 0
    assert manifest.exists()
    assert "Wrote" in capsys.readouterr().err


def test_main_sum_cost_prints_single_float(
    small_samples: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    rc = mw.main(
        [
            "sum-cost",
            "--seeds",
            f"{_NO_MEETING_SEED},{_MEETING_SEED}",
            "--sample-dir",
            str(small_samples),
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out.strip()
    # The only thing on stdout is a parseable float ($0 on the Ollama record).
    assert float(out) == 0.0


def test_main_update_stamps_sha(
    small_samples: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    manifest = tmp_path / "MANIFEST.md"
    mw.main(
        ["rebuild", "--sample-dir", str(small_samples), "--manifest", str(manifest)]
    )
    rc = mw.main(
        [
            "update",
            "--seeds",
            "22",
            "--git-sha",
            "deadbee",
            "--refreshed-at",
            "2026-05-28",
            "--sample-dir",
            str(small_samples),
            "--manifest",
            str(manifest),
        ]
    )
    assert rc == 0
    rows = mw.parse_manifest(manifest.read_text())
    assert rows[22].git_sha == "deadbee"


def test_main_requires_subcommand() -> None:
    with pytest.raises(SystemExit):
        mw.main([])


def test_main_update_rejects_bad_seeds(small_samples: Path, tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        mw.main(
            [
                "update",
                "--seeds",
                "3,x",
                "--sample-dir",
                str(small_samples),
                "--manifest",
                str(tmp_path / "M.md"),
            ]
        )


def test_update_model_override_attributes_no_call_seed(
    small_samples: Path, tmp_path: Path
) -> None:
    manifest = tmp_path / "MANIFEST.md"
    mw.update_manifest(
        manifest,
        small_samples,
        [_NO_MEETING_SEED, _MEETING_SEED],
        git_sha="s",
        refreshed_at="2026-05-28",
        model_override="claude-opus-4-8",
    )
    rows = mw.parse_manifest(manifest.read_text())
    # No meetings -> attributed to the active (override) model...
    assert rows[_NO_MEETING_SEED].model == "claude-opus-4-8"
    # ...but a seed that recorded calls keeps its own recorded model.
    assert rows[22].model == "qwen3.5:9b"


def test_prune_drops_rows_without_files(small_samples: Path, tmp_path: Path) -> None:
    manifest = tmp_path / "MANIFEST.md"
    mw.rebuild_manifest(manifest, small_samples)  # rows for seeds 12 and 22
    stale = "| 99 | m | (none — no meetings) | d | s | 0.0000 | CREWMATES |\n"
    manifest.write_text(manifest.read_text() + stale)
    assert set(mw.parse_manifest(manifest.read_text())) == {
        _NO_MEETING_SEED,
        _MEETING_SEED,
        99,
    }
    dropped = mw.prune_manifest(manifest, small_samples)
    assert dropped == 1  # seed 99 has no replay file
    assert set(mw.parse_manifest(manifest.read_text())) == {
        _NO_MEETING_SEED,
        _MEETING_SEED,
    }


def test_update_routes_to_per_set_subdir_manifest(small_samples: Path) -> None:
    # Per-set routing (Task 7.4): an update targeting a 9p2i-style subdir defaults
    # the manifest to that subdir's MANIFEST.md (from --sample-dir), never the flat
    # set's — so a 9p/2i refresh cannot overwrite the 4p/1i baseline's provenance.
    subset = small_samples / "9p2i"
    subset.mkdir()
    (subset / "replay-seed-22.jsonl").write_bytes(
        (small_samples / "replay-seed-22.jsonl").read_bytes()
    )
    # No --manifest passed: it must default to <sample-dir>/MANIFEST.md.
    rc = mw.main(["update", "--seeds", "22", "--sample-dir", str(subset)])
    assert rc == 0
    assert set(mw.parse_manifest((subset / "MANIFEST.md").read_text())) == {22}
    # The flat set's manifest was never created or touched by the per-set update.
    assert not (small_samples / "MANIFEST.md").exists()


def test_main_prune_keeps_rows_with_files(small_samples: Path, tmp_path: Path) -> None:
    manifest = tmp_path / "MANIFEST.md"
    mw.rebuild_manifest(manifest, small_samples)
    rc = mw.main(
        ["prune", "--sample-dir", str(small_samples), "--manifest", str(manifest)]
    )
    assert rc == 0
    assert set(mw.parse_manifest(manifest.read_text())) == {
        _NO_MEETING_SEED,
        _MEETING_SEED,
    }


def test_remove_noncanonical_replays_drops_aliases_and_strays(tmp_path: Path) -> None:
    sample_dir = tmp_path / "samples"
    sample_dir.mkdir()
    src = (_REAL_SAMPLES / "replay-seed-1.jsonl").read_bytes()
    # Canonical seed-1 sample, a zero-padded alias of it, a stray seed > 49, and a
    # non-numeric hand-named file that must be left alone.
    (sample_dir / "replay-seed-1.jsonl").write_bytes(src)
    (sample_dir / "replay-seed-01.jsonl").write_bytes(src)
    (sample_dir / "replay-seed-50.jsonl").write_bytes(src)
    (sample_dir / "replay-seed-debug.jsonl").write_bytes(src)
    removed = mw.remove_noncanonical_replays(sample_dir, range(50))
    assert sorted(p.name for p in removed) == [
        "replay-seed-01.jsonl",
        "replay-seed-50.jsonl",
    ]
    remaining = sorted(p.name for p in sample_dir.glob("replay-seed-*.jsonl"))
    assert remaining == ["replay-seed-1.jsonl", "replay-seed-debug.jsonl"]


def test_remove_noncanonical_replays_keeps_canonical_set(tmp_path: Path) -> None:
    sample_dir = tmp_path / "samples"
    sample_dir.mkdir()
    src = (_REAL_SAMPLES / "replay-seed-1.jsonl").read_bytes()
    for seed in (0, 1, 49):
        (sample_dir / f"replay-seed-{seed}.jsonl").write_bytes(src)
    assert mw.remove_noncanonical_replays(sample_dir, range(50)) == []
    assert len(list(sample_dir.glob("replay-seed-*.jsonl"))) == 3


def test_canonicalize_removes_alias_and_prunes_stray_row(tmp_path: Path) -> None:
    sample_dir = tmp_path / "samples"
    sample_dir.mkdir()
    src = (_REAL_SAMPLES / "replay-seed-1.jsonl").read_bytes()
    (sample_dir / "replay-seed-1.jsonl").write_bytes(src)
    (sample_dir / "replay-seed-01.jsonl").write_bytes(src)  # alias to drop
    (sample_dir / "replay-seed-50.jsonl").write_bytes(src)  # stray to drop
    manifest = sample_dir / "MANIFEST.md"
    manifest.write_text(
        "| seed | model | prompt_versions | refreshed_at | git_sha | cost_usd | winner |\n"
        "|------|-------|-----------------|--------------|---------|----------|--------|\n"
        "| 1 | m | (none) | d | s | 0.0000 | CREWMATES |\n"
        "| 50 | m | (none) | d | s | 0.0000 | CREWMATES |\n"
    )
    rc = mw.main(
        [
            "canonicalize",
            "--seeds",
            ",".join(str(s) for s in range(50)),
            "--sample-dir",
            str(sample_dir),
            "--manifest",
            str(manifest),
        ]
    )
    assert rc == 0
    # Only the canonical seed-1 sample survives; the alias and the stray are gone.
    assert sorted(p.name for p in sample_dir.glob("replay-seed-*.jsonl")) == [
        "replay-seed-1.jsonl"
    ]
    # The stray seed-50 row is pruned (no file); seed-1 keeps its row.
    assert set(mw.parse_manifest(manifest.read_text())) == {1}


# -- roster descriptor (Task 7.4) ---------------------------------------------


def test_ensure_roster_writes_sidecar_for_non_default(tmp_path: Path) -> None:
    status = mw.ensure_roster_descriptor(
        tmp_path, num_players=9, num_impostors=2, tasks_per_crewmate=2
    )
    assert "wrote roster descriptor" in status
    assert json.loads((tmp_path / "roster.json").read_text()) == {
        "num_players": 9,
        "num_impostors": 2,
        "tasks_per_crewmate": 2,
    }


def test_ensure_roster_written_sidecar_parses_via_loader(tmp_path: Path) -> None:
    # The writer's output must round-trip through the loader's reader unchanged,
    # or a generated 9p/2i set would fail to reconstruct after spend.
    from api.replay_loader import RosterConfig, _load_roster_config

    mw.ensure_roster_descriptor(
        tmp_path, num_players=9, num_impostors=2, tasks_per_crewmate=2
    )
    assert _load_roster_config(tmp_path) == RosterConfig(
        num_players=9, num_impostors=2, tasks_per_crewmate=2
    )


# Task 12.12 removed the flat-baseline-DIR special case (no `_DEFAULT_SAMPLE_DIR`,
# no `_is_flat_baseline_dir`): every set is a named subdir, so EVERY refresh target
# gets an explicit roster.json — including a 4p/1i set, which no longer skips the
# sidecar. The committed flat 4p1i baseline stays descriptor-less only because it
# is never re-recorded. `test_ensure_roster_subdir_always_writes_descriptor` below
# (parametrized over the 4p/1i baseline roster) covers that always-write behaviour.


def test_ensure_roster_4p1i_roster_now_writes_a_sidecar(tmp_path: Path) -> None:
    # Post-12.12: a 4p/1i roster is no longer a special descriptor-less case —
    # there is no privileged flat-root dir to detect, so a refresh writes the
    # explicit sidecar like any other set.
    status = mw.ensure_roster_descriptor(
        tmp_path, num_players=4, num_impostors=1, tasks_per_crewmate=1
    )
    assert "wrote roster descriptor" in status
    assert json.loads((tmp_path / "roster.json").read_text()) == {
        "num_players": 4,
        "num_impostors": 1,
        "tasks_per_crewmate": 1,
    }


@pytest.mark.parametrize(
    "roster",
    [
        {"num_players": 4, "num_impostors": 2, "tasks_per_crewmate": 1},  # impostors
        {"num_players": 4, "num_impostors": 1, "tasks_per_crewmate": 2},  # tasks
        {"num_players": 7, "num_impostors": 1, "tasks_per_crewmate": 1},  # players
    ],
)
def test_ensure_roster_rejects_contradicting_descriptorless_set(
    tmp_path: Path, roster: dict[str, int]
) -> None:
    # Regression (Codex P1): a dir with committed replays + no roster.json is a
    # descriptor-less set; a refresh roster that contradicts the loader default
    # (num_impostors/tasks_per_crewmate != 1) or the set name's player count would
    # corrupt the untouched replays, so it is refused BEFORE any write — replacing
    # the removed flat-root guard (e.g. a refresh that forgot AILIBI_SAMPLE_DIR and
    # pointed AILIBI_NUM_IMPOSTORS=2 at the committed 4p1i set).
    set_dir = tmp_path / "4p1i"
    set_dir.mkdir()
    (set_dir / "replay-seed-0.jsonl").write_bytes(
        (_REAL_SAMPLES / "replay-seed-0.jsonl").read_bytes()
    )
    with pytest.raises(ValueError):
        mw.ensure_roster_descriptor(set_dir, **roster)
    assert not (set_dir / "roster.json").exists()  # nothing written on rejection


def test_ensure_roster_rejects_player_override_on_misnamed_descriptorless_set(
    tmp_path: Path,
) -> None:
    # Regression (Codex round-4 P1): a descriptor-less set whose dir name does NOT
    # match <P>p<I>i (e.g. a copied/misnamed 4p1i set) is still protected — the
    # player count is inferred from the RECORDED REPLAYS, so a num_players override
    # is rejected even without the name convention to lean on.
    set_dir = tmp_path / "mygames"  # name does not parse as <P>p<I>i
    set_dir.mkdir()
    (set_dir / "replay-seed-0.jsonl").write_bytes(
        (_REAL_SAMPLES / "replay-seed-0.jsonl").read_bytes()  # a 4-player replay
    )
    with pytest.raises(ValueError):
        mw.ensure_roster_descriptor(
            set_dir, num_players=7, num_impostors=1, tasks_per_crewmate=1
        )
    assert not (set_dir / "roster.json").exists()


def test_ensure_roster_allows_matching_roster_on_descriptorless_set(
    tmp_path: Path,
) -> None:
    # The legitimate in-place refresh: the default (4,1,1) is exactly what the
    # descriptor-less 4p1i replays reconstruct at, so it is allowed and writes the
    # sidecar (an empty/new dir is also allowed — the guard only gates dirs that
    # ALREADY hold committed replays).
    set_dir = tmp_path / "4p1i"
    set_dir.mkdir()
    (set_dir / "replay-seed-0.jsonl").write_bytes(
        (_REAL_SAMPLES / "replay-seed-0.jsonl").read_bytes()
    )
    status = mw.ensure_roster_descriptor(
        set_dir, num_players=4, num_impostors=1, tasks_per_crewmate=1
    )
    assert "wrote roster descriptor" in status
    assert json.loads((set_dir / "roster.json").read_text()) == {
        "num_players": 4,
        "num_impostors": 1,
        "tasks_per_crewmate": 1,
    }


def test_ensure_roster_is_idempotent_when_matching(tmp_path: Path) -> None:
    mw.ensure_roster_descriptor(
        tmp_path, num_players=9, num_impostors=2, tasks_per_crewmate=2
    )
    before = (tmp_path / "roster.json").read_bytes()
    status = mw.ensure_roster_descriptor(
        tmp_path, num_players=9, num_impostors=2, tasks_per_crewmate=2
    )
    assert "already matches" in status
    assert (tmp_path / "roster.json").read_bytes() == before


def test_ensure_roster_fails_loud_on_disagreement(tmp_path: Path) -> None:
    # A pre-existing descriptor that disagrees with the requested roster must
    # raise (before any spend), never be silently overwritten — this catches a
    # refresh that forgot/mistyped the roster env vars for a committed set.
    mw.ensure_roster_descriptor(
        tmp_path, num_players=9, num_impostors=2, tasks_per_crewmate=2
    )
    with pytest.raises(ValueError):
        mw.ensure_roster_descriptor(
            tmp_path, num_players=9, num_impostors=1, tasks_per_crewmate=2
        )


def test_main_roster_writes_descriptor(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    rc = mw.main(
        [
            "roster",
            "--sample-dir",
            str(tmp_path),
            "--num-players",
            "9",
            "--num-impostors",
            "2",
            "--tasks-per-crewmate",
            "2",
        ]
    )
    assert rc == 0
    assert (tmp_path / "roster.json").exists()
    assert "wrote roster descriptor" in capsys.readouterr().err


@pytest.mark.parametrize(
    "roster",
    [
        {
            "num_players": 7,
            "num_impostors": 1,
            "tasks_per_crewmate": 1,
        },  # num-players only
        {
            "num_players": 4,
            "num_impostors": 1,
            "tasks_per_crewmate": 1,
        },  # baseline roster
        {
            "num_players": 9,
            "num_impostors": 2,
            "tasks_per_crewmate": 2,
        },  # 9p/2i: 7*2=14 instances over 12 map tasks — the pre-instance cap
        # rejected this; per-player overlap (DESIGN.md §3.2/§3.5) makes it seedable,
        # so _validate_roster_is_seedable now accepts it before writing the sidecar.
    ],
)
def test_ensure_roster_subdir_always_writes_descriptor(
    tmp_path: Path, roster: dict[str, int]
) -> None:
    # Post-12.12 every set is a named subdir, so a refresh ALWAYS writes an explicit
    # descriptor — including a 4p/1i set (e.g. a refresh that forgot the roster env
    # vars) — and a refreshed set is never left descriptor-less.
    status = mw.ensure_roster_descriptor(tmp_path, **roster)
    assert "wrote roster descriptor" in status
    assert json.loads((tmp_path / "roster.json").read_text()) == roster


@pytest.mark.parametrize(
    ("payload", "requested"),
    [
        # 7.0 == 7 and true == 1 under Python dict equality, so a plain `!=` check
        # would treat these as matching — but the loader rejects float/bool, so
        # they must be caught at this pre-spend gate, not after the money is spent.
        (
            '{"num_players": 7.0, "num_impostors": 2, "tasks_per_crewmate": 2}',
            {"num_players": 7, "num_impostors": 2, "tasks_per_crewmate": 2},
        ),
        (
            '{"num_players": 7, "num_impostors": 2, "tasks_per_crewmate": true}',
            {"num_players": 7, "num_impostors": 2, "tasks_per_crewmate": 1},
        ),
    ],
)
def test_ensure_roster_rejects_type_malformed_existing_descriptor(
    tmp_path: Path, payload: str, requested: dict[str, int]
) -> None:
    (tmp_path / "roster.json").write_text(payload, encoding="utf-8")
    with pytest.raises(ValueError):
        mw.ensure_roster_descriptor(tmp_path, **requested)


@pytest.mark.parametrize(
    "bad",
    [
        {"num_players": 7, "num_impostors": 2, "tasks_per_crewmate": 0},
        {"num_players": 0, "num_impostors": 1, "tasks_per_crewmate": 1},
        {"num_players": 7, "num_impostors": -1, "tasks_per_crewmate": 2},
    ],
)
def test_ensure_roster_rejects_non_positive_requested(
    tmp_path: Path, bad: dict[str, int]
) -> None:
    # A mistyped non-positive env value must raise BEFORE writing, so no malformed
    # sidecar is left in the directory to poison the set.
    with pytest.raises(ValueError):
        mw.ensure_roster_descriptor(tmp_path, **bad)
    assert not (tmp_path / "roster.json").exists()


@pytest.mark.parametrize(
    "invalid",
    [
        {"num_players": 1, "num_impostors": 1, "tasks_per_crewmate": 1},  # players < 2
        {
            "num_players": 2,
            "num_impostors": 2,
            "tasks_per_crewmate": 1,
        },  # impostors==players
        {
            "num_players": 3,
            "num_impostors": 1,
            "tasks_per_crewmate": 13,
        },  # tasks_per_crewmate beyond the 12-task pool (per-player overlap removed
        # the old num_crewmates*tasks_per_crewmate cap, but one crewmate's
        # instances must still be distinct map tasks — DESIGN.md §3.2)
    ],
)
def test_ensure_roster_rejects_seeder_invalid_roster(
    tmp_path: Path, invalid: dict[str, int]
) -> None:
    # Positive ints the SEEDER rejects (bad parity / tasks_per_crewmate beyond the
    # map's task pool) must fail BEFORE writing, so a failed refresh leaves no
    # poison sidecar that a later corrected refresh would refuse to overwrite (and
    # the loader would fail on).
    with pytest.raises(ValueError):
        mw.ensure_roster_descriptor(tmp_path, **invalid)
    assert not (tmp_path / "roster.json").exists()
