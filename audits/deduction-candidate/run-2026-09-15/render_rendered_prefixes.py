"""Write out the prefixes this run rendered — and only those.

Rendering a held-out prefix to the model converts it to development data, which
is why the rendered ones are archived here. The prefixes this run regenerated,
checked against the frozen digests and then discarded UNRENDERED are still held
out and are deliberately absent: the seeds this script writes are read off the
archived replays, never off the freeze record.

    .venv/bin/python audits/deduction-candidate/run-2026-09-15/render_rendered_prefixes.py \
      audits/deduction-candidate/run-2026-09-15 \
      > audits/deduction-candidate/run-2026-09-15/rendered-prefixes.json
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
    "archived here; the other 37 accepted prefixes of the 7000-7999 freeze were "
    "regenerated in process, checked against the frozen digests and discarded "
    "unrendered, so they stay held out and are deliberately absent."
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
