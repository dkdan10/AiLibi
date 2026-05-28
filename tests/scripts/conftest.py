"""Make the top-level ``scripts/`` modules importable from these tests.

The project resolves script modules as top-level names (``mypy_path = "scripts"``
in pyproject.toml; ``scripts/`` has no ``__init__.py``). Importing them as
``scripts.foo`` would make mypy see the same file under two module names, so the
tests import the bare module name (``import _manifest_writer``) and this conftest
puts ``scripts/`` on ``sys.path`` so that resolves at runtime too.
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
