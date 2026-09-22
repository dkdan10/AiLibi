"""One home for locating, reading and writing a set's tournament eval report.

The committed report is stored **gzipped** — ``tournament-eval-report.json.gz``
— and the uncompressed ``.json`` is tracked nowhere. That is a DELIVERY-PATH
choice and nothing else: the bytes inside the archive are the identical bytes
``scripts/build_sample_report.py`` has always written, so no measured value
moves with it. The owner took the decision on 2026-09-22, at the re-record that
first pushed a report over GitHub's hard 100 MB per-file limit
(``replays/ml_corpus/9p2i`` reached 102.70 MB, and gzip ``-9`` takes it to
8.92 MB — the four sets compress 6.9x to 11.7x).

Everything that resolves, reads or writes that file goes through THIS module, so
a later format change is one edit rather than ten. The readers it serves are the
live loader (:mod:`api.replay_loader`), the eval route, the report builder's own
``--check``, the front-door fact checker, the offline counterfactual, and the
tests that read a committed set.

**Determinism matters and is enforced here.** ``gzip`` normally stamps an mtime
and the source filename into the header, which would make two archives of
identical bytes differ and turn every rebuild into a spurious diff. This writer
pins ``mtime=0`` and an empty embedded filename, so the archive is a pure
function of its contents: compressing the same report twice gives byte-identical
output, and ``--check`` stays a real consistency gate rather than noise.

Reading is strict, with no silent fallback (AGENTS.md). A set holding only a
legacy uncompressed ``.json`` raises a message naming the conversion rather than
quietly reading it, because a stale uncompressed file beside a fresh archive is
exactly the drift this module exists to prevent.
"""

from __future__ import annotations

import gzip
import json
from pathlib import Path
from typing import Any, Final

#: The committed report's filename, gzipped.
REPORT_FILENAME: Final[str] = "tournament-eval-report.json.gz"

#: The pre-2026-09-22 uncompressed name. Kept ONLY so a reader can say what is
#: wrong when it finds one; nothing reads it as a report.
LEGACY_REPORT_FILENAME: Final[str] = "tournament-eval-report.json"

#: Matches the ratio measured at the adopting record (11.5x on the corpus set).
COMPRESSLEVEL: Final[int] = 9


def report_path(set_dir: Path | str) -> Path:
    """The report archive's path inside ``set_dir``."""

    return Path(set_dir) / REPORT_FILENAME


def legacy_report_path(set_dir: Path | str) -> Path:
    """Where an unconverted uncompressed report would sit."""

    return Path(set_dir) / LEGACY_REPORT_FILENAME


def compress_report_text(text: str) -> bytes:
    """Serialize report text to deterministic gzip bytes.

    ``mtime=0`` and an empty embedded filename are what make this a pure
    function of ``text``: without them the header carries the wall clock and the
    source path, and two archives of identical bytes would differ.
    """

    import io

    buffer = io.BytesIO()
    with gzip.GzipFile(
        filename="", mode="wb", compresslevel=COMPRESSLEVEL, fileobj=buffer, mtime=0
    ) as archive:
        archive.write(text.encode("utf-8"))
    return buffer.getvalue()


def write_report_text(path: Path | str, text: str) -> Path:
    """Write ``text`` to ``path`` as a deterministic gzip archive."""

    destination = Path(path)
    destination.write_bytes(compress_report_text(text))
    return destination


def read_report_text(path: Path | str) -> str:
    """Read a report archive back to its exact uncompressed text.

    Raises :class:`FileNotFoundError` when the archive is absent — the eval
    route maps that to an HTTP 404 — and names the legacy file explicitly when
    one is sitting there unconverted, rather than reading it.
    """

    source = Path(path)
    if not source.exists():
        legacy = source.with_name(LEGACY_REPORT_FILENAME)
        if legacy.exists():
            raise FileNotFoundError(
                f"{source} is absent but {legacy} is present: this set holds an "
                "UNCONVERTED uncompressed report. Rebuild it with "
                "`scripts/build_sample_report.py --sample-dir <set>`, which "
                "writes the gzipped form; the uncompressed file is tracked "
                "nowhere."
            )
        raise FileNotFoundError(str(source))
    with gzip.open(source, "rt", encoding="utf-8") as archive:
        return archive.read()


def open_report_text(path: Path | str) -> Any:
    """Open a report archive as a LINE-ITERABLE text stream.

    The committed reports reach tens of megabytes uncompressed, and
    ``scripts/check_doc_facts.py`` decodes one named block by streaming rather
    than loading the document. Gzip streams line by line just as a plain file
    does, so that property survives the delivery change; the caller closes it.
    """

    return gzip.open(Path(path), "rt", encoding="utf-8")


def load_report(path: Path | str) -> Any:
    """Read a report archive and parse its JSON."""

    return json.loads(read_report_text(path))


def read_set_report_text(set_dir: Path | str) -> str:
    """:func:`read_report_text` for a set directory."""

    return read_report_text(report_path(set_dir))


def load_set_report(set_dir: Path | str) -> Any:
    """:func:`load_report` for a set directory."""

    return load_report(report_path(set_dir))


__all__ = [
    "COMPRESSLEVEL",
    "LEGACY_REPORT_FILENAME",
    "REPORT_FILENAME",
    "compress_report_text",
    "legacy_report_path",
    "load_report",
    "load_set_report",
    "open_report_text",
    "read_report_text",
    "read_set_report_text",
    "report_path",
    "write_report_text",
]
