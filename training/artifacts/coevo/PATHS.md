# Recording paths — operator-recorded vs repository-relative

> **Since Task 19.22, most of the paths this file maps are not in your working
> tree.** The prune moved every byte under `training/artifacts/coevo/` that no
> test opens — the per-seed recordings, their rosters and manifests, the
> unpinned genome directories — onto ONE pinned evidence commit. Every path
> below is still exactly where those bytes belong, and
> `bash scripts/fetch_evidence.sh` restores them there by that pinned sha.
> The pin, the digests and the enumeration of what stayed are in
> [`EVIDENCE-MANIFEST.md`](EVIDENCE-MANIFEST.md); the retention rule is
> [`docs/artifacts.md`](../../../docs/artifacts.md). Nothing about the prefix
> maps or the layout changed — only whether the bytes are present before you ask
> for them.

Every committed ranking row (`ranking-*.jsonl`) and instrument sweep (`sweep-*.json`)
carries a `replay_set_dir` / `sample_dir` field **exactly as the recording process wrote
it** — an operator-machine absolute path under
`/Users/danielkeinan/ailibi-campaign-1824/`. Those fields are
verbatim library output and are deliberately NOT rewritten: they are the as-recorded
provenance of the run, and editing them would make the committed extract disagree with
the process that produced it.

The recordings themselves are PRESERVED, at paths that mirror the operator tree 1:1 —
in-tree until Task 19.22, on the pinned evidence commit since (see the note above).
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
is byte-identical and sha256-verified by the `recordings-manifest.sha256` in each root.
Both the recordings and their manifest moved together at 19.22, so this still works
verbatim once they are restored:

```bash
bash scripts/fetch_evidence.sh   # once — restores the bytes by the pinned sha
cd training/artifacts/coevo/realpath && shasum -a 256 -c recordings-manifest.sha256
```

Re-running an instrument fold or the validity gate over those bytes therefore means
pointing the tool at the repository-relative directory, e.g.

```bash
uv run python -c "from pathlib import Path; from eval.off_menu import compute_off_menu_report; print(compute_off_menu_report(Path('training/artifacts/coevo/realpath/run-04-freepolicy-v3/recordings-4000-4002/000-run-04-freepolicy-v3-alternating-freeze-champion-gen9-27f852fe0919')))"
```

Every recording directory also carries the `roster.json` descriptor
(`{"num_players": 9, "num_impostors": 2, "tasks_per_crewmate": 2}`) the instrument walks
require — without it `resolve_roster_knobs` falls back to the legacy 4p1i roster and the
state-hash fence refuses at tick 0.

Audit sidecars (`*.audit.jsonl`) are excluded from the committed tree: no instrument or
gate reads them, and they are ~10× the size of the replays they accompany.

## The 18.25 crew campaign (operator root `/Users/danielkeinan/ailibi-campaign-1825/`)

| as-recorded absolute prefix | repository-relative prefix |
|---|---|
| `/Users/danielkeinan/ailibi-campaign-1825/realpath/<run>/` | `training/artifacts/coevo/realpath-crew/<run>/` |

The fake-path work directories under `/Users/danielkeinan/ailibi-campaign-1825/<run>/work/`
(named in the session logs and harnesses) were CONSOLIDATED, not mirrored 1:1 — the
per-artifact map:

| as-recorded operator path | repository location |
|---|---|
| `<run>/work/campaign-rows.jsonl` (main runs) | `training/reports/results-crew-campaign.jsonl` (concatenated in run order: run-c1 rows 1–12, run-c2 rows 13–24) |
| `<run>/work/campaign-rows.jsonl` + `campaign-plan.json` (ablation twins) | `training/artifacts/coevo/ablation-<run-suffix>/` |
| `<run>/work/gen-champions/` | `training/artifacts/coevo/gen-champions/<run>/` |
| hall_root (written in-tree by the driver) | `training/artifacts/coevo/<run>/` |
| harnesses + leg scripts | `training/artifacts/coevo/provenance/harnesses/` |

**Sweep provenance split (18.25):** the paragraph above about as-recorded operator
paths applies to RANKING rows and the 18.24 sweeps. The four 18.25 crew sweeps
(`realpath-crew/*/sweep-*.json`) were REGENERATED from the committed recording bytes at
their committed locations after the CF4 relocation (disclosed in report-crew-campaign.md
§5 + PR #316 review round 2/3), so their `sample_dir`/`replay_set_dir` fields are
repository-relative and need no prefix map. The 18.25 ranking rows keep as-recorded
operator-absolute paths covered by the `ailibi-campaign-1825` map above.
