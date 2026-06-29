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
import os
import pickle
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from agents.strategic.prompts.loader import accusation_round_prompt
from meetings.schemas import MeetingTurn
from llm.featherless_client import (
    DEFAULT_RESPONSE_FORMAT_MODE,
    ResponseFormatMode,
)
from llm.provider import _extract_json_block
from experiments.lab.probe_backends import (
    DEFAULT_PROBE_THINKING_POLICY,
    active_substrate_flags,
    call_turn,
)
from experiments.model_probe.probe import _ollama_host, preflight
from experiments.lab.deception_battery import ReplyContext, build_reply_contexts
from experiments.lab.deflection_probe import _body, _grade

WORK = Path("experiments/lab")
CTX_PKL = WORK / "model-ceiling-contexts.pkl"
# Sidecar recording the substrate-flag config ACTIVE WHEN THE CONTEXTS WERE
# DUMPED (Task 14.3). ``dump`` reconstructs rendered memory through the 13.5
# ``*_enabled()`` reads, so the flag config is baked into ``CTX_PKL``; run /
# grade are separate invocations whose live env may differ. Stamping rows from
# this sidecar (not the run-time env) keeps the flag-OFF/flag-ON comparison
# honest even if an operator dumps flag-ON and later runs with the flags unset.
CTX_FLAGS = WORK / "model-ceiling-contexts-flags.json"
PROMPTS = WORK / "model-ceiling-prompts.json"
N_HARD = 16
RAW_CAP = 40  # pull this many reply contexts, then keep the body-meeting ones


def _dumped_substrate_flags() -> dict[str, bool]:
    """Substrate flags baked into ``CTX_PKL`` at dump time (Task 14.3).

    Reads the :data:`CTX_FLAGS` sidecar written by :func:`do_dump`. Falls back to
    a live :func:`active_substrate_flags` snapshot — with a loud warning — only
    when the sidecar is absent (a pickle dumped before flag-stamping landed), so
    a stale dump is flagged rather than silently mis-tagged.
    """

    if CTX_FLAGS.exists():
        loaded: dict[str, bool] = json.loads(CTX_FLAGS.read_text())
        return loaded
    flags = active_substrate_flags()
    print(
        f"WARNING: {CTX_FLAGS} missing (dump predates flag-stamping); tagging "
        f"rows with the RUN-TIME substrate flags {flags} — re-run `dump` to "
        "stamp the dump-time config.",
        flush=True,
    )
    return flags


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
    # Stamp the dump-time substrate-flag config alongside the pickle so run /
    # grade tag rows with the config that actually produced the rendered memory.
    flags = active_substrate_flags()
    CTX_FLAGS.write_text(json.dumps(flags, indent=2))
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
    print(
        f"dumped {len(ctxs)} hard body-meeting contexts (substrate {flags}) -> "
        f"{CTX_PKL} / {PROMPTS} / {CTX_FLAGS}"
    )


async def _call_ollama(
    prompt: str, model: str, think: bool, num_ctx: int, num_predict: int
) -> tuple[MeetingTurn | None, str, float]:
    # Generalized to the provider-neutral seam (Task 14.3); the ollama wire call
    # stays byte-identical (same temperature/seed/options/think) so the committed
    # ``results-model-ceiling-*.jsonl`` reproduce.
    result = await call_turn(
        prompt,
        MeetingTurn,
        backend="ollama",
        model=model,
        temperature=0.4,
        max_tokens=num_predict,
        ollama_host=_ollama_host(),
        seed=0,
        num_ctx=num_ctx,
        think=think,
    )
    return result.parsed, result.raw_text, result.latency_s


def do_run_ollama(
    model: str, think: bool, tag: str, num_ctx: int, num_predict: int
) -> None:
    preflight((model,))
    ctxs: list[ReplyContext] = pickle.loads(CTX_PKL.read_bytes())
    flags = _dumped_substrate_flags()
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
                    "substrate_flags": flags,
                }
                if turn is None:
                    rec["raw_head"] = raw[:200]
                else:
                    rec.update(_grade(turn, ctx, br, bt))
                sink.write(json.dumps(rec) + "\n")
                sink.flush()
                print(
                    f"  {tag} {n + 1}/{len(ctxs)} (parsed={turn is not None})",
                    flush=True,
                )

    asyncio.run(_run())
    print(f"wrote {out}")


def do_run_featherless(
    model: str,
    tag: str,
    *,
    num_predict: int,
    request_thinking: bool,
    base_url: str | None,
    response_format_mode: ResponseFormatMode,
) -> None:
    """Run the dumped hard contexts through the Featherless backend (Task 14.3).

    Shares the frozen ``contexts.pkl`` (``dump``) and the mechanical
    ``deflection_probe._grade``, so the only moving variable vs ``run-ollama`` is
    the provider. Reasoning is discarded explicitly (``thinking_policy='strip'``)
    so a reasoning model does not abort the sweep; the request-time thinking
    toggle drives the non-thinking/thinking axis. Graded results can also be
    produced from external turns via ``grade-frontier``.
    """

    api_key = os.environ.get("FEATHERLESS_API_KEY")
    if not api_key:
        raise SystemExit("run-featherless requires FEATHERLESS_API_KEY in the env.")
    ctxs: list[ReplyContext] = pickle.loads(CTX_PKL.read_bytes())
    flags = _dumped_substrate_flags()
    out = WORK / f"results-model-ceiling-{tag}.jsonl"

    async def _run() -> None:
        with out.open("w", encoding="utf-8") as sink:
            for n, ctx in enumerate(ctxs):
                br, bt = _body(ctx)
                result = await call_turn(
                    _prompt(ctx),
                    MeetingTurn,
                    backend="featherless",
                    model=model,
                    temperature=0.4,
                    max_tokens=num_predict,
                    api_key=api_key,
                    base_url=base_url,
                    request_thinking=request_thinking,
                    thinking_policy=DEFAULT_PROBE_THINKING_POLICY,
                    response_format_mode=response_format_mode,
                    # Tag with the DUMP-TIME substrate config (baked into the
                    # pickle), not call_turn's run-time snapshot.
                    substrate_flags=flags,
                )
                turn = result.parsed
                rec: dict[str, Any] = {
                    "item": ctx.item_id,
                    "tag": tag,
                    "parsed_ok": turn is not None,
                    "latency_s": round(result.latency_s, 1),
                    "in_tokens": result.in_tokens,
                    "out_tokens": result.out_tokens,
                    "substrate_flags": result.substrate_flags,
                }
                if turn is None:
                    rec["raw_head"] = result.raw_text[:200]
                else:
                    rec.update(_grade(turn, ctx, br, bt))
                sink.write(json.dumps(rec) + "\n")
                sink.flush()
                print(
                    f"  {tag} {n + 1}/{len(ctxs)} (parsed={turn is not None})",
                    flush=True,
                )

    asyncio.run(_run())
    print(f"wrote {out}")


def do_grade_frontier(turns_path: Path, tag: str) -> None:
    ctxs: list[ReplyContext] = pickle.loads(CTX_PKL.read_bytes())
    by_id = {c.item_id: c for c in ctxs}
    turns = json.loads(turns_path.read_text())  # {item_id: turn-json (obj or str)}
    flags = _dumped_substrate_flags()
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
                turn = MeetingTurn.model_validate_json(
                    _extract_json_block(payload, MeetingTurn)
                )
            except ValidationError as exc:
                sink.write(
                    json.dumps(
                        {
                            "item": item_id,
                            "tag": tag,
                            "parsed_ok": False,
                            "err": str(exc)[:160],
                            "substrate_flags": flags,
                        }
                    )
                    + "\n"
                )
                continue
            rec = {
                "item": item_id,
                "tag": tag,
                "parsed_ok": True,
                "substrate_flags": flags,
                **_grade(turn, ctx, br, bt),
            }
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
    f = sub.add_parser("run-featherless")
    f.add_argument("--model", required=True)
    f.add_argument("--tag", required=True)
    f.add_argument("--num-predict", type=int, default=2048)
    f.add_argument(
        "--request-thinking",
        action="store_true",
        help="Request-time thinking toggle (the non-thinking/thinking sweep axis).",
    )
    f.add_argument(
        "--base-url",
        type=str,
        default=None,
        help="Featherless base URL; default resolves AILIBI_FEATHERLESS_BASE_URL, "
        "else the hosted endpoint.",
    )
    f.add_argument(
        "--response-format-mode",
        choices=["json_object", "json_schema", "none"],
        default=DEFAULT_RESPONSE_FORMAT_MODE,
    )
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
    elif args.mode == "run-featherless":
        do_run_featherless(
            args.model,
            args.tag,
            num_predict=args.num_predict,
            request_thinking=args.request_thinking,
            base_url=args.base_url,
            response_format_mode=args.response_format_mode,
        )
    else:
        do_grade_frontier(args.turns, args.tag)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
