"""Conversation-quality probe — opening-accusation behavior on both models.

The model decision (7B vs 9B) now turns on conversation quality, not vote
conversion (v1_verdict fixes votes on both). The opening accusation is the
highest-leverage conversational turn: it drives the whole chain, and the audit
found chains dying on "unsure" openings. This probe reconstructs each reporter's
opening context from committed replays, renders the role-dispatched report
prompt, runs BOTH models (constrained on ``MeetingTurn``), and grades
deterministically:

- **decisiveness** — did the opening produce an ``AccusationClaim`` (vs staying
  unsure / naming no one)? An unsure opening terminates the chain immediately.
- **accuracy** — of the accusations, did it name a TRUE impostor?
- **richness** — free_text length, observation count, claim count (proxies for
  how much concrete content the turn carries).

Plus it dumps side-by-side 7B-vs-9B openings on the SAME context, because the
ultimate read on "richer conversations" is reading them. Crewmate reporters only
(decisive+accurate accusation is the clean deduction signal; impostor-opening
deception is a separate, frozen-build question).

Usage::

    python -m experiments.model_probe.conversation --seeds 0,1,2,3,4 [--examples 6]
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

from agents.strategic.prompts.loader import crewmate_report_prompt
from api.replay_loader import ReplayLoader
from engine.world import load_canonical_map
from experiments.model_probe.corpus import (
    DEFAULT_SAMPLE_DIR,
    _roles_for_seed,
    _roster,
)
from experiments.model_probe.probe import _ollama_host, preflight
from llm.ollama_client import _default_send
from llm.provider import _extract_json_block
from meetings.schemas import MeetingTurn
from orchestrator.replay import MeetingReplayEntry, read_all_entries

MODELS = ("qwen2.5:7b-instruct", "qwen3.5:9b")
SEED = 0
TEMPERATURE = 0.0
NUM_CTX = 8192
NUM_PREDICT = 1024  # openings are short turns; 4096 caused the slow 9B run
RESULTS_DIR = Path(__file__).resolve().parent / "results"
_VARIANT_DIR = Path(__file__).resolve().parent / "variants" / "templates"
_VENV = Environment(
    loader=FileSystemLoader(_VARIANT_DIR),
    autoescape=False,
    undefined=StrictUndefined,
    trim_blocks=True,
    lstrip_blocks=True,
)


@dataclass(frozen=True)
class OpeningItem:
    seed: int
    game_id: str
    meeting_id: str
    reporter: str
    current_tick: int
    meeting_trigger: str
    rendered_memory: str
    impostor_ids: tuple[str, ...]  # living impostors (ground truth)
    recorded_accused: str | None  # who the recorded opening accused (baseline)

    @property
    def item_id(self) -> str:
        return f"{self.seed}:{self.meeting_id}:{self.reporter}"


def _accusation(turn: MeetingTurn) -> tuple[str | None, float | None]:
    for claim in turn.claims:
        if claim.type == "accusation":
            return claim.against, claim.confidence
    return None, None


def build_opening_corpus(
    sample_dir: Path = DEFAULT_SAMPLE_DIR, *, seeds: set[int] | None = None
) -> list[OpeningItem]:
    game_map = load_canonical_map()
    roster = _roster(sample_dir)
    loader = ReplayLoader(sample_dir, game_map=game_map)
    paths = sorted(
        sample_dir.glob("replay-seed-*.jsonl"),
        key=lambda p: int(p.stem.rsplit("-", 1)[1]),
    )
    items: list[OpeningItem] = []
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
            if not turns:
                continue
            opening = turns[0]
            reporter = opening.speaker
            if roles.get(reporter) != "CREWMATE":  # crewmate reporters only
                continue
            living = {b.voter for b in meeting.ballots} or {t.speaker for t in turns}
            try:
                view = loader.get_meeting_memory(game_id, meeting.meeting_id, reporter)
            except KeyError:
                continue
            rec_accused = next(
                (c.against for c in opening.claims if c.type == "accusation"), None
            )
            items.append(
                OpeningItem(
                    seed=seed,
                    game_id=game_id,
                    meeting_id=meeting.meeting_id,
                    reporter=reporter,
                    current_tick=meeting.tick,
                    meeting_trigger=f"{reporter} reported a body at tick {meeting.tick}",
                    rendered_memory=view.rendered_memory_text,
                    impostor_ids=tuple(sorted(impostors & living)),
                    recorded_accused=rec_accused,
                )
            )
    return items


def _render(item: OpeningItem, variant: str) -> str:
    if variant == "baseline":
        return crewmate_report_prompt(
            agent_id=item.reporter,
            current_tick=item.current_tick,
            meeting_trigger=item.meeting_trigger,
            rendered_memory=item.rendered_memory,
            public_transcript="",
        )
    return _VENV.get_template(f"{variant}.j2").render(
        agent_id=item.reporter,
        current_tick=item.current_tick,
        meeting_trigger=item.meeting_trigger,
        rendered_memory=item.rendered_memory,
        public_transcript="",
    )


async def _run_one(item: OpeningItem, model: str, variant: str) -> dict[str, object]:
    prompt = _render(item, variant)
    rec: dict[str, object] = {
        "item_id": item.item_id,
        "model": model,
        "variant": variant,
        "impostor_ids": list(item.impostor_ids),
        "recorded_accused": item.recorded_accused,
    }
    started = time.perf_counter()
    try:
        raw = await _default_send(
            host=_ollama_host(),
            model=model,
            prompt=prompt,
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
    accused, conf = _accusation(turn)
    rec["parsed_ok"] = True
    rec["accused"] = accused
    rec["confidence"] = conf
    rec["accused_is_impostor"] = accused in item.impostor_ids if accused else False
    rec["n_observations"] = len(turn.observations)
    rec["n_claims"] = len(turn.claims)
    rec["free_text_chars"] = len(turn.free_text)
    rec["free_text"] = turn.free_text
    return rec


async def run(
    items: list[OpeningItem], variants: list[str], out_path: Path
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


def _mean(rows: list[dict[str, object]], key: str) -> float:
    vals = [
        float(v)
        for r in rows
        if isinstance((v := r.get(key)), (int, float)) and not isinstance(v, bool)
    ]
    return sum(vals) / len(vals) if vals else 0.0


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
        accusing = [r for r in rows if r.get("accused")]
        accurate = [r for r in accusing if r.get("accused_is_impostor")]
        summary[f"{model} / {variant}"] = {
            "n": n,
            "accusation_rate": round(len(accusing) / n, 3) if n else 0.0,
            "accusation_accuracy": (
                round(len(accurate) / len(accusing), 3) if accusing else None
            ),
            "decisive_and_correct": round(len(accurate) / n, 3) if n else 0.0,
            # the v2-lesson guardrail: decisiveness must not become reckless.
            "false_accusation_rate": (
                round((len(accusing) - len(accurate)) / n, 3) if n else 0.0
            ),
            "mean_free_text_chars": round(_mean(rows, "free_text_chars")),
        }
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample-dir", type=Path, default=DEFAULT_SAMPLE_DIR)
    parser.add_argument("--seeds", type=str, default=None)
    parser.add_argument("--variants", type=str, default="baseline,report_decisive")
    parser.add_argument("--examples", type=int, default=8)
    parser.add_argument("--out", type=str, default="conv")
    args = parser.parse_args()

    seeds = {int(s) for s in args.seeds.split(",") if s.strip()} if args.seeds else None
    variants = [v.strip() for v in args.variants.split(",") if v.strip()]
    items = build_opening_corpus(args.sample_dir, seeds=seeds)
    print(
        f"crewmate openings: {len(items)} × {len(MODELS)} models × {len(variants)} variants",
        flush=True,
    )
    out_path = RESULTS_DIR / f"conversation-{args.out}.jsonl"
    records = asyncio.run(run(items, variants, out_path))

    print("\n=== opening-accusation quality (crewmate, by model × variant) ===")
    for cell, s in grade(records).items():
        print(
            f"  {cell:36} accuse={s['accusation_rate']:.0%}  "
            f"accuracy={s['accusation_accuracy']}  "
            f"decisive+correct={s['decisive_and_correct']:.0%}  "
            f"false_acc={s['false_accusation_rate']:.0%}  "
            f"ftext~{s['mean_free_text_chars']}ch"
        )

    # Examples: per item, every model × variant cell (see if 'decisive' flips a
    # baseline hedge into a grounded accusation).
    by_item: dict[str, dict[str, dict[str, object]]] = {}
    for r in records:
        key = f"{r['model']}/{r.get('variant', 'baseline')}"
        by_item.setdefault(str(r["item_id"]), {})[key] = r
    lines: list[str] = ["# Opening accusations — baseline vs decisive, both models\n"]
    for shown, (item_id, per) in enumerate(by_item.items()):
        if shown >= args.examples:
            break
        any_rec = next(iter(per.values()))
        lines.append(f"\n## {item_id}  (impostors: {any_rec.get('impostor_ids')})")
        for model in MODELS:
            for variant in variants:
                r = per.get(f"{model}/{variant}", {})
                lines.append(
                    f"\n**{model} / {variant}** — accused `{r.get('accused')}` "
                    f"(impostor={r.get('accused_is_impostor')}, conf={r.get('confidence')}):\n"
                    f"> {str(r.get('free_text', ''))[:500]}"
                )
    (RESULTS_DIR / f"conversation-examples-{args.out}.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )
    print(f"\nexamples -> {RESULTS_DIR / f'conversation-examples-{args.out}.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
