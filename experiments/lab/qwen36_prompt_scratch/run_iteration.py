"""FROZEN (Phase 19 tier map, training/README.md): pre-lock prompt scratch, concluded.
Bug fixes and evidence readers only; no new search.

Iteration driver for the from-scratch qwen3.6-27b prompt set (owner-directed, 2026-07-11).

Renders one of the version directories in THIS folder through the loader's own
render functions (custom Jinja environment, identical strict-undefined / trim /
lstrip policy) and runs `Qwen/Qwen3.6-27B` NON-THINKING over the pinned 9p2i
corpora via the sweep harness cell functions — no `agents/strategic/prompts/`
registration needed, so the experiment iterates without touching the production
prompt surface (a productized set is Task 16.13's, post-lock).

The versions are an evidence LADDER (see README.md): each adds ONE rule
targeting the previous version's observed failure. Reproduce a version::

    PYTHONPATH=. uv run python experiments/lab/qwen36_prompt_scratch/run_iteration.py v5 \
        --full --facts /tmp/ailibi-gameplay-facts-9p2i.json

Reply-corpus-only (no --full) is the fast iteration loop; --votes-only is the
vote loop. Results land beside this script as results-<version>.jsonl.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import statistics
from functools import partial
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined

import agents.strategic.prompts.loader as loader
import experiments.lab.featherless_sweep as fs

HERE: Path = Path(__file__).resolve().parent


def binding_for_dir(version: str) -> fs.RenderBinding:
    """A sweep RenderBinding over this folder's ``<version>/`` template dir."""

    env = Environment(
        loader=FileSystemLoader(HERE / version),
        autoescape=False,
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    renderers = loader.PromptRenderers(
        crewmate_report=partial(loader.crewmate_report_prompt, environment=env),
        impostor_report=partial(loader.impostor_report_prompt, environment=env),
        statement=partial(loader.accusation_round_prompt, environment=env),
        vote=partial(loader.vote_ballot_prompt, environment=env),
    )
    return fs.RenderBinding(
        renderers=renderers,
        prompt_set=f"qwen36_scratch_{version}",
        is_bespoke=True,
        force_adapter=True,
        reply_is_impostor=True,
    )


def _pct(n: int, d: int) -> str:
    return f"{n}/{d} ({100 * n / d:.0f}%)" if d else "0/0"


async def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("version", help="template directory name in this folder, e.g. v5")
    ap.add_argument("--full", action="store_true", help="also run votes + openings")
    ap.add_argument(
        "--votes-only", action="store_true", help="run only the vote corpus"
    )
    ap.add_argument(
        "--facts",
        type=Path,
        default=None,
        help="extractor facts JSON (enables the opening corpus under --full)",
    )
    ap.add_argument("--concurrency", type=int, default=2)
    args = ap.parse_args()

    api_key = os.environ["FEATHERLESS_API_KEY"]
    binding = binding_for_dir(args.version)
    cfg = fs.SweepConfig(
        sample_dir=Path("replays/samples/9p2i"),
        facts_path=args.facts if args.full else None,
        prompt_set=fs.PROBE_PROMPT_SET,  # pinning only; the binding overrides the render
    )
    flags = fs._set_substrate(True)
    pinned = fs._pin_ids(cfg)
    _, replies, votes, openings = fs._contexts_for(cfg, True, pinned)
    spec = next(s for s in fs.SLATE if s.label == "qwen3-6-27b")
    sem = asyncio.Semaphore(args.concurrency)
    common: dict[str, Any] = dict(
        spec=spec,
        request_thinking=False,
        flags=flags,
        api_key=api_key,
        base_url=None,
        sem=sem,
        binding=binding,
    )

    out = HERE / f"results-{args.version}.jsonl"
    rows: list[dict[str, Any]] = []
    if args.votes_only:
        rows += await asyncio.gather(*[fs._vote_cell(item=i, **common) for i in votes])
        out.write_text("".join(json.dumps(r) + "\n" for r in rows))
        vp = [r for r in rows if r.get("parsed_ok")]
        conv = sum(1 for r in vp if r.get("voted_available_impostor"))
        print(f"vote: parse {len(vp)}/{len(rows)} conv {conv}/{len(vp)}")
        for r in vp:
            if not r.get("voted_available_impostor"):
                print(f"  MISS {r['item']} voted {r.get('target')}")
        print(f"wrote {out}")
        return 0

    rows += await asyncio.gather(
        *[
            fs._reply_cell(ctx=c, cover=cover, **common)
            for cover in (False, True)
            for c in replies
        ]
    )
    if args.full:
        rows += await asyncio.gather(*[fs._vote_cell(item=i, **common) for i in votes])
        rows += await asyncio.gather(
            *[fs._opening_cell(ctx=k, **common) for k in openings]
        )
    out.write_text("".join(json.dumps(r) + "\n" for r in rows))

    for cover in ("off", "on"):
        rr = [r for r in rows if r["corpus"] == "reply" and r["cover"] == cover]
        pp = [r for r in rr if r.get("parsed_ok")]
        print(
            f"reply cover={cover}: parse {_pct(len(pp), len(rr))} | "
            f"self-co {_pct(sum(1 for r in pp if r.get('self_co_locates_body')), len(pp))} "
            f"(alibi-in-room {sum(1 for r in pp if r.get('self_alibi_in_body_room'))}) | "
            f"deflect {_pct(sum(1 for r in pp if r.get('deflects_legal')), len(pp))} | "
            f"self-flag {_pct(sum(1 for r in pp if r.get('new_self_flag')), len(pp))} | "
            f"errors {sum(1 for r in rr if r.get('error'))}"
        )
    lat = [
        r["latency_s"] for r in rows if r["corpus"] == "reply" and r.get("parsed_ok")
    ]
    if lat:
        print(f"reply latency mean {statistics.mean(lat):.1f}s")
    if args.full:
        v = [r for r in rows if r["corpus"] == "vote"]
        vp = [r for r in v if r.get("parsed_ok")]
        o = [r for r in rows if r["corpus"] == "opening"]
        op = [r for r in o if r.get("parsed_ok")]
        print(
            f"vote: parse {_pct(len(vp), len(v))} conv "
            f"{_pct(sum(1 for r in vp if r.get('voted_available_impostor')), len(vp))} | "
            f"opening: parse {_pct(len(op), len(o))} tell "
            f"{_pct(sum(1 for r in op if r.get('self_co_locates_kill')), len(op))} "
            f"confess {_pct(sum(1 for r in op if r.get('self_incriminating_text')), len(op))}"
        )
    for r in rows:
        if (
            r["corpus"] == "reply"
            and r.get("parsed_ok")
            and r.get("self_co_locates_body")
        ):
            kind = "ALIBI-IN-ROOM" if r.get("self_alibi_in_body_room") else "FOUND-TEXT"
            print(
                f"  [{kind}] cover={r['cover']} {r['item']}: {(r.get('free_text') or '')[:150]}"
            )
        if r.get("error"):
            print(f"  [ERROR] {r['corpus']} {r.get('item')}: {str(r['error'])[:100]}")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
