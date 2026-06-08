"""Reply-turn probe — does the reactive chain engage, or die at one hop?

The accusation-chain protocol's whole point is the reactive middle: an accused
player answers and (if their evidence warrants) redirects, passing the floor on.
The audit found this degenerate — chains are one-hop, 0/45 replies counter-accuse
— and the reply prompt (accusation_round.v4) is the suspect: it frames the turn
as defensive-first ("OPTIONALLY counter-accuse… or stay purely defensive to LET
THE CHAIN END", "prefer a defensive turn over a guessed accusation").

This probe reconstructs each recorded CREWMATE reply context from the committed
replays (the speaker, the accusation against them, the transcript-so-far, their
memory), renders the production prompt vs a decisive-but-grounded reframe, runs
both models, and grades whether the reply COUNTER-ACCUSES (drives the chain) and
whether that redirect targets a true impostor (vs an innocent — the v2 guardrail).

Usage::

    python -m experiments.model_probe.reply --seeds 0,1,2,3,4 [--variants baseline,reply_decisive]
"""

from __future__ import annotations

import argparse
import asyncio
import json
import time
from dataclasses import dataclass
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from pydantic import ValidationError

from agents.strategic.prompts.loader import accusation_round_prompt
from api.replay_loader import ReplayLoader
from engine.world import load_canonical_map
from experiments.model_probe.corpus import DEFAULT_SAMPLE_DIR, _roles_for_seed, _roster
from experiments.model_probe.probe import _ollama_host, preflight
from llm.ollama_client import _default_send
from llm.provider import _extract_json_block
from meetings.schemas import ContradictionRef, MeetingTranscript, MeetingTurn
from orchestrator.replay import MeetingReplayEntry, read_all_entries

MODELS = ("qwen2.5:7b-instruct", "qwen3.5:9b")
SEED = 0
TEMPERATURE = 0.0
NUM_CTX = 8192
NUM_PREDICT = 1024
RESULTS_DIR = Path(__file__).resolve().parent / "results"
_VENV = Environment(
    loader=FileSystemLoader(Path(__file__).resolve().parent / "variants" / "templates"),
    autoescape=False,
    undefined=StrictUndefined,
    trim_blocks=True,
    lstrip_blocks=True,
)


@dataclass(frozen=True)
class ReplyItem:
    seed: int
    game_id: str
    meeting_id: str
    speaker: str
    accuser: str | None
    transcript: MeetingTranscript
    prior_turn: MeetingTurn | None
    contradictions: tuple[ContradictionRef, ...]
    rendered_memory: str
    impostor_ids: tuple[str, ...]
    recorded_counter_accused: str | None

    @property
    def item_id(self) -> str:
        return f"{self.seed}:{self.meeting_id}:{self.speaker}"


def _counter_accusation(
    turn: MeetingTurn, speaker: str
) -> tuple[str | None, float | None]:
    for claim in turn.claims:
        if claim.type == "accusation" and claim.against != speaker:
            return claim.against, claim.confidence
    return None, None


def build_reply_corpus(
    sample_dir: Path = DEFAULT_SAMPLE_DIR, *, seeds: set[int] | None = None
) -> list[ReplyItem]:
    game_map = load_canonical_map()
    roster = _roster(sample_dir)
    loader = ReplayLoader(sample_dir, game_map=game_map)
    paths = sorted(
        sample_dir.glob("replay-seed-*.jsonl"),
        key=lambda p: int(p.stem.rsplit("-", 1)[1]),
    )
    items: list[ReplyItem] = []
    for path in paths:
        seed = int(path.stem.rsplit("-", 1)[1])
        if seeds is not None and seed not in seeds:
            continue
        game_id = f"headless-seed-{seed}"
        roles = _roles_for_seed(seed, game_map, roster)
        impostors = {pid for pid, r in roles.items() if r == "IMPOSTOR"}
        for meeting in (
            e for e in read_all_entries(path) if isinstance(e, MeetingReplayEntry)
        ):
            turns = meeting.transcript.turns
            by_id = {t.turn_id: t for t in turns}
            living = {b.voter for b in meeting.ballots} or {t.speaker for t in turns}
            for i, turn in enumerate(turns):
                if turn.turn_kind != "reply" or roles.get(turn.speaker) != "CREWMATE":
                    continue
                prior = by_id.get(turn.reply_to) if turn.reply_to else None
                try:
                    view = loader.get_meeting_memory(
                        game_id, meeting.meeting_id, turn.speaker
                    )
                except KeyError:
                    continue
                rec_ca, _ = _counter_accusation(turn, turn.speaker)
                items.append(
                    ReplyItem(
                        seed=seed,
                        game_id=game_id,
                        meeting_id=meeting.meeting_id,
                        speaker=turn.speaker,
                        accuser=prior.speaker if prior else None,
                        transcript=MeetingTranscript(turns=tuple(turns[:i])),
                        prior_turn=prior,
                        contradictions=meeting.contradictions,
                        rendered_memory=view.rendered_memory_text,
                        impostor_ids=tuple(sorted(impostors & living)),
                        recorded_counter_accused=rec_ca,
                    )
                )
    return items


def _render(item: ReplyItem, variant: str) -> str:
    if variant == "baseline":
        return accusation_round_prompt(
            agent_id=item.speaker,
            rendered_memory=item.rendered_memory,
            transcript=item.transcript,
            contradictions=item.contradictions,
            prior_turn=item.prior_turn,
            turn_kind="reply",
        )
    return _VENV.get_template(f"{variant}.j2").render(
        agent_id=item.speaker,
        rendered_memory=item.rendered_memory,
        transcript=item.transcript,
        contradictions=item.contradictions,
        prior_turn=item.prior_turn,
        turn_kind="reply",
        fellow_impostor_ids=(),
    )


async def _run_one(item: ReplyItem, model: str, variant: str) -> dict[str, object]:
    rec: dict[str, object] = {
        "item_id": item.item_id,
        "model": model,
        "variant": variant,
        "impostor_ids": list(item.impostor_ids),
        "recorded_counter_accused": item.recorded_counter_accused,
    }
    started = time.perf_counter()
    try:
        raw = await _default_send(
            host=_ollama_host(),
            model=model,
            prompt=_render(item, variant),
            format_schema=MeetingTurn.model_json_schema(),
            options={
                "temperature": TEMPERATURE,
                "seed": SEED,
                "num_predict": NUM_PREDICT,
                "num_ctx": NUM_CTX,
            },
            think=False,
        )
    except Exception as exc:  # noqa: BLE001
        rec["parsed_ok"] = False
        rec["error"] = f"{type(exc).__name__}: {exc}"[:200]
        return rec
    rec["latency_s"] = round(time.perf_counter() - started, 2)
    try:
        turn = MeetingTurn.model_validate_json(
            _extract_json_block(raw.text, MeetingTurn)
        )
    except ValidationError as exc:
        rec["parsed_ok"] = False
        rec["error"] = f"parse: {exc}"[:160]
        return rec
    accused, conf = _counter_accusation(turn, item.speaker)
    rec["parsed_ok"] = True
    rec["counter_accused"] = accused
    rec["confidence"] = conf
    rec["counter_is_impostor"] = accused in item.impostor_ids if accused else False
    rec["free_text"] = turn.free_text
    return rec


async def run(
    items: list[ReplyItem], variants: list[str], out_path: Path
) -> list[dict[str, object]]:
    preflight(MODELS)
    out: list[dict[str, object]] = []
    total = len(items) * len(MODELS) * len(variants)
    done = 0
    out_path.parent.mkdir(exist_ok=True)
    with out_path.open("w", encoding="utf-8") as sink:
        for model in MODELS:
            for variant in variants:
                for item in items:
                    rec = await _run_one(item, model, variant)
                    sink.write(json.dumps(rec) + "\n")
                    sink.flush()
                    out.append(rec)
                    done += 1
                    if done % 10 == 0 or done == total:
                        print(f"  {done}/{total}", flush=True)
    return out


def grade(records: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    summary: dict[str, dict[str, object]] = {}
    cells = sorted(
        {(str(r["model"]), str(r.get("variant", "baseline"))) for r in records}
    )
    for model, variant in cells:
        rows = [
            r
            for r in records
            if r["model"] == model
            and r.get("variant", "baseline") == variant
            and r.get("parsed_ok")
        ]
        n = len(rows)
        ca = [r for r in rows if r.get("counter_accused")]
        ca_correct = [r for r in ca if r.get("counter_is_impostor")]
        summary[f"{model} / {variant}"] = {
            "n": n,
            "counter_accuse_rate": round(len(ca) / n, 3) if n else 0.0,
            "counter_accuracy": (round(len(ca_correct) / len(ca), 3) if ca else None),
            "redirect_to_impostor": round(len(ca_correct) / n, 3) if n else 0.0,
            "false_counter_accuse": (
                round((len(ca) - len(ca_correct)) / n, 3) if n else 0.0
            ),
        }
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample-dir", type=Path, default=DEFAULT_SAMPLE_DIR)
    parser.add_argument("--seeds", type=str, default=None)
    parser.add_argument("--variants", type=str, default="baseline,reply_decisive")
    parser.add_argument("--examples", type=int, default=8)
    parser.add_argument("--out", type=str, default="reply")
    args = parser.parse_args()

    seeds = {int(s) for s in args.seeds.split(",") if s.strip()} if args.seeds else None
    variants = [v.strip() for v in args.variants.split(",") if v.strip()]
    items = build_reply_corpus(args.sample_dir, seeds=seeds)
    print(
        f"crewmate reply turns: {len(items)} × {len(MODELS)} models × {len(variants)} variants",
        flush=True,
    )
    if not items:
        raise SystemExit(
            "no reply items (try more seeds — replies need 2+ turn chains)"
        )
    out_path = RESULTS_DIR / f"reply-{args.out}.jsonl"
    records = asyncio.run(run(items, variants, out_path))

    print("\n=== reply-turn engagement (crewmate, by model × variant) ===")
    for cell, s in grade(records).items():
        print(
            f"  {cell:36} n={s['n']}  counter_accuse={s['counter_accuse_rate']:.0%}  "
            f"accuracy={s['counter_accuracy']}  "
            f"redirect→impostor={s['redirect_to_impostor']:.0%}  "
            f"false_counter={s['false_counter_accuse']:.0%}"
        )

    by_item: dict[str, dict[str, dict[str, object]]] = {}
    for r in records:
        by_item.setdefault(str(r["item_id"]), {})[
            f"{r['model']}/{r.get('variant', 'baseline')}"
        ] = r
    lines = ["# Reply turns — baseline vs decisive, both models\n"]
    for shown, (item_id, per) in enumerate(by_item.items()):
        if shown >= args.examples:
            break
        any_rec = next(iter(per.values()))
        lines.append(f"\n## {item_id}  (impostors: {any_rec.get('impostor_ids')})")
        for model in MODELS:
            for variant in variants:
                r = per.get(f"{model}/{variant}", {})
                lines.append(
                    f"\n**{model} / {variant}** — counter-accused "
                    f"`{r.get('counter_accused')}` (impostor={r.get('counter_is_impostor')}):\n"
                    f"> {str(r.get('free_text', ''))[:400]}"
                )
    (RESULTS_DIR / f"reply-examples-{args.out}.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )
    print(f"\nexamples -> {RESULTS_DIR / f'reply-examples-{args.out}.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
