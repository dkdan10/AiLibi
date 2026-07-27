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

import pytest

import generate_campaign_tables as gct

_REPO_ROOT = Path(__file__).resolve().parents[2]
_COEVO = _REPO_ROOT / "training" / "artifacts" / "coevo"
_STABILITY_ARTIFACT = _COEVO / "measurement-stability.json"
_RUN_01_LEG = _COEVO / "realpath" / "run-01-utility-champion"
_CAMPAIGN_ROWS = _REPO_ROOT / "training" / "reports" / "results-impostor-campaign.jsonl"


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
    """

    row = dict(source_row)
    row["seeds"] = list(seeds)
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
    """One ranking file is one tranche; disagreeing rows are corruption."""

    first, second = _committed_row(0), _committed_row(1)
    first["seeds"] = [1, 2, 3]
    second["seeds"] = [4, 5, 6]
    leg = tmp_path / "campaign" / "leg-01"
    leg.mkdir(parents=True)
    (leg / "ranking-mixed.jsonl").write_text(
        json.dumps(first) + "\n" + json.dumps(second) + "\n", encoding="utf-8"
    )
    with pytest.raises(SystemExit, match="mixes seed sets"):
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
