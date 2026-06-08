"""Matrix runner — drive local Ollama over the reconstructed decision corpus.

For each cell (model x think x num_ctx x prompt-variant) and each corpus item,
render the vote-ballot prompt and call Ollama DIRECTLY via
:func:`llm.ollama_client._default_send` — bypassing ``OllamaClient.complete``
(which hardcodes ``think=False`` and *raises* on thinking) so the harness owns
the ``think`` toggle and can capture the separate ``thinking`` channel. The
response text is parsed through the SAME production path
(:func:`llm.provider._extract_json_block` + ``VoteBallot.model_validate_json``)
so parse fidelity matches the sim.

Per call it records: parsed target/confidence, rationale + thinking token-proxy
lengths, input/output tokens, wall latency, and parse success — the raw material
for both the F1 decision analysis and the F2 config (latency/pollution/
truncation) analysis. Ground truth is carried on each record so ``grade.py``
needs no re-join.

Runs sequentially (Ollama serves one stream; clean per-call timing). $0.

Usage::

    # P1 config probe (baseline prompt, full config matrix):
    python -m experiments.model_probe.probe --seeds 0,1,2,3,4 --out p1

    # smoke one cell:
    python -m experiments.model_probe.probe --seeds 0 --models qwen3.5:9b \\
        --think false --num-ctx 8192 --limit 2 --out smoke
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import time
import urllib.request
from collections.abc import Callable
from pathlib import Path

from pydantic import ValidationError

from experiments.model_probe.corpus import (
    DEFAULT_SAMPLE_DIR,
    CorpusItem,
    VoteContext,
    build_corpus,
    render_prompt,
)
from experiments.model_probe.variants import variant_renderers
from llm.ollama_client import _default_send
from llm.provider import _extract_json_block
from meetings.schemas import VoteBallot

DEFAULT_MODELS = ("qwen2.5:7b-instruct", "qwen3.5:9b")
DEFAULT_NUM_CTX = (8192, 16384)
DEFAULT_THINK = (False, True)
# Generous output cap so num_ctx is the binding constraint we study (F2): the
# 9B think=false rationale balloons past the old 1024 vote cap, so let it run
# and measure how long it wants to be.
NUM_PREDICT = 6000
SEED = 0
TEMPERATURE = 0.0
RESULTS_DIR = Path(__file__).resolve().parent / "results"


def _ollama_host() -> str:
    return os.environ.get("AILIBI_OLLAMA_HOST", "localhost:11434")


def preflight(models: tuple[str, ...]) -> None:
    """Fail loud if Ollama is down or a model is not pulled (no silent fallback)."""

    host = _ollama_host()
    base = host if host.startswith(("http://", "https://")) else "http://" + host
    url = base.rstrip("/") + "/api/tags"
    with urllib.request.urlopen(url, timeout=5) as resp:  # noqa: S310 (localhost)
        payload = json.loads(resp.read().decode("utf-8"))
    pulled = {str(entry.get("name", "")) for entry in payload.get("models", [])}
    missing = [m for m in models if m not in pulled]
    if missing:
        raise SystemExit(
            f"Models not pulled: {missing}. Pulled: {sorted(pulled)}. "
            f"Run `ollama pull <model>` first."
        )


def select_corpus(
    items: list[CorpusItem],
    *,
    all_votes: bool,
    crew_all: bool,
    limit: int | None,
) -> list[CorpusItem]:
    """Select the corpus subset to probe.

    Default: crew votes WITH a visible impostor (the conversion-relevant set —
    exhibits the F1 inversion + F2 length/latency). ``--crew-all`` adds the crew
    votes WITHOUT an available impostor too, so the grader can measure
    false-ejection (a symmetric variant must lift conversion WITHOUT inflating
    wrong ejections). ``--all-votes`` widens to every recorded vote (incl.
    impostor voters).
    """

    if all_votes:
        chosen = list(items)
    elif crew_all:
        chosen = [i for i in items if i.voter_role == "CREWMATE"]
    else:
        chosen = [
            i for i in items if i.voter_role == "CREWMATE" and i.available_impostor_ids
        ]
    if limit is not None:
        chosen = chosen[:limit]
    return chosen


async def _one_call(
    *,
    item: CorpusItem,
    render: Callable[[VoteContext], str],
    variant: str,
    model: str,
    think: bool,
    num_ctx: int,
    temperature: float,
    num_predict: int,
) -> dict[str, object]:
    prompt = render(item.context)
    record: dict[str, object] = {
        "item_id": item.item_id,
        "seed": item.seed,
        "meeting_id": item.meeting_id,
        "voter_id": item.voter_id,
        "voter_role": item.voter_role,
        "recorded_target": item.recorded_target,
        "is_inversion": item.is_inversion,
        "available_impostor_ids": list(item.available_impostor_ids),
        "max_impostor_suspicion": round(item.max_impostor_suspicion, 4),
        "model": model,
        "think": think,
        "num_ctx": num_ctx,
        "temperature": temperature,
        "variant": variant,
        "prompt_chars": len(prompt),
    }
    started = time.perf_counter()
    try:
        raw = await _default_send(
            host=_ollama_host(),
            model=model,
            prompt=prompt,
            format_schema=VoteBallot.model_json_schema(),
            options={
                "temperature": temperature,
                "seed": SEED,
                "num_predict": num_predict,
                "num_ctx": num_ctx,
            },
            think=think,
        )
    except Exception as exc:  # noqa: BLE001 — record transport failures, don't abort the matrix
        record["latency_s"] = round(time.perf_counter() - started, 3)
        record["error"] = f"{type(exc).__name__}: {exc}"[:300]
        record["parsed_ok"] = False
        return record

    record["latency_s"] = round(time.perf_counter() - started, 3)
    record["in_tokens"] = raw.prompt_eval_count
    record["out_tokens"] = raw.eval_count
    record["thinking_chars"] = len(raw.thinking)
    text = _extract_json_block(raw.text, VoteBallot)
    try:
        parsed = VoteBallot.model_validate_json(text)
    except ValidationError as exc:
        record["parsed_ok"] = False
        record["rationale_chars"] = len(raw.text)
        record["error"] = f"parse: {exc}"[:200]
        return record
    record["parsed_ok"] = True
    record["target"] = parsed.target
    record["confidence"] = parsed.confidence
    record["primary_reason_id"] = parsed.primary_reason_id
    record["rationale_chars"] = len(parsed.rationale_text)
    record["voted_available_impostor"] = parsed.target in item.available_impostor_ids
    return record


async def run_matrix(
    items: list[CorpusItem],
    *,
    models: tuple[str, ...],
    thinks: tuple[bool, ...],
    num_ctxs: tuple[int, ...],
    variants: dict[str, Callable[[VoteContext], str]],
    temperature: float,
    num_predict: int,
    out_path: Path,
) -> int:
    total = len(items) * len(models) * len(thinks) * len(num_ctxs) * len(variants)
    print(
        f"matrix: {len(items)} items x {len(models)} models x {len(thinks)} think "
        f"x {len(num_ctxs)} ctx x {len(variants)} variant = {total} calls"
    )
    done = 0
    out_path.parent.mkdir(exist_ok=True)
    with out_path.open("w", encoding="utf-8") as sink:
        for model in models:
            for think in thinks:
                for num_ctx in num_ctxs:
                    for variant, render in variants.items():
                        for item in items:
                            record = await _one_call(
                                item=item,
                                render=render,
                                variant=variant,
                                model=model,
                                think=think,
                                num_ctx=num_ctx,
                                temperature=temperature,
                                num_predict=num_predict,
                            )
                            sink.write(json.dumps(record) + "\n")
                            sink.flush()
                            done += 1
                            if done % 10 == 0 or done == total:
                                print(f"  {done}/{total}")
    print(f"results -> {out_path}")
    return 0


def _parse_seeds(raw: str | None) -> set[int] | None:
    if not raw:
        return None
    return {int(token) for token in raw.split(",") if token.strip()}


def _parse_bools(raw: str) -> tuple[bool, ...]:
    return tuple(token.strip().lower() == "true" for token in raw.split(","))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample-dir", type=Path, default=DEFAULT_SAMPLE_DIR)
    parser.add_argument("--seeds", type=str, default=None)
    parser.add_argument("--models", type=str, default=",".join(DEFAULT_MODELS))
    parser.add_argument("--think", type=str, default="false,true")
    parser.add_argument("--num-ctx", type=str, default="8192,16384")
    parser.add_argument(
        "--variants",
        type=str,
        default="baseline",
        help="Comma list: baseline + any template in variants/ (see registry).",
    )
    parser.add_argument("--temperature", type=float, default=TEMPERATURE)
    parser.add_argument("--num-predict", type=int, default=NUM_PREDICT)
    parser.add_argument("--all-votes", action="store_true")
    parser.add_argument(
        "--crew-all",
        action="store_true",
        help="Include crew votes with NO available impostor (for false-eject).",
    )
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument(
        "--out", type=str, default="run", help="results/probe-<out>.jsonl"
    )
    args = parser.parse_args()

    models = tuple(m.strip() for m in args.models.split(",") if m.strip())
    preflight(models)

    items = build_corpus(args.sample_dir, seeds=_parse_seeds(args.seeds))
    items = select_corpus(
        items, all_votes=args.all_votes, crew_all=args.crew_all, limit=args.limit
    )
    if not items:
        raise SystemExit("no corpus items selected")

    registry = variant_renderers(
        [v.strip() for v in args.variants.split(",") if v.strip()],
        baseline=render_prompt,
    )

    out_path = RESULTS_DIR / f"probe-{args.out}.jsonl"
    return asyncio.run(
        run_matrix(
            items,
            models=models,
            thinks=_parse_bools(args.think),
            num_ctxs=tuple(int(c) for c in args.num_ctx.split(",")),
            variants=registry,
            temperature=args.temperature,
            num_predict=args.num_predict,
            out_path=out_path,
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())
