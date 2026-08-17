"""The API imports and serves from a FOREIGN working directory (Task 19.24).

``api/main.py`` builds its app at module scope (``app = create_app()``, what
``docker-compose.yml``'s ``uvicorn api.main:app`` loads), and until Task 19.24 it
resolved its replay root through ``Path("./replays")``. Both facts together made
a plain ``import api.main`` from anywhere but the repo root raise at IMPORT time
— not on the first request, where an operator might connect it to their setup —
and made "which corpus is this serving?" a function of where the process
happened to be started.

This is the executable half of the fix. It has to run in a SUBPROCESS: the
in-process ``api.main`` is imported long before any test body runs, so only a
fresh interpreter, started elsewhere, actually re-executes module scope. The
subprocess gets ``PYTHONPATH=<repo root>`` — the "installed elsewhere, run from
elsewhere" posture, which is exactly the case the repo anchor exists for — and a
scrubbed ``AILIBI_REPLAY_DIR`` so the ANCHORED FALLBACK is what carries the test
rather than an env var pointing home.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from api.main import ENV_REPLAY_DIR

_REPO_ROOT = Path(__file__).resolve().parents[2]

# Import the app the deployment entry point imports (module scope, no factory
# call of our own), serve two routes through it, and report what came back.
_PROBE = """
import json
import os
import sys

from fastapi.testclient import TestClient

import api.main

client = TestClient(api.main.app)
health = client.get("/health")
sets = client.get("/sets")
print(
    json.dumps(
        {
            "cwd": os.getcwd(),
            "module_file": api.main.__file__,
            "health_status": health.status_code,
            "health_body": health.json(),
            "sets_status": sets.status_code,
            "sets": sets.json(),
        }
    )
)
"""


def _run_probe(cwd: Path, *, replay_dir: str | None = None) -> dict[str, object]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(_REPO_ROOT)
    env.pop(ENV_REPLAY_DIR, None)
    if replay_dir is not None:
        env[ENV_REPLAY_DIR] = replay_dir
    proc = subprocess.run(
        [sys.executable, "-c", _PROBE],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, (
        f"importing and serving api.main from {cwd} failed "
        f"(exit {proc.returncode}):\n{proc.stderr}"
    )
    # The app announces its replay root on stderr, so the payload is the LAST
    # stdout line rather than the whole stream.
    payload = json.loads(proc.stdout.strip().splitlines()[-1])
    assert isinstance(payload, dict)
    return payload


def test_api_imports_and_serves_from_a_foreign_cwd(tmp_path: Path) -> None:
    """A fresh interpreter, started in an empty directory, serves the corpus."""

    foreign = tmp_path / "somewhere-else"
    foreign.mkdir()

    result = _run_probe(foreign)

    assert result["cwd"] == str(foreign.resolve())
    # The repo's api/main.py — not some shadow copy under the foreign directory.
    assert result["module_file"] == str(_REPO_ROOT / "api" / "main.py")
    assert result["health_status"] == 200
    assert result["health_body"] == {"status": "ok", "service": "ailibi-api"}
    # And it is really serving the recorded corpus, not an empty registry.
    assert result["sets_status"] == 200
    sets = result["sets"]
    assert isinstance(sets, dict)
    assert sets["sets"], "the foreign-CWD app resolved a replay root with no sets"


def test_the_served_corpus_does_not_depend_on_the_working_directory(
    tmp_path: Path,
) -> None:
    """Two CWDs, one answer — the property the anchor buys.

    The foreign directory is seeded with a DECOY ``replays/9p2i/`` that the old
    CWD-relative resolver would have picked up in preference to the repo's own
    corpus. The two runs must agree.
    """

    foreign = tmp_path / "with-a-decoy-corpus"
    decoy_set = foreign / "replays" / "9p2i"
    decoy_set.mkdir(parents=True)
    (decoy_set / "replay-seed-0.jsonl").write_text("{}\n", encoding="utf-8")

    from_repo = _run_probe(_REPO_ROOT)
    from_foreign = _run_probe(foreign)

    assert from_foreign["sets"] == from_repo["sets"]


def test_a_relative_configured_replay_dir_is_anchored_too(tmp_path: Path) -> None:
    """The shipped setters configure a RELATIVE path, so it gets the same test.

    ``scripts/run_spectator.sh`` exports ``AILIBI_REPLAY_DIR=replays/samples`` and
    ``frontend/playwright.config.ts`` passes the same string. Scrubbing the
    variable (as the cases above do) would leave the most common real
    configuration untested — and read against the CWD it lands on the decoy
    planted here rather than the repo's corpus.
    """

    foreign = tmp_path / "relative-env-decoy"
    decoy_set = foreign / "replays" / "samples" / "decoy-set"
    decoy_set.mkdir(parents=True)
    (decoy_set / "replay-seed-0.jsonl").write_text("{}\n", encoding="utf-8")

    result = _run_probe(foreign, replay_dir="replays/samples")

    assert result["sets_status"] == 200
    sets = result["sets"]
    assert isinstance(sets, dict)
    assert "decoy-set" not in sets["sets"], (
        "a relative AILIBI_REPLAY_DIR resolved against the working directory"
    )
    # Same answer as the unconfigured run from the repo root: the relative path
    # names the repo's corpus from a foreign CWD, exactly as it does from home.
    assert sets == _run_probe(_REPO_ROOT)["sets"]
