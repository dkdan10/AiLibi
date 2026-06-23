"""Live-detector threshold sweep over the committed 9p2i set (50 games / 114 meetings):
how do we light R7 (STRONG-flag meeting share off 0/114), and at what precision (impostor TP
vs crew FP)? Unlike forward_redesign_probes.py (a hand-rolled approximation), this runs the
MERGED detector (`meetings.transcript.detect_contradictions`) on `model_validate`'d committed
transcripts, so the numbers are the real code's. See report-forward-redesign-probes.md (Probe 3).

Verdict: there is NO precision-safe config knob. The detector emits 112 flags, ALL WEAK (111
alibi_vs_sighting + 1 alibi_conflict; zero alibi_vs_physical), so `MIN_VOICES` (the co-presence
path) is a dead knob. The only lever that lights R7 is promoting the single-witness
`alibi_vs_sighting` band to STRONG = 54/114 meetings at ~81% precision; corroboration makes it
worse. Lighting R7 is a precision/recall trade, not a tweak.

Run: uv run python experiments/lab/forward_redesign_detector_sweep.py  ($0, reads committed replays).
"""

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))  # lab bootstrap so meetings.* imports resolve

import meetings.transcript as T  # noqa: E402
from meetings.schemas import MeetingTranscript  # noqa: E402
from meetings.transcript import detect_contradictions, is_weak_contradiction  # noqa: E402

SAMP = REPO / "replays" / "samples" / "9p2i"


def meetings_of(seed):
    lines = (SAMP / f"replay-seed-{seed}.jsonl").read_text().splitlines()
    return [
        r
        for r in (json.loads(s) for s in lines if s.strip())
        if r.get("kind") == "meeting"
    ]


def main():
    rep = json.loads((SAMP / "tournament-eval-report.json").read_text())
    meta = {g["seed"]: g for g in rep["report"]["games"]}

    configs = (
        "current(MINV=2)",
        "MINV=1",
        "promote_all_avs",
        "promote_avs_corrob>=2sightings",
    )
    cfg = {k: {"mtgs": 0, "tp": 0, "fp": 0} for k in configs}
    n_meetings = avs_meetings = fails = 0
    kinds = Counter()
    samples = []

    for seed in sorted(meta):
        roles = meta[seed]["roles"]
        roster = frozenset(roles)
        for m in meetings_of(seed):
            n_meetings += 1
            try:
                tr = MeetingTranscript.model_validate(m["transcript"])
            except Exception:  # noqa: BLE001 - a malformed transcript is just skipped + counted
                fails += 1
                continue
            flags_by = {}
            for minv in (2, 1):
                T.PHYSICAL_CONTRADICTION_MIN_VOICES = minv
                flags_by[minv] = detect_contradictions(tr, roster=roster)
            for minv, cname in ((2, "current(MINV=2)"), (1, "MINV=1")):
                subj = {
                    s
                    for f in flags_by[minv]
                    if not is_weak_contradiction(f)
                    for s in f.subjects
                    if s in roster
                }
                _tally(cfg[cname], subj, roles)
            flags = flags_by[2]
            for f in flags:
                kinds[(f.kind, "WEAK" if is_weak_contradiction(f) else "STRONG")] += 1
            avs = [f for f in flags if f.kind == "alibi_vs_sighting"]
            if avs:
                avs_meetings += 1
            if len(samples) < 4 and avs:
                samples.append(
                    (seed, list(avs[0].subjects), (avs[0].description or "")[:88])
                )
            _tally(
                cfg["promote_all_avs"],
                {s for f in avs for s in f.subjects if s in roster},
                roles,
            )
            per_subj = defaultdict(set)
            for f in avs:
                for s in f.subjects:
                    if s in roster:
                        per_subj[s].add(f.event_b_id)
            _tally(
                cfg["promote_avs_corrob>=2sightings"],
                {s for s, ev in per_subj.items() if len(ev) >= 2},
                roles,
            )

    print(
        f"meetings={n_meetings}  model_validate fails={fails}  alibi_vs_sighting meetings={avs_meetings}"
    )
    print("flag kinds (kind, class):", dict(kinds))
    print("sample alibi_vs_sighting (seed, subjects, description):")
    for s in samples:
        print("   ", s)
    print(
        f"\n{'config':30}{'R7 strong-mtgs':>16}{'TP imp':>8}{'FP crew':>9}{'precision':>11}"
    )
    for cname, c in cfg.items():
        tot = c["tp"] + c["fp"]
        prec = (c["tp"] / tot) if tot else 0.0
        print(f"  {cname:28}{c['mtgs']:>16}{c['tp']:>8}{c['fp']:>9}{prec:>10.0%}")


def _tally(acc, subjects, roles):
    if not subjects:
        return
    acc["mtgs"] += 1
    for s in subjects:
        acc["tp" if roles[s] == "IMPOSTOR" else "fp"] += 1


if __name__ == "__main__":
    main()
