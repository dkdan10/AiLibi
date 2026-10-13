"""Write out the prefixes this run rendered — and only those.

Rendering a held-out prefix to the model converts it to development data, which
is why the rendered ones are archived here. This run completed all fifty
accepted seeds of the 8000-8999 freeze, so all fifty are written: the seeds are
read off the archived replays, never off the freeze record, so the rule this
script enforces is the same one the four stopped runs' archives enforced when
they wrote out only the handful they had reached.

    .venv/bin/python audits/deduction-candidate/run-2026-09-16/render_rendered_prefixes.py \
      audits/deduction-candidate/run-2026-09-16 \
      > audits/deduction-candidate/run-2026-09-16/rendered-prefixes.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Run by path, ``sys.path[0]`` is this directory rather than the repository
# root, so the generator this script exists to call would not import. The root
# is three levels up from here (audits/deduction-candidate/run-<date>/).
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from experiments.held_out_prefixes import (  # noqa: E402
    MANIFEST_PATH,
    PREREGISTERED_BAND,
    canonical_prefix_json,
    generate,
    prefix_sha256,
)

NOTE = (
    "The prefixes this run RENDERED to the model, and only those. Rendering "
    "converts a held-out input to development data, which is why they are "
    "archived here. This run completed all one hundred units, so all fifty "
    "accepted prefixes of the 8000-8999 freeze were rendered and all fifty are "
    "written out; the seeds are read off the archived replays rather than off "
    "the freeze record, so a stopped run using this script would write only the "
    "ones it reached."
)


def main(directory: Path) -> int:
    rendered_seeds = sorted(
        {int(path.stem.partition("-seed-")[2]) for path in directory.glob("*.jsonl")}
    )
    frozen = {
        row["seed"]: row["sha256"]
        for row in json.loads(Path(MANIFEST_PATH).read_text())["accepted"]
    }
    # The unchanged generator, drawing the preregistered band exactly as the run
    # did; only the seeds the replays name are written out.
    regenerated = {prefix.seed: prefix for prefix in generate().prefixes}
    rendered = []
    for seed in rendered_seeds:
        prefix = regenerated[seed]
        digest = prefix_sha256(prefix)
        if digest != frozen[seed]:
            raise SystemExit(f"seed {seed} does not rebuild to its frozen digest")
        rendered.append(
            {
                "seed": seed,
                "sha256": digest,
                "frozen_sha256": frozen[seed],
                "canonical_json": json.loads(canonical_prefix_json(prefix)),
            }
        )
    print(
        json.dumps(
            {
                "band": {
                    "first_seed": PREREGISTERED_BAND.first_seed,
                    "last_seed": PREREGISTERED_BAND.last_seed,
                    "size": PREREGISTERED_BAND.size,
                },
                "note": NOTE,
                "rendered": rendered,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))
