# Recording paths — operator-recorded vs repository-relative

Every committed ranking row (`ranking-*.jsonl`) and instrument sweep (`sweep-*.json`)
carries a `replay_set_dir` / `sample_dir` field **exactly as the recording process wrote
it** — an operator-machine absolute path under
`/Users/danielkeinan/ailibi-campaign-1824/`. Those fields are
verbatim library output and are deliberately NOT rewritten: they are the as-recorded
provenance of the run, and editing them would make the committed extract disagree with
the process that produced it.

The recordings themselves ARE committed, at paths that mirror the operator tree 1:1.
To follow any `replay_set_dir` field from a fresh checkout, apply this prefix map.
The recorded fields carry the operator's ABSOLUTE home path — literally
`/Users/danielkeinan/ailibi-campaign-1824/...` — so match on that prefix, not on a
tilde form:

| as-recorded absolute prefix | repository-relative prefix |
|---|---|
| `/Users/danielkeinan/ailibi-campaign-1824/realpath/<run>/` | `training/artifacts/coevo/realpath/<run>/` |
| `/Users/danielkeinan/ailibi-campaign-1824/realpath-backfill/<run>/` | `training/artifacts/coevo/realpath-backfill/<run>/` |
| `/Users/danielkeinan/ailibi-campaign-1824/realpath-runnerups/<run>/` | `training/artifacts/coevo/realpath-runnerups/<run>/` |
| `/Users/danielkeinan/ailibi-campaign-1824/realpath-runnerups-gen3/<run>/` | `training/artifacts/coevo/realpath-runnerups-gen3/<run>/` |
| `/Users/danielkeinan/ailibi-campaign-1824/realpath-ablation/<name>/` | `training/artifacts/coevo/realpath-ablation/<name>/` |
| `/Users/danielkeinan/ailibi-campaign-1824/realpath-comparator/` | `training/artifacts/coevo/realpath-comparator/` |

A one-line translation, if you are scripting it:

```bash
sed 's#/Users/danielkeinan/ailibi-campaign-1824/#training/artifacts/coevo/#'
```

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

Every committed recording directory also carries the `roster.json` descriptor
(`{"num_players": 9, "num_impostors": 2, "tasks_per_crewmate": 2}`) the instrument walks
require — without it `resolve_roster_knobs` falls back to the legacy 4p1i roster and the
state-hash fence refuses at tick 0.

Audit sidecars (`*.audit.jsonl`) are excluded from the committed tree: no instrument or
gate reads them, and they are ~10× the size of the replays they accompany.

## The 18.25 crew campaign (operator root `/Users/danielkeinan/ailibi-campaign-1825/`)

| as-recorded absolute prefix | repository-relative prefix |
|---|---|
| `/Users/danielkeinan/ailibi-campaign-1825/realpath/<run>/` | `training/artifacts/coevo/realpath/<run>/` |
