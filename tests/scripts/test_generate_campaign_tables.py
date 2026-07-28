"""Tests for scripts/generate_campaign_tables.py (Task 18.31).

The 18.24 campaign report's tables were hand-assembled from JSON that was
already correct, and six of that PR's review findings were transcription or
arithmetic errors (training/reports/report-impostor-campaign.md §11 defect 5).
These tests pin the generator that removes the transcription step:

* the §4.0 stability numbers REPRODUCE the committed
  ``training/artifacts/coevo/measurement-stability.json`` exactly from the
  committed ranking files — that reproduction is the acceptance fixture, free
  and already in-tree — and the ``--check`` CLI is the gate;
* the same computation runs against ANY two-tranche ranking set, which is the
  free protocol precondition F12 asks every future campaign to run after its
  FIRST retest;
* the §3 row tables and §4 leg tables render deterministically (same bytes
  twice) and reproduce the committed report's own published cells;
* malformed or unsupported inputs fail loud rather than rendering a plausible
  wrong table.

Everything reads committed bytes read-only: no test writes into
``training/artifacts/``.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import pytest

import generate_campaign_tables as gct

_REPO_ROOT = Path(__file__).resolve().parents[2]
_COEVO = _REPO_ROOT / "training" / "artifacts" / "coevo"
_STABILITY_ARTIFACT = _COEVO / "measurement-stability.json"
_RUN_01_LEG = _COEVO / "realpath" / "run-01-utility-champion"
_CAMPAIGN_ROWS = _REPO_ROOT / "training" / "reports" / "results-impostor-campaign.jsonl"

#: Sentinel meaning "delete this stamp key", distinct from any JSON value.
_DROP: Any = object()


def _default_roots() -> list[Path]:
    return [_REPO_ROOT / root for root in gct.DEFAULT_RANKING_ROOTS]


# --------------------------------------------------------------------------- #
# The §4.0 stability table — the committed reproduction.                       #
# --------------------------------------------------------------------------- #


def test_stability_reproduces_the_committed_artifact() -> None:
    """Every committed stability number recomputes from the committed rows.

    Key-for-key equality against ``measurement-stability.json``, including the
    combination rule the artifact states (it CHANGES the numbers: one arm is a
    ``(leg, genome)`` pair, so a genome recorded in two lineage legs counts
    twice).
    """

    computed = gct.compute_stability(gct.find_ranking_files(_default_roots()))
    committed = json.loads(_STABILITY_ARTIFACT.read_text(encoding="utf-8"))
    assert computed == committed
    # And the headline reads the way §4.0 publishes it.
    assert computed["arms_with_both_tranches"] == 22
    assert computed["distinct_genomes"] == 21
    assert computed["mean_abs_flags_swing"] == 0.7415
    assert computed["noise_to_threshold_ratio"] == 0.6797
    assert computed["arms_with_impossible_conversion_floor"] == 12
    assert computed["arms_swinging_ge_one_game"] == 10
    assert (computed["referee_passes_total"], computed["referee_passes_retested"]) == (
        3,
        1,
    )
    assert computed["referee_passes_replicated"] == 0


def test_stability_check_cli_passes_and_detects_drift(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """``--check`` is the gate: exit 0 on reproduction, non-zero on drift."""

    assert gct.main(["stability", "--check"]) == 0
    assert "reproduces exactly" in capsys.readouterr().out

    drifted = tmp_path / "drifted.json"
    committed = json.loads(_STABILITY_ARTIFACT.read_text(encoding="utf-8"))
    committed["arms_with_both_tranches"] = 999
    drifted.write_text(json.dumps(committed), encoding="utf-8")
    assert gct.main(["stability", "--check", str(drifted)]) == 1
    captured = capsys.readouterr()
    assert "arms_with_both_tranches" in captured.err

    # The committed artifact is untouched by any of this.
    assert (
        json.loads(_STABILITY_ARTIFACT.read_text(encoding="utf-8"))[
            "arms_with_both_tranches"
        ]
        == 22
    )


def test_stability_table_renders_the_published_cells() -> None:
    """The rendered §4.0 table carries the report's own published values."""

    stability = gct.compute_stability(gct.find_ranking_files(_default_roots()))
    table = gct.render_stability_table(stability)
    for expected in (
        "**22 ARMS** (21 distinct genomes)",
        "**0.7415**",
        "1.0909",
        "**68%**",
        "**12 of 22**",
        "0.55",
        "**10 of 22**",
        "**3 / 1 / 0**",
    ):
        assert expected in table
    assert gct.COMBINATION_RULE in table
    # Deterministic: the same inputs render the same bytes.
    assert gct.render_stability_table(stability) == table


def test_stability_runs_against_any_two_tranche_ranking_set(tmp_path: Path) -> None:
    """The F12 precondition: the computation needs only two tranches (18.31 fix 6).

    Nothing about it is 18.24-specific — point it at whatever a campaign has
    recorded after its FIRST retest. Here one leg's two committed tranches are
    copied to a throwaway root and read as a standalone campaign.
    """

    leg = tmp_path / "campaign" / "leg-01"
    leg.mkdir(parents=True)
    for name in ("ranking-4000-4002.jsonl", "ranking-4003-4005.jsonl"):
        shutil.copy(_RUN_01_LEG / name, leg / name)

    stability = gct.compute_stability(gct.find_ranking_files([tmp_path / "campaign"]))
    assert stability["arms_with_both_tranches"] == 2
    assert stability["distinct_genomes"] == 2
    assert stability["combination_rule"] == gct.COMBINATION_RULE
    assert stability["flags_floor"] == pytest.approx(1.0909090909090908)
    assert 0.0 <= stability["noise_to_threshold_ratio"]
    assert gct.render_stability_table(stability).startswith("| stability check")


def test_stability_fails_loud_without_a_retest(tmp_path: Path) -> None:
    """A single-tranche set has no stability to report; it says so (18.31)."""

    leg = tmp_path / "campaign" / "leg-01"
    leg.mkdir(parents=True)
    shutil.copy(
        _RUN_01_LEG / "ranking-4000-4002.jsonl", leg / "ranking-4000-4002.jsonl"
    )
    with pytest.raises(SystemExit, match="FIRST retested candidate"):
        gct.compute_stability(gct.find_ranking_files([tmp_path / "campaign"]))


def test_stability_refuses_unpaired_rows_from_a_third_tranche(tmp_path: Path) -> None:
    """The pair is chosen from PAIRED arms, so a third tranche can hide (Codex #314).

    An arm read on T1/T2 plus a different, single-read arm on T3 leaves
    ``tranche_pairs`` holding only (T1, T2) — the set looks like a clean
    two-tranche experiment. But the ``referee_passes_total`` fold walks every
    read, so the T3 row's PASS count enters the published totals while appearing
    in no swing in the table.
    """

    row = _committed_row(0)
    other = _committed_row(1)
    leg = tmp_path / "campaign" / "leg-01"
    _write_arm(leg, "t1", row, seeds=(1, 2, 3))
    _write_arm(leg, "t2", row, seeds=(4, 5, 6))
    # A DIFFERENT arm, read once, on a tranche outside the pair.
    _write_arm(leg, "t3", other, seeds=(7, 8, 9))

    with pytest.raises(SystemExit, match="outside the compared pair"):
        gct.compute_stability(gct.find_ranking_files([tmp_path / "campaign"]))

    # No over-reach: a single-read arm on one of the COMPARED tranches is
    # legitimate — it is what referee_passes_total vs _retested distinguishes —
    # and must still be accepted.
    # t1 ranks BOTH candidates; t2 re-reads only the first. So the second arm
    # is single-read on a compared tranche — legitimate, and exactly what
    # referee_passes_total vs _retested distinguishes.
    kept = tmp_path / "kept" / "leg-01"
    kept.mkdir(parents=True)
    both = [
        {**row, "seeds": [1, 2, 3], "rank": 1},
        {**other, "seeds": [1, 2, 3], "rank": 2},
    ]
    (kept / "ranking-t1.jsonl").write_text(
        "".join(json.dumps(entry) + "\n" for entry in both), encoding="utf-8"
    )
    _write_arm(kept, "t2", row, seeds=(4, 5, 6))
    stability = gct.compute_stability(gct.find_ranking_files([tmp_path / "kept"]))
    assert stability["arms_with_both_tranches"] == 1


def test_stability_refuses_a_third_tranche_of_one_arm(tmp_path: Path) -> None:
    """Three reads of one arm are not a two-tranche comparison (18.31)."""

    row = _committed_row(0)
    leg = tmp_path / "campaign" / "leg-01"
    for tranche, seeds in (("t1", (1, 2, 3)), ("t2", (4, 5, 6)), ("t3", (7, 8, 9))):
        _write_arm(leg, tranche, row, seeds=seeds)
    with pytest.raises(SystemExit, match="exactly two independent tranches"):
        gct.compute_stability(gct.find_ranking_files([tmp_path / "campaign"]))


# --------------------------------------------------------------------------- #
# The §3 campaign-row tables.                                                  #
# --------------------------------------------------------------------------- #


def test_rows_tables_reproduce_the_committed_report_cells() -> None:
    """The generated §3.1 table matches the report's published rows cell for cell.

    The committed row stream holds the campaign's five runs concatenated, split
    on ``generation_index`` restarting at 1 (§3's own boundary rule). The
    run-01 segment's first and last rows are the report's §3.1 table verbatim,
    including the exploiter cell's ``**frozen** <fitness>><bar>`` form.
    """

    document = gct.render_rows_document(
        _CAMPAIGN_ROWS, labels=["run-01-utility-champion"]
    )
    assert "### run-01-utility-champion" in document
    assert (
        "| 1 | 0 | impostor | 0 | 20.5544 | no | 19.8713 | 11.7684 | not-found | 151 "
        "| 170 |"
    ) in document
    assert (
        "| 12 | 3 | crew | 7 | 11.6537 | yes | 10.5242 | 16.7500 | **frozen** "
        "21.00>16.75 | 2717 | 2358 |"
    ) in document
    # §3.1's own prose: 2 358 games, 12 rows, 7 exploiter freezes.
    assert "Rows: 12; swaps: 4; games: 2358;" in document
    assert "exploiter freezes: 7." in document
    # Later segments fall back to a positional name rather than inventing one.
    assert "### segment-2" in document


def test_rows_document_is_byte_deterministic() -> None:
    first = gct.render_rows_document(_CAMPAIGN_ROWS, labels=[])
    second = gct.render_rows_document(_CAMPAIGN_ROWS, labels=[])
    assert first == second
    assert first.endswith("\n")


def test_rows_split_refuses_a_partial_extract(tmp_path: Path) -> None:
    """A stream that does not start at generation 1 is an extract, not a run."""

    rows = _CAMPAIGN_ROWS.read_text(encoding="utf-8").splitlines()
    partial = tmp_path / "partial.jsonl"
    partial.write_text("\n".join(rows[1:5]) + "\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="does not begin at generation_index 1"):
        gct.render_rows_document(partial, labels=[])


# --------------------------------------------------------------------------- #
# The §4 leg tables.                                                           #
# --------------------------------------------------------------------------- #


def test_leg_tables_reproduce_the_committed_reads() -> None:
    """The §4.2 leg tables reproduce from the committed ranking bytes.

    Selection scores, the win / ejection-accuracy channels, the 17.14 stamp
    proof, and the SIGNED floor distances all come from the row itself — no
    number is re-derived and none is retyped.
    """

    document = gct.render_leg_tables(_RUN_01_LEG / "ranking-4000-4002.jsonl")
    text = "\n".join(document)
    assert "| 1 | `8ac3652a…` | 62.60 | PASS | FAIL | 0.000 | 0.857 |" in text
    assert "| 2 | `6d327dcb…` | 41.27 | PASS | FAIL | 0.667 | 0.750 |" in text
    assert "3/3 games stamped, uniform, sha == computed digest" in text
    assert "0.8333 − 1.0909 = **-0.2576 FAIL**" in text
    assert "0.5000 − 0.7508 = **-0.2508 FAIL**" in text
    assert "0.2308 − 0.0339 = **+0.1969 PASS**" in text
    # The legend keeps the full label + sha beside the shorthand (lossless).
    assert "8ac3652a74f81e72440f960a68fa8ae258dd033451d9982592fb48daaa1a7d45" in text


def test_leg_document_is_byte_deterministic_over_a_whole_leg() -> None:
    paths = gct.find_ranking_files([_RUN_01_LEG])
    assert len(paths) == 2
    first = gct.render_legs_document(paths)
    second = gct.render_legs_document(paths)
    assert first == second
    assert first.count("### Leg — ") == 2


def test_leg_table_renders_an_empty_denominator_honestly() -> None:
    """A ``None`` measured gauge renders as a FAIL, never as a zero.

    The v3 lineage never killed, so its ``witnessed_event_rate`` has an empty
    denominator — the report's own "None vs 0.0339 → FAIL (0 kills)" cell.
    """

    document = "\n".join(
        gct.render_leg_tables(
            _COEVO / "realpath" / "run-04-freepolicy-v3" / "ranking-4000-4002.jsonl"
        )
    )
    assert "None vs 0.0339 → **FAIL** (denominator empty)" in document
    assert "6.6667 − 1.0909 = **+5.5758 PASS**" in document


# --------------------------------------------------------------------------- #
# CLI plumbing.                                                                #
# --------------------------------------------------------------------------- #


def test_cli_writes_each_family_to_a_file(tmp_path: Path) -> None:
    rows_out = tmp_path / "rows.md"
    legs_out = tmp_path / "legs.md"
    table_out = tmp_path / "stability.md"
    json_out = tmp_path / "stability.json"

    assert (
        gct.main(
            [
                "rows",
                "--rows-path",
                str(_CAMPAIGN_ROWS),
                "--label",
                "run-01-utility-champion",
                "--out",
                str(rows_out),
            ]
        )
        == 0
    )
    assert (
        gct.main(["legs", "--leg-dir", str(_RUN_01_LEG), "--out", str(legs_out)]) == 0
    )
    assert (
        gct.main(["stability", "--out", str(table_out), "--json-out", str(json_out)])
        == 0
    )

    assert rows_out.read_text(encoding="utf-8").startswith("## Campaign rows — ")
    assert legs_out.read_text(encoding="utf-8").startswith("## Real-path re-rank legs")
    assert table_out.read_text(encoding="utf-8").startswith("| stability check")
    # The JSON writer emits the committed artifact's byte form exactly.
    assert json_out.read_text(encoding="utf-8") == _STABILITY_ARTIFACT.read_text(
        encoding="utf-8"
    )


def test_cli_rejects_an_unknown_ranking_root(tmp_path: Path) -> None:
    with pytest.raises(SystemExit, match="is not a directory"):
        gct.main(["stability", "--ranking-root", str(tmp_path / "nope")])


def test_cli_refuses_to_check_and_render_at_once(tmp_path: Path) -> None:
    """``--check`` writes nothing, so a render flag beside it is a contradiction."""

    with pytest.raises(SystemExit, match="VERIFIES a committed artifact"):
        gct.main(["stability", "--check", "--out", str(tmp_path / "out.md")])


def _write_arm(
    leg: Path,
    tranche: str,
    source_row: dict[str, object],
    *,
    seeds: tuple[int, ...],
    **overrides: object,
) -> None:
    """Write a one-row ranking file derived from a committed row.

    ``seeds`` is the tranche's real identity (the generator keys on the
    recorded seeds, not the filename), so every synthetic tranche declares its
    own seed set.

    ``rank`` is normalised to 1 because the file holds exactly one row: a
    committed row carrying ``rank: 2`` in a one-row file is a shape no recorder
    produces, and the ranking-integrity guard now refuses it before any arm is
    folded. An override may still set it deliberately.
    """

    row = dict(source_row)
    row["seeds"] = list(seeds)
    row["rank"] = 1
    row.update(overrides)
    leg.mkdir(parents=True, exist_ok=True)
    (leg / f"ranking-{tranche}.jsonl").write_text(
        json.dumps(row) + "\n", encoding="utf-8"
    )


def _committed_row(index: int = 0) -> dict[str, object]:
    line = (
        (_RUN_01_LEG / "ranking-4000-4002.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()[index]
    )
    row: dict[str, object] = json.loads(line)
    return row


def test_stability_refuses_mixed_tranche_pairs(tmp_path: Path) -> None:
    """Every arm must share ONE tranche pair (Codex on PR #314).

    Two arms each read twice is not a two-tranche measurement if they were read
    on DIFFERENT pairs: the aggregate silently mixes comparisons while the table
    presents it as one. The per-arm "exactly two reads" check cannot see this.
    """

    first, second = _committed_row(0), _committed_row(1)
    root = tmp_path / "campaign"
    _write_arm(root / "leg-a", "t1", first, seeds=(1, 2, 3))
    _write_arm(root / "leg-a", "t2", first, seeds=(4, 5, 6))
    _write_arm(root / "leg-b", "t2", second, seeds=(4, 5, 6))
    _write_arm(root / "leg-b", "t3", second, seeds=(7, 8, 9))

    with pytest.raises(SystemExit, match="do not share ONE tranche pair"):
        gct.compute_stability(gct.find_ranking_files([root]))


def test_stability_refuses_unequal_game_counts(tmp_path: Path) -> None:
    """A win swing IN GAMES needs one denominator (Codex on PR #314).

    Subtracting raw win counts across unequal totals would read identical 50%
    rates over 2 and 4 games as a one-game swing.
    """

    row = _committed_row(0)
    root = tmp_path / "campaign"
    _write_arm(root / "leg-a", "t1", row, seeds=(1, 2, 3), core_games_total=3)
    _write_arm(root / "leg-a", "t2", row, seeds=(4, 5, 6), core_games_total=4)

    with pytest.raises(SystemExit, match="needs one denominator"):
        gct.compute_stability(gct.find_ranking_files([root]))


def test_stability_refuses_a_mixed_global_denominator(tmp_path: Path) -> None:
    """Two internally-consistent arms of different sizes still cannot be pooled."""

    first, second = _committed_row(0), _committed_row(1)
    root = tmp_path / "campaign"
    _write_arm(root / "leg-a", "t1", first, seeds=(1, 2, 3), core_games_total=3)
    _write_arm(root / "leg-a", "t2", first, seeds=(4, 5, 6), core_games_total=3)
    _write_arm(root / "leg-b", "t1", second, seeds=(1, 2, 3), core_games_total=5)
    _write_arm(root / "leg-b", "t2", second, seeds=(4, 5, 6), core_games_total=5)

    with pytest.raises(SystemExit, match="games per tranche"):
        gct.compute_stability(gct.find_ranking_files([root]))


def test_tranche_identity_comes_from_the_recorded_seeds(tmp_path: Path) -> None:
    """Two files over the SAME seeds are one draw, whatever they are named.

    A filename suffix is a label an operator chose; the recorded ``seeds`` are
    the experiment. Counting a mislabelled duplicate as a second independent
    provider draw would manufacture a reliability result out of one recording
    (Codex on PR #314).
    """

    row = _committed_row(0)
    leg = tmp_path / "campaign" / "leg-01"
    _write_arm(leg, "first-pass", row, seeds=(1, 2, 3))
    _write_arm(leg, "second-pass", row, seeds=(1, 2, 3))

    with pytest.raises(SystemExit, match="appears twice in tranche"):
        gct.compute_stability(gct.find_ranking_files([tmp_path / "campaign"]))


def test_ranking_file_mixing_seed_sets_is_refused(tmp_path: Path) -> None:
    """One ranking file is one tranche; disagreeing rows are corruption.

    The refusal now comes from the shared ranking-integrity check (``seeds`` is
    a leg-level field), which runs before the tranche identity is derived — an
    earlier, better-named stop than the identity helper's own guard, which
    remains as defence.
    """

    first, second = _committed_row(0), _committed_row(1)
    first["seeds"] = [1, 2, 3]
    second["seeds"] = [4, 5, 6]
    leg = tmp_path / "campaign" / "leg-01"
    leg.mkdir(parents=True)
    (leg / "ranking-mixed.jsonl").write_text(
        json.dumps(first) + "\n" + json.dumps(second) + "\n", encoding="utf-8"
    )
    with pytest.raises(SystemExit, match="disagree on the leg-level field 'seeds'"):
        gct.compute_stability(gct.find_ranking_files([tmp_path / "campaign"]))


def test_ranking_paths_are_sorted_regardless_of_root_order() -> None:
    """Root order must not change the rendered bytes (Codex on PR #314).

    Sorting each root's walk separately still let the caller's argument order
    reorder the document, which is not the determinism the module documents.
    """

    roots = _default_roots()
    forward = gct.find_ranking_files(roots)
    reversed_order = gct.find_ranking_files(list(reversed(roots)))
    assert forward == reversed_order == sorted(forward)


def test_explicit_ranking_argument_order_does_not_change_the_bytes(
    tmp_path: Path,
) -> None:
    """``--ranking a --ranking b`` renders the same bytes as ``b`` then ``a``."""

    leg_paths = gct.find_ranking_files([_RUN_01_LEG])
    assert len(leg_paths) == 2
    forward, backward = tmp_path / "forward.md", tmp_path / "backward.md"
    assert (
        gct.main(
            [
                "legs",
                *[arg for p in leg_paths for arg in ("--ranking", str(p))],
                "--out",
                str(forward),
            ]
        )
        == 0
    )
    assert (
        gct.main(
            [
                "legs",
                *[arg for p in reversed(leg_paths) for arg in ("--ranking", str(p))],
                "--out",
                str(backward),
            ]
        )
        == 0
    )
    assert forward.read_bytes() == backward.read_bytes()


def test_reordered_seed_lists_are_one_tranche(tmp_path: Path) -> None:
    """The seed SET is the experiment; recording order is not (Codex #314).

    ``[1, 2, 3]`` and ``[3, 2, 1]`` are one tranche recorded twice, so the
    seed-derived identity is canonicalised before use — otherwise the new guard
    could still be walked around by a reordered list.
    """

    row = _committed_row(0)
    leg = tmp_path / "campaign" / "leg-01"
    _write_arm(leg, "forward", row, seeds=(1, 2, 3))
    _write_arm(leg, "reversed", row, seeds=(3, 2, 1))

    with pytest.raises(SystemExit, match="appears twice in tranche"):
        gct.compute_stability(gct.find_ranking_files([tmp_path / "campaign"]))


def test_stability_refuses_encoder_family_drift_within_an_arm(tmp_path: Path) -> None:
    """One arm is ONE policy read twice (Codex on PR #314).

    Identical float bytes stamped for two different families are two policies
    whose layouts collide — the exact ambiguity the artifact stamps remove — so
    a "swing" between them measures nothing.
    """

    first, second = _committed_row(0), _committed_row(0)
    drifted_stamp = dict(second["stamp"])  # type: ignore[call-overload]
    drifted_stamp["encoder_version"] = "v3"
    second["stamp"] = drifted_stamp
    leg = tmp_path / "campaign" / "leg-01"
    _write_arm(leg, "t1", first, seeds=(1, 2, 3))
    _write_arm(leg, "t2", second, seeds=(4, 5, 6))

    # The check now covers the whole five-field stamp, so the message names the
    # field that drifted (Codex round 8); the encoder case is one of five.
    with pytest.raises(SystemExit, match="stamped encoder_version="):
        gct.compute_stability(gct.find_ranking_files([tmp_path / "campaign"]))


def _v2_row(*, index: int = 0, **overrides: object) -> dict[str, object]:
    """A committed row upgraded to the ``-v2`` schema that names its recorder."""

    row = _committed_row(index)
    row["schema_version"] = gct._RECORDER_IDENTITY_SCHEMA
    row["recording_backend_sha256"] = "a" * 64
    row["game_map_sha256"] = "c" * 64
    row.update(overrides)
    return row


def test_stability_requires_one_recorder_and_one_map_per_arm(tmp_path: Path) -> None:
    """Recorder and map identity are protocol from ``-v2`` on (Codex on PR #314).

    Two tranche rankings written into one leg directory by separate calls can
    use different providers, prompt sets, custom runners or maps while agreeing
    on every protocol field — and ``compute_stability`` would then report that
    behavioural change as provider/seed noise. ``run_realpath_rerank`` now names
    the recorder in every row it writes, and an arm's two reads must agree.

    Keyed on the ROW's declared schema so the frozen ``-v1`` corpus is handled
    as what it is: a record made before the field existed, not a pair that
    silently agrees on its own absence. An arm that is half ``-v1`` and half
    ``-v2`` is refused rather than compared on the half that happens to exist.
    """

    for field in gct._RECORDER_IDENTITY_FIELDS:
        leg = tmp_path / field / "leg-01"
        drifted = _v2_row()
        drifted[field] = "d" * 64
        _write_arm(leg, "t1", _v2_row(), seeds=(1, 2, 3))
        _write_arm(leg, "t2", drifted, seeds=(4, 5, 6))
        with pytest.raises(SystemExit, match="not provider/seed noise"):
            gct.compute_stability(gct.find_ranking_files([tmp_path / field]))

    # A ``-v2`` row that OMITS the identity is refused where the file is read.
    dropped = _v2_row()
    del dropped["recording_backend_sha256"]
    leg = tmp_path / "omitted" / "leg-01"
    _write_arm(leg, "t1", dropped, seeds=(1, 2, 3))
    with pytest.raises(SystemExit, match="a ranking row names the recorder"):
        gct.read_validated_ranking(leg / "ranking-t1.jsonl")

    # Half-``v1``/half-``v2`` is not comparable: the pair is refused, never
    # compared on the read that happens to carry an identity.
    leg = tmp_path / "mixed" / "leg-01"
    _write_arm(leg, "t1", _committed_row(0), seeds=(1, 2, 3))
    _write_arm(leg, "t2", _v2_row(), seeds=(4, 5, 6))
    with pytest.raises(SystemExit, match="different schema_version"):
        gct.compute_stability(gct.find_ranking_files([tmp_path / "mixed"]))

    # A FUTURE schema is required to carry the identity too: the legacy set is
    # closed, so a generation that forgot the fields is refused rather than
    # read as pre-18.31. (A ``>=`` string compare would have got this backwards
    # — ``"...-v10"`` sorts below ``"...-v2"``.)
    future = _v2_row(schema_version="realpath-rerank-v10")
    del future["game_map_sha256"]
    leg = tmp_path / "future" / "leg-01"
    _write_arm(leg, "t1", future, seeds=(1, 2, 3))
    with pytest.raises(SystemExit, match="a ranking row names the recorder"):
        gct.read_validated_ranking(leg / "ranking-t1.jsonl")

    # Agreeing ``-v2`` reads fold normally, and so does the frozen ``-v1`` pair.
    leg = tmp_path / "agree" / "leg-01"
    _write_arm(leg, "t1", _v2_row(), seeds=(1, 2, 3))
    _write_arm(leg, "t2", _v2_row(), seeds=(4, 5, 6))
    assert len(gct.compute_stability(gct.find_ranking_files([tmp_path / "agree"]))) >= 1
    assert gct.main(["stability", "--check"]) == 0


def test_the_emitted_rule_describes_the_fold_that_ran(tmp_path: Path) -> None:
    """The artifact's self-description matches its arm key (Codex on PR #314).

    ``COMBINATION_RULE`` says each ``(leg, genome)`` pair is ONE arm, but the key
    has carried the LABEL since round 6 — because refusing a same-genome /
    two-label ranking was itself a round-6 finding. On such a set the frozen
    sentence understates the keying.

    Neither refusing (re-breaks round 6) nor rewriting the frozen sentence
    (breaks the committed artifact's byte reproduction, of which it is a key) is
    available, so the artifact self-describes accurately in both cases.
    """

    row = _committed_row(0)
    twin = _committed_row(0)
    twin["label"] = "a-second-label-over-one-genome"

    leg = tmp_path / "labelled" / "leg-01"
    for tranche, seeds in (("t1", (1, 2, 3)), ("t2", (4, 5, 6))):
        rows = []
        for rank, source in enumerate((row, twin), start=1):
            entry = dict(source)
            entry["seeds"] = list(seeds)
            entry["rank"] = rank
            rows.append(entry)
        leg.mkdir(parents=True, exist_ok=True)
        (leg / f"ranking-{tranche}.jsonl").write_text(
            "".join(json.dumps(entry) + "\n" for entry in rows), encoding="utf-8"
        )

    labelled = gct.compute_stability(gct.find_ranking_files([tmp_path / "labelled"]))
    # Two labels over one genome ARE two arms (the round-6 finding) …
    assert labelled["arms_with_both_tranches"] == 2
    assert labelled["distinct_genomes"] == 1
    # … and the emitted rule SAYS so, rather than claiming the (leg, genome)
    # keying it was not computed under.
    assert labelled["combination_rule"] == (
        gct.COMBINATION_RULE + gct.COMBINATION_RULE_LABEL_CLAUSE
    )
    assert "(leg, genome, LABEL)" in labelled["combination_rule"]

    # And where the two keyings agree — every arm of the committed corpus — the
    # frozen sentence is emitted unchanged, so the artifact still reproduces.
    committed = gct.compute_stability(gct.find_ranking_files(_default_roots()))
    assert committed["combination_rule"] == gct.COMBINATION_RULE
    assert gct.main(["stability", "--check"]) == 0


def test_the_generator_never_overwrites_an_artifact_it_read(tmp_path: Path) -> None:
    """A read-only generator must not be able to destroy its own inputs (#314).

    ``rows --out`` naming its ``--rows-path``, ``legs --out`` naming a ranking
    file, or a stability output naming an input ranking would render the source
    and then replace that committed JSON/JSONL evidence with generated Markdown,
    returning 0.
    """

    # rows: --out aliasing --rows-path.
    rows_copy = tmp_path / "rows.jsonl"
    rows_copy.write_bytes(_CAMPAIGN_ROWS.read_bytes())
    before = rows_copy.read_bytes()
    with pytest.raises(SystemExit, match="it is an INPUT this render just read"):
        gct.main(["rows", "--rows-path", str(rows_copy), "--out", str(rows_copy)])
    assert rows_copy.read_bytes() == before

    # legs: --out aliasing one of the ranking files it renders.
    leg = tmp_path / "leg"
    leg.mkdir()
    for name in ("ranking-4000-4002.jsonl", "ranking-4003-4005.jsonl"):
        (leg / name).write_bytes((_RUN_01_LEG / name).read_bytes())
    target = leg / "ranking-4003-4005.jsonl"
    original = target.read_bytes()
    with pytest.raises(SystemExit, match="it is an INPUT this render just read"):
        gct.main(["legs", "--leg-dir", str(leg), "--out", str(target)])
    assert target.read_bytes() == original

    # stability: --json-out aliasing an input ranking (via a ``..`` detour, so
    # the check is on the RESOLVED path rather than the string).
    detour = leg / "sub" / ".." / "ranking-4000-4002.jsonl"
    (leg / "sub").mkdir()
    kept = (leg / "ranking-4000-4002.jsonl").read_bytes()
    with pytest.raises(SystemExit, match="it is an INPUT this render just read"):
        gct.main(
            ["stability", "--ranking-root", str(tmp_path), "--json-out", str(detour)]
        )
    assert (leg / "ranking-4000-4002.jsonl").read_bytes() == kept

    # A separate path still writes.
    out = tmp_path / "elsewhere.md"
    assert gct.main(["rows", "--rows-path", str(rows_copy), "--out", str(out)]) == 0
    assert out.read_text(encoding="utf-8").startswith("## Campaign rows")


def test_a_symlinked_ranking_root_is_not_two_campaigns(tmp_path: Path) -> None:
    """The same tree under two spellings is one input (Codex on PR #314).

    Supplying a ranking tree through both its real path and a symlink gave the
    identical files different LEXICAL leg keys, so every arm folded twice and
    the counts doubled behind a valid-looking artifact.
    """

    real = tmp_path / "campaign" / "leg-01"
    real.mkdir(parents=True)
    for name in ("ranking-4000-4002.jsonl", "ranking-4003-4005.jsonl"):
        shutil.copy(_RUN_01_LEG / name, real / name)
    link = tmp_path / "aliased"
    link.symlink_to(tmp_path / "campaign", target_is_directory=True)

    once = gct.compute_stability(gct.find_ranking_files([tmp_path / "campaign"]))
    twice = gct.compute_stability(gct.find_ranking_files([tmp_path / "campaign", link]))
    assert once["arms_with_both_tranches"] == 2
    assert twice == once, "an aliased root must not double the arms"


def test_a_label_may_not_change_genome_between_tranches(tmp_path: Path) -> None:
    """A label naming two genomes is drift, and must be reported (Codex #314).

    The digest rides the arm key, so a label reused for a different genome
    became two unrelated ONE-tranche arms — both dropped by the ``len(reads) <
    2`` branch, so the identity drift was silently omitted while the result
    succeeded on the other arms.
    """

    first, second = _committed_row(0), _committed_row(1)
    second["label"] = first["label"]  # same label, different genome
    assert first["weights_sha256"] != second["weights_sha256"]

    leg = tmp_path / "campaign" / "leg-01"
    _write_arm(leg, "t1", first, seeds=(1, 2, 3))
    _write_arm(leg, "t2", second, seeds=(4, 5, 6))
    with pytest.raises(SystemExit, match="a label that moves between genomes is drift"):
        gct.compute_stability(gct.find_ranking_files([tmp_path / "campaign"]))


def test_stability_refuses_one_path_for_both_artifacts(tmp_path: Path) -> None:
    """``--out`` and ``--json-out`` emit DIFFERENT artifacts (Codex on PR #314).

    Pointing both at one file wrote the JSON and then immediately overwrote it
    with the Markdown, returning success while silently discarding one of the
    two things the operator asked for.
    """

    shared = tmp_path / "both.json"
    with pytest.raises(SystemExit, match="they emit different artifacts"):
        gct.main(["stability", "--out", str(shared), "--json-out", str(shared)])
    assert not shared.exists()

    # Recognised through path normalisation, not just string equality.
    with pytest.raises(SystemExit, match="they emit different artifacts"):
        gct.main(
            [
                "stability",
                "--out",
                str(tmp_path / "both.json"),
                "--json-out",
                str(tmp_path / "." / "both.json"),
            ]
        )

    # And through a SYMLINK: two different path strings resolving to one file.
    # The round-11 equality check missed this; `_same_file` catches it.
    real = tmp_path / "real.md"
    real.write_text("", encoding="utf-8")
    alias = tmp_path / "alias.md"
    alias.symlink_to(real)
    with pytest.raises(SystemExit, match="they emit different artifacts"):
        gct.main(["stability", "--out", str(real), "--json-out", str(alias)])

    # Two distinct paths still emit both artifacts.
    table_out, json_out = tmp_path / "t.md", tmp_path / "t.json"
    assert (
        gct.main(["stability", "--out", str(table_out), "--json-out", str(json_out)])
        == 0
    )
    assert table_out.read_text(encoding="utf-8").startswith("| stability check")
    assert (
        json.loads(json_out.read_text(encoding="utf-8"))["arms_with_both_tranches"]
        == 22
    )


def test_no_output_may_land_under_a_frozen_evidence_root(tmp_path: Path) -> None:
    """Containment, not just aliasing, is the rule (Codex review on PR #314).

    My round-12 alias check protects only the files THIS invocation read, so an
    output naming an unrelated committed artifact — the stability record itself,
    say — overwrote frozen evidence and returned 0, in a tool whose module
    docstring and ``_emit`` both call those roots read-only history.
    """

    for frozen_root in gct.FROZEN_EVIDENCE_ROOTS:
        target = gct._REPO_ROOT / frozen_root / "__round14_probe.md"
        assert not target.exists()
        try:
            with pytest.raises(SystemExit, match="read-only history"):
                gct.main(["stability", "--out", str(target)])
            assert not target.exists()
        finally:
            # This pin writes into the REPO if the guard regresses, so it clears
            # up after itself rather than leaving the working tree dirty for
            # whoever runs the suite next.
            target.unlink(missing_ok=True)

    # The committed artifact this generator reproduces is itself protected, and
    # is byte-identical afterwards.
    committed = gct._REPO_ROOT / gct.DEFAULT_STABILITY_ARTIFACT
    original = committed.read_bytes()
    with pytest.raises(SystemExit, match="read-only history"):
        gct.main(["stability", "--json-out", str(committed)])
    assert committed.read_bytes() == original

    # A `..` segment cannot walk back in.
    with pytest.raises(SystemExit, match="read-only history"):
        gct.main(
            [
                "stability",
                "--out",
                str(
                    gct._REPO_ROOT
                    / "training"
                    / "artifacts"
                    / ".."
                    / "artifacts"
                    / "escaped.md"
                ),
            ]
        )

    # No over-reach: rendering anywhere else still works.
    outside = tmp_path / "rendered.md"
    assert gct.main(["stability", "--out", str(outside)]) == 0
    assert outside.read_text(encoding="utf-8").startswith("| stability check")


def test_rows_refuse_a_foreign_schema_version(tmp_path: Path) -> None:
    """The CLI promises ``coevo-campaign-v1``; nothing checked it (Codex #314).

    A later schema can keep these field names and change what they mean, so an
    unchecked stream renders an authoritative-looking table that is simply
    wrong — the transcription-error class this tool exists to remove.
    """

    rows = [
        json.loads(line)
        for line in _CAMPAIGN_ROWS.read_text(encoding="utf-8").splitlines()[:3]
    ]
    assert {row["schema_version"] for row in rows} == {gct.CAMPAIGN_ROWS_SCHEMA}

    forged = tmp_path / "rows.jsonl"
    bumped = [{**row, "schema_version": "coevo-campaign-v99"} for row in rows]
    forged.write_text(
        "".join(json.dumps(row) + "\n" for row in bumped), encoding="utf-8"
    )
    with pytest.raises(SystemExit, match="coevo-campaign-v99"):
        gct.render_rows_document(forged, labels=["run-01"])

    # EVERY row, not just the first: a concatenated mixed-schema stream must not
    # be judged by its opening line.
    mixed = tmp_path / "mixed.jsonl"
    mixed.write_text(
        json.dumps(rows[0]) + "\n" + json.dumps(bumped[1]) + "\n", encoding="utf-8"
    )
    with pytest.raises(SystemExit, match="coevo-campaign-v99"):
        gct.render_rows_document(mixed, labels=["run-01"])


def test_no_output_may_be_a_hard_link(tmp_path: Path) -> None:
    """Containment cannot see through a hard link (Codex review on PR #314).

    A second name OUTSIDE the frozen roots shares a frozen artifact's inode, so
    the resolved path is legitimately outside and the write truncates the shared
    bytes anyway. Resolution answers "where is this name?", which is the wrong
    question for a link that has no separate bytes to protect.
    """

    # A COPY of the frozen artifact, never the artifact itself. This pin exists
    # because a missing guard TRUNCATES the linked bytes — so pointing it at the
    # committed record would destroy that record the moment the guard regressed.
    # (It did, exactly once, during this fix's own mutation check.)
    stand_in = tmp_path / "frozen-stand-in.json"
    stand_in.write_bytes(_STABILITY_ARTIFACT.read_bytes())
    original = stand_in.read_bytes()

    link = tmp_path / "outside-the-frozen-roots.md"
    link.hardlink_to(stand_in)
    assert link.stat().st_nlink > 1

    with pytest.raises(SystemExit, match="hard link"):
        gct.main(["stability", "--out", str(link)])
    assert stand_in.read_bytes() == original
    assert _STABILITY_ARTIFACT.read_bytes() == original

    # No over-reach: an ordinary singly-linked path still renders.
    plain = tmp_path / "plain.md"
    assert gct.main(["stability", "--out", str(plain)]) == 0
    assert plain.read_text(encoding="utf-8").startswith("| stability check")


def test_a_ranking_row_must_carry_the_complete_stamp(tmp_path: Path) -> None:
    """An incomplete stamp can no longer certify its own agreement (Codex #314).

    The stability fold read identity fields with ``.get``, so a field absent
    from BOTH tranche rows collapsed to ``{None}`` and the arm passed as one
    policy read twice — a missing identity vouching for itself. And a stamp
    whose ``weights_sha256`` names other bytes than the row it sits on is a
    17.14-style conflation. Both are file-integrity properties, so both are
    checked where the file is read, not where the table is folded.
    """

    def _mutate(**stamp_overrides: object) -> dict[str, object]:
        row = _committed_row(0)
        stamp: dict[str, Any] = dict(row["stamp"])  # type: ignore[call-overload]
        for key, value in stamp_overrides.items():
            if value is _DROP:
                del stamp[key]
            else:
                stamp[key] = value
        row["stamp"] = stamp
        return row

    # The same field missing from BOTH tranches: the defect exactly.
    leg = tmp_path / "missing" / "leg-01"
    dropped = _mutate(method=_DROP)
    _write_arm(leg, "t1", dropped, seeds=(1, 2, 3))
    _write_arm(leg, "t2", dropped, seeds=(4, 5, 6))
    with pytest.raises(SystemExit, match="EXACTLY the five fields"):
        gct.compute_stability(gct.find_ranking_files([tmp_path / "missing"]))

    # A sixth field is equally not a TacticalPolicyStamp.
    leg = tmp_path / "extra" / "leg-01"
    _write_arm(leg, "t1", _mutate(surprise="x"), seeds=(1, 2, 3))
    with pytest.raises(SystemExit, match="EXACTLY the five fields"):
        gct.read_validated_ranking(leg / "ranking-t1.jsonl")

    # A non-string field would pass a set comparison and fail the consumer.
    leg = tmp_path / "typed" / "leg-01"
    _write_arm(leg, "t1", _mutate(method=7), seeds=(1, 2, 3))
    with pytest.raises(SystemExit, match="are not strings"):
        gct.read_validated_ranking(leg / "ranking-t1.jsonl")

    # A stamp naming other bytes than the row it sits on.
    leg = tmp_path / "conflated" / "leg-01"
    _write_arm(leg, "t1", _mutate(weights_sha256="b" * 64), seeds=(1, 2, 3))
    with pytest.raises(SystemExit, match="conflation guard"):
        gct.read_validated_ranking(leg / "ranking-t1.jsonl")

    # The unmutated committed row still reads cleanly.
    leg = tmp_path / "ok" / "leg-01"
    _write_arm(leg, "t1", _committed_row(0), seeds=(1, 2, 3))
    assert len(gct.read_validated_ranking(leg / "ranking-t1.jsonl")) == 1


def test_rows_split_refuses_a_gap_inside_a_segment(tmp_path: Path) -> None:
    """A missing or reordered row must not be absorbed into a segment.

    Only checking that a segment STARTS at 1 let a run that lost its
    generation-1 row merge into its predecessor, making every rendered count,
    swap total and game total plausible but wrong (Codex on PR #314).
    """

    rows = [
        json.loads(line)
        for line in _CAMPAIGN_ROWS.read_text(encoding="utf-8").splitlines()[:12]
    ]
    gapped = tmp_path / "gapped.jsonl"
    # Drop generation 5 from an otherwise well-formed run.
    kept = [row for row in rows if row["generation_index"] != 5]
    gapped.write_text("".join(json.dumps(row) + "\n" for row in kept), encoding="utf-8")
    with pytest.raises(SystemExit, match="not the consecutive"):
        gct.render_rows_document(gapped, labels=[])


def test_leg_rows_must_agree_on_the_leg_level_fields(tmp_path: Path) -> None:
    """One leg table describes ONE experiment (Codex on PR #314).

    The heading quotes seeds/roster/baseline/mode/budget from rank 1; a
    concatenated file would otherwise render an authoritative-looking table
    whose heading describes only the first candidate.
    """

    first, second = _committed_row(0), _committed_row(1)
    second["baseline_id"] = "baseline-5"
    mixed = tmp_path / "ranking-mixed.jsonl"
    mixed.write_text(
        json.dumps(first) + "\n" + json.dumps(second) + "\n", encoding="utf-8"
    )
    with pytest.raises(SystemExit, match="disagree on the leg-level field"):
        gct.render_leg_tables(mixed)


def test_stability_refuses_overlapping_tranche_seed_sets(tmp_path: Path) -> None:
    """Two tranches must be DISJOINT draws, not merely distinct ones (Codex on PR #314).

    Canonicalising on the seed set makes ``(1, 2, 3)`` and ``(3, 4, 5)`` two
    identities, so the round-3 guard passes them — but they share seed 3, whose
    single game is then counted on BOTH sides of every swing. A shared seed
    reports agreement the pair never independently observed, in the table whose
    whole job is to say how independent the measurements are.
    """

    leg = tmp_path / "campaign" / "leg"
    row = _committed_row()
    _write_arm(leg, "a", row, seeds=(1, 2, 3))
    _write_arm(leg, "b", row, seeds=(3, 4, 5))
    with pytest.raises(SystemExit, match=r"share seeds \[3\]"):
        gct.compute_stability(gct.find_ranking_files([tmp_path / "campaign"]))


def test_disjoint_tranches_over_the_same_arm_are_accepted(tmp_path: Path) -> None:
    """The disjointness guard rejects only the overlap, not two honest draws."""

    leg = tmp_path / "campaign" / "leg"
    row = _committed_row()
    _write_arm(leg, "a", row, seeds=(1, 2, 3))
    _write_arm(leg, "b", row, seeds=(4, 5, 6))
    stability = gct.compute_stability(gct.find_ranking_files([tmp_path / "campaign"]))
    assert stability["arms_with_both_tranches"] == 1


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("baseline_id", "some-other-baseline"),
        ("mode", "champion-trace"),
        ("max_ticks", 99999),
        ("num_players", 10),
        ("meeting_timeout_seconds", 12.5),
        ("max_attempts", 7),
    ],
)
def test_stability_refuses_protocol_drift_across_an_arms_reads(
    tmp_path: Path, field: str, value: object
) -> None:
    """An arm is one policy under ONE protocol, read twice (Codex on PR #314).

    Round 3 required the two reads to share an encoder FAMILY, which says the
    bytes are the same policy but nothing about the experiment around them. A
    changed roster / baseline / mode / budget between the reads makes the swing
    a measured effect of that change, which the table would then publish as
    measurement instability.
    """

    leg = tmp_path / "campaign" / "leg"
    row = _committed_row()
    # The override must actually MOVE the field, or this case asserts nothing:
    # `num_players` is already 9 in the committed row, so an unchecked 9 here
    # silently tested a matching pair and still "passed" the raises-check.
    assert row[field] != value, f"{field} override matches the committed value"
    _write_arm(leg, "a", row, seeds=(1, 2, 3))
    _write_arm(leg, "b", row, seeds=(4, 5, 6), **{field: value})
    with pytest.raises(SystemExit, match=f"different {field} across tranches"):
        gct.compute_stability(gct.find_ranking_files([tmp_path / "campaign"]))


def test_check_rejects_byte_drift_that_every_value_survives(tmp_path: Path) -> None:
    """``--check`` enforces BYTE reproduction, not value equality (Codex on PR #314).

    The PR's accepted invariant is that ``--json-out`` over the committed
    artifact is a no-op diff. A decoded comparison passes through key
    reordering, indent drift and numeric respelling, so the check would keep
    reporting "reproduces exactly" while regenerating the file changed it.
    """

    committed = gct.stability_json(
        gct.compute_stability(gct.find_ranking_files(_default_roots()))
    )
    reformatted = json.dumps(json.loads(committed), indent=4, sort_keys=True) + "\n"
    assert json.loads(reformatted) == json.loads(committed)  # every VALUE agrees
    artifact = tmp_path / "measurement-stability.json"
    artifact.write_text(reformatted, encoding="utf-8")
    assert gct.main(["stability", "--check", str(artifact)]) == 1


def test_check_passes_on_the_committed_artifact_bytes() -> None:
    """The tightened check still accepts the committed artifact unchanged."""

    assert gct.main(["stability", "--check", str(gct.DEFAULT_STABILITY_ARTIFACT)]) == 0


def test_leg_tables_refuse_a_non_contiguous_rank_sequence(tmp_path: Path) -> None:
    """Ranks must be exactly ``1..N`` (Codex on PR #314).

    Sorting by ``rank`` renders an authoritative-looking table out of a
    duplicated or truncated file, with repeated or missing positions. This
    generator exists to remove hand-assembly errors, not to reproduce them
    faster.
    """

    first, second = _committed_row(0), _committed_row(1)
    second["rank"] = 3
    path = tmp_path / "ranking-gap.jsonl"
    path.write_text(json.dumps(first) + "\n" + json.dumps(second) + "\n", "utf-8")
    with pytest.raises(SystemExit, match="not a contiguous 1..2 sequence"):
        gct.render_leg_tables(path)


def test_leg_tables_refuse_a_duplicated_candidate(tmp_path: Path) -> None:
    """One candidate holds exactly one rank — a concatenated file is refused."""

    first, second = _committed_row(0), _committed_row(0)
    second["rank"] = 2
    path = tmp_path / "ranking-dup.jsonl"
    path.write_text(json.dumps(first) + "\n" + json.dumps(second) + "\n", "utf-8")
    with pytest.raises(SystemExit, match="appears more than once"):
        gct.render_leg_tables(path)


def test_negative_seeds_do_not_break_the_disjointness_guard(tmp_path: Path) -> None:
    """Tranche seed sets are kept STRUCTURED, not reparsed from the display string.

    The identity string is lossy: seeds ``(-3, -2, -1)`` render as ``-3--2--1``,
    which splitting on ``-`` cannot invert. Round 4's guard reparsed it and
    raised ``ValueError`` on artifacts the recorder happily produces — nothing
    constrains seeds to be non-negative (Codex on PR #314).
    """

    leg = tmp_path / "campaign" / "leg"
    row = _committed_row()
    _write_arm(leg, "a", row, seeds=(-3, -2, -1))
    _write_arm(leg, "b", row, seeds=(-6, -5, -4))
    stability = gct.compute_stability(gct.find_ranking_files([tmp_path / "campaign"]))
    assert stability["arms_with_both_tranches"] == 1


def test_negative_seed_overlap_is_still_refused(tmp_path: Path) -> None:
    """Structured seed sets keep the disjointness guard working for negatives."""

    leg = tmp_path / "campaign" / "leg"
    row = _committed_row()
    _write_arm(leg, "a", row, seeds=(-3, -2, -1))
    _write_arm(leg, "b", row, seeds=(-1, 4, 5))
    with pytest.raises(SystemExit, match="share seeds"):
        gct.compute_stability(gct.find_ranking_files([tmp_path / "campaign"]))


def test_stability_validates_ranking_integrity_before_folding(tmp_path: Path) -> None:
    """The stability fold runs the SAME per-file checks the leg renderer does.

    The stability path read rows directly, so duplicated ranks/candidates or
    mixed leg settings could still yield an authoritative stability artifact as
    long as each genome had a matching read in the other tranche (Codex on
    PR #314). File integrity is a property of the file, not of the table.
    """

    leg = tmp_path / "campaign" / "leg"
    row = _committed_row()
    _write_arm(leg, "b", row, seeds=(4, 5, 6))
    # A duplicated candidate inside one tranche file.
    leg.mkdir(parents=True, exist_ok=True)
    dup = dict(row)
    dup["seeds"] = [1, 2, 3]
    dup["rank"] = 1
    second = dict(dup)
    second["rank"] = 2
    (leg / "ranking-a.jsonl").write_text(
        json.dumps(dup) + "\n" + json.dumps(second) + "\n", encoding="utf-8"
    )
    with pytest.raises(SystemExit, match="appears more than once"):
        gct.compute_stability(gct.find_ranking_files([tmp_path / "campaign"]))


def test_check_compares_raw_bytes_not_newline_normalized_text(
    tmp_path: Path,
) -> None:
    """``read_text`` normalizes newlines, which would defeat the byte invariant.

    A CRLF artifact decodes equal to the generator's LF-only string, so
    ``--check`` would report byte-for-byte reproduction while ``--json-out``
    rewrote the file to different bytes (Codex on PR #314).
    """

    committed = gct.stability_json(
        gct.compute_stability(gct.find_ranking_files(_default_roots()))
    )
    artifact = tmp_path / "measurement-stability.json"
    artifact.write_bytes(committed.replace("\n", "\r\n").encode("utf-8"))
    # Text-mode reading makes these look identical; the bytes are not.
    assert artifact.read_text() == committed
    assert artifact.read_bytes() != committed.encode("utf-8")
    assert gct.main(["stability", "--check", str(artifact)]) == 1


def test_one_genome_under_two_labels_is_a_valid_ranking(tmp_path: Path) -> None:
    """Two labels over ONE genome is output the recorder legitimately emits.

    ``run_realpath_rerank`` permits it (the 18.17 tie-break fixture, pinned by
    ``test_prescreen_coverage_is_by_candidate_identity_not_digest_set``), so
    round 4's duplicate-``weights_sha256`` refusal made this generator reject a
    ranking this PR's own recorder produces (Codex on PR #314). Labels are the
    candidate identity; digests are not.
    """

    first, second = _committed_row(0), _committed_row(0)
    second["rank"] = 2
    second["label"] = "arm-b"
    path = tmp_path / "ranking-tie.jsonl"
    path.write_text(json.dumps(first) + "\n" + json.dumps(second) + "\n", "utf-8")
    rows = gct.read_validated_ranking(path)
    assert [row["label"] for row in rows] == [first["label"], "arm-b"]
    assert len({row["weights_sha256"] for row in rows}) == 1
    # It renders, and both candidates keep their own row.
    assert len(gct.render_leg_tables(path)) > 0


def test_same_genome_two_labels_are_two_arms(tmp_path: Path) -> None:
    """Arm identity carries the LABEL, so tie-break candidates do not collapse."""

    leg = tmp_path / "campaign" / "leg"
    row = _committed_row()
    for tranche, seeds in (("a", (1, 2, 3)), ("b", (4, 5, 6))):
        first = dict(row, seeds=list(seeds), rank=1)
        second = dict(row, seeds=list(seeds), rank=2, label="arm-b")
        leg.mkdir(parents=True, exist_ok=True)
        (leg / f"ranking-{tranche}.jsonl").write_text(
            json.dumps(first) + "\n" + json.dumps(second) + "\n", encoding="utf-8"
        )
    stability = gct.compute_stability(gct.find_ranking_files([tmp_path / "campaign"]))
    # Two labels over one genome = two arms, one distinct genome.
    assert stability["arms_with_both_tranches"] == 2
    assert stability["distinct_genomes"] == 1


def test_stability_is_pure_across_independent_invocations(tmp_path: Path) -> None:
    """No process-wide state leaks between folds (Codex on PR #314).

    The tranche seed sets were briefly kept in a module-level registry that
    ``_tranche_identity`` mutated on every read. They are now threaded through
    the fold, so an unrelated invocation cannot influence a later one.
    """

    leg = tmp_path / "campaign" / "leg"
    row = _committed_row()
    _write_arm(leg, "a", row, seeds=(1, 2, 3))
    _write_arm(leg, "b", row, seeds=(4, 5, 6))
    paths = gct.find_ranking_files([tmp_path / "campaign"])

    first = gct.compute_stability(paths)
    # An unrelated fold in between must not change the next result.
    gct.compute_stability(gct.find_ranking_files(_default_roots()))
    assert gct.compute_stability(paths) == first
    assert not hasattr(gct, "_TRANCHE_SEEDS")


@pytest.mark.parametrize("field", ["policy_id", "method", "anchor_policy"])
def test_stability_refuses_stamp_identity_drift_across_an_arms_reads(
    tmp_path: Path, field: str
) -> None:
    """An arm's two reads must share the COMPLETE five-field stamp.

    This repository treats the whole stamp as policy identity — the resume
    predicate compares all five for exactly this reason — so two reads agreeing
    only on the encoder family can still be two different policies, and a swing
    between them is not measurement noise (Codex on PR #314).
    """

    leg = tmp_path / "campaign" / "leg"
    row = _committed_row()
    _write_arm(leg, "a", row, seeds=(1, 2, 3))
    stamp: dict[str, Any] = dict(row["stamp"])  # type: ignore[call-overload]
    assert stamp[field] != "some-other-value"
    stamp[field] = "some-other-value"
    drifted = dict(row)
    drifted["stamp"] = stamp
    _write_arm(leg, "b", drifted, seeds=(4, 5, 6))
    with pytest.raises(SystemExit, match=f"stamped {field}="):
        gct.compute_stability(gct.find_ranking_files([tmp_path / "campaign"]))


def test_the_saturated_floor_row_does_not_claim_impossibility() -> None:
    """A floor of exactly 1.000 is attainable at perfection, not unpassable.

    ``evaluate_supply_floors`` clears a gauge on ``measured >= floor``, so the
    rendered table must not call a saturated floor "structurally unpassable"
    (Codex on PR #314). The COUNT and its artifact key are unchanged — they
    reproduce the frozen 18.24 record — but the generator's own claim is now
    accurate.
    """

    stability = gct.compute_stability(gct.find_ranking_files(_default_roots()))
    table = gct.render_stability_table(stability)
    assert "structurally unpassable" not in table
    assert "saturated at 1.000" in table
    assert "100% conversion required" in table
    # The frozen count is untouched.
    assert stability["arms_with_impossible_conversion_floor"] == 12
    assert "**12 of 22**" in table
