#!/usr/bin/env python3
"""Check the front door's generated facts against their sources (Task 19.1).

The cheap half of the front-door truth sweep: seconds, no network, no LLM, no
engine playback. Every *checked fact* README.md and .env.example carry is
re-derived here from the committed bytes that own it, and any drift between the
prose and its source fails loud. ``scripts/verify_samples.sh`` proves the replay
bytes still reconstruct; this proves the prose still describes them — the drift
class the 19.1 sweep cleaned (a stale refresh date, a stale win rate, a stale
ladder tip, a graduated lever still documented as a live knob) is exactly what
regenerates silently otherwise.

Three checks. Each accumulates precise errors; all of them are reported
together, so one run names every drifted fact rather than the first.

1. **Sample provenance.** ``replays/samples/<set>/MANIFEST.md`` owns each sample
   set's outcomes and refresh date. The impostor win rate is recomputed from the
   ``winner`` column (rounded to a whole percent) and the newest ``refreshed_at``
   is taken across both sets; README must carry that date literally and each
   recomputed rate as the exact substring ``"<rate>% (<set>)"``.
2. **Ladder tip.** ``audits/audit-phase-18-close.md`` owns which baseline the
   substrate ladder stands at. Every README sentence naming the "ladder tip"
   must name that baseline and no other.
3. **Lever registry vs .env.example.** ``orchestrator.replay`` owns the live
   substrate-lever registry. Every still-toggleable lever must be documented
   with a commented example line showing its bare-environment default; every
   graduated lever must be named in the graduated note by its registry key and
   must NOT appear as an ``AILIBI_*=`` assignment, commented or not — its env
   gate was deleted at graduation, so an assignment line would hand out a knob
   this build does not read.

``--repo-root`` points the document and source reads at another tree (the unit
tests perturb a copy); it defaults to this checkout. The lever registry ALWAYS
comes from the live import, never from ``--repo-root``: the registry is code,
and a doc copy is checked against the levers this build actually ships.

Exit 0 when every checked fact matches, 1 with every failure printed.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Final

_REPO_ROOT: Final = Path(__file__).resolve().parents[1]
_SCRIPTS_DIR: Final = Path(__file__).resolve().parent
# Make both the top-level packages (``orchestrator``) and the sibling script
# modules (``_manifest_writer``, a top-level name per ``mypy_path = "scripts"``)
# importable under ``uv run python scripts/check_doc_facts.py``. Mirrors
# scripts/build_sample_report.py.
for _bootstrap_path in (_REPO_ROOT, _SCRIPTS_DIR):
    if str(_bootstrap_path) not in sys.path:
        sys.path.insert(0, str(_bootstrap_path))

from _manifest_writer import parse_manifest  # noqa: E402

from orchestrator.replay import (  # noqa: E402
    SUBSTRATE_FLAG_KEYS,
    TOGGLEABLE_SUBSTRATE_FLAG_KEYS,
    substrate_flag_snapshot,
)

_README: Final = "README.md"
_ENV_EXAMPLE: Final = ".env.example"
_LADDER_TIP_AUDIT: Final = "audits/audit-phase-18-close.md"
_SAMPLE_SETS: Final[tuple[str, ...]] = ("4p1i", "9p2i")
_MANIFEST_PATH: Final = "replays/samples/{name}/MANIFEST.md"

# The ``winner`` cell a manifest row carries when the impostors took the game.
_IMPOSTOR_WINNER: Final = "IMPOSTORS"
# ``refreshed_at`` is ISO ``YYYY-MM-DD``, so lexicographic max is chronological.
_ISO_DATE: Final = re.compile(r"\d{4}-\d{2}-\d{2}\Z")

_AUDIT_LADDER_TIP: Final = re.compile(
    r"ladder tip stands at \*{0,2}baseline (\d+)", re.IGNORECASE
)
_LADDER_TIP_PHRASE: Final = re.compile(r"ladder tip", re.IGNORECASE)
_BASELINE_MENTION: Final = re.compile(r"baseline[ -](\d+)", re.IGNORECASE)
# A sentence boundary: a period followed by whitespace or end of text, so
# version numbers and decimals ("18.12", "0.8646") do not end a sentence.
_SENTENCE_END: Final = re.compile(r"\.(?=\s|\Z)")
_SENTENCE_WINDOW: Final = 120


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check README.md and .env.example against the committed bytes that "
            "own their facts (Task 19.1)."
        )
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=_REPO_ROOT,
        help=(
            "Tree whose documents and sources are read (default: this "
            "checkout). The substrate-lever registry always comes from the "
            "live import, never from this tree."
        ),
    )
    args = parser.parse_args(argv)
    repo_root: Path = args.repo_root

    errors = check_facts(repo_root)
    if errors:
        print("Doc-fact check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        f"Doc facts verified: {_README} and {_ENV_EXAMPLE} agree with "
        f"{len(_SAMPLE_SETS)} sample manifests, {_LADDER_TIP_AUDIT}, and the "
        f"{len(SUBSTRATE_FLAG_KEYS)}-lever substrate registry."
    )
    return 0


def check_facts(repo_root: Path) -> list[str]:
    """Every checked-fact failure under ``repo_root``, in check order."""

    errors: list[str] = []
    readme = read_document(repo_root, _README, errors)
    if readme is not None:
        check_sample_provenance(repo_root, readme, errors)
        check_ladder_tip(repo_root, readme, errors)
    check_lever_registry(repo_root, errors)
    return errors


def check_sample_provenance(repo_root: Path, readme: str, errors: list[str]) -> None:
    """README's sample refresh date + win rates, re-derived from the MANIFESTs.

    The rate is ``rows won by IMPOSTORS / rows``, rounded to a whole percent —
    the same arithmetic the README paragraph states in prose. A manifest that
    parses to zero rows is a hard failure rather than a vacuous pass: silent
    format drift would otherwise let any claim through.
    """

    dates: list[str] = []
    for name in _SAMPLE_SETS:
        relative_path = _MANIFEST_PATH.format(name=name)
        text = read_document(repo_root, relative_path, errors)
        if text is None:
            continue
        rows = list(parse_manifest(text).values())
        if not rows:
            errors.append(
                f"{relative_path}: parsed zero table rows — the manifest format "
                "drifted away from _manifest_writer.parse_manifest, so neither "
                "the win rate nor the refresh date can be re-derived."
            )
            continue

        impostor_wins = sum(
            1 for row in rows if row.winner.strip().upper() == _IMPOSTOR_WINNER
        )
        claim = f"{round(100 * impostor_wins / len(rows))}% ({name})"
        if claim not in readme:
            errors.append(
                f"{_README}: missing the recorded impostor win rate {claim!r} — "
                f"{relative_path} records {impostor_wins}/{len(rows)} games won "
                "by the impostors."
            )

        set_dates = [
            row.refreshed_at.strip()
            for row in rows
            if _ISO_DATE.match(row.refreshed_at.strip())
        ]
        if not set_dates:
            errors.append(
                f"{relative_path}: no row carries an ISO refreshed_at date, so "
                "the sample-set refresh date cannot be re-derived."
            )
        dates.extend(set_dates)

    if not dates:
        return
    newest = max(dates)
    if newest not in readme:
        errors.append(
            f"{_README}: missing the sample-set refresh date {newest!r} — the "
            "newest refreshed_at across "
            f"{', '.join(_MANIFEST_PATH.format(name=name) for name in _SAMPLE_SETS)}."
        )


def check_ladder_tip(repo_root: Path, readme: str, errors: list[str]) -> None:
    """No README "ladder tip" sentence may name a baseline other than the tip.

    The tip itself is parsed from the phase-18 close audit, which is where the
    ladder's standing is recorded; whitespace is collapsed first because the
    audit wraps its prose mid-sentence.
    """

    audit = read_document(repo_root, _LADDER_TIP_AUDIT, errors)
    if audit is None:
        return
    recorded = _AUDIT_LADDER_TIP.findall(re.sub(r"\s+", " ", audit))
    if not recorded:
        errors.append(
            f"{_LADDER_TIP_AUDIT}: no 'the ladder tip stands at baseline N' "
            "sentence — the ladder tip has no committed source to check against."
        )
        return
    if len(set(recorded)) > 1:
        named = ", ".join(f"baseline {tip}" for tip in sorted(set(recorded)))
        errors.append(
            f"{_LADDER_TIP_AUDIT}: disagreeing ladder-tip records ({named}); "
            "the audit must record one tip."
        )
        return

    tip = recorded[0]
    for phrase in _LADDER_TIP_PHRASE.finditer(readme):
        window = sentence_window(readme, phrase.start(), phrase.end())
        for mention in _BASELINE_MENTION.finditer(window):
            if mention.group(1) == tip:
                continue
            errors.append(
                f"{_README}:{line_number(readme, phrase.start())}: a 'ladder "
                f"tip' sentence names baseline {mention.group(1)}, but "
                f"{_LADDER_TIP_AUDIT} records the ladder tip at baseline "
                f"{tip} — “{window.strip()}”."
            )


def check_lever_registry(repo_root: Path, errors: list[str]) -> None:
    """.env.example against the live substrate-lever registry.

    Toggleable levers must be documented with a commented example line showing
    the value this build resolves under a bare environment. Graduated levers
    must be named by their registry key — the recording stamp and the MANIFEST
    ``flags`` cell still carry them — but must never appear as an ``AILIBI_*=``
    assignment: their env gate is gone, so such a line documents nothing.
    """

    text = read_document(repo_root, _ENV_EXAMPLE, errors)
    if text is None:
        return
    bare_defaults = substrate_flag_snapshot({})

    for key in TOGGLEABLE_SUBSTRATE_FLAG_KEYS:
        variable = env_var_for(key)
        if variable not in text:
            errors.append(
                f"{_ENV_EXAMPLE}: live toggle {key!r} is undocumented — "
                f"{variable} appears nowhere, so the one substrate knob this "
                "build still reads is invisible to anyone copying the template."
            )
            continue
        default = "1" if bare_defaults.get(key, False) else "0"
        example = re.compile(
            rf"^#[ \t]*{re.escape(variable)}={default}[ \t]*$", re.MULTILINE
        )
        if example.search(text) is None:
            errors.append(
                f"{_ENV_EXAMPLE}: live toggle {key!r} has no commented example "
                f"line '# {variable}={default}' showing its bare-environment "
                "default in this build."
            )

    toggleable = set(TOGGLEABLE_SUBSTRATE_FLAG_KEYS)
    for key in SUBSTRATE_FLAG_KEYS:
        if key in toggleable:
            continue
        if re.search(rf"\b{re.escape(key)}\b", text) is None:
            errors.append(
                f"{_ENV_EXAMPLE}: graduated lever {key!r} is missing from the "
                "graduated-levers note; orchestrator.replay still stamps it "
                "into every recording, so the template must keep naming it."
            )
        assignment = f"{env_var_for(key)}="
        if assignment in text:
            errors.append(
                f"{_ENV_EXAMPLE}: {assignment!r} documents a knob that no "
                f"longer exists — {key!r} graduated to unconditionally ON and "
                "its env gate was deleted, so setting the variable does nothing."
            )


def env_var_for(key: str) -> str:
    """The ``AILIBI_*`` variable a substrate-lever registry key derives."""

    return f"AILIBI_{key.upper()}"


def sentence_window(text: str, start: int, end: int) -> str:
    """The sentence-ish neighbourhood of ``text[start:end]``.

    Up to :data:`_SENTENCE_WINDOW` characters each side, clipped at the nearest
    sentence boundary. README paragraphs are single long lines, so the clip —
    not the line — is what keeps one paragraph's baselines from bleeding into
    another sentence's ladder-tip claim.
    """

    left = text[max(0, start - _SENTENCE_WINDOW) : start]
    boundaries = list(_SENTENCE_END.finditer(left))
    if boundaries:
        left = left[boundaries[-1].end() :]
    right = text[end : end + _SENTENCE_WINDOW]
    boundary = _SENTENCE_END.search(right)
    if boundary is not None:
        right = right[: boundary.start()]
    return left + text[start:end] + right


def line_number(text: str, offset: int) -> int:
    """The 1-indexed line ``offset`` falls on."""

    return text.count("\n", 0, offset) + 1


def read_document(repo_root: Path, relative_path: str, errors: list[str]) -> str | None:
    """``repo_root/relative_path``'s text, or ``None`` with an error recorded."""

    try:
        return (repo_root / relative_path).read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"{relative_path}: unreadable ({exc}).")
        return None


if __name__ == "__main__":
    raise SystemExit(main())
