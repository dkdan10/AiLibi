"""Opt-in / corroboration probe — does the crew pile onto a correct accusation?

The opt-in is the terminal info-share before the vote: a non-speaking crewmate
with relevant evidence can second an accusation, building the shared belief (and
the vote consensus) needed to clear the SKIP-plurality bar. The recorded crew
opt-ins are sparse (10) but already corroborate 6/10 — so rather than the tiny
recorded set, this SYNTHESIZES the real question: for every meeting where a true
impostor was accused, each non-speaking living crewmate gets an opt-in context
(the full chain transcript + their memory). It measures whether they CONTRIBUTE
to the case (corroborate / add an implicating accusation) and whether that
contribution is aimed at the real impostor — baseline vs a corroboration-pushing
reframe, on both models.

Usage::

    python -m experiments.model_probe.optin --seeds 0,1,2,3,4 [--variants baseline,optin_decisive]
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
class OptinItem:
    seed: int
    game_id: str
    meeting_id: str
    speaker: str
    transcript: MeetingTranscript
    contradictions: tuple[ContradictionRef, ...]
    rendered_memory: str
    impostor_ids: tuple[str, ...]
    accusers_of_impostor: tuple[str, ...]  # players who accused a true impostor

    @property
    def item_id(self) -> str:
        return f"{self.seed}:{self.meeting_id}:{self.speaker}"


def build_optin_corpus(
    sample_dir: Path = DEFAULT_SAMPLE_DIR, *, seeds: set[int] | None = None
) -> list[OptinItem]:
    game_map = load_canonical_map()
    roster = _roster(sample_dir)
    loader = ReplayLoader(sample_dir, game_map=game_map)
    paths = sorted(
        sample_dir.glob("replay-seed-*.jsonl"),
        key=lambda p: int(p.stem.rsplit("-", 1)[1]),
    )
    items: list[OptinItem] = []
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
            accusers = tuple(
                sorted(
                    {
                        t.speaker
                        for t in turns
                        for c in t.claims
                        if c.type == "accusation" and c.against in impostors
                    }
                )
            )
            if not accusers:  # only meetings where a true impostor is on the table
                continue
            speakers = {t.speaker for t in turns}
            living = {b.voter for b in meeting.ballots} or speakers
            for crew in sorted(living):
                if roles.get(crew) != "CREWMATE" or crew in speakers:
                    continue  # non-speaking living crewmate
                try:
                    view = loader.get_meeting_memory(game_id, meeting.meeting_id, crew)
                except KeyError:
                    continue
                items.append(
                    OptinItem(
                        seed=seed,
                        game_id=game_id,
                        meeting_id=meeting.meeting_id,
                        speaker=crew,
                        transcript=meeting.transcript,
                        contradictions=meeting.contradictions,
                        rendered_memory=view.rendered_memory_text,
                        impostor_ids=tuple(sorted(impostors & living)),
                        accusers_of_impostor=accusers,
                    )
                )
    return items


def _render(item: OptinItem, variant: str) -> str:
    if variant == "baseline":
        return accusation_round_prompt(
            agent_id=item.speaker,
            rendered_memory=item.rendered_memory,
            transcript=item.transcript,
            contradictions=item.contradictions,
            prior_turn=None,
            turn_kind="opt_in",
        )
    return _VENV.get_template(f"{variant}.j2").render(
        agent_id=item.speaker,
        rendered_memory=item.rendered_memory,
        transcript=item.transcript,
        contradictions=item.contradictions,
        prior_turn=None,
        turn_kind="opt_in",
        fellow_impostor_ids=(),
    )


def _classify(turn: MeetingTurn, item: OptinItem) -> dict[str, object]:
    accuses_impostor = any(
        c.type == "accusation" and c.against in item.impostor_ids for c in turn.claims
    )
    corroborates = any(c.type == "corroboration" for c in turn.claims)
    # corroboration that backs a player who accused a true impostor = toward-impostor
    corrob_impostor_case = any(
        c.type == "corroboration" and c.supports in item.accusers_of_impostor
        for c in turn.claims
    )
    return {
        "accuses_impostor": accuses_impostor,
        "corroborates": corroborates,
        "toward_impostor": accuses_impostor or corrob_impostor_case,
        "contribution": accuses_impostor or corroborates,
    }


async def _run_one(item: OptinItem, model: str, variant: str) -> dict[str, object]:
    rec: dict[str, object] = {
        "item_id": item.item_id,
        "model": model,
        "variant": variant,
        "impostor_ids": list(item.impostor_ids),
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
    rec["parsed_ok"] = True
    rec.update(_classify(turn, item))
    rec["free_text"] = turn.free_text
    return rec


async def run(
    items: list[OptinItem], variants: list[str], out_path: Path
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

        def rate(key: str, rows: list[dict[str, object]] = rows, n: int = n) -> float:
            return round(sum(1 for r in rows if r.get(key)) / n, 3) if n else 0.0

        summary[f"{model} / {variant}"] = {
            "n": n,
            "contribution": rate("contribution"),
            "corroborates": rate("corroborates"),
            "accuses_impostor": rate("accuses_impostor"),
            "toward_impostor": rate("toward_impostor"),
        }
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample-dir", type=Path, default=DEFAULT_SAMPLE_DIR)
    parser.add_argument("--seeds", type=str, default=None)
    parser.add_argument("--variants", type=str, default="baseline,optin_decisive")
    parser.add_argument("--examples", type=int, default=8)
    parser.add_argument("--out", type=str, default="optin")
    args = parser.parse_args()

    seeds = {int(s) for s in args.seeds.split(",") if s.strip()} if args.seeds else None
    variants = [v.strip() for v in args.variants.split(",") if v.strip()]
    items = build_optin_corpus(args.sample_dir, seeds=seeds)
    print(
        f"synthesized opt-in candidates (non-speaking crew, impostor on table): "
        f"{len(items)} × {len(MODELS)} models × {len(variants)} variants",
        flush=True,
    )
    if not items:
        raise SystemExit("no opt-in candidates")
    out_path = RESULTS_DIR / f"optin-{args.out}.jsonl"
    records = asyncio.run(run(items, variants, out_path))

    print("\n=== opt-in consensus contribution (crewmate, by model × variant) ===")
    for cell, s in grade(records).items():
        print(
            f"  {cell:36} n={s['n']:3}  contribution={s['contribution']:.0%}  "
            f"corroborates={s['corroborates']:.0%}  "
            f"accuses_impostor={s['accuses_impostor']:.0%}  "
            f"toward_impostor={s['toward_impostor']:.0%}"
        )

    by_item: dict[str, dict[str, dict[str, object]]] = {}
    for r in records:
        by_item.setdefault(str(r["item_id"]), {})[
            f"{r['model']}/{r.get('variant', 'baseline')}"
        ] = r
    lines = ["# Opt-in turns — baseline vs decisive, both models\n"]
    for shown, (item_id, per) in enumerate(by_item.items()):
        if shown >= args.examples:
            break
        any_rec = next(iter(per.values()))
        lines.append(f"\n## {item_id}  (impostors: {any_rec.get('impostor_ids')})")
        for model in MODELS:
            for variant in variants:
                r = per.get(f"{model}/{variant}", {})
                lines.append(
                    f"\n**{model} / {variant}** — toward_impostor={r.get('toward_impostor')} "
                    f"(corrob={r.get('corroborates')}, accuse_imp={r.get('accuses_impostor')}):\n"
                    f"> {str(r.get('free_text', ''))[:380]}"
                )
    (RESULTS_DIR / f"optin-examples-{args.out}.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )
    print(f"\nexamples -> {RESULTS_DIR / f'optin-examples-{args.out}.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
