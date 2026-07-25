# Recording paths — operator-recorded vs repository-relative

Every committed ranking row (`ranking-*.jsonl`) and instrument sweep (`sweep-*.json`)
carries a `replay_set_dir` / `sample_dir` field **exactly as the recording process wrote
it** — an operator-machine path under `~/ailibi-campaign-1824/`. Those fields are
verbatim library output and are deliberately NOT rewritten: they are the as-recorded
provenance of the run, and editing them would make the committed extract disagree with
the process that produced it.

The recordings themselves ARE committed, at paths that mirror the operator tree 1:1.
To follow any `replay_set_dir` field from a fresh checkout, apply this prefix map:

| as-recorded prefix | repository-relative prefix |
|---|---|
| `~/ailibi-campaign-1824/realpath/<run>/` | `training/artifacts/coevo/realpath/<run>/` |
| `~/ailibi-campaign-1824/realpath-backfill/<run>/` | `training/artifacts/coevo/realpath-backfill/<run>/` |
| `~/ailibi-campaign-1824/realpath-ablation/<name>/` | `training/artifacts/coevo/realpath-ablation/<name>/` |
| `~/ailibi-campaign-1824/realpath-comparator/` | `training/artifacts/coevo/realpath-comparator/` |

Everything below those prefixes (`recordings-<tranche>/<NNN>-<label>/replay-seed-<seed>.jsonl`)
is byte-identical and sha256-verified by the `recordings-manifest.sha256` in each root:

```bash
cd training/artifacts/coevo/realpath && shasum -a 256 -c recordings-manifest.sha256
```

Re-running an instrument fold or the validity gate over committed bytes therefore means
pointing the tool at the repository-relative directory, e.g.

```bash
uv run python -c "from pathlib import Path; from eval.off_menu import compute_off_menu_report; print(compute_off_menu_report(Path('training/artifacts/coevo/realpath/run-04-freepolicy-v3/recordings-4000-4002/000-run-04-freepolicy-v3-alternating-freeze-champion-gen9-27f852fe0919')))"
```

Audit sidecars (`*.audit.jsonl`) are excluded from the committed tree: no instrument or
gate reads them, and they are ~10× the size of the replays they accompany.
