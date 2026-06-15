"""Model-ceiling vs information-ceiling adjudication (diagnostic, $0 + frontier).

Runs the IDENTICAL hard impostor reply contexts (production accusation_round
reply prompt, baseline — no cover injection) across a model-strength curve:
  - qwen2.5:7b-instruct  (think=False)   -- scale-down point
  - qwen3.5:9b           (think=False)   -- production
  - qwen3.5:9b           (think=True)    -- reasoning-channel ablation
  - Claude/Opus frontier (via subagents) -- run separately through grade-frontier

Same contexts, same grader (deflection_probe._grade): self_co_locates_body,
new_self_flag (a structured detector contradiction minted on the speaker),
deflects_legal. If self-flagging does NOT fall as model strength rises, the
binding constraint is INFORMATION (the impostor lies into a checker fed by
sightings it never saw), not the model.

Modes:
  dump                         -> write prompts.json + contexts.pkl
  run-ollama --model M --think B --tag T [--num-ctx N --num-predict P]
  grade-frontier --turns F --tag T   (F = {item_id: <MeetingTurn json>})
"""

from __future__ import annotations

import argparse
import asyncio
import json
import pickle
import time
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from agents.strategic.prompts.loader import accusation_round_prompt
from meetings.schemas import MeetingTurn
from llm.ollama_client import _default_send
from llm.provider import _extract_json_block
from experiments.model_probe.probe import _ollama_host, preflight
from experiments.lab.deception_battery import ReplyContext, build_reply_contexts
from experiments.lab.deflection_probe import _body, _grade

WORK = Path("experiments/lab")
CTX_PKL = WORK / "model-ceiling-contexts.pkl"
PROMPTS = WORK / "model-ceiling-prompts.json"
N_HARD = 16
RAW_CAP = 40  # pull this many reply contexts, then keep the body-meeting ones


def _prompt(ctx: ReplyContext) -> str:
    return accusation_round_prompt(
        agent_id=ctx.speaker,
        rendered_memory=ctx.rendered_memory,
        transcript=ctx.transcript,
        contradictions=ctx.contradictions,
        prior_turn=ctx.prior_turn,
        turn_kind="reply",
        fellow_impostor_ids=ctx.fellow_living,
        living_ids=tuple(p for p in ctx.living if p != ctx.speaker),
        dead_ids=tuple(ctx.dead),
    )


def _select(sample_dir: Path) -> list[ReplyContext]:
    ctxs = build_reply_contexts(sample_dir, RAW_CAP)
    body = [c for c in ctxs if _body(c)[0] is not None]
    return body[:N_HARD]


def do_dump(sample_dir: Path) -> None:
    ctxs = _select(sample_dir)
    CTX_PKL.write_bytes(pickle.dumps(ctxs))
    rows = []
    for c in ctxs:
        br, bt = _body(c)
        rows.append(
            {
                "item_id": c.item_id,
                "speaker": c.speaker,
                "body_room": br,
                "body_tick": bt,
                "prompt": _prompt(c),
            }
        )
    PROMPTS.write_text(json.dumps(rows, indent=2))
    print(f"dumped {len(ctxs)} hard body-meeting contexts -> {CTX_PKL} / {PROMPTS}")


async def _call_ollama(
    prompt: str, model: str, think: bool, num_ctx: int, num_predict: int
) -> tuple[MeetingTurn | None, str, float]:
    started = time.perf_counter()
    raw = await _default_send(
        host=_ollama_host(),
        model=model,
        prompt=prompt,
        format_schema=MeetingTurn.model_json_schema(),
        options={
            "temperature": 0.4,
            "seed": 0,
            "num_predict": num_predict,
            "num_ctx": num_ctx,
        },
        think=think,
    )
    lat = time.perf_counter() - started
    try:
        turn = MeetingTurn.model_validate_json(_extract_json_block(raw.text, MeetingTurn))
        return turn, raw.text, lat
    except ValidationError:
        return None, raw.text, lat


def do_run_ollama(
    model: str, think: bool, tag: str, num_ctx: int, num_predict: int
) -> None:
    preflight((model,))
    ctxs: list[ReplyContext] = pickle.loads(CTX_PKL.read_bytes())
    out = WORK / f"results-model-ceiling-{tag}.jsonl"

    async def _run() -> None:
        with out.open("w", encoding="utf-8") as sink:
            for n, ctx in enumerate(ctxs):
                br, bt = _body(ctx)
                turn, raw, lat = await _call_ollama(
                    _prompt(ctx), model, think, num_ctx, num_predict
                )
                rec: dict[str, Any] = {
                    "item": ctx.item_id,
                    "tag": tag,
                    "parsed_ok": turn is not None,
                    "latency_s": round(lat, 1),
                }
                if turn is None:
                    rec["raw_head"] = raw[:200]
                else:
                    rec.update(_grade(turn, ctx, br, bt))
                sink.write(json.dumps(rec) + "\n")
                sink.flush()
                print(f"  {tag} {n + 1}/{len(ctxs)} (parsed={turn is not None})", flush=True)

    asyncio.run(_run())
    print(f"wrote {out}")


def do_grade_frontier(turns_path: Path, tag: str) -> None:
    ctxs: list[ReplyContext] = pickle.loads(CTX_PKL.read_bytes())
    by_id = {c.item_id: c for c in ctxs}
    turns = json.loads(turns_path.read_text())  # {item_id: turn-json (obj or str)}
    out = WORK / f"results-model-ceiling-{tag}.jsonl"
    with out.open("w", encoding="utf-8") as sink:
        for item_id, raw_turn in turns.items():
            ctx = by_id.get(item_id)
            if ctx is None:
                print(f"  SKIP unknown item {item_id}")
                continue
            br, bt = _body(ctx)
            payload = raw_turn if isinstance(raw_turn, str) else json.dumps(raw_turn)
            try:
                turn = MeetingTurn.model_validate_json(_extract_json_block(payload, MeetingTurn))
            except ValidationError as exc:
                sink.write(json.dumps({"item": item_id, "tag": tag, "parsed_ok": False, "err": str(exc)[:160]}) + "\n")
                continue
            rec = {"item": item_id, "tag": tag, "parsed_ok": True, **_grade(turn, ctx, br, bt)}
            sink.write(json.dumps(rec) + "\n")
    print(f"wrote {out}")


def main() -> int:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="mode", required=True)
    d = sub.add_parser("dump")
    d.add_argument("--sample-dir", type=Path, required=True)
    r = sub.add_parser("run-ollama")
    r.add_argument("--model", required=True)
    r.add_argument("--think", choices=["true", "false"], required=True)
    r.add_argument("--tag", required=True)
    r.add_argument("--num-ctx", type=int, default=8192)
    r.add_argument("--num-predict", type=int, default=2048)
    g = sub.add_parser("grade-frontier")
    g.add_argument("--turns", type=Path, required=True)
    g.add_argument("--tag", required=True)
    args = p.parse_args()
    if args.mode == "dump":
        do_dump(args.sample_dir)
    elif args.mode == "run-ollama":
        do_run_ollama(
            args.model, args.think == "true", args.tag, args.num_ctx, args.num_predict
        )
    else:
        do_grade_frontier(args.turns, args.tag)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
