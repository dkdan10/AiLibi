"""The gzipped eval report: determinism, strictness, and the planted failure.

The committed report became ``tournament-eval-report.json.gz`` at the owner's
delivery decision of 2026-09-22, when ``replays/ml_corpus/9p2i`` reached
102.70 MB and GitHub refused the push at its hard 100 MB per-file limit. The
change is DELIVERY ONLY: the bytes inside the archive are the bytes the builder
has always written, which the adopting record proves by sha256 on all four sets.

These tests hold the three properties that claim depends on.
"""

from __future__ import annotations

import gzip
import json
from pathlib import Path

import pytest

from eval.report_io import (
    LEGACY_REPORT_FILENAME,
    REPORT_FILENAME,
    compress_report_text,
    load_report,
    open_report_text,
    read_report_text,
    report_path,
    write_report_text,
)

_PAYLOAD = json.dumps({"report": {"games": [{"seed": 0}]}}, indent=2) + "\n"


class TestTheArchiveIsDeterministic:
    """Two archives of the same text must be byte-identical.

    Without this the gzip header's mtime and embedded filename would vary per
    build, every rebuild would look like a diff, and ``--check`` would stop
    being a consistency gate.
    """

    def test_compressing_twice_gives_identical_bytes(self) -> None:
        assert compress_report_text(_PAYLOAD) == compress_report_text(_PAYLOAD)

    def test_the_header_carries_no_mtime_and_no_filename(self) -> None:
        blob = compress_report_text(_PAYLOAD)
        # RFC 1952: MTIME is bytes 4-7, and FNAME (flag bit 3) would follow.
        assert blob[4:8] == b"\x00\x00\x00\x00", "mtime must be pinned to 0"
        assert not blob[3] & 0x08, "no source filename may be embedded"

    def test_writing_twice_gives_identical_files(self, tmp_path: Path) -> None:
        first = write_report_text(tmp_path / "a.gz", _PAYLOAD).read_bytes()
        second = write_report_text(tmp_path / "b.gz", _PAYLOAD).read_bytes()
        assert first == second


class TestTheContentSurvivesTheDeliveryChange:
    def test_round_trip_is_exact(self, tmp_path: Path) -> None:
        path = write_report_text(report_path(tmp_path), _PAYLOAD)
        assert read_report_text(path) == _PAYLOAD

    def test_load_report_parses_the_decompressed_json(self, tmp_path: Path) -> None:
        write_report_text(report_path(tmp_path), _PAYLOAD)
        assert load_report(report_path(tmp_path)) == json.loads(_PAYLOAD)

    def test_the_archive_streams_line_by_line(self, tmp_path: Path) -> None:
        # check_doc_facts decodes ONE block by streaming; the committed reports
        # are tens of megabytes uncompressed and must never be loaded whole.
        write_report_text(report_path(tmp_path), _PAYLOAD)
        with open_report_text(report_path(tmp_path)) as handle:
            lines = list(handle)
        assert lines == _PAYLOAD.splitlines(keepends=True)


class TestReadingIsStrictWithNoSilentFallback:
    def test_a_missing_archive_raises_file_not_found(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            read_report_text(report_path(tmp_path))

    def test_an_unconverted_legacy_file_is_named_not_read(self, tmp_path: Path) -> None:
        # The drift this module exists to prevent: a stale uncompressed report
        # beside an absent archive must FAIL LOUD, never be read as the report.
        (tmp_path / LEGACY_REPORT_FILENAME).write_text(_PAYLOAD, encoding="utf-8")
        with pytest.raises(FileNotFoundError) as excinfo:
            read_report_text(report_path(tmp_path))
        assert LEGACY_REPORT_FILENAME in str(excinfo.value)
        assert "build_sample_report.py" in str(excinfo.value)


class TestThePlantedCheckFailure:
    """A ``.gz`` whose decompressed bytes differ from the rebuild fails --check.

    The delivery change must not weaken the consistency gate: compressing a
    WRONG report has to be caught exactly as writing a wrong report was.
    """

    def test_a_tampered_archive_decompresses_to_different_bytes(
        self, tmp_path: Path
    ) -> None:
        path = report_path(tmp_path)
        write_report_text(path, _PAYLOAD)
        assert read_report_text(path) == _PAYLOAD

        tampered = json.loads(_PAYLOAD)
        tampered["report"]["games"][0]["seed"] = 999
        write_report_text(path, json.dumps(tampered, indent=2) + "\n")

        assert read_report_text(path) != _PAYLOAD
        assert json.loads(read_report_text(path))["report"]["games"][0]["seed"] == 999

    def test_a_valid_gzip_of_the_wrong_payload_is_still_readable_and_wrong(
        self, tmp_path: Path
    ) -> None:
        # The failure mode --check must catch: a well-formed archive is NOT
        # evidence that its contents match the replays. Readability and
        # correctness are separate, and only the second is a gate.
        path = report_path(tmp_path)
        with gzip.open(path, "wt", encoding="utf-8") as handle:
            handle.write('{"report": {"games": []}}\n')
        assert json.loads(read_report_text(path))["report"]["games"] == []
        assert read_report_text(path) != _PAYLOAD


def test_the_filename_is_the_gzipped_one() -> None:
    assert REPORT_FILENAME == "tournament-eval-report.json.gz"
    assert LEGACY_REPORT_FILENAME == "tournament-eval-report.json"
