# The Phase-18 co-evolution evidence — the manifest and the pin

> **Task:** 19.22 (`tasks/phase-19.md`) — artifact classes + the coevo prune +
> the fast-clone path — implementing Phase-19 **locked decision 5**
> (*"artifact retention: prune coevo only"*).
> **Anchors:** `audits/audit-phase-19-triage.md` §7 item 23 \[C; VERIFIED §8
> row 11\]; `audits/audit-phase-18-close.md` §6.3 C4 (the coevo namespace
> rules — this prune does not touch `DEFAULT_RANKING_ROOTS` semantics).
> **The classes this file instantiates:** `docs/artifacts.md`.
> **Restore the moved bytes:** `bash scripts/fetch_evidence.sh`.

This file is the **manifest commit** for the class-(c) bytes of the closed
Phase-18 co-evolution campaign. It pins the commit that holds them, records
which bytes stayed behind and *what pins each one*, and carries a sha-256 for
every file on that commit. It is class (b) — a manifest in git — and it is the
authority: where the evidence branch's own README and this file disagree, this
file wins.

## 1. The pin

| | |
|---|---|
| branch | `evidence/phase-18-coevo` |
| **tip sha — THE PIN** | **`476a1f85492439277350af9708f1d120eb1c0a71`** |
| commits | **1** — an orphan commit, and it stays one commit |
| files | 2,953 |
| bytes | 418,648,282 (399.254 MiB) of payload, plus the branch README |

`scripts/fetch_evidence.sh` fetches **by that sha, never by the branch name**.
A branch name is a moving pointer; the sha is not, so the sha is the
immutability guarantee. A second commit on that branch would not corrupt
anything — it would simply be unreachable by every consumer, which is the
point.

## 2. What the prune did

| | files | bytes | MiB |
|---|---:|---:|---:|
| `training/artifacts/coevo/` before | 1,473 | 106,514,778 | 101.580 |
| **moved** to the evidence commit | **1,383** | **106,008,002** | **101.097** |
| retained in-tree (§3) | 90 | 506,776 | 0.483 (494.9 KiB) |

The **net** effect on the whole tracked working tree is smaller than the
moved figure, because this task also ADDS three tracked files (this
manifest, `docs/artifacts.md`, `scripts/fetch_evidence.sh`) and grows two
more. Measured from the trees themselves, not by subtraction:

| tracked working tree | files | bytes | MiB |
|---|---:|---:|---:|
| before | 3,049 | 374,298,090 | 356.958 |
| after | 1,669 | 268,616,660 | 256.173 |
| **net** | **-1,380** | **-105,681,430** | **-100.786** |

That is a **28.2%** reduction, all of it out of this one directory.
`replays/` did not move (locked decision 5).

**No history was rewritten.** The moved blobs remain in this repository's
history, so a full-history clone is not smaller — see the fast-clone note in
`README.md` and `docs/reading-guide.md` §2 for the honest version of that.

## 3. What stayed in-tree — the consumer enumeration

The contract's first step, and its output: **the consumers are the authority
on what may not move.** The enumeration was taken empirically, not from the
prose — a CPython audit hook (`open`, `os.scandir`, `os.listdir`,
`shutil.copy*`) recorded every filesystem touch under this directory across a
full `uv run pytest` run (4,834 passed / 20 skipped / 3 xfailed), and the
result was re-derived per consumer file to attribute each byte to the test
that pins it.

**47 files are opened by the suite. 43 more are retained by contract rule.**
Everything else moved.

The planning session's consumer set named TWO test files. The trace found a
**third**: `tests/training/test_realpath_schema.py` reads coevo bytes through
`_ARTIFACT_ROOT.rglob("ranking*.jsonl")` — an exhaustiveness census that
opens **every** `ranking*.jsonl` under this root (all 30 of them), plus the six
`realpath-crew/` files it pins by name. It is listed below beside the two the
contract named; no test was edited.

| retained path | retained because |
|---|---|
| `PATHS.md` | **rule** — the tree's reading key (it maps every as-recorded path) |
| `intermediates/run-02-utility-lambda4/gen-2/ea4bc955dfe0beb8f82663d659e6c990083cebb26a1dab9600c6b68b7783d79f/config.json` | **rule** — the provenance of a PINNED genome dir (see §5) |
| `intermediates/run-02-utility-lambda4/gen-2/ea4bc955dfe0beb8f82663d659e6c990083cebb26a1dab9600c6b68b7783d79f/stamp.json` | **rule** — the provenance of a PINNED genome dir (see §5) |
| `intermediates/run-02-utility-lambda4/gen-2/ea4bc955dfe0beb8f82663d659e6c990083cebb26a1dab9600c6b68b7783d79f/weights.json` | `tests/training/test_finalist_eval_pins.py` (the finalist arm's committed weights + sidecar) |
| `intermediates/run-02-utility-lambda4/gen-2/ea4bc955dfe0beb8f82663d659e6c990083cebb26a1dab9600c6b68b7783d79f/weights.json.sha256` | `tests/training/test_finalist_eval_pins.py` (the finalist arm's committed weights + sidecar) |
| `measurement-stability.json` | `tests/scripts/test_generate_campaign_tables.py` (reproduces `measurement-stability.json` key-for-key) |
| `provenance/chain-session2.log` | **rule** — a provenance record; the contract keeps them in-tree |
| `provenance/chain-session3-backfill.log` | **rule** — a provenance record; the contract keeps them in-tree |
| `provenance/harnesses/harness_run_c1.py.txt` | **rule** — a provenance record; the contract keeps them in-tree |
| `provenance/harnesses/harness_run_c1_ablation.py.txt` | **rule** — a provenance record; the contract keeps them in-tree |
| `provenance/harnesses/harness_run_c2.py.txt` | **rule** — a provenance record; the contract keeps them in-tree |
| `provenance/harnesses/harness_run_c2_ablation.py.txt` | **rule** — a provenance record; the contract keeps them in-tree |
| `provenance/harnesses/leg_c1_t1.py.txt` | **rule** — a provenance record; the contract keeps them in-tree |
| `provenance/harnesses/leg_c1_t2.py.txt` | **rule** — a provenance record; the contract keeps them in-tree |
| `provenance/harnesses/leg_c2_t1.py.txt` | **rule** — a provenance record; the contract keeps them in-tree |
| `provenance/harnesses/leg_c2_t2.py.txt` | **rule** — a provenance record; the contract keeps them in-tree |
| `provenance/session1-chain.log` | **rule** — a provenance record; the contract keeps them in-tree |
| `provenance/session1-leg-01-t1.log` | **rule** — a provenance record; the contract keeps them in-tree |
| `provenance/session1-leg-02-t1.log` | **rule** — a provenance record; the contract keeps them in-tree |
| `provenance/session1-leg-03-t1.log` | **rule** — a provenance record; the contract keeps them in-tree |
| `provenance/session1-leg-04-t1.log` | **rule** — a provenance record; the contract keeps them in-tree |
| `provenance/session2-ablation-twins.log` | **rule** — a provenance record; the contract keeps them in-tree |
| `provenance/session2-leg-c1-t1.log` | **rule** — a provenance record; the contract keeps them in-tree |
| `provenance/session2-leg-c1-t2.log` | **rule** — a provenance record; the contract keeps them in-tree |
| `provenance/session2-leg-c2-t1.log` | **rule** — a provenance record; the contract keeps them in-tree |
| `provenance/session2-leg-c2-t2.log` | **rule** — a provenance record; the contract keeps them in-tree |
| `provenance/session3-ablation-encoder-v3.log` | **rule** — a provenance record; the contract keeps them in-tree |
| `provenance/session4-fsm-comparator.log` | **rule** — a provenance record; the contract keeps them in-tree |
| `provenance/session4-gen3-runnerup-leg.log` | **rule** — a provenance record; the contract keeps them in-tree |
| `provenance/session4-runnerup-leg-t1.log` | **rule** — a provenance record; the contract keeps them in-tree |
| `provenance/session4-runnerup-leg-t2.log` | **rule** — a provenance record; the contract keeps them in-tree |
| `provenance/session4-runnerup-recovery.log` | **rule** — a provenance record; the contract keeps them in-tree |
| `realpath-ablation/ablation-run-04-encoder-v3/ranking-4000-4002.jsonl` | `tests/training/test_realpath_schema.py` (the `ranking*.jsonl` census + the `-v3` round-trip) |
| `realpath-ablation/ablation-run-04-encoder-v3/ranking-4003-4005.jsonl` | `tests/training/test_realpath_schema.py` (the `ranking*.jsonl` census + the `-v3` round-trip) |
| `realpath-backfill/run-02-utility-lambda4/ranking-4000-4002.jsonl` | `tests/scripts/test_generate_campaign_tables.py` (the §4.0 stability reproduction, over `DEFAULT_RANKING_ROOTS`) + `tests/training/test_realpath_schema.py` (the `ranking*.jsonl` census) |
| `realpath-backfill/run-02-utility-lambda4/ranking-4003-4005.jsonl` | `tests/scripts/test_generate_campaign_tables.py` (the §4.0 stability reproduction, over `DEFAULT_RANKING_ROOTS`) + `tests/training/test_realpath_schema.py` (the `ranking*.jsonl` census) |
| `realpath-backfill/run-03-utility-bcanchor/ranking-4000-4002.jsonl` | `tests/scripts/test_generate_campaign_tables.py` (the §4.0 stability reproduction, over `DEFAULT_RANKING_ROOTS`) + `tests/training/test_realpath_schema.py` (the `ranking*.jsonl` census) |
| `realpath-backfill/run-03-utility-bcanchor/ranking-4003-4005.jsonl` | `tests/scripts/test_generate_campaign_tables.py` (the §4.0 stability reproduction, over `DEFAULT_RANKING_ROOTS`) + `tests/training/test_realpath_schema.py` (the `ranking*.jsonl` census) |
| `realpath-backfill/run-04-freepolicy-v3/ranking-4000-4002.jsonl` | `tests/scripts/test_generate_campaign_tables.py` (the §4.0 stability reproduction, over `DEFAULT_RANKING_ROOTS`) + `tests/training/test_realpath_schema.py` (the `ranking*.jsonl` census) |
| `realpath-backfill/run-04-freepolicy-v3/ranking-4003-4005.jsonl` | `tests/scripts/test_generate_campaign_tables.py` (the §4.0 stability reproduction, over `DEFAULT_RANKING_ROOTS`) + `tests/training/test_realpath_schema.py` (the `ranking*.jsonl` census) |
| `realpath-crew/controls/crew-owned-tasks-es-gen0/config.json` | **rule** — the provenance of a PINNED genome dir (see §5) |
| `realpath-crew/controls/crew-owned-tasks-es-gen0/stamp.json` | **rule** — the provenance of a PINNED genome dir (see §5) |
| `realpath-crew/controls/crew-owned-tasks-es-gen0/weights.json` | `tests/training/test_finalist_eval_pins.py` (the finalist arm's committed weights + sidecar) |
| `realpath-crew/controls/crew-owned-tasks-es-gen0/weights.json.sha256` | `tests/training/test_finalist_eval_pins.py` (the finalist arm's committed weights + sidecar) |
| `realpath-crew/controls/crew-utility-es-gen0/config.json` | **rule** — the provenance of a PINNED genome dir (see §5) |
| `realpath-crew/controls/crew-utility-es-gen0/stamp.json` | **rule** — the provenance of a PINNED genome dir (see §5) |
| `realpath-crew/controls/crew-utility-es-gen0/weights.json` | `tests/training/test_finalist_eval_pins.py` (the finalist arm's committed weights + sidecar) |
| `realpath-crew/controls/crew-utility-es-gen0/weights.json.sha256` | `tests/training/test_finalist_eval_pins.py` (the finalist arm's committed weights + sidecar) |
| `realpath-crew/run-c1-crew-owned-tasks/ranking-4000-4002.jsonl` | `tests/training/test_realpath_schema.py` (the `ranking*.jsonl` census + the `-v3` round-trip) |
| `realpath-crew/run-c1-crew-owned-tasks/ranking-4003-4005.jsonl` | `tests/training/test_realpath_schema.py` (the `ranking*.jsonl` census + the `-v3` round-trip) |
| `realpath-crew/run-c2-crew-general/ranking-4000-4002.jsonl` | `tests/training/test_realpath_schema.py` (the `ranking*.jsonl` census + the `-v3` round-trip) |
| `realpath-crew/run-c2-crew-general/ranking-4003-4005.jsonl` | `tests/training/test_realpath_schema.py` (the `ranking*.jsonl` census + the `-v3` round-trip) |
| `realpath-crew/run-c2-crew-general/stability-inputs-filtered/ranking-4000-4002.jsonl` | `tests/training/test_realpath_schema.py` (the `ranking*.jsonl` census + the `-v3` round-trip) |
| `realpath-crew/run-c2-crew-general/stability-inputs-filtered/ranking-4003-4005.jsonl` | `tests/training/test_realpath_schema.py` (the `ranking*.jsonl` census + the `-v3` round-trip) |
| `realpath-runnerups-gen3/run-02-utility-lambda4/ranking-4000-4002.jsonl` | `tests/scripts/test_generate_campaign_tables.py` (the §4.0 stability reproduction, over `DEFAULT_RANKING_ROOTS`) + `tests/training/test_realpath_schema.py` (the `ranking*.jsonl` census) |
| `realpath-runnerups-gen3/run-02-utility-lambda4/ranking-4003-4005.jsonl` | `tests/scripts/test_generate_campaign_tables.py` (the §4.0 stability reproduction, over `DEFAULT_RANKING_ROOTS`) + `tests/training/test_realpath_schema.py` (the `ranking*.jsonl` census) |
| `realpath-runnerups/run-01-utility-champion/ranking-4000-4002.jsonl` | `tests/scripts/test_generate_campaign_tables.py` (the §4.0 stability reproduction, over `DEFAULT_RANKING_ROOTS`) + `tests/training/test_realpath_schema.py` (the `ranking*.jsonl` census) |
| `realpath-runnerups/run-02-utility-lambda4/ranking-4000-4002.jsonl` | `tests/scripts/test_generate_campaign_tables.py` (the §4.0 stability reproduction, over `DEFAULT_RANKING_ROOTS`) + `tests/training/test_realpath_schema.py` (the `ranking*.jsonl` census) |
| `realpath-runnerups/run-02-utility-lambda4/ranking-4003-4005.jsonl` | `tests/scripts/test_generate_campaign_tables.py` (the §4.0 stability reproduction, over `DEFAULT_RANKING_ROOTS`) + `tests/training/test_realpath_schema.py` (the `ranking*.jsonl` census) |
| `realpath-runnerups/run-03-utility-bcanchor/ranking-4000-4002.jsonl` | `tests/scripts/test_generate_campaign_tables.py` (the §4.0 stability reproduction, over `DEFAULT_RANKING_ROOTS`) + `tests/training/test_realpath_schema.py` (the `ranking*.jsonl` census) |
| `realpath/run-01-utility-champion/ranking-4000-4002.jsonl` | `tests/scripts/test_generate_campaign_tables.py` (the §4.0 stability reproduction, over `DEFAULT_RANKING_ROOTS`) + `tests/training/test_realpath_schema.py` (the `ranking*.jsonl` census) |
| `realpath/run-01-utility-champion/ranking-4003-4005.jsonl` | `tests/scripts/test_generate_campaign_tables.py` (the §4.0 stability reproduction, over `DEFAULT_RANKING_ROOTS`) + `tests/training/test_realpath_schema.py` (the `ranking*.jsonl` census) |
| `realpath/run-02-utility-lambda4/ranking-4000-4002.jsonl` | `tests/scripts/test_generate_campaign_tables.py` (the §4.0 stability reproduction, over `DEFAULT_RANKING_ROOTS`) + `tests/training/test_realpath_schema.py` (the `ranking*.jsonl` census) |
| `realpath/run-02-utility-lambda4/ranking-4003-4005.jsonl` | `tests/scripts/test_generate_campaign_tables.py` (the §4.0 stability reproduction, over `DEFAULT_RANKING_ROOTS`) + `tests/training/test_realpath_schema.py` (the `ranking*.jsonl` census) |
| `realpath/run-03-utility-bcanchor/ranking-4000-4002.jsonl` | `tests/scripts/test_generate_campaign_tables.py` (the §4.0 stability reproduction, over `DEFAULT_RANKING_ROOTS`) + `tests/training/test_realpath_schema.py` (the `ranking*.jsonl` census) |
| `realpath/run-03-utility-bcanchor/ranking-4003-4005.jsonl` | `tests/scripts/test_generate_campaign_tables.py` (the §4.0 stability reproduction, over `DEFAULT_RANKING_ROOTS`) + `tests/training/test_realpath_schema.py` (the `ranking*.jsonl` census) |
| `realpath/run-04-freepolicy-v3/ranking-4000-4002.jsonl` | `tests/scripts/test_generate_campaign_tables.py` (the §4.0 stability reproduction, over `DEFAULT_RANKING_ROOTS`) + `tests/training/test_realpath_schema.py` (the `ranking*.jsonl` census) |
| `realpath/run-04-freepolicy-v3/ranking-4003-4005.jsonl` | `tests/scripts/test_generate_campaign_tables.py` (the §4.0 stability reproduction, over `DEFAULT_RANKING_ROOTS`) + `tests/training/test_realpath_schema.py` (the `ranking*.jsonl` census) |
| `realpath/run-05-freepolicy-v2-founders/ranking-4000-4002.jsonl` | `tests/scripts/test_generate_campaign_tables.py` (the §4.0 stability reproduction, over `DEFAULT_RANKING_ROOTS`) + `tests/training/test_realpath_schema.py` (the `ranking*.jsonl` census) |
| `realpath/run-05-freepolicy-v2-founders/ranking-4003-4005.jsonl` | `tests/scripts/test_generate_campaign_tables.py` (the §4.0 stability reproduction, over `DEFAULT_RANKING_ROOTS`) + `tests/training/test_realpath_schema.py` (the `ranking*.jsonl` census) |
| `run-01-utility-champion/impostor/gen-3/6d327dcbde940a5ee1bb4f9e22ff91fbbc4d74c0ddb33797043fdff69fef71d0/config.json` | **rule** — the provenance of a PINNED genome dir (see §5) |
| `run-01-utility-champion/impostor/gen-3/6d327dcbde940a5ee1bb4f9e22ff91fbbc4d74c0ddb33797043fdff69fef71d0/stamp.json` | **rule** — the provenance of a PINNED genome dir (see §5) |
| `run-01-utility-champion/impostor/gen-3/6d327dcbde940a5ee1bb4f9e22ff91fbbc4d74c0ddb33797043fdff69fef71d0/weights.json` | `tests/training/test_finalist_eval_pins.py` (the finalist arm's committed weights + sidecar) |
| `run-01-utility-champion/impostor/gen-3/6d327dcbde940a5ee1bb4f9e22ff91fbbc4d74c0ddb33797043fdff69fef71d0/weights.json.sha256` | `tests/training/test_finalist_eval_pins.py` (the finalist arm's committed weights + sidecar) |
| `run-c1-crew-owned-tasks/crew/gen-9/0bf179b719a67c1b40f97377ba49bad6512d08932e0d944e4d024691f60e71df/config.json` | **rule** — the provenance of a PINNED genome dir (see §5) |
| `run-c1-crew-owned-tasks/crew/gen-9/0bf179b719a67c1b40f97377ba49bad6512d08932e0d944e4d024691f60e71df/stamp.json` | **rule** — the provenance of a PINNED genome dir (see §5) |
| `run-c1-crew-owned-tasks/crew/gen-9/0bf179b719a67c1b40f97377ba49bad6512d08932e0d944e4d024691f60e71df/weights.json` | `tests/training/test_finalist_eval_pins.py` (the finalist arm's committed weights + sidecar) |
| `run-c1-crew-owned-tasks/crew/gen-9/0bf179b719a67c1b40f97377ba49bad6512d08932e0d944e4d024691f60e71df/weights.json.sha256` | `tests/training/test_finalist_eval_pins.py` (the finalist arm's committed weights + sidecar) |
| `run-c2-crew-general/crew/gen-9/515fc066f7aafc5d3603ab531adb9fe78cd496192c7565e9d8b4d3ff7b09a635/config.json` | **rule** — the provenance of a PINNED genome dir (see §5) |
| `run-c2-crew-general/crew/gen-9/515fc066f7aafc5d3603ab531adb9fe78cd496192c7565e9d8b4d3ff7b09a635/stamp.json` | **rule** — the provenance of a PINNED genome dir (see §5) |
| `run-c2-crew-general/crew/gen-9/515fc066f7aafc5d3603ab531adb9fe78cd496192c7565e9d8b4d3ff7b09a635/weights.json` | `tests/training/test_finalist_eval_pins.py` (the finalist arm's committed weights + sidecar) |
| `run-c2-crew-general/crew/gen-9/515fc066f7aafc5d3603ab531adb9fe78cd496192c7565e9d8b4d3ff7b09a635/weights.json.sha256` | `tests/training/test_finalist_eval_pins.py` (the finalist arm's committed weights + sidecar) |
| `runnerups/run-02-utility-lambda4/gen-9/bfd145cb4883fa7fd0f009811cdc6e660b4f4a62105534f384afbb45b2c12ee8/config.json` | **rule** — the provenance of a PINNED genome dir (see §5) |
| `runnerups/run-02-utility-lambda4/gen-9/bfd145cb4883fa7fd0f009811cdc6e660b4f4a62105534f384afbb45b2c12ee8/stamp.json` | **rule** — the provenance of a PINNED genome dir (see §5) |
| `runnerups/run-02-utility-lambda4/gen-9/bfd145cb4883fa7fd0f009811cdc6e660b4f4a62105534f384afbb45b2c12ee8/weights.json` | `tests/training/test_finalist_eval_pins.py` (the finalist arm's committed weights + sidecar) |
| `runnerups/run-02-utility-lambda4/gen-9/bfd145cb4883fa7fd0f009811cdc6e660b4f4a62105534f384afbb45b2c12ee8/weights.json.sha256` | `tests/training/test_finalist_eval_pins.py` (the finalist arm's committed weights + sidecar) |
| `runnerups/run-03-utility-bcanchor/gen-8/7f73929d5b91f4afe67adc1b2ac7ca42bdd3ab1f49ed0393342ab21c7db0985e/config.json` | **rule** — the provenance of a PINNED genome dir (see §5) |
| `runnerups/run-03-utility-bcanchor/gen-8/7f73929d5b91f4afe67adc1b2ac7ca42bdd3ab1f49ed0393342ab21c7db0985e/stamp.json` | **rule** — the provenance of a PINNED genome dir (see §5) |
| `runnerups/run-03-utility-bcanchor/gen-8/7f73929d5b91f4afe67adc1b2ac7ca42bdd3ab1f49ed0393342ab21c7db0985e/weights.json` | `tests/training/test_finalist_eval_pins.py` (the finalist arm's committed weights + sidecar) |
| `runnerups/run-03-utility-bcanchor/gen-8/7f73929d5b91f4afe67adc1b2ac7ca42bdd3ab1f49ed0393342ab21c7db0985e/weights.json.sha256` | `tests/training/test_finalist_eval_pins.py` (the finalist arm's committed weights + sidecar) |

## 4. What moved

| class | files |
|---|---:|
| raw per-seed recordings (`realpath*/…/recordings-*/…`) | 219 |
| recording-dir roster descriptors | 73 |
| unpinned genome weights | 245 |
| their sha-256 sidecars (kept PAIRED — §5) | 245 |
| unpinned genome config + stamp | 488 |
| per-tranche recordings manifests | 15 |
| hall-of-fame files | 24 |
| campaign plans, rows, sweeps, quotes, corpora | 74 |
| **total** | **1,383** |

Plus the **Phase-18 finalist raw slate** — 1,569 files / 298.157 MiB under
`finalist-eval-raw/`, recovered at Task 19.21 and folded into the same commit
from `evidence/raw-slate-staging` @
`c27ab7b5f5e7e10bfab5c6dc752362b137862cac`. Every one of its
1,569 files was re-verified against
`training/reports/_finalist_eval_raw/MANIFEST.md` §7 **before** the fold
(1,569/1,569 OK, 0 failures) and the two path sets were compared row for row.

**The staging ref is superseded, and its deletion is the one step this task
could not execute.** The fold is complete and verified — the slate's durable
home is the pinned commit above, and nothing reads the staging ref any more —
but `git push origin --delete evidence/raw-slate-staging` was **refused by
GitHub with HTTP 403** from this session (the same credential created
`evidence/phase-18-coevo` in the same run, so this is a ref-deletion
permission or ruleset, not an egress block; the egress proxy recorded no
failure). **Owner step, one command, no data at risk:**

```bash
git push origin --delete evidence/raw-slate-staging   # @ c27ab7b5f5e7e10bfab5c6dc752362b137862cac
```

Until that runs, `evidence/raw-slate-staging` still exists on the remote as a
second copy of bytes this commit already carries and hashes. This manifest is
the authority on that ref's status — the evidence branch's own README calls it
retired, meaning superseded by the fold, and defers to this file.

One caution carried forward from that ref, because it is a real disagreement
in the bytes: the staging ref's own root `README.md` was the ONE staged file no
committed sha covered (its `MANIFEST.md` §2 says so openly), and it states two
figures the bytes contradict. It is **not** carried forward verbatim, its
digest is on the record here, and its two numbers appear nowhere in this tree:

| the staging README said | the bytes say |
|---|---|
| `1,569 files, 297.8 MiB` | 1,569 files, **298.157 MiB** (312,640,280 bytes) — `MANIFEST.md` states this correctly as 298.2 |
| recorded `2026-07-29 → 2026-08-01` | `2026-07-29T07:17:48Z → `**`2026-07-31T18:00:06Z`** — the last timestamp anywhere in the slate; no `2026-08` timestamp exists in it |

| the uncovered staged file | sha-256 | bytes |
|---|---|---:|
| `evidence/raw-slate-staging:README.md` (superseded) | `ea4e4ff1f50ecaae88000b69f707f9a478ec96eb7065a39ade1d48d5bad3b8fb` | 1,841 |

## 5. Weight/sidecar pairing — the rule the prune obeyed

A genome directory is `config.json` + `stamp.json` + `weights.json` +
`weights.json.sha256`. **A weight and its sidecar always travel together**: a
weight in one place and its sidecar in the other would be a manifest error —
verification-after-fetch would silently have nothing to check against.

So the unit of the prune is the **directory**, not the file:

- the **8 genome directories a test opens** stay whole, in-tree — their
  `weights.json` + `weights.json.sha256` are what
  `tests/training/test_finalist_eval_pins.py` reads, and their `config.json` +
  `stamp.json` are that artifact's provenance:

  - `intermediates/run-02-utility-lambda4/gen-2/ea4bc955dfe0beb8f82663d659e6c990083cebb26a1dab9600c6b68b7783d79f`
  - `realpath-crew/controls/crew-owned-tasks-es-gen0`
  - `realpath-crew/controls/crew-utility-es-gen0`
  - `run-01-utility-champion/impostor/gen-3/6d327dcbde940a5ee1bb4f9e22ff91fbbc4d74c0ddb33797043fdff69fef71d0`
  - `run-c1-crew-owned-tasks/crew/gen-9/0bf179b719a67c1b40f97377ba49bad6512d08932e0d944e4d024691f60e71df`
  - `run-c2-crew-general/crew/gen-9/515fc066f7aafc5d3603ab531adb9fe78cd496192c7565e9d8b4d3ff7b09a635`
  - `runnerups/run-02-utility-lambda4/gen-9/bfd145cb4883fa7fd0f009811cdc6e660b4f4a62105534f384afbb45b2c12ee8`
  - `runnerups/run-03-utility-bcanchor/gen-8/7f73929d5b91f4afe67adc1b2ac7ca42bdd3ab1f49ed0393342ab21c7db0985e`

- the remaining **245** genome directories moved whole. Their sidecars moved
  with them, which is why `scripts/verify_ml_evidence.py` (19.23) must class
  them as EVIDENCE-BRANCH-ABSENT until `scripts/fetch_evidence.sh` has run —
  never as a silent skip.

The same rule covers the 15 per-tranche `recordings-manifest*.sha256` files:
they hash the recordings, the recordings moved, so they moved too and verify
in place after a restore exactly as `PATHS.md` documents.

## 6. Verify

```bash
bash scripts/fetch_evidence.sh            # fetch by the pinned sha, restore, verify
bash scripts/fetch_evidence.sh --verify   # verify what is already restored
bash scripts/fetch_evidence.sh --clean    # remove the restored bytes again
```

`--verify` peels §7's fenced block and §8's delegated block into one
`sha256sum -c` input and checks the restored bytes against it, so *every* file
the evidence commit carries is covered by a digest this repository owns.

## 7. sha-256 — the `coevo/` payload and the branch README

Paths are relative to the evidence commit's root. `coevo/<x>` restores to
`training/artifacts/coevo/<x>`. `shasum -a 256 -c`-compatible, matching the
`recordings-manifest.sha256` idiom this tree already uses.

```sha256
d6e416b0074c9342d4ef8892da3300bdf60911dc35838d2c04c4b0f76635ee70  README.md
66022039495c070627b39c644dece4d3b2d6c5742c1c7299e6a1aab56ae5af23  coevo/ablation-run-01-conviction-term/campaign-plan.json
c5324d476cfee19f51bf26cbbd5e358e2ce9dcda8453f45fa28b7806dfcc3062  coevo/ablation-run-01-conviction-term/campaign-rows.jsonl
735dd272a08c3375a41e64dd45f64fed9034ca98d68efc77c6455368b1635fd2  coevo/ablation-run-01-conviction-term/crew/gen-12/81ea76a44ab6cfe39f648c7d88f0a7c3dad4cbf5a91e72efc4496b92d4256473/config.json
ff37be887e1bbd7347efb3e99bbbe5793a1ffa797b3ba5391e860383771dbe58  coevo/ablation-run-01-conviction-term/crew/gen-12/81ea76a44ab6cfe39f648c7d88f0a7c3dad4cbf5a91e72efc4496b92d4256473/stamp.json
81ea76a44ab6cfe39f648c7d88f0a7c3dad4cbf5a91e72efc4496b92d4256473  coevo/ablation-run-01-conviction-term/crew/gen-12/81ea76a44ab6cfe39f648c7d88f0a7c3dad4cbf5a91e72efc4496b92d4256473/weights.json
2b5a7d7c81d3c74d82a817d129e0209f5265d3d6f7047e2d2b145852bfb053c4  coevo/ablation-run-01-conviction-term/crew/gen-12/81ea76a44ab6cfe39f648c7d88f0a7c3dad4cbf5a91e72efc4496b92d4256473/weights.json.sha256
05401b87b6b025b60992e3d78cc7caa9d532c0fb3cf4627512febc7b40ad1630  coevo/ablation-run-01-conviction-term/crew/gen-6/22c9707e0ddcea03f7f4ab1fbe179cc1be7d00bcba5df8eb9ce93b69d97e8971/config.json
3e8ead89b1835483ec04b0ab7e199a9c42fa8bc7b448dee2847ed28d0f186041  coevo/ablation-run-01-conviction-term/crew/gen-6/22c9707e0ddcea03f7f4ab1fbe179cc1be7d00bcba5df8eb9ce93b69d97e8971/stamp.json
22c9707e0ddcea03f7f4ab1fbe179cc1be7d00bcba5df8eb9ce93b69d97e8971  coevo/ablation-run-01-conviction-term/crew/gen-6/22c9707e0ddcea03f7f4ab1fbe179cc1be7d00bcba5df8eb9ce93b69d97e8971/weights.json
1f61a5436018c0c2d31c0236013acbf479d6a494dcd24efab68c9455d195baf2  coevo/ablation-run-01-conviction-term/crew/gen-6/22c9707e0ddcea03f7f4ab1fbe179cc1be7d00bcba5df8eb9ce93b69d97e8971/weights.json.sha256
bafe6b41307af256138339f0efca480e474cdb59e72f30e071f616ae3ead6fdd  coevo/ablation-run-01-conviction-term/crew/gen-9/31c01b9ae1ac47b3fe9fdf7707f1b0f1cd9c80a7065a71bb0a8cc155a7520b24/config.json
f37165bfa2d91700f93c4bb05781575ab35fd417868b1b403e468b25ff7ef858  coevo/ablation-run-01-conviction-term/crew/gen-9/31c01b9ae1ac47b3fe9fdf7707f1b0f1cd9c80a7065a71bb0a8cc155a7520b24/stamp.json
31c01b9ae1ac47b3fe9fdf7707f1b0f1cd9c80a7065a71bb0a8cc155a7520b24  coevo/ablation-run-01-conviction-term/crew/gen-9/31c01b9ae1ac47b3fe9fdf7707f1b0f1cd9c80a7065a71bb0a8cc155a7520b24/weights.json
41e75b047dcad0d61bd4f0c3d9f5bdf0e1b58cd376e97c443e9ebe2953fd8901  coevo/ablation-run-01-conviction-term/crew/gen-9/31c01b9ae1ac47b3fe9fdf7707f1b0f1cd9c80a7065a71bb0a8cc155a7520b24/weights.json.sha256
65fc42d5b0e9e1dfebe4673e403b2b2ca19c3e91c63662d44627fb7d41472c47  coevo/ablation-run-01-conviction-term/crew/hall_of_fame.json
3676d190990a91823b695717f80466b94ab069d3eb890ece6138ac0bfd86ba5f  coevo/ablation-run-01-conviction-term/impostor/gen-10/46ee734a3319145dd8b12021e3d444c997dc0942798e6b0ee2c9539f82d5eb1f/config.json
0664084db7cc985df39ee3387b57ee33c6aeb33f5adf5c87b93a1650c6084876  coevo/ablation-run-01-conviction-term/impostor/gen-10/46ee734a3319145dd8b12021e3d444c997dc0942798e6b0ee2c9539f82d5eb1f/stamp.json
46ee734a3319145dd8b12021e3d444c997dc0942798e6b0ee2c9539f82d5eb1f  coevo/ablation-run-01-conviction-term/impostor/gen-10/46ee734a3319145dd8b12021e3d444c997dc0942798e6b0ee2c9539f82d5eb1f/weights.json
10331ff284663c3ffbb514397eddf59d9cab0fcfa61d785f1ff2ae14f815d7cc  coevo/ablation-run-01-conviction-term/impostor/gen-10/46ee734a3319145dd8b12021e3d444c997dc0942798e6b0ee2c9539f82d5eb1f/weights.json.sha256
7615e1bfcac255fa639e343105f2e27f30809c5170ca5684da13942993a47058  coevo/ablation-run-01-conviction-term/impostor/gen-11/6ba2019e85da1c038fd5ce06b14db00e1a35112ec4dd209bd76f6111c18680ac/config.json
2e7e151e8bacbbb66020f7e0a2975f17a06f907c77bea7a1cd75e2c49d4f015e  coevo/ablation-run-01-conviction-term/impostor/gen-11/6ba2019e85da1c038fd5ce06b14db00e1a35112ec4dd209bd76f6111c18680ac/stamp.json
6ba2019e85da1c038fd5ce06b14db00e1a35112ec4dd209bd76f6111c18680ac  coevo/ablation-run-01-conviction-term/impostor/gen-11/6ba2019e85da1c038fd5ce06b14db00e1a35112ec4dd209bd76f6111c18680ac/weights.json
85924b3dea876b5cde23318c8a3cdb8094204df8a0fe329375a4cfc3dc3ae8ba  coevo/ablation-run-01-conviction-term/impostor/gen-11/6ba2019e85da1c038fd5ce06b14db00e1a35112ec4dd209bd76f6111c18680ac/weights.json.sha256
ccdd66f84bdc0c31c47344cf4dd543d21b59a5245f8642ba0d3c004ecfb97414  coevo/ablation-run-01-conviction-term/impostor/gen-12/7ffd56f635017c4aaf51a3325fedb18e7e5d96efc5af7ade9d78c8bdae3db47c/config.json
05ad176f386ad4494a2b29947ae4c1e9137ebea42dcb4006fecae0655d61ddca  coevo/ablation-run-01-conviction-term/impostor/gen-12/7ffd56f635017c4aaf51a3325fedb18e7e5d96efc5af7ade9d78c8bdae3db47c/stamp.json
7ffd56f635017c4aaf51a3325fedb18e7e5d96efc5af7ade9d78c8bdae3db47c  coevo/ablation-run-01-conviction-term/impostor/gen-12/7ffd56f635017c4aaf51a3325fedb18e7e5d96efc5af7ade9d78c8bdae3db47c/weights.json
d7e581f2168d2bf9fa0ac71d4d110bdf9e715ab1eca6cf4d0ebfcd647d77d009  coevo/ablation-run-01-conviction-term/impostor/gen-12/7ffd56f635017c4aaf51a3325fedb18e7e5d96efc5af7ade9d78c8bdae3db47c/weights.json.sha256
c4e54abfba42de8808006e509513b96779f1c604b3f6efca2c92fe10f1131ace  coevo/ablation-run-01-conviction-term/impostor/gen-3/6d327dcbde940a5ee1bb4f9e22ff91fbbc4d74c0ddb33797043fdff69fef71d0/config.json
66bb488499b2890b60c5d5cebf569ac1404edf6433f959e3465c26c3f77499b3  coevo/ablation-run-01-conviction-term/impostor/gen-3/6d327dcbde940a5ee1bb4f9e22ff91fbbc4d74c0ddb33797043fdff69fef71d0/stamp.json
6d327dcbde940a5ee1bb4f9e22ff91fbbc4d74c0ddb33797043fdff69fef71d0  coevo/ablation-run-01-conviction-term/impostor/gen-3/6d327dcbde940a5ee1bb4f9e22ff91fbbc4d74c0ddb33797043fdff69fef71d0/weights.json
f893500dcbadee64f134260391e0d9f7afbc87c98b830e476eab4cb99d770037  coevo/ablation-run-01-conviction-term/impostor/gen-3/6d327dcbde940a5ee1bb4f9e22ff91fbbc4d74c0ddb33797043fdff69fef71d0/weights.json.sha256
005de46ba760a304a4d627d6356e1ef5d5e9cf7224e6e36f13098f12b83234f2  coevo/ablation-run-01-conviction-term/impostor/gen-4/a88f726205c8e75d5220a59dde205347a1cfd62411fd426a957e2295021c0aad/config.json
1a6d3d8759839ca2aa46c62fa00ba5e2da040de22cad5d42d3d7c27e3d46c721  coevo/ablation-run-01-conviction-term/impostor/gen-4/a88f726205c8e75d5220a59dde205347a1cfd62411fd426a957e2295021c0aad/stamp.json
a88f726205c8e75d5220a59dde205347a1cfd62411fd426a957e2295021c0aad  coevo/ablation-run-01-conviction-term/impostor/gen-4/a88f726205c8e75d5220a59dde205347a1cfd62411fd426a957e2295021c0aad/weights.json
43fbbbe27783cec0517d75b754a5a9d24b7ec5e3bed9379ac4ac3be1c085dc08  coevo/ablation-run-01-conviction-term/impostor/gen-4/a88f726205c8e75d5220a59dde205347a1cfd62411fd426a957e2295021c0aad/weights.json.sha256
3b3fbb22545bbf3461d27c9f00df64d726b6d731fa907870c1a9dcda6a4ff20e  coevo/ablation-run-01-conviction-term/impostor/gen-5/ec9de936c1f78996c072922e9c590fc6292949f5d8a20235319bdb044a00fd96/config.json
b15fbfa0fb707ce428ce83492a262ccd9a39ec6e82e0626c16f03933781c5c70  coevo/ablation-run-01-conviction-term/impostor/gen-5/ec9de936c1f78996c072922e9c590fc6292949f5d8a20235319bdb044a00fd96/stamp.json
ec9de936c1f78996c072922e9c590fc6292949f5d8a20235319bdb044a00fd96  coevo/ablation-run-01-conviction-term/impostor/gen-5/ec9de936c1f78996c072922e9c590fc6292949f5d8a20235319bdb044a00fd96/weights.json
2118e13df0386972c39e26f9ec8ea471b5629f5134cc566f9e005df859b26f25  coevo/ablation-run-01-conviction-term/impostor/gen-5/ec9de936c1f78996c072922e9c590fc6292949f5d8a20235319bdb044a00fd96/weights.json.sha256
1f7d62f1dc6b2033ec7cd8884fe3fb73273df55445adc41a178866896f7ee97b  coevo/ablation-run-01-conviction-term/impostor/gen-6/472f93b8716d839ee974c7c1081fc509bad7438da2a7dc9ae8ac6757f198677d/config.json
82fb78796cdf425175f4007e899a64963a864c80639d4af8134222462a953893  coevo/ablation-run-01-conviction-term/impostor/gen-6/472f93b8716d839ee974c7c1081fc509bad7438da2a7dc9ae8ac6757f198677d/stamp.json
472f93b8716d839ee974c7c1081fc509bad7438da2a7dc9ae8ac6757f198677d  coevo/ablation-run-01-conviction-term/impostor/gen-6/472f93b8716d839ee974c7c1081fc509bad7438da2a7dc9ae8ac6757f198677d/weights.json
70f262799933a481e126b764930110f6641a84055091b51b3edc81f3fb17e4ce  coevo/ablation-run-01-conviction-term/impostor/gen-6/472f93b8716d839ee974c7c1081fc509bad7438da2a7dc9ae8ac6757f198677d/weights.json.sha256
6f0d2960fc19b7cbe1fed2ba8ebca49d490b1173c1ced3d621444f6b9ff428c7  coevo/ablation-run-01-conviction-term/impostor/gen-9/8ac3652a74f81e72440f960a68fa8ae258dd033451d9982592fb48daaa1a7d45/config.json
e3f9ea50a33525f32735c6778d3d0c1bf45cdfd00e661cd7dd7b3bc597c23891  coevo/ablation-run-01-conviction-term/impostor/gen-9/8ac3652a74f81e72440f960a68fa8ae258dd033451d9982592fb48daaa1a7d45/stamp.json
8ac3652a74f81e72440f960a68fa8ae258dd033451d9982592fb48daaa1a7d45  coevo/ablation-run-01-conviction-term/impostor/gen-9/8ac3652a74f81e72440f960a68fa8ae258dd033451d9982592fb48daaa1a7d45/weights.json
dd5402fd45d519d455dd4980a0292ae947006079ec3ced59741ce767de61e4c9  coevo/ablation-run-01-conviction-term/impostor/gen-9/8ac3652a74f81e72440f960a68fa8ae258dd033451d9982592fb48daaa1a7d45/weights.json.sha256
a80bff579b1e19fec84aab50fd963d25f5c10ece406dca447952ae826d82c8ec  coevo/ablation-run-01-conviction-term/impostor/hall_of_fame.json
66022039495c070627b39c644dece4d3b2d6c5742c1c7299e6a1aab56ae5af23  coevo/ablation-run-02-anchor-lambda/campaign-plan.json
94a82ba27d81659260357cdacc66355b2e81be9844e6f6e580237de5c820a01e  coevo/ablation-run-02-anchor-lambda/campaign-rows.jsonl
dce463bc9f1cb4b361b4c3693a4e9612d0401e17aebddf7ec0502ba460c65fc2  coevo/ablation-run-02-anchor-lambda/crew/gen-1/d15a5e12284a3bbac3971c63b9ddd81a4e95316c978afd54d69a0ef206bab8b4/config.json
3fc38256751d47a3d93aec9599655b6700eee67797bbb1d6915642c2873bac72  coevo/ablation-run-02-anchor-lambda/crew/gen-1/d15a5e12284a3bbac3971c63b9ddd81a4e95316c978afd54d69a0ef206bab8b4/stamp.json
d15a5e12284a3bbac3971c63b9ddd81a4e95316c978afd54d69a0ef206bab8b4  coevo/ablation-run-02-anchor-lambda/crew/gen-1/d15a5e12284a3bbac3971c63b9ddd81a4e95316c978afd54d69a0ef206bab8b4/weights.json
8cdae8dd53c9ad203aeaf5386f19f9aa55666e5962dbaa6db47270ba163cbda6  coevo/ablation-run-02-anchor-lambda/crew/gen-1/d15a5e12284a3bbac3971c63b9ddd81a4e95316c978afd54d69a0ef206bab8b4/weights.json.sha256
45c36660fc1c8c167a701169994f195f52405101feee1917942af4e3b49939ae  coevo/ablation-run-02-anchor-lambda/crew/gen-12/53d755165fa0b2ca2a627ac053dd3048e4f584ebcd061331eb68fd33832e05db/config.json
0cbb82c0cf9194dfaa68ec0f6d0b1c4697e4a610a450acced60d91b44e3420d9  coevo/ablation-run-02-anchor-lambda/crew/gen-12/53d755165fa0b2ca2a627ac053dd3048e4f584ebcd061331eb68fd33832e05db/stamp.json
53d755165fa0b2ca2a627ac053dd3048e4f584ebcd061331eb68fd33832e05db  coevo/ablation-run-02-anchor-lambda/crew/gen-12/53d755165fa0b2ca2a627ac053dd3048e4f584ebcd061331eb68fd33832e05db/weights.json
22e3a39f10d29c13be238e34b849de3ad65192e55698d6200c455f1ca9cec27c  coevo/ablation-run-02-anchor-lambda/crew/gen-12/53d755165fa0b2ca2a627ac053dd3048e4f584ebcd061331eb68fd33832e05db/weights.json.sha256
497d346e579eb43d876fbf249c492a6fd4a1072183612cd2bb91f9ffdae3c340  coevo/ablation-run-02-anchor-lambda/crew/gen-2/11bde07828e63d9dc8102ac3621d4a5591e8a44864cfd235aab4c47f5a51e4ea/config.json
43ac978ef059ce31ae9ac3f775aea1ef64a3e5ab4383ba2bec676a5bc9d84aa3  coevo/ablation-run-02-anchor-lambda/crew/gen-2/11bde07828e63d9dc8102ac3621d4a5591e8a44864cfd235aab4c47f5a51e4ea/stamp.json
11bde07828e63d9dc8102ac3621d4a5591e8a44864cfd235aab4c47f5a51e4ea  coevo/ablation-run-02-anchor-lambda/crew/gen-2/11bde07828e63d9dc8102ac3621d4a5591e8a44864cfd235aab4c47f5a51e4ea/weights.json
57475d5b5becbee12c802cdc4cf0d1719cc5635801e0cfb1c73be04962d8beb3  coevo/ablation-run-02-anchor-lambda/crew/gen-2/11bde07828e63d9dc8102ac3621d4a5591e8a44864cfd235aab4c47f5a51e4ea/weights.json.sha256
547ae06f86c1a7ab9602bebb8022fe349c01145e35ecbc03e33fcc45d4fef4f6  coevo/ablation-run-02-anchor-lambda/crew/gen-3/ed9c1d2cc528380fe59fd4ea5969fd7e61e94a229d5eaef959572def55a58921/config.json
a8b7be77d043d8e845efd6c6edb13002976afe490120e27ae2b8601449638497  coevo/ablation-run-02-anchor-lambda/crew/gen-3/ed9c1d2cc528380fe59fd4ea5969fd7e61e94a229d5eaef959572def55a58921/stamp.json
ed9c1d2cc528380fe59fd4ea5969fd7e61e94a229d5eaef959572def55a58921  coevo/ablation-run-02-anchor-lambda/crew/gen-3/ed9c1d2cc528380fe59fd4ea5969fd7e61e94a229d5eaef959572def55a58921/weights.json
63c22ebeb9e67daa9d59685d6a782aa11a9e5748ebb40771bd519ae01706e285  coevo/ablation-run-02-anchor-lambda/crew/gen-3/ed9c1d2cc528380fe59fd4ea5969fd7e61e94a229d5eaef959572def55a58921/weights.json.sha256
5f0bc4a649b51ba19e246b7138bc9ec6c5fa36f0df0730a51306f7177357df59  coevo/ablation-run-02-anchor-lambda/crew/gen-6/1baf6fefec590c1fef6e5570846b0633c4090391b7fb264f9324ab62238c06fa/config.json
026f160488527a7fd0b6f24c43ac15b2b27146221ee51cfc532b2af91693096e  coevo/ablation-run-02-anchor-lambda/crew/gen-6/1baf6fefec590c1fef6e5570846b0633c4090391b7fb264f9324ab62238c06fa/stamp.json
1baf6fefec590c1fef6e5570846b0633c4090391b7fb264f9324ab62238c06fa  coevo/ablation-run-02-anchor-lambda/crew/gen-6/1baf6fefec590c1fef6e5570846b0633c4090391b7fb264f9324ab62238c06fa/weights.json
9b0b97a4ddb044ee9aeecba4f847a370da5b1f426b1de98f4fa6aad94ee8a73b  coevo/ablation-run-02-anchor-lambda/crew/gen-6/1baf6fefec590c1fef6e5570846b0633c4090391b7fb264f9324ab62238c06fa/weights.json.sha256
b9b86bd8cf6d922daf33b24a7ad503fb0c2549971f5b8e8120ba1372a2b260d5  coevo/ablation-run-02-anchor-lambda/crew/gen-7/4ca21b4d8a72233284be1d32f481f019be12998a9dbce3effdc0d026ed71ed36/config.json
4dbf07f7b20dff3cd5974f08f522d8f57f60db0fad2f965763adcfc912c51b0a  coevo/ablation-run-02-anchor-lambda/crew/gen-7/4ca21b4d8a72233284be1d32f481f019be12998a9dbce3effdc0d026ed71ed36/stamp.json
4ca21b4d8a72233284be1d32f481f019be12998a9dbce3effdc0d026ed71ed36  coevo/ablation-run-02-anchor-lambda/crew/gen-7/4ca21b4d8a72233284be1d32f481f019be12998a9dbce3effdc0d026ed71ed36/weights.json
a31f30ef315958befee6c7395fb3bfaa1604b31e7cedc6b6ffb26373872058fa  coevo/ablation-run-02-anchor-lambda/crew/gen-7/4ca21b4d8a72233284be1d32f481f019be12998a9dbce3effdc0d026ed71ed36/weights.json.sha256
24018e653d009a2b32af1b50bd470c9cbe6bf0ae6ba16f6c0d85e202fbfcfd02  coevo/ablation-run-02-anchor-lambda/crew/gen-8/5567bde85e66dbc20b11ce64a4db2b5bde215f4948fd7d103ed76fa64b74f4ec/config.json
e2101846c41a0e3773b08a6a6dbe89a3c25624e3668ca5e6f1cf9acf8c1e76a1  coevo/ablation-run-02-anchor-lambda/crew/gen-8/5567bde85e66dbc20b11ce64a4db2b5bde215f4948fd7d103ed76fa64b74f4ec/stamp.json
5567bde85e66dbc20b11ce64a4db2b5bde215f4948fd7d103ed76fa64b74f4ec  coevo/ablation-run-02-anchor-lambda/crew/gen-8/5567bde85e66dbc20b11ce64a4db2b5bde215f4948fd7d103ed76fa64b74f4ec/weights.json
35fb69c7fa71e41e12c61e4ef198bb9c35f13fbd3c000f5a44719cf4465fc8bc  coevo/ablation-run-02-anchor-lambda/crew/gen-8/5567bde85e66dbc20b11ce64a4db2b5bde215f4948fd7d103ed76fa64b74f4ec/weights.json.sha256
e257e3884b96db33813fe93dbd9ce59fddf698ed6c38af165898e9261b539683  coevo/ablation-run-02-anchor-lambda/crew/gen-9/62cfc1c54c6cdcf652e795879c32abdba8f6c6c6069d9e25b195eea3c7286a95/config.json
47879d82997941b82d72048cfd6fc4d0097eb2054b14dda321369d4d05fd72ae  coevo/ablation-run-02-anchor-lambda/crew/gen-9/62cfc1c54c6cdcf652e795879c32abdba8f6c6c6069d9e25b195eea3c7286a95/stamp.json
62cfc1c54c6cdcf652e795879c32abdba8f6c6c6069d9e25b195eea3c7286a95  coevo/ablation-run-02-anchor-lambda/crew/gen-9/62cfc1c54c6cdcf652e795879c32abdba8f6c6c6069d9e25b195eea3c7286a95/weights.json
5ee3752d14d45fc6d003a44069423b3b6e517b53fdccd5a314bd3aa01d3600b1  coevo/ablation-run-02-anchor-lambda/crew/gen-9/62cfc1c54c6cdcf652e795879c32abdba8f6c6c6069d9e25b195eea3c7286a95/weights.json.sha256
272ffe60da5e19dd7fb540382ecd9c6e992b2748869d32d8dfbae276ab64eb10  coevo/ablation-run-02-anchor-lambda/crew/hall_of_fame.json
35af01d37c0b6f5c1f7f3101ba8cc9e85a1cbea6d5cd4346518a376a7f869d1d  coevo/ablation-run-02-anchor-lambda/impostor/gen-10/62a9e7cd705a0031c0028b7e1273ad8ef11d83ae4471a6ce7b32f467891c7603/config.json
eec9304de460eb28b4bfda73f883faed2f917110e7ee5eef9e4efeb2c8e2733a  coevo/ablation-run-02-anchor-lambda/impostor/gen-10/62a9e7cd705a0031c0028b7e1273ad8ef11d83ae4471a6ce7b32f467891c7603/stamp.json
62a9e7cd705a0031c0028b7e1273ad8ef11d83ae4471a6ce7b32f467891c7603  coevo/ablation-run-02-anchor-lambda/impostor/gen-10/62a9e7cd705a0031c0028b7e1273ad8ef11d83ae4471a6ce7b32f467891c7603/weights.json
b6a767ac50dd262c870f48a5337e3761051c9426ed704a1d63fae6df0a3b4610  coevo/ablation-run-02-anchor-lambda/impostor/gen-10/62a9e7cd705a0031c0028b7e1273ad8ef11d83ae4471a6ce7b32f467891c7603/weights.json.sha256
a9d04a78544fba0b231229f70fb776d58e2eeed4f7c5c2ccb5b0a683ac54f9a6  coevo/ablation-run-02-anchor-lambda/impostor/gen-11/daab294d381dbc9f6ad7ee084f38f3072202eb74c347976129576d699b31ac18/config.json
94f5288b91d817b198a78c79c5f08b0725255f282f30494395386bdd6ccf7746  coevo/ablation-run-02-anchor-lambda/impostor/gen-11/daab294d381dbc9f6ad7ee084f38f3072202eb74c347976129576d699b31ac18/stamp.json
daab294d381dbc9f6ad7ee084f38f3072202eb74c347976129576d699b31ac18  coevo/ablation-run-02-anchor-lambda/impostor/gen-11/daab294d381dbc9f6ad7ee084f38f3072202eb74c347976129576d699b31ac18/weights.json
1400cd79a15641f19e057f32821a2916fc2dc065ecf0925a0af9d50a9edc2520  coevo/ablation-run-02-anchor-lambda/impostor/gen-11/daab294d381dbc9f6ad7ee084f38f3072202eb74c347976129576d699b31ac18/weights.json.sha256
dbee858260f9eca1019fcdc1a3ff4be57afe1105eecc0fe6fe21ba9fc1775f03  coevo/ablation-run-02-anchor-lambda/impostor/gen-12/45647871d25da1487eba41d42a920048ff6b227f43490ce75583ad71468d33de/config.json
1503d448b74ca4dbf1b247891a21919151308c95123bc22a7a1d54d0e613eeb7  coevo/ablation-run-02-anchor-lambda/impostor/gen-12/45647871d25da1487eba41d42a920048ff6b227f43490ce75583ad71468d33de/stamp.json
45647871d25da1487eba41d42a920048ff6b227f43490ce75583ad71468d33de  coevo/ablation-run-02-anchor-lambda/impostor/gen-12/45647871d25da1487eba41d42a920048ff6b227f43490ce75583ad71468d33de/weights.json
ee1deb1b784abcae39349fd759ef14b2d47045ae5c9bde234bfd6412e0bf607f  coevo/ablation-run-02-anchor-lambda/impostor/gen-12/45647871d25da1487eba41d42a920048ff6b227f43490ce75583ad71468d33de/weights.json.sha256
2fbdfed0f6e5d0cc3dc922303165724954b8bc15359ce3e0515c0844c4a4216b  coevo/ablation-run-02-anchor-lambda/impostor/gen-3/ea4bc955dfe0beb8f82663d659e6c990083cebb26a1dab9600c6b68b7783d79f/config.json
b48245ccfa2c26621504e3829f158d08dd40fb566703399a0035c67538650a56  coevo/ablation-run-02-anchor-lambda/impostor/gen-3/ea4bc955dfe0beb8f82663d659e6c990083cebb26a1dab9600c6b68b7783d79f/stamp.json
ea4bc955dfe0beb8f82663d659e6c990083cebb26a1dab9600c6b68b7783d79f  coevo/ablation-run-02-anchor-lambda/impostor/gen-3/ea4bc955dfe0beb8f82663d659e6c990083cebb26a1dab9600c6b68b7783d79f/weights.json
4b4b8f5a26a8a2ac682f6bfd6970d9ec44b682335c848ae7b1254f3032c14be1  coevo/ablation-run-02-anchor-lambda/impostor/gen-3/ea4bc955dfe0beb8f82663d659e6c990083cebb26a1dab9600c6b68b7783d79f/weights.json.sha256
8c49b124c7a74515e44a39b6ce1227463abae35b11d0d5ab5431d25610813c53  coevo/ablation-run-02-anchor-lambda/impostor/gen-4/b83c09fd3eb367f0c34b7fa780431d04a8ea7de75910d4be08f9e3a44925cda0/config.json
0553a7953a8dc688efa1822105d772f05b22709dc60c26216339692a568d4f41  coevo/ablation-run-02-anchor-lambda/impostor/gen-4/b83c09fd3eb367f0c34b7fa780431d04a8ea7de75910d4be08f9e3a44925cda0/stamp.json
b83c09fd3eb367f0c34b7fa780431d04a8ea7de75910d4be08f9e3a44925cda0  coevo/ablation-run-02-anchor-lambda/impostor/gen-4/b83c09fd3eb367f0c34b7fa780431d04a8ea7de75910d4be08f9e3a44925cda0/weights.json
ffc7a62253a994e5e08843118c93d41815c0749d1ee9f7ff5806dae0ee8fc43b  coevo/ablation-run-02-anchor-lambda/impostor/gen-4/b83c09fd3eb367f0c34b7fa780431d04a8ea7de75910d4be08f9e3a44925cda0/weights.json.sha256
29863dfae4a6dde324f903a94e4513d6032525d11699863f97b242e1158dc3f4  coevo/ablation-run-02-anchor-lambda/impostor/gen-5/1bdf85c5d64a894efdb896eb276d2c97b4485fc619c474a787468020092790e3/config.json
4b7eba9c76adab503f7d6537da9ab7fdb2e38d6c283072ede9102ea1a3017479  coevo/ablation-run-02-anchor-lambda/impostor/gen-5/1bdf85c5d64a894efdb896eb276d2c97b4485fc619c474a787468020092790e3/stamp.json
1bdf85c5d64a894efdb896eb276d2c97b4485fc619c474a787468020092790e3  coevo/ablation-run-02-anchor-lambda/impostor/gen-5/1bdf85c5d64a894efdb896eb276d2c97b4485fc619c474a787468020092790e3/weights.json
f06728e2acdc7791512e4d4845e31aa1d28ad38bea76889aef40f1c18a00686c  coevo/ablation-run-02-anchor-lambda/impostor/gen-5/1bdf85c5d64a894efdb896eb276d2c97b4485fc619c474a787468020092790e3/weights.json.sha256
d281262008ac69a2493e1638f1a30de3ffcb8e539dd9725263211af277f32d2a  coevo/ablation-run-02-anchor-lambda/impostor/gen-6/054254ffd70785db1b0b075a0976c8aa21c65fd38fa002f74fe553558b850c11/config.json
e055c8d0ed17b8a9abc95467998455358236669252d0750c20cae0948ece1fb0  coevo/ablation-run-02-anchor-lambda/impostor/gen-6/054254ffd70785db1b0b075a0976c8aa21c65fd38fa002f74fe553558b850c11/stamp.json
054254ffd70785db1b0b075a0976c8aa21c65fd38fa002f74fe553558b850c11  coevo/ablation-run-02-anchor-lambda/impostor/gen-6/054254ffd70785db1b0b075a0976c8aa21c65fd38fa002f74fe553558b850c11/weights.json
fcf11fb821d2610d0cc2c6b288b2b8554c65ae059e5180871dbbea17126c80b0  coevo/ablation-run-02-anchor-lambda/impostor/gen-6/054254ffd70785db1b0b075a0976c8aa21c65fd38fa002f74fe553558b850c11/weights.json.sha256
fce2b6a2bdc9eb32172568500bf44b92f228e95f1ae8bf12e4ac91826f00a4a1  coevo/ablation-run-02-anchor-lambda/impostor/hall_of_fame.json
d263e71949ea6d9d354a0a6cb1c26420431e1b963f40402c2a827eeaf753fbfc  coevo/ablation-run-04-encoder-v3/campaign-plan.json
052072b0ecacfcc92062002212a01fbafe5dde11edec00c94cbe394899184247  coevo/ablation-run-04-encoder-v3/campaign-rows.jsonl
f2bbc4e499eebd8e7407dfe2398240b8ce0a032ca872f1548ebec37a94875c9e  coevo/ablation-run-04-encoder-v3/crew/gen-1/e3b91354e6c48a390c21a5cf01b7a2845055c14bfe4050391983ffd8e74608de/config.json
e15b62076ca950ae450fa55f70211c3d409be71cd1a6b37749e247984ce4f5af  coevo/ablation-run-04-encoder-v3/crew/gen-1/e3b91354e6c48a390c21a5cf01b7a2845055c14bfe4050391983ffd8e74608de/stamp.json
e3b91354e6c48a390c21a5cf01b7a2845055c14bfe4050391983ffd8e74608de  coevo/ablation-run-04-encoder-v3/crew/gen-1/e3b91354e6c48a390c21a5cf01b7a2845055c14bfe4050391983ffd8e74608de/weights.json
fb56ec0679f9436dca1a52b7c2febfe0fac923d73c29d3b1d8ac6a363f3c9fc3  coevo/ablation-run-04-encoder-v3/crew/gen-1/e3b91354e6c48a390c21a5cf01b7a2845055c14bfe4050391983ffd8e74608de/weights.json.sha256
d6ac4f465db34a7bb802050382ae81228984077cd535acf733802a222579ecdb  coevo/ablation-run-04-encoder-v3/crew/gen-12/d29181092aae07a49b14b90720f317cfb4c19a31af7d53dc524b1a191fcc2bdc/config.json
bcdfc986b13ab87f2609f0bb07c8b9ed3719400bc465df054458558f3aec293d  coevo/ablation-run-04-encoder-v3/crew/gen-12/d29181092aae07a49b14b90720f317cfb4c19a31af7d53dc524b1a191fcc2bdc/stamp.json
d29181092aae07a49b14b90720f317cfb4c19a31af7d53dc524b1a191fcc2bdc  coevo/ablation-run-04-encoder-v3/crew/gen-12/d29181092aae07a49b14b90720f317cfb4c19a31af7d53dc524b1a191fcc2bdc/weights.json
3f830a18b3dedde462b0615669ec06e121485dff7f4a6e6ee3642c998ea08642  coevo/ablation-run-04-encoder-v3/crew/gen-12/d29181092aae07a49b14b90720f317cfb4c19a31af7d53dc524b1a191fcc2bdc/weights.json.sha256
7b9f07826b6d88da414e0fc783135d7c46859a52c983df7be18f546817e4f3fa  coevo/ablation-run-04-encoder-v3/crew/gen-2/c61d0856951ef0b783ee216aa1eef6261f564a6c1be1ed72123d0ce5ace82562/config.json
0c6e294a58d4f04b3859006350c7e427f54aadbb4149cf7d605c7fd37200e8bc  coevo/ablation-run-04-encoder-v3/crew/gen-2/c61d0856951ef0b783ee216aa1eef6261f564a6c1be1ed72123d0ce5ace82562/stamp.json
c61d0856951ef0b783ee216aa1eef6261f564a6c1be1ed72123d0ce5ace82562  coevo/ablation-run-04-encoder-v3/crew/gen-2/c61d0856951ef0b783ee216aa1eef6261f564a6c1be1ed72123d0ce5ace82562/weights.json
1c737c233f4a0a089002c612a156028148d9c4c17a1f5e517edece9a2e34af9e  coevo/ablation-run-04-encoder-v3/crew/gen-2/c61d0856951ef0b783ee216aa1eef6261f564a6c1be1ed72123d0ce5ace82562/weights.json.sha256
3fb16569f1efd15f3f9e4e628301adf0d22916ded5bd911a6d4f04a595b93e62  coevo/ablation-run-04-encoder-v3/crew/gen-3/36befc4b0671eea151f52a8034075196e3284c392921e831e921db8b79ff4f03/config.json
650fe0a7ceadfe4bfda53f8d3d693f7517f1df3232284223dd4cde16341cf2f2  coevo/ablation-run-04-encoder-v3/crew/gen-3/36befc4b0671eea151f52a8034075196e3284c392921e831e921db8b79ff4f03/stamp.json
36befc4b0671eea151f52a8034075196e3284c392921e831e921db8b79ff4f03  coevo/ablation-run-04-encoder-v3/crew/gen-3/36befc4b0671eea151f52a8034075196e3284c392921e831e921db8b79ff4f03/weights.json
1962eee474359183601945fd36b00efcfba2db482d9d036b591856cbd6c9b987  coevo/ablation-run-04-encoder-v3/crew/gen-3/36befc4b0671eea151f52a8034075196e3284c392921e831e921db8b79ff4f03/weights.json.sha256
bcc9f993a74c2e791e800b106ef6673701f17c74317e6c13da895b3305b47e7c  coevo/ablation-run-04-encoder-v3/crew/gen-6/04e68454218549afbcd4987b1aaaca3006eb87cfdc194f9515bfe32c8ef7a6af/config.json
1d67a5abc50050e77cb424d53ccffbc1d9c7d393ca7f5e625322cc36253170ba  coevo/ablation-run-04-encoder-v3/crew/gen-6/04e68454218549afbcd4987b1aaaca3006eb87cfdc194f9515bfe32c8ef7a6af/stamp.json
04e68454218549afbcd4987b1aaaca3006eb87cfdc194f9515bfe32c8ef7a6af  coevo/ablation-run-04-encoder-v3/crew/gen-6/04e68454218549afbcd4987b1aaaca3006eb87cfdc194f9515bfe32c8ef7a6af/weights.json
b19df42b33827605a2531ecbb4bbea545f9b97273fed65b89e0dc0c32d411626  coevo/ablation-run-04-encoder-v3/crew/gen-6/04e68454218549afbcd4987b1aaaca3006eb87cfdc194f9515bfe32c8ef7a6af/weights.json.sha256
9a999de9c35156ce867abd5322036e30d22e84cee3b56a6f3ccd1533202328e0  coevo/ablation-run-04-encoder-v3/crew/hall_of_fame.json
817db35a0a75ee4d94bdc7d38bc69278be627d41e08ed8920a163b21f5c9afc4  coevo/ablation-run-04-encoder-v3/impostor/gen-10/9b89f2c8f980411bc0132c60af86f258ebe62a1853c1ccec56deb63e22807940/config.json
85c167af35791bd66ec021ef02d67be61372bc2312409eee4a9cd09b4486d146  coevo/ablation-run-04-encoder-v3/impostor/gen-10/9b89f2c8f980411bc0132c60af86f258ebe62a1853c1ccec56deb63e22807940/stamp.json
9b89f2c8f980411bc0132c60af86f258ebe62a1853c1ccec56deb63e22807940  coevo/ablation-run-04-encoder-v3/impostor/gen-10/9b89f2c8f980411bc0132c60af86f258ebe62a1853c1ccec56deb63e22807940/weights.json
b031e31c42f1bbf0536efa27201106a93d66327961d907779c38324f4c7ebfe8  coevo/ablation-run-04-encoder-v3/impostor/gen-10/9b89f2c8f980411bc0132c60af86f258ebe62a1853c1ccec56deb63e22807940/weights.json.sha256
e162af1b81fa5f041982ab273a52b07afbcb6f401c0b73dba5f51118781ab235  coevo/ablation-run-04-encoder-v3/impostor/gen-11/953bb5f600acfba4cfc73babb571f33f6edaefd3039386cf0d27b88dd6dfd205/config.json
7412e834b30b268bca271244fcfc8466d5267efd7456b315edaa352abd9b3ba4  coevo/ablation-run-04-encoder-v3/impostor/gen-11/953bb5f600acfba4cfc73babb571f33f6edaefd3039386cf0d27b88dd6dfd205/stamp.json
953bb5f600acfba4cfc73babb571f33f6edaefd3039386cf0d27b88dd6dfd205  coevo/ablation-run-04-encoder-v3/impostor/gen-11/953bb5f600acfba4cfc73babb571f33f6edaefd3039386cf0d27b88dd6dfd205/weights.json
3ab84f6340b9807c44e176d42e50381ee262b190005abf47d4d580ebcb40742c  coevo/ablation-run-04-encoder-v3/impostor/gen-11/953bb5f600acfba4cfc73babb571f33f6edaefd3039386cf0d27b88dd6dfd205/weights.json.sha256
66fffa46fbe2666dbe3454757ddcc9c80806d49993e1e59f7306bcebda4ee27d  coevo/ablation-run-04-encoder-v3/impostor/gen-12/a11c80232a67c2fbc2ad55d1d1de70730edff851fa85d821ab13f67c10aa777f/config.json
91cda4ea7b8aab6d7d2df29173ad7c372bc93da0fb9a773c23a281c27f028d8d  coevo/ablation-run-04-encoder-v3/impostor/gen-12/a11c80232a67c2fbc2ad55d1d1de70730edff851fa85d821ab13f67c10aa777f/stamp.json
a11c80232a67c2fbc2ad55d1d1de70730edff851fa85d821ab13f67c10aa777f  coevo/ablation-run-04-encoder-v3/impostor/gen-12/a11c80232a67c2fbc2ad55d1d1de70730edff851fa85d821ab13f67c10aa777f/weights.json
4052cf152e85d4ef47b8f93768898b7808fa48d96c3c93bc788fbe2a8c0598ba  coevo/ablation-run-04-encoder-v3/impostor/gen-12/a11c80232a67c2fbc2ad55d1d1de70730edff851fa85d821ab13f67c10aa777f/weights.json.sha256
e5a2d076ca94324e52fbf5db65a4565f05f4ecd49c9f0958d820892e882fe41a  coevo/ablation-run-04-encoder-v3/impostor/gen-3/a4076d294a32e81cbc1b276a10c0bd3a73b7d4cc053bcae74ac9837ab14c547f/config.json
bd183dca4b0d98e4dfde8136094f2799c10b68434630cbfa4f2257d41c8dab5b  coevo/ablation-run-04-encoder-v3/impostor/gen-3/a4076d294a32e81cbc1b276a10c0bd3a73b7d4cc053bcae74ac9837ab14c547f/stamp.json
a4076d294a32e81cbc1b276a10c0bd3a73b7d4cc053bcae74ac9837ab14c547f  coevo/ablation-run-04-encoder-v3/impostor/gen-3/a4076d294a32e81cbc1b276a10c0bd3a73b7d4cc053bcae74ac9837ab14c547f/weights.json
66c850b4a823539784fae1a4c272f1baeda7fc5c9df61ffb6665d23424f795d6  coevo/ablation-run-04-encoder-v3/impostor/gen-3/a4076d294a32e81cbc1b276a10c0bd3a73b7d4cc053bcae74ac9837ab14c547f/weights.json.sha256
680751cd306167993203a9f4df800af66665cdd15277a32b4d702c8dda7c497f  coevo/ablation-run-04-encoder-v3/impostor/gen-6/6649c1b360b9fe4d19a5ea9e2b8d3fabf87e2da9f4dffadcf5305ef07d4ab333/config.json
9b523cd1317afb8cbd84af3aadaa891dbc9a9b7f6354a8a65a87545cb6bf82a5  coevo/ablation-run-04-encoder-v3/impostor/gen-6/6649c1b360b9fe4d19a5ea9e2b8d3fabf87e2da9f4dffadcf5305ef07d4ab333/stamp.json
6649c1b360b9fe4d19a5ea9e2b8d3fabf87e2da9f4dffadcf5305ef07d4ab333  coevo/ablation-run-04-encoder-v3/impostor/gen-6/6649c1b360b9fe4d19a5ea9e2b8d3fabf87e2da9f4dffadcf5305ef07d4ab333/weights.json
73e8955d397b69c6b798095ecdf9b200a0587e9fe1ea8121f41cbea3f88e95a2  coevo/ablation-run-04-encoder-v3/impostor/gen-6/6649c1b360b9fe4d19a5ea9e2b8d3fabf87e2da9f4dffadcf5305ef07d4ab333/weights.json.sha256
6c91d4cb0b93955bd625c6c93de94e32b5d757a45e03b2236af0d5b4e16b05a1  coevo/ablation-run-04-encoder-v3/impostor/gen-9/bfa517676dd433173b752485865a98beb8cca3987de264856271a24bb1865705/config.json
c058e712d91126f83c5143126cd2a034040971f2d29b271636e9e6e05f874452  coevo/ablation-run-04-encoder-v3/impostor/gen-9/bfa517676dd433173b752485865a98beb8cca3987de264856271a24bb1865705/stamp.json
bfa517676dd433173b752485865a98beb8cca3987de264856271a24bb1865705  coevo/ablation-run-04-encoder-v3/impostor/gen-9/bfa517676dd433173b752485865a98beb8cca3987de264856271a24bb1865705/weights.json
392dd3c7478c14c7319e9a9cc1584ba2de49d84f760abc25369729b70added62  coevo/ablation-run-04-encoder-v3/impostor/gen-9/bfa517676dd433173b752485865a98beb8cca3987de264856271a24bb1865705/weights.json.sha256
f51a4692ae6034dc67f8d5c13d81922db747cdca0608dbcb5416ffd1b1d1e85c  coevo/ablation-run-04-encoder-v3/impostor/hall_of_fame.json
66022039495c070627b39c644dece4d3b2d6c5742c1c7299e6a1aab56ae5af23  coevo/ablation-run-c1-conviction-term/campaign-plan.json
435707472f9a98cdfc91288fbc88289823aecc82828634b90435213f9f187ace  coevo/ablation-run-c1-conviction-term/campaign-rows.jsonl
597f5f9998d5f9dfd40fd3ef2427e7291abaf9bf32488342e6f869f17076d6d9  coevo/ablation-run-c1-conviction-term/crew/gen-10/b73fa94210f6d814b329737e3454b024ccee41eb0156dee4bc09e55987c88dad/config.json
2b11e7b2231bb0b74a68a15de52fb1ac60a2c6fcafd4300b9e51aaf523f64573  coevo/ablation-run-c1-conviction-term/crew/gen-10/b73fa94210f6d814b329737e3454b024ccee41eb0156dee4bc09e55987c88dad/stamp.json
b73fa94210f6d814b329737e3454b024ccee41eb0156dee4bc09e55987c88dad  coevo/ablation-run-c1-conviction-term/crew/gen-10/b73fa94210f6d814b329737e3454b024ccee41eb0156dee4bc09e55987c88dad/weights.json
aa66a1463bcdec430b47b08bc80b16af48216f038e743355be82652148ee51e5  coevo/ablation-run-c1-conviction-term/crew/gen-10/b73fa94210f6d814b329737e3454b024ccee41eb0156dee4bc09e55987c88dad/weights.json.sha256
b7fd4e461608fbeea200d2ecdbb4cd87be398fc8d85eecdb642b7093c860a8bc  coevo/ablation-run-c1-conviction-term/crew/gen-11/039be4e25f20f85fe9b546922c0e7d76bb4549476fb5fa469b30e42314620700/config.json
49aa9f06b462f125f9e5a849f7a9eaa4abefa97cdcb27e21a4db1bab548fe8b1  coevo/ablation-run-c1-conviction-term/crew/gen-11/039be4e25f20f85fe9b546922c0e7d76bb4549476fb5fa469b30e42314620700/stamp.json
039be4e25f20f85fe9b546922c0e7d76bb4549476fb5fa469b30e42314620700  coevo/ablation-run-c1-conviction-term/crew/gen-11/039be4e25f20f85fe9b546922c0e7d76bb4549476fb5fa469b30e42314620700/weights.json
0a2418cfb49298674ad9d0795dc2231850393aa15fff220c3e2f5d55f0d51c03  coevo/ablation-run-c1-conviction-term/crew/gen-11/039be4e25f20f85fe9b546922c0e7d76bb4549476fb5fa469b30e42314620700/weights.json.sha256
bd4e44ddd06cfecea4d793b59ec7fdc6cedd7217e681a91bee380c42a2a31903  coevo/ablation-run-c1-conviction-term/crew/gen-12/9a6b3cea33b73d036eb245d7504936022558b07325bce4e928cc0b5e99ed9dbc/config.json
73a580627598e2ad0d57245f78f8e26c1dff7e6ba5fedaf8d63673e78b6adb53  coevo/ablation-run-c1-conviction-term/crew/gen-12/9a6b3cea33b73d036eb245d7504936022558b07325bce4e928cc0b5e99ed9dbc/stamp.json
9a6b3cea33b73d036eb245d7504936022558b07325bce4e928cc0b5e99ed9dbc  coevo/ablation-run-c1-conviction-term/crew/gen-12/9a6b3cea33b73d036eb245d7504936022558b07325bce4e928cc0b5e99ed9dbc/weights.json
a1766cf8ad896b37a5a0d706ee6b5f75693b01e02172a6d1c4038a852cef388e  coevo/ablation-run-c1-conviction-term/crew/gen-12/9a6b3cea33b73d036eb245d7504936022558b07325bce4e928cc0b5e99ed9dbc/weights.json.sha256
0a26de8684ebf3f3c1306c3d56702f986697e6c630994f3c39442ebcc809b130  coevo/ablation-run-c1-conviction-term/crew/gen-3/72adb41c9286d61d5a81ea4ed2bd347c0d7da52ad89ae6497f1dcbf2237ca4e5/config.json
654809d6565e6074c4e27d2fe0cb16511dde39d469acb5feabf5c8afb05988a3  coevo/ablation-run-c1-conviction-term/crew/gen-3/72adb41c9286d61d5a81ea4ed2bd347c0d7da52ad89ae6497f1dcbf2237ca4e5/stamp.json
72adb41c9286d61d5a81ea4ed2bd347c0d7da52ad89ae6497f1dcbf2237ca4e5  coevo/ablation-run-c1-conviction-term/crew/gen-3/72adb41c9286d61d5a81ea4ed2bd347c0d7da52ad89ae6497f1dcbf2237ca4e5/weights.json
e937d76813ced95a20e0e81fecdd650ebf774972eca5269d1e84cdbbbe385715  coevo/ablation-run-c1-conviction-term/crew/gen-3/72adb41c9286d61d5a81ea4ed2bd347c0d7da52ad89ae6497f1dcbf2237ca4e5/weights.json.sha256
989b18708ff0b8925350b523ec00a4c120d529b406325613146b5becfb8183f5  coevo/ablation-run-c1-conviction-term/crew/gen-4/26636fab45e3025d54f8948db12f0a08fea9dec73e21876e4031540845cb3bbc/config.json
57606a99eaa3b4b9d432593dc0d88bc5616968a19694c079105371267d76cc74  coevo/ablation-run-c1-conviction-term/crew/gen-4/26636fab45e3025d54f8948db12f0a08fea9dec73e21876e4031540845cb3bbc/stamp.json
26636fab45e3025d54f8948db12f0a08fea9dec73e21876e4031540845cb3bbc  coevo/ablation-run-c1-conviction-term/crew/gen-4/26636fab45e3025d54f8948db12f0a08fea9dec73e21876e4031540845cb3bbc/weights.json
be613d1d026ae2b268144e580653ee93503da9983e028765f2c571afb1ea6adf  coevo/ablation-run-c1-conviction-term/crew/gen-4/26636fab45e3025d54f8948db12f0a08fea9dec73e21876e4031540845cb3bbc/weights.json.sha256
99e79c745ed91deca58772f6468516e2fe04845b80296271cc798cc33316e15e  coevo/ablation-run-c1-conviction-term/crew/gen-5/d007fc37a84d1f74d66e1d26b901f944dfe8b2874bdc26859ee15ef5ebee20e1/config.json
c585164bb5965fec66e73eacbac7dcc668d01969cc40a2b7037896feca9ef4d1  coevo/ablation-run-c1-conviction-term/crew/gen-5/d007fc37a84d1f74d66e1d26b901f944dfe8b2874bdc26859ee15ef5ebee20e1/stamp.json
d007fc37a84d1f74d66e1d26b901f944dfe8b2874bdc26859ee15ef5ebee20e1  coevo/ablation-run-c1-conviction-term/crew/gen-5/d007fc37a84d1f74d66e1d26b901f944dfe8b2874bdc26859ee15ef5ebee20e1/weights.json
df010be34bd9a6bde613a5c526f91f700fcb58c8f889cefedb87803f5e3277f6  coevo/ablation-run-c1-conviction-term/crew/gen-5/d007fc37a84d1f74d66e1d26b901f944dfe8b2874bdc26859ee15ef5ebee20e1/weights.json.sha256
153c4a12003a6ca127d768f5387903d15c0328a3245a78f42ed11e50ff5acc3e  coevo/ablation-run-c1-conviction-term/crew/gen-6/2530b11d4b5a6fe88f60f897ec8e7a04a29255ae882d014c771779172d8b2a6d/config.json
3da745c602d76391449944bce1f5f7a6d77352c6b9901c79bf5f4aac05946f95  coevo/ablation-run-c1-conviction-term/crew/gen-6/2530b11d4b5a6fe88f60f897ec8e7a04a29255ae882d014c771779172d8b2a6d/stamp.json
2530b11d4b5a6fe88f60f897ec8e7a04a29255ae882d014c771779172d8b2a6d  coevo/ablation-run-c1-conviction-term/crew/gen-6/2530b11d4b5a6fe88f60f897ec8e7a04a29255ae882d014c771779172d8b2a6d/weights.json
5b7cb77a415c1fdf4abfabe09ea6ee3c8851909e5ffac644265ccab1bc00d553  coevo/ablation-run-c1-conviction-term/crew/gen-6/2530b11d4b5a6fe88f60f897ec8e7a04a29255ae882d014c771779172d8b2a6d/weights.json.sha256
fd9988bf45d2b941259d27b04bbb137941438d8d820e357b1a86ad240312f574  coevo/ablation-run-c1-conviction-term/crew/gen-9/a0ab72e26d40e289fc64c719d079e070ece960956d73bf4eae230f7c8fa7fbd3/config.json
94a0beea198329c6226f1a23fa564dd5d8a73f41b5d3ca0c898ebf528ce7ff6c  coevo/ablation-run-c1-conviction-term/crew/gen-9/a0ab72e26d40e289fc64c719d079e070ece960956d73bf4eae230f7c8fa7fbd3/stamp.json
a0ab72e26d40e289fc64c719d079e070ece960956d73bf4eae230f7c8fa7fbd3  coevo/ablation-run-c1-conviction-term/crew/gen-9/a0ab72e26d40e289fc64c719d079e070ece960956d73bf4eae230f7c8fa7fbd3/weights.json
25c602c11f5affbb5cd69d64b4dd0a6d1193593a9594ede15065bcb45df91f85  coevo/ablation-run-c1-conviction-term/crew/gen-9/a0ab72e26d40e289fc64c719d079e070ece960956d73bf4eae230f7c8fa7fbd3/weights.json.sha256
1e10ef7458dc63cba4ecbe452cef56e4729c4ade8272e2594426d160914ab431  coevo/ablation-run-c1-conviction-term/crew/hall_of_fame.json
cb82c68f3e03eae261124cfd2a13af9fd65733138b4a72bef45d6e5933faec81  coevo/ablation-run-c1-conviction-term/impostor/gen-1/d8afecd74e2a8aa048c561e569409d5e6a9c0c0d77eb97fca4997b198f85a92f/config.json
7b6192c2c488ca9e1b66b75072e6e55fdda5456f78285522d44f282976eb1e64  coevo/ablation-run-c1-conviction-term/impostor/gen-1/d8afecd74e2a8aa048c561e569409d5e6a9c0c0d77eb97fca4997b198f85a92f/stamp.json
d8afecd74e2a8aa048c561e569409d5e6a9c0c0d77eb97fca4997b198f85a92f  coevo/ablation-run-c1-conviction-term/impostor/gen-1/d8afecd74e2a8aa048c561e569409d5e6a9c0c0d77eb97fca4997b198f85a92f/weights.json
c0f944ca29706dd7803df1423521317c4e4fb9bbfa19c444fae5e6280dedaf8a  coevo/ablation-run-c1-conviction-term/impostor/gen-1/d8afecd74e2a8aa048c561e569409d5e6a9c0c0d77eb97fca4997b198f85a92f/weights.json.sha256
6ea33f6f4bbe6e8313a785bad8a7ca25401da30140ca513e70a1bcfb5ba6c2b0  coevo/ablation-run-c1-conviction-term/impostor/gen-2/00716018dd5e9b90357183e47b3647722a75041218a9002fac80c8c2b6c0b6fd/config.json
8383cda7ef9c1cf25672a34217dd8597452f536acf3976c419dbc5f93253790a  coevo/ablation-run-c1-conviction-term/impostor/gen-2/00716018dd5e9b90357183e47b3647722a75041218a9002fac80c8c2b6c0b6fd/stamp.json
00716018dd5e9b90357183e47b3647722a75041218a9002fac80c8c2b6c0b6fd  coevo/ablation-run-c1-conviction-term/impostor/gen-2/00716018dd5e9b90357183e47b3647722a75041218a9002fac80c8c2b6c0b6fd/weights.json
636b769dffb2111abc734c0a187d26250c51dd38336b476ead2141ad6969c665  coevo/ablation-run-c1-conviction-term/impostor/gen-2/00716018dd5e9b90357183e47b3647722a75041218a9002fac80c8c2b6c0b6fd/weights.json.sha256
3e662995a12a7d682c0e4229387d03e6362554716342a1e9f02cbd95870a5905  coevo/ablation-run-c1-conviction-term/impostor/gen-3/5faa43e93122eb95060eaf2153486e7775adc1a2569e18c7e4236268b3f67056/config.json
f5a2279eca6f3d93eea07900ae19f9761a0114eb20679195803472ffab2401e5  coevo/ablation-run-c1-conviction-term/impostor/gen-3/5faa43e93122eb95060eaf2153486e7775adc1a2569e18c7e4236268b3f67056/stamp.json
5faa43e93122eb95060eaf2153486e7775adc1a2569e18c7e4236268b3f67056  coevo/ablation-run-c1-conviction-term/impostor/gen-3/5faa43e93122eb95060eaf2153486e7775adc1a2569e18c7e4236268b3f67056/weights.json
222d70fcc3dfa1051a0150473425fc8cc646faa50aad8ddb04e2c94ab56f634d  coevo/ablation-run-c1-conviction-term/impostor/gen-3/5faa43e93122eb95060eaf2153486e7775adc1a2569e18c7e4236268b3f67056/weights.json.sha256
afca9848290d26a457a6cb619d325d1d6b2d807b223d2577504e6cdfa9fc6960  coevo/ablation-run-c1-conviction-term/impostor/gen-6/7ddc3709188f2bb335ef4f19542e72be9154164c04a071729f573c27c9291e02/config.json
b6c20b5c880b0d7b6294a435c5a4c98395e0bfa7b8d53fedc2b2cd95c21b0387  coevo/ablation-run-c1-conviction-term/impostor/gen-6/7ddc3709188f2bb335ef4f19542e72be9154164c04a071729f573c27c9291e02/stamp.json
7ddc3709188f2bb335ef4f19542e72be9154164c04a071729f573c27c9291e02  coevo/ablation-run-c1-conviction-term/impostor/gen-6/7ddc3709188f2bb335ef4f19542e72be9154164c04a071729f573c27c9291e02/weights.json
4d5d592516a83d3b240f605a3da2e9cf75860c1dff1dd5f5e3e4ceef7fe73335  coevo/ablation-run-c1-conviction-term/impostor/gen-6/7ddc3709188f2bb335ef4f19542e72be9154164c04a071729f573c27c9291e02/weights.json.sha256
bfe98bd99edc7d619a01a7b31fe2e5628755792913898095c121522a4c88b257  coevo/ablation-run-c1-conviction-term/impostor/gen-7/8bd92b7e4f5c3dbf59a81648f64e8f8485a4578c6410f7d7c12161c117878963/config.json
892e1f423a3005f1beedea4c761c6980bc0328046b7f85671b5680588a73793d  coevo/ablation-run-c1-conviction-term/impostor/gen-7/8bd92b7e4f5c3dbf59a81648f64e8f8485a4578c6410f7d7c12161c117878963/stamp.json
8bd92b7e4f5c3dbf59a81648f64e8f8485a4578c6410f7d7c12161c117878963  coevo/ablation-run-c1-conviction-term/impostor/gen-7/8bd92b7e4f5c3dbf59a81648f64e8f8485a4578c6410f7d7c12161c117878963/weights.json
b6486bc2da405c22d75bb96d9c81eda2345bf0f15885ef16bf0636fa10b902fa  coevo/ablation-run-c1-conviction-term/impostor/gen-7/8bd92b7e4f5c3dbf59a81648f64e8f8485a4578c6410f7d7c12161c117878963/weights.json.sha256
b1e9390823e210cb31cbdd71dc177a8a929bf15b6642e4de576c84a39e75cd24  coevo/ablation-run-c1-conviction-term/impostor/gen-8/ec0b220e391512d87c043f9dc0ec5daeaf0b74258f6fc108017ad5088efa05a0/config.json
73a468d0072914366f7b8d506150f2cdd370b25975b19119f1b9fbde4e9015bd  coevo/ablation-run-c1-conviction-term/impostor/gen-8/ec0b220e391512d87c043f9dc0ec5daeaf0b74258f6fc108017ad5088efa05a0/stamp.json
ec0b220e391512d87c043f9dc0ec5daeaf0b74258f6fc108017ad5088efa05a0  coevo/ablation-run-c1-conviction-term/impostor/gen-8/ec0b220e391512d87c043f9dc0ec5daeaf0b74258f6fc108017ad5088efa05a0/weights.json
950920df9971debd99404a24f29700e7663df521832194a4bc7345ef99a1c011  coevo/ablation-run-c1-conviction-term/impostor/gen-8/ec0b220e391512d87c043f9dc0ec5daeaf0b74258f6fc108017ad5088efa05a0/weights.json.sha256
0b0974c3dcb86b473a721e70a879ffc9e424c6257a4be6dcde457a57de43a51d  coevo/ablation-run-c1-conviction-term/impostor/hall_of_fame.json
66022039495c070627b39c644dece4d3b2d6c5742c1c7299e6a1aab56ae5af23  coevo/ablation-run-c2-conviction-term/campaign-plan.json
1d0668d15c6635b2098b04054e6096d93f3f4dc669b28236e548b0ad4e324c03  coevo/ablation-run-c2-conviction-term/campaign-rows.jsonl
89ee0ea45153a1d9f1f05f1e270d7e549b36d6a273a29092090d8ef32f22cbb0  coevo/ablation-run-c2-conviction-term/crew/gen-10/bff79fc8dfe1e0701fc9fba7266e93626ca47fbd6ccaf258e21b5c0875334ce7/config.json
08fde7ee4f02607a09c5442fb2d4dc8be6365c3c1594bc47ff3caaf802d52701  coevo/ablation-run-c2-conviction-term/crew/gen-10/bff79fc8dfe1e0701fc9fba7266e93626ca47fbd6ccaf258e21b5c0875334ce7/stamp.json
bff79fc8dfe1e0701fc9fba7266e93626ca47fbd6ccaf258e21b5c0875334ce7  coevo/ablation-run-c2-conviction-term/crew/gen-10/bff79fc8dfe1e0701fc9fba7266e93626ca47fbd6ccaf258e21b5c0875334ce7/weights.json
6bcbb73d6422c6678bebbe7421e9f5440d5dfbda47cb9442818a761dace20771  coevo/ablation-run-c2-conviction-term/crew/gen-10/bff79fc8dfe1e0701fc9fba7266e93626ca47fbd6ccaf258e21b5c0875334ce7/weights.json.sha256
861f5ce61d08a226fbb8dc0b39dfe8627c371abbaaec8a8ed3dde9ab32fb85cd  coevo/ablation-run-c2-conviction-term/crew/gen-11/51a784e46a9ab125b6f9131114d6a46907b9f09f79d23b81ee7f9756bd31c8c2/config.json
4db8da9ad012345196c46f2fcbd3ce7d0dc72b4ddc0306eedea38cb642a00688  coevo/ablation-run-c2-conviction-term/crew/gen-11/51a784e46a9ab125b6f9131114d6a46907b9f09f79d23b81ee7f9756bd31c8c2/stamp.json
51a784e46a9ab125b6f9131114d6a46907b9f09f79d23b81ee7f9756bd31c8c2  coevo/ablation-run-c2-conviction-term/crew/gen-11/51a784e46a9ab125b6f9131114d6a46907b9f09f79d23b81ee7f9756bd31c8c2/weights.json
e0941b4693cf0515483a6ea9677201f244c0cb55f584e3ad6abc5c325066b2af  coevo/ablation-run-c2-conviction-term/crew/gen-11/51a784e46a9ab125b6f9131114d6a46907b9f09f79d23b81ee7f9756bd31c8c2/weights.json.sha256
cb6a1b19bc875bed78289ec6e192ef86c95ab750b25c7acfb8751e481e857980  coevo/ablation-run-c2-conviction-term/crew/gen-12/404526a5b35a78f19036421e614dab0f8b9252dedd88b1d15ddc8294be1202a2/config.json
9a531f4c26deb143ecde54dee980a5f84326710fe5bd06c0248118f3a4f77b99  coevo/ablation-run-c2-conviction-term/crew/gen-12/404526a5b35a78f19036421e614dab0f8b9252dedd88b1d15ddc8294be1202a2/stamp.json
404526a5b35a78f19036421e614dab0f8b9252dedd88b1d15ddc8294be1202a2  coevo/ablation-run-c2-conviction-term/crew/gen-12/404526a5b35a78f19036421e614dab0f8b9252dedd88b1d15ddc8294be1202a2/weights.json
eeb57552958463a60558396f9961d03ea53f12b2e5d63d8e94d429e6b635d528  coevo/ablation-run-c2-conviction-term/crew/gen-12/404526a5b35a78f19036421e614dab0f8b9252dedd88b1d15ddc8294be1202a2/weights.json.sha256
912e263a9d7211401f3ddf1e6bc46cea5c2962de12f48d8aade6856c8ee7cac9  coevo/ablation-run-c2-conviction-term/crew/gen-3/fc43ba4e68093db30a1a022bd8860a49dd908cf80ca2feebbc55dd20d0b8be0f/config.json
6fc58b5633d9070abac016de4cd9678d81b02149caa51e55b16510a24dc25f41  coevo/ablation-run-c2-conviction-term/crew/gen-3/fc43ba4e68093db30a1a022bd8860a49dd908cf80ca2feebbc55dd20d0b8be0f/stamp.json
fc43ba4e68093db30a1a022bd8860a49dd908cf80ca2feebbc55dd20d0b8be0f  coevo/ablation-run-c2-conviction-term/crew/gen-3/fc43ba4e68093db30a1a022bd8860a49dd908cf80ca2feebbc55dd20d0b8be0f/weights.json
a7261d93f0704a8d35328857fe628e5f40032bcc5218d8cbe3a4d648a2a0eb1d  coevo/ablation-run-c2-conviction-term/crew/gen-3/fc43ba4e68093db30a1a022bd8860a49dd908cf80ca2feebbc55dd20d0b8be0f/weights.json.sha256
a8165a9e07c4691d8d6800b82ce4b444ea2282cbf53d6d6a7f3fa0559cb5e0d2  coevo/ablation-run-c2-conviction-term/crew/gen-4/b049c4f2037484d3f818ecca6086a9cdb465375bc874358601d7c1ceb81d0b3e/config.json
0ba6b277e5b3d875de57a99490885c5ab5e953a5f1c79cc122bc3b3bfa01abc1  coevo/ablation-run-c2-conviction-term/crew/gen-4/b049c4f2037484d3f818ecca6086a9cdb465375bc874358601d7c1ceb81d0b3e/stamp.json
b049c4f2037484d3f818ecca6086a9cdb465375bc874358601d7c1ceb81d0b3e  coevo/ablation-run-c2-conviction-term/crew/gen-4/b049c4f2037484d3f818ecca6086a9cdb465375bc874358601d7c1ceb81d0b3e/weights.json
0c4e8694a37aeda6836311c54ad36d72003bad5bf07b96d57caf6cf8fba955f3  coevo/ablation-run-c2-conviction-term/crew/gen-4/b049c4f2037484d3f818ecca6086a9cdb465375bc874358601d7c1ceb81d0b3e/weights.json.sha256
5201d92948c84e677b07eb1f4feb1562c7ac0cbffba37403379ef90eb1ee94de  coevo/ablation-run-c2-conviction-term/crew/gen-5/69122bfbefab294f27c70e546874b22274d5bc74b527fa6b328bcbbd17945d8b/config.json
1852f4fbe40c9bd4381a99f6124db6281dca5b7258b0d410bfa1e4c7d0a6e048  coevo/ablation-run-c2-conviction-term/crew/gen-5/69122bfbefab294f27c70e546874b22274d5bc74b527fa6b328bcbbd17945d8b/stamp.json
69122bfbefab294f27c70e546874b22274d5bc74b527fa6b328bcbbd17945d8b  coevo/ablation-run-c2-conviction-term/crew/gen-5/69122bfbefab294f27c70e546874b22274d5bc74b527fa6b328bcbbd17945d8b/weights.json
561372c46d90eb849c99e153e325e6c29c0aa40268823b41cd79cccd750d0e48  coevo/ablation-run-c2-conviction-term/crew/gen-5/69122bfbefab294f27c70e546874b22274d5bc74b527fa6b328bcbbd17945d8b/weights.json.sha256
6defa1f6151aae1a440bf4728435e0452c453928e13d0e2755b74691da87f12e  coevo/ablation-run-c2-conviction-term/crew/gen-6/76d949469cf522d12e0b196768aa3e8d3a1cf86f38c806e0fa0b47e8bc648d02/config.json
b2e07e4d6d2b93290419e92167c639b2dff22bd539c91e599505667232cbfe1c  coevo/ablation-run-c2-conviction-term/crew/gen-6/76d949469cf522d12e0b196768aa3e8d3a1cf86f38c806e0fa0b47e8bc648d02/stamp.json
76d949469cf522d12e0b196768aa3e8d3a1cf86f38c806e0fa0b47e8bc648d02  coevo/ablation-run-c2-conviction-term/crew/gen-6/76d949469cf522d12e0b196768aa3e8d3a1cf86f38c806e0fa0b47e8bc648d02/weights.json
db8a921890c19b920da717c53bc16cb36222313083d028e5af148982417b3170  coevo/ablation-run-c2-conviction-term/crew/gen-6/76d949469cf522d12e0b196768aa3e8d3a1cf86f38c806e0fa0b47e8bc648d02/weights.json.sha256
b22276ba8346762849bdcc60db2cf4a7b9002927b0cb67f5b3fb195bd238e9c7  coevo/ablation-run-c2-conviction-term/crew/gen-9/b07c2a3a56f275b53ce61a9cb4379810a83d2fcb4ce24d9289a45e5eb592cab9/config.json
dffc935100063d0dac336160d8c99785f62d7f560ed752263f182e918af801f3  coevo/ablation-run-c2-conviction-term/crew/gen-9/b07c2a3a56f275b53ce61a9cb4379810a83d2fcb4ce24d9289a45e5eb592cab9/stamp.json
b07c2a3a56f275b53ce61a9cb4379810a83d2fcb4ce24d9289a45e5eb592cab9  coevo/ablation-run-c2-conviction-term/crew/gen-9/b07c2a3a56f275b53ce61a9cb4379810a83d2fcb4ce24d9289a45e5eb592cab9/weights.json
5fb34ad926569b57a0e37cb1381636676d68f9fc523de3e5c31207c1be2df024  coevo/ablation-run-c2-conviction-term/crew/gen-9/b07c2a3a56f275b53ce61a9cb4379810a83d2fcb4ce24d9289a45e5eb592cab9/weights.json.sha256
37197afa2466c950d31f4f48c13cfa89d9f2faa2e3535f717f9619053ad25220  coevo/ablation-run-c2-conviction-term/crew/hall_of_fame.json
25028837637d62d00ce461f98eeaf0e4b31ef2298077e92e25c8399af8ca2282  coevo/ablation-run-c2-conviction-term/impostor/gen-1/c5671ccab33bb27393e37ae3879b062e6199011688140f9329007e66afe07b8f/config.json
98f48f94db17153940e60d5e9cda0c0b07171393acca0ec4a8fde9221b0a70ef  coevo/ablation-run-c2-conviction-term/impostor/gen-1/c5671ccab33bb27393e37ae3879b062e6199011688140f9329007e66afe07b8f/stamp.json
c5671ccab33bb27393e37ae3879b062e6199011688140f9329007e66afe07b8f  coevo/ablation-run-c2-conviction-term/impostor/gen-1/c5671ccab33bb27393e37ae3879b062e6199011688140f9329007e66afe07b8f/weights.json
c1f8e821cadeb7605021edcf00ee30cf55d1ddefa943298eb0de26a2ecb75a13  coevo/ablation-run-c2-conviction-term/impostor/gen-1/c5671ccab33bb27393e37ae3879b062e6199011688140f9329007e66afe07b8f/weights.json.sha256
b05662e362936039fb3879dc54b46a079337fed97b231f50a04fde8d35dc8349  coevo/ablation-run-c2-conviction-term/impostor/gen-12/aa337c7e1d7d9bfd0a888c0c6d7d401df41e091709e871e5e47aa440778e4a5e/config.json
6d17cd7ea7a52ee5adea08e582f8f9e42412f35fd250436e9ae7d3da5886a1b0  coevo/ablation-run-c2-conviction-term/impostor/gen-12/aa337c7e1d7d9bfd0a888c0c6d7d401df41e091709e871e5e47aa440778e4a5e/stamp.json
aa337c7e1d7d9bfd0a888c0c6d7d401df41e091709e871e5e47aa440778e4a5e  coevo/ablation-run-c2-conviction-term/impostor/gen-12/aa337c7e1d7d9bfd0a888c0c6d7d401df41e091709e871e5e47aa440778e4a5e/weights.json
51802e9edde0a43237e2574e998ef6a874c758c440c9ce38ac1d34e895002b9f  coevo/ablation-run-c2-conviction-term/impostor/gen-12/aa337c7e1d7d9bfd0a888c0c6d7d401df41e091709e871e5e47aa440778e4a5e/weights.json.sha256
9d221e99cbfcfee1a0d2122c5998b69e1f118f8364fd19e3f622ae06eb0e353c  coevo/ablation-run-c2-conviction-term/impostor/gen-2/d5ad5bb40e7d1c6343b88a7bccc4678d258e3678cea48d5cdbf47db4276b635b/config.json
e649e56adaa0b54a8446c2f41ec6720d50c664531688da2ec87e065d5946e051  coevo/ablation-run-c2-conviction-term/impostor/gen-2/d5ad5bb40e7d1c6343b88a7bccc4678d258e3678cea48d5cdbf47db4276b635b/stamp.json
d5ad5bb40e7d1c6343b88a7bccc4678d258e3678cea48d5cdbf47db4276b635b  coevo/ablation-run-c2-conviction-term/impostor/gen-2/d5ad5bb40e7d1c6343b88a7bccc4678d258e3678cea48d5cdbf47db4276b635b/weights.json
71e8b703db9ea032e6972163279d03fa559c2b80576f29be3ea0e1c2e13a7f8f  coevo/ablation-run-c2-conviction-term/impostor/gen-2/d5ad5bb40e7d1c6343b88a7bccc4678d258e3678cea48d5cdbf47db4276b635b/weights.json.sha256
e9e866632cbf98fde7a024c0c021a93adeeab929645b5a2bf2abe6dc991fd930  coevo/ablation-run-c2-conviction-term/impostor/gen-3/7e5fe988f2cdc91328ead651ba1da9d75e81c6b0169c58b18db6dbe35c6fba7f/config.json
528cce2b45a203e1142a6372ba0de48e4c4972dc2e8670eadf7fa364cdf41086  coevo/ablation-run-c2-conviction-term/impostor/gen-3/7e5fe988f2cdc91328ead651ba1da9d75e81c6b0169c58b18db6dbe35c6fba7f/stamp.json
7e5fe988f2cdc91328ead651ba1da9d75e81c6b0169c58b18db6dbe35c6fba7f  coevo/ablation-run-c2-conviction-term/impostor/gen-3/7e5fe988f2cdc91328ead651ba1da9d75e81c6b0169c58b18db6dbe35c6fba7f/weights.json
62fb0baf2b690e795337e9c03c91780bda351033a79fa36b941bd43f41892bc8  coevo/ablation-run-c2-conviction-term/impostor/gen-3/7e5fe988f2cdc91328ead651ba1da9d75e81c6b0169c58b18db6dbe35c6fba7f/weights.json.sha256
1d734ba89d03a21ceddb9438d25c567e9e7f2d56dbd5683cbbe439caa40573b1  coevo/ablation-run-c2-conviction-term/impostor/gen-6/1577942ba6435b20c9298dd2ce3c07af1135a70c55d69905675bfcf3e94dc9a4/config.json
366e318afba9f0f1ea19ee3ac98608ed38310b04732e65e5f5f08ef3765220c9  coevo/ablation-run-c2-conviction-term/impostor/gen-6/1577942ba6435b20c9298dd2ce3c07af1135a70c55d69905675bfcf3e94dc9a4/stamp.json
1577942ba6435b20c9298dd2ce3c07af1135a70c55d69905675bfcf3e94dc9a4  coevo/ablation-run-c2-conviction-term/impostor/gen-6/1577942ba6435b20c9298dd2ce3c07af1135a70c55d69905675bfcf3e94dc9a4/weights.json
b23cb1818bbc4c1b76606826eabe74df8d1bcaa42920285bb3072697f0d6e205  coevo/ablation-run-c2-conviction-term/impostor/gen-6/1577942ba6435b20c9298dd2ce3c07af1135a70c55d69905675bfcf3e94dc9a4/weights.json.sha256
333a23e36a9c8fd1af789733e665ee4ab4ba04d8a95b4c7ba027b7b0b9fa1cda  coevo/ablation-run-c2-conviction-term/impostor/gen-7/fa205b75f5a50040391fbdf835bd009d3a729cef2f064db7a10efaa81596a8a3/config.json
13be85ef3fb260c8126f922982c9d993f751ea4ee1869d7362dd9a7ca30141c7  coevo/ablation-run-c2-conviction-term/impostor/gen-7/fa205b75f5a50040391fbdf835bd009d3a729cef2f064db7a10efaa81596a8a3/stamp.json
fa205b75f5a50040391fbdf835bd009d3a729cef2f064db7a10efaa81596a8a3  coevo/ablation-run-c2-conviction-term/impostor/gen-7/fa205b75f5a50040391fbdf835bd009d3a729cef2f064db7a10efaa81596a8a3/weights.json
f36ed092af6c94437b2a9e41d30fd47d34f91aba2f3032950315311fd047cd4a  coevo/ablation-run-c2-conviction-term/impostor/gen-7/fa205b75f5a50040391fbdf835bd009d3a729cef2f064db7a10efaa81596a8a3/weights.json.sha256
32b9a0b0753355d837980247148ec6fdfff18869f0c11b4d35d73da9343934c8  coevo/ablation-run-c2-conviction-term/impostor/gen-8/4af070f6fa9659250ab75a6155f4a7527397c3fb5b89b188461ca0e22564c2b0/config.json
3a28b539290633bb820bcdd9d40e5f5da1b6ffc19adbbcdceb35abb8ec799424  coevo/ablation-run-c2-conviction-term/impostor/gen-8/4af070f6fa9659250ab75a6155f4a7527397c3fb5b89b188461ca0e22564c2b0/stamp.json
4af070f6fa9659250ab75a6155f4a7527397c3fb5b89b188461ca0e22564c2b0  coevo/ablation-run-c2-conviction-term/impostor/gen-8/4af070f6fa9659250ab75a6155f4a7527397c3fb5b89b188461ca0e22564c2b0/weights.json
5a2d4ca1e65b57ed94e649c47fe9b5a619f88d9bdd111b7407e02e6f75ed2c05  coevo/ablation-run-c2-conviction-term/impostor/gen-8/4af070f6fa9659250ab75a6155f4a7527397c3fb5b89b188461ca0e22564c2b0/weights.json.sha256
32084ab471e0cd0abd185834e56d345edc102986a00f5a492a9545041a901649  coevo/ablation-run-c2-conviction-term/impostor/gen-9/442793227ee9afbb17728aa85f54256faf7f572707ed55aeeb9f58a732f51b79/config.json
26497e6620fc324400c78d3207a6864762562d6cfb68028e5dafd2f598c0502a  coevo/ablation-run-c2-conviction-term/impostor/gen-9/442793227ee9afbb17728aa85f54256faf7f572707ed55aeeb9f58a732f51b79/stamp.json
442793227ee9afbb17728aa85f54256faf7f572707ed55aeeb9f58a732f51b79  coevo/ablation-run-c2-conviction-term/impostor/gen-9/442793227ee9afbb17728aa85f54256faf7f572707ed55aeeb9f58a732f51b79/weights.json
bb82ce5ec64911d410252f0ce6bc3b85296bf91f969dbc73c3488858cbc5bd15  coevo/ablation-run-c2-conviction-term/impostor/gen-9/442793227ee9afbb17728aa85f54256faf7f572707ed55aeeb9f58a732f51b79/weights.json.sha256
1b9b3f486e03dd3de6cd6767c50d4bc8114c9af32aa2db865d37fdedb30954a5  coevo/ablation-run-c2-conviction-term/impostor/hall_of_fame.json
921d6447fd458b0c39a58c59e22a7a6f2c038adf428f6efb4371f14ed598a1af  coevo/gen-champions/ablation-run-c1-conviction-term/gen-1/5eb3f040225411fa8ffdde37496979b6472b90f3920f28c6922ae316d6f226e5/config.json
5e03bf16d5c11b28d84a59e81f982b8de77ce2d6b7d81a31125ae1f128ae9cff  coevo/gen-champions/ablation-run-c1-conviction-term/gen-1/5eb3f040225411fa8ffdde37496979b6472b90f3920f28c6922ae316d6f226e5/stamp.json
5eb3f040225411fa8ffdde37496979b6472b90f3920f28c6922ae316d6f226e5  coevo/gen-champions/ablation-run-c1-conviction-term/gen-1/5eb3f040225411fa8ffdde37496979b6472b90f3920f28c6922ae316d6f226e5/weights.json
f25ea8fe4befeaedfaf0d14be82f69a60bba0201e783d77d7c6802ee92d4ea90  coevo/gen-champions/ablation-run-c1-conviction-term/gen-1/5eb3f040225411fa8ffdde37496979b6472b90f3920f28c6922ae316d6f226e5/weights.json.sha256
1bc3c68cea7fa22c0099f8a54d012566895ab39d98cbb662452eb4a418727e88  coevo/gen-champions/ablation-run-c1-conviction-term/gen-10/7ddc3709188f2bb335ef4f19542e72be9154164c04a071729f573c27c9291e02/config.json
291e416fc8c3cba39003c6d82f2751ed937cb60570f301b528d14687895edd2f  coevo/gen-champions/ablation-run-c1-conviction-term/gen-10/7ddc3709188f2bb335ef4f19542e72be9154164c04a071729f573c27c9291e02/stamp.json
7ddc3709188f2bb335ef4f19542e72be9154164c04a071729f573c27c9291e02  coevo/gen-champions/ablation-run-c1-conviction-term/gen-10/7ddc3709188f2bb335ef4f19542e72be9154164c04a071729f573c27c9291e02/weights.json
4d5d592516a83d3b240f605a3da2e9cf75860c1dff1dd5f5e3e4ceef7fe73335  coevo/gen-champions/ablation-run-c1-conviction-term/gen-10/7ddc3709188f2bb335ef4f19542e72be9154164c04a071729f573c27c9291e02/weights.json.sha256
3a93b840a596292ff9dd3cf3ce4f688171198671ddd432e95dd00a9fb81ef192  coevo/gen-champions/ablation-run-c1-conviction-term/gen-11/7ddc3709188f2bb335ef4f19542e72be9154164c04a071729f573c27c9291e02/config.json
194175935eee9d12af2e780314e7bc055b620dc8c55ebb375d3243059c7f4c7f  coevo/gen-champions/ablation-run-c1-conviction-term/gen-11/7ddc3709188f2bb335ef4f19542e72be9154164c04a071729f573c27c9291e02/stamp.json
7ddc3709188f2bb335ef4f19542e72be9154164c04a071729f573c27c9291e02  coevo/gen-champions/ablation-run-c1-conviction-term/gen-11/7ddc3709188f2bb335ef4f19542e72be9154164c04a071729f573c27c9291e02/weights.json
4d5d592516a83d3b240f605a3da2e9cf75860c1dff1dd5f5e3e4ceef7fe73335  coevo/gen-champions/ablation-run-c1-conviction-term/gen-11/7ddc3709188f2bb335ef4f19542e72be9154164c04a071729f573c27c9291e02/weights.json.sha256
811d9204bea2fe0b6128fe7f13af1662e45827320cb8a55daa4340699ae0034f  coevo/gen-champions/ablation-run-c1-conviction-term/gen-12/7ddc3709188f2bb335ef4f19542e72be9154164c04a071729f573c27c9291e02/config.json
29cc603acc0c732ef4bbb703ab04d97c14c6eaa4c4e33632c09686b9542fbea2  coevo/gen-champions/ablation-run-c1-conviction-term/gen-12/7ddc3709188f2bb335ef4f19542e72be9154164c04a071729f573c27c9291e02/stamp.json
7ddc3709188f2bb335ef4f19542e72be9154164c04a071729f573c27c9291e02  coevo/gen-champions/ablation-run-c1-conviction-term/gen-12/7ddc3709188f2bb335ef4f19542e72be9154164c04a071729f573c27c9291e02/weights.json
4d5d592516a83d3b240f605a3da2e9cf75860c1dff1dd5f5e3e4ceef7fe73335  coevo/gen-champions/ablation-run-c1-conviction-term/gen-12/7ddc3709188f2bb335ef4f19542e72be9154164c04a071729f573c27c9291e02/weights.json.sha256
dad5d8e30b5a1e93344aa51eaffcd3d2221526de87950b7cd50a0a6e5a265d17  coevo/gen-champions/ablation-run-c1-conviction-term/gen-2/a1fc26cc530534320ddeb7e750d5b4809310a67b1be34e5a9ce4abf44420ce42/config.json
3ea4eb6aa8540fdb7e73aa1fa787d6e859cb029921cc1d0fb99a6d856cc9e554  coevo/gen-champions/ablation-run-c1-conviction-term/gen-2/a1fc26cc530534320ddeb7e750d5b4809310a67b1be34e5a9ce4abf44420ce42/stamp.json
a1fc26cc530534320ddeb7e750d5b4809310a67b1be34e5a9ce4abf44420ce42  coevo/gen-champions/ablation-run-c1-conviction-term/gen-2/a1fc26cc530534320ddeb7e750d5b4809310a67b1be34e5a9ce4abf44420ce42/weights.json
b6c806923a2234308de8845183b2160a2b1fee09f419ec4220e4cc298d4bb8b8  coevo/gen-champions/ablation-run-c1-conviction-term/gen-2/a1fc26cc530534320ddeb7e750d5b4809310a67b1be34e5a9ce4abf44420ce42/weights.json.sha256
8ca35d9303bcf0a0e4d9859838944dd84e585b8f7ac6d18172d4e874809d4ab1  coevo/gen-champions/ablation-run-c1-conviction-term/gen-3/72adb41c9286d61d5a81ea4ed2bd347c0d7da52ad89ae6497f1dcbf2237ca4e5/config.json
1aa9b9c1a0c5b2a59b304384b421e29be6273d42d627b4c732151b97407a5119  coevo/gen-champions/ablation-run-c1-conviction-term/gen-3/72adb41c9286d61d5a81ea4ed2bd347c0d7da52ad89ae6497f1dcbf2237ca4e5/stamp.json
72adb41c9286d61d5a81ea4ed2bd347c0d7da52ad89ae6497f1dcbf2237ca4e5  coevo/gen-champions/ablation-run-c1-conviction-term/gen-3/72adb41c9286d61d5a81ea4ed2bd347c0d7da52ad89ae6497f1dcbf2237ca4e5/weights.json
e937d76813ced95a20e0e81fecdd650ebf774972eca5269d1e84cdbbbe385715  coevo/gen-champions/ablation-run-c1-conviction-term/gen-3/72adb41c9286d61d5a81ea4ed2bd347c0d7da52ad89ae6497f1dcbf2237ca4e5/weights.json.sha256
575deb4f59b9934ada4b2d305725bf924ab0c67f638e6cfb7f8fd749b0e8d7f2  coevo/gen-champions/ablation-run-c1-conviction-term/gen-4/0ca3a382a0e3566dfb225d99cd72abd48e988709dba0cbae9fa5f96d68fa4f52/config.json
90156b9fa2b60142f7b103b7a4c11ea35bbfc56e85731f659ed3d317953ad2f0  coevo/gen-champions/ablation-run-c1-conviction-term/gen-4/0ca3a382a0e3566dfb225d99cd72abd48e988709dba0cbae9fa5f96d68fa4f52/stamp.json
0ca3a382a0e3566dfb225d99cd72abd48e988709dba0cbae9fa5f96d68fa4f52  coevo/gen-champions/ablation-run-c1-conviction-term/gen-4/0ca3a382a0e3566dfb225d99cd72abd48e988709dba0cbae9fa5f96d68fa4f52/weights.json
8f344cdb6358193869a691db34d68cf40c5689af1fa4b2cc352c34f36d95d128  coevo/gen-champions/ablation-run-c1-conviction-term/gen-4/0ca3a382a0e3566dfb225d99cd72abd48e988709dba0cbae9fa5f96d68fa4f52/weights.json.sha256
124488f27a5fb928fcd0c6a9cfad34d5e941e3103c3864241a468e45edcb339a  coevo/gen-champions/ablation-run-c1-conviction-term/gen-5/7ddc3709188f2bb335ef4f19542e72be9154164c04a071729f573c27c9291e02/config.json
eccb4ca9e3e995cc141e9033e13a4b6b9d7b4551d4608e2bf4eedbc3e562600f  coevo/gen-champions/ablation-run-c1-conviction-term/gen-5/7ddc3709188f2bb335ef4f19542e72be9154164c04a071729f573c27c9291e02/stamp.json
7ddc3709188f2bb335ef4f19542e72be9154164c04a071729f573c27c9291e02  coevo/gen-champions/ablation-run-c1-conviction-term/gen-5/7ddc3709188f2bb335ef4f19542e72be9154164c04a071729f573c27c9291e02/weights.json
4d5d592516a83d3b240f605a3da2e9cf75860c1dff1dd5f5e3e4ceef7fe73335  coevo/gen-champions/ablation-run-c1-conviction-term/gen-5/7ddc3709188f2bb335ef4f19542e72be9154164c04a071729f573c27c9291e02/weights.json.sha256
88061d37a0916c041b2a3aff6f8d202107482a7a48e2cc88bb94109989ace718  coevo/gen-champions/ablation-run-c1-conviction-term/gen-6/7ddc3709188f2bb335ef4f19542e72be9154164c04a071729f573c27c9291e02/config.json
95ea068d93972da8e89f571c862d53f01abd5f1a450d924d89a5a838e0e3067a  coevo/gen-champions/ablation-run-c1-conviction-term/gen-6/7ddc3709188f2bb335ef4f19542e72be9154164c04a071729f573c27c9291e02/stamp.json
7ddc3709188f2bb335ef4f19542e72be9154164c04a071729f573c27c9291e02  coevo/gen-champions/ablation-run-c1-conviction-term/gen-6/7ddc3709188f2bb335ef4f19542e72be9154164c04a071729f573c27c9291e02/weights.json
4d5d592516a83d3b240f605a3da2e9cf75860c1dff1dd5f5e3e4ceef7fe73335  coevo/gen-champions/ablation-run-c1-conviction-term/gen-6/7ddc3709188f2bb335ef4f19542e72be9154164c04a071729f573c27c9291e02/weights.json.sha256
b2a777213c2b894607a62c89642902aee090e0aa7f70a99529ba94fdc2fe63e9  coevo/gen-champions/ablation-run-c1-conviction-term/gen-7/cab1c0a3f61e70f544a0ec71d02035013d12fd145590d8bcf342a97a46accf42/config.json
bb951e0d551feb6c45fee7473ba8a9e7eaf90ce090caccfc61c66ff69c5be087  coevo/gen-champions/ablation-run-c1-conviction-term/gen-7/cab1c0a3f61e70f544a0ec71d02035013d12fd145590d8bcf342a97a46accf42/stamp.json
cab1c0a3f61e70f544a0ec71d02035013d12fd145590d8bcf342a97a46accf42  coevo/gen-champions/ablation-run-c1-conviction-term/gen-7/cab1c0a3f61e70f544a0ec71d02035013d12fd145590d8bcf342a97a46accf42/weights.json
8b209eed750fa53691a34d0595ec389f328f2a3dafedd2d4c8b66cf7d6317e01  coevo/gen-champions/ablation-run-c1-conviction-term/gen-7/cab1c0a3f61e70f544a0ec71d02035013d12fd145590d8bcf342a97a46accf42/weights.json.sha256
7a42fcf5ae35039f6255e746098a580d6fc28c445e69017942055bf96cfec938  coevo/gen-champions/ablation-run-c1-conviction-term/gen-8/b9235fafa9fd33af719b47d520d91045586d73ccde66dc413cd1d5616e83b75e/config.json
abe6fb19eb65a73bcfa7abddb872470baa4c47a472496a82a6b7175c3b0626da  coevo/gen-champions/ablation-run-c1-conviction-term/gen-8/b9235fafa9fd33af719b47d520d91045586d73ccde66dc413cd1d5616e83b75e/stamp.json
b9235fafa9fd33af719b47d520d91045586d73ccde66dc413cd1d5616e83b75e  coevo/gen-champions/ablation-run-c1-conviction-term/gen-8/b9235fafa9fd33af719b47d520d91045586d73ccde66dc413cd1d5616e83b75e/weights.json
b317d210320286950ccd6813255f5a5cbf6a083e7bff471b116a5c4f34280fa7  coevo/gen-champions/ablation-run-c1-conviction-term/gen-8/b9235fafa9fd33af719b47d520d91045586d73ccde66dc413cd1d5616e83b75e/weights.json.sha256
df0cb36ad7a81421d9952308f776db102c1600618f865afe1054e1b460d59fcc  coevo/gen-champions/ablation-run-c1-conviction-term/gen-9/a0ab72e26d40e289fc64c719d079e070ece960956d73bf4eae230f7c8fa7fbd3/config.json
332c6975779030889f12e47d124bd8b89f2a891b9ea064e9fa6c222c1d2fa27a  coevo/gen-champions/ablation-run-c1-conviction-term/gen-9/a0ab72e26d40e289fc64c719d079e070ece960956d73bf4eae230f7c8fa7fbd3/stamp.json
a0ab72e26d40e289fc64c719d079e070ece960956d73bf4eae230f7c8fa7fbd3  coevo/gen-champions/ablation-run-c1-conviction-term/gen-9/a0ab72e26d40e289fc64c719d079e070ece960956d73bf4eae230f7c8fa7fbd3/weights.json
25c602c11f5affbb5cd69d64b4dd0a6d1193593a9594ede15065bcb45df91f85  coevo/gen-champions/ablation-run-c1-conviction-term/gen-9/a0ab72e26d40e289fc64c719d079e070ece960956d73bf4eae230f7c8fa7fbd3/weights.json.sha256
ee8dc5c3f46d39f3f54042a0fb8e709991f6aa1688ff1e72519d0d404da190ff  coevo/gen-champions/ablation-run-c2-conviction-term/gen-1/888046d082daf62853c9d10d25dde04e20691c042dcd6a6609492d554ed569bf/config.json
ab4444afa737a8219ec0501c9e5d9ce2f80ac5f342472dcb5e0770017e58827e  coevo/gen-champions/ablation-run-c2-conviction-term/gen-1/888046d082daf62853c9d10d25dde04e20691c042dcd6a6609492d554ed569bf/stamp.json
888046d082daf62853c9d10d25dde04e20691c042dcd6a6609492d554ed569bf  coevo/gen-champions/ablation-run-c2-conviction-term/gen-1/888046d082daf62853c9d10d25dde04e20691c042dcd6a6609492d554ed569bf/weights.json
3bc930aeefc9ee9b144959259c6375dde8873f7c6ab647f9806a8537300bd5e9  coevo/gen-champions/ablation-run-c2-conviction-term/gen-1/888046d082daf62853c9d10d25dde04e20691c042dcd6a6609492d554ed569bf/weights.json.sha256
1871e32ac494082e418b56db05160876e9657cbd5402c9045c4579251119442c  coevo/gen-champions/ablation-run-c2-conviction-term/gen-10/e37b009b0febbf4fb6498e2cb0d8af946ac8878aaede90dcf74134fd668c1044/config.json
e495cd9d9f7679ed1240ea1a0b19b5bbf8b4a6a41be95c1f2ddb59c48ab867eb  coevo/gen-champions/ablation-run-c2-conviction-term/gen-10/e37b009b0febbf4fb6498e2cb0d8af946ac8878aaede90dcf74134fd668c1044/stamp.json
e37b009b0febbf4fb6498e2cb0d8af946ac8878aaede90dcf74134fd668c1044  coevo/gen-champions/ablation-run-c2-conviction-term/gen-10/e37b009b0febbf4fb6498e2cb0d8af946ac8878aaede90dcf74134fd668c1044/weights.json
60d1ddfb4ba6e847e742930483098bf6bc5daad69432532949a5595b693bd5ae  coevo/gen-champions/ablation-run-c2-conviction-term/gen-10/e37b009b0febbf4fb6498e2cb0d8af946ac8878aaede90dcf74134fd668c1044/weights.json.sha256
6d9ea46167eaf507d377d63c26d30f8d631a18aa2c552bc9735c2cdd754eaeac  coevo/gen-champions/ablation-run-c2-conviction-term/gen-11/e37b009b0febbf4fb6498e2cb0d8af946ac8878aaede90dcf74134fd668c1044/config.json
d78e310fa8e4178ec348e98ed22040fcf0c135054306f3a22d13be98a0167dfb  coevo/gen-champions/ablation-run-c2-conviction-term/gen-11/e37b009b0febbf4fb6498e2cb0d8af946ac8878aaede90dcf74134fd668c1044/stamp.json
e37b009b0febbf4fb6498e2cb0d8af946ac8878aaede90dcf74134fd668c1044  coevo/gen-champions/ablation-run-c2-conviction-term/gen-11/e37b009b0febbf4fb6498e2cb0d8af946ac8878aaede90dcf74134fd668c1044/weights.json
60d1ddfb4ba6e847e742930483098bf6bc5daad69432532949a5595b693bd5ae  coevo/gen-champions/ablation-run-c2-conviction-term/gen-11/e37b009b0febbf4fb6498e2cb0d8af946ac8878aaede90dcf74134fd668c1044/weights.json.sha256
8cd880486bb419d2ef7bc1d6186dfdad9ba90d1946618b13edf0dcf752420ddf  coevo/gen-champions/ablation-run-c2-conviction-term/gen-12/aa337c7e1d7d9bfd0a888c0c6d7d401df41e091709e871e5e47aa440778e4a5e/config.json
644f2ce328b82603009b0bfdd930a00e7aab72d6f3bc180a6dd83a35ade6808b  coevo/gen-champions/ablation-run-c2-conviction-term/gen-12/aa337c7e1d7d9bfd0a888c0c6d7d401df41e091709e871e5e47aa440778e4a5e/stamp.json
aa337c7e1d7d9bfd0a888c0c6d7d401df41e091709e871e5e47aa440778e4a5e  coevo/gen-champions/ablation-run-c2-conviction-term/gen-12/aa337c7e1d7d9bfd0a888c0c6d7d401df41e091709e871e5e47aa440778e4a5e/weights.json
51802e9edde0a43237e2574e998ef6a874c758c440c9ce38ac1d34e895002b9f  coevo/gen-champions/ablation-run-c2-conviction-term/gen-12/aa337c7e1d7d9bfd0a888c0c6d7d401df41e091709e871e5e47aa440778e4a5e/weights.json.sha256
86c4354be4e21fa89e3ffb8dff4b13614ebbbc81cbd8efd10c77aaf134a96706  coevo/gen-champions/ablation-run-c2-conviction-term/gen-2/bd7770afb500087454504b78ee9a2520449faad7740078194e11a8961a56e534/config.json
09026e1565523dbda86e0c247c5f2b1b6f672c584f6c8f9ebc28323e5ae00913  coevo/gen-champions/ablation-run-c2-conviction-term/gen-2/bd7770afb500087454504b78ee9a2520449faad7740078194e11a8961a56e534/stamp.json
bd7770afb500087454504b78ee9a2520449faad7740078194e11a8961a56e534  coevo/gen-champions/ablation-run-c2-conviction-term/gen-2/bd7770afb500087454504b78ee9a2520449faad7740078194e11a8961a56e534/weights.json
65ddde3e13e6d88155415c7aaafc3f784fcd362782fd1c17c4e3d6b0d126f4e3  coevo/gen-champions/ablation-run-c2-conviction-term/gen-2/bd7770afb500087454504b78ee9a2520449faad7740078194e11a8961a56e534/weights.json.sha256
08d923f37b433332a230970e97b4a4a0a2e0b6daa961efe5ecce46612fa85edd  coevo/gen-champions/ablation-run-c2-conviction-term/gen-3/fc43ba4e68093db30a1a022bd8860a49dd908cf80ca2feebbc55dd20d0b8be0f/config.json
9b8c8e0bdc9fcd723a0f54c0dba530934c3cc3c6b9f8861701f6bff8fc8c97bc  coevo/gen-champions/ablation-run-c2-conviction-term/gen-3/fc43ba4e68093db30a1a022bd8860a49dd908cf80ca2feebbc55dd20d0b8be0f/stamp.json
fc43ba4e68093db30a1a022bd8860a49dd908cf80ca2feebbc55dd20d0b8be0f  coevo/gen-champions/ablation-run-c2-conviction-term/gen-3/fc43ba4e68093db30a1a022bd8860a49dd908cf80ca2feebbc55dd20d0b8be0f/weights.json
a7261d93f0704a8d35328857fe628e5f40032bcc5218d8cbe3a4d648a2a0eb1d  coevo/gen-champions/ablation-run-c2-conviction-term/gen-3/fc43ba4e68093db30a1a022bd8860a49dd908cf80ca2feebbc55dd20d0b8be0f/weights.json.sha256
8b7be3129ac71e9ed023196036a4e204d55333c6476c998152cc5c605a9b0746  coevo/gen-champions/ablation-run-c2-conviction-term/gen-4/1577942ba6435b20c9298dd2ce3c07af1135a70c55d69905675bfcf3e94dc9a4/config.json
e2a0dd0d170a476621ac4ca4cfce8449e8a2d3de30c5af07197668dbb0e50faf  coevo/gen-champions/ablation-run-c2-conviction-term/gen-4/1577942ba6435b20c9298dd2ce3c07af1135a70c55d69905675bfcf3e94dc9a4/stamp.json
1577942ba6435b20c9298dd2ce3c07af1135a70c55d69905675bfcf3e94dc9a4  coevo/gen-champions/ablation-run-c2-conviction-term/gen-4/1577942ba6435b20c9298dd2ce3c07af1135a70c55d69905675bfcf3e94dc9a4/weights.json
b23cb1818bbc4c1b76606826eabe74df8d1bcaa42920285bb3072697f0d6e205  coevo/gen-champions/ablation-run-c2-conviction-term/gen-4/1577942ba6435b20c9298dd2ce3c07af1135a70c55d69905675bfcf3e94dc9a4/weights.json.sha256
a2d79dc58e8a6ff779097fee46d648c9a49dabf233cfea600bf26ce7378c6130  coevo/gen-champions/ablation-run-c2-conviction-term/gen-5/1577942ba6435b20c9298dd2ce3c07af1135a70c55d69905675bfcf3e94dc9a4/config.json
76374b9414d994429ad01400e833a695e13e7cc96d699f5a945112aa54100beb  coevo/gen-champions/ablation-run-c2-conviction-term/gen-5/1577942ba6435b20c9298dd2ce3c07af1135a70c55d69905675bfcf3e94dc9a4/stamp.json
1577942ba6435b20c9298dd2ce3c07af1135a70c55d69905675bfcf3e94dc9a4  coevo/gen-champions/ablation-run-c2-conviction-term/gen-5/1577942ba6435b20c9298dd2ce3c07af1135a70c55d69905675bfcf3e94dc9a4/weights.json
b23cb1818bbc4c1b76606826eabe74df8d1bcaa42920285bb3072697f0d6e205  coevo/gen-champions/ablation-run-c2-conviction-term/gen-5/1577942ba6435b20c9298dd2ce3c07af1135a70c55d69905675bfcf3e94dc9a4/weights.json.sha256
65372670adda69ffa0e541fd7f39e0477f3a020ee8728dfe572e59d78c686ed8  coevo/gen-champions/ablation-run-c2-conviction-term/gen-6/1577942ba6435b20c9298dd2ce3c07af1135a70c55d69905675bfcf3e94dc9a4/config.json
7325c7479cca58cead6e6dde381dc500cad03d94ebdcc92a2ce186996afd8abd  coevo/gen-champions/ablation-run-c2-conviction-term/gen-6/1577942ba6435b20c9298dd2ce3c07af1135a70c55d69905675bfcf3e94dc9a4/stamp.json
1577942ba6435b20c9298dd2ce3c07af1135a70c55d69905675bfcf3e94dc9a4  coevo/gen-champions/ablation-run-c2-conviction-term/gen-6/1577942ba6435b20c9298dd2ce3c07af1135a70c55d69905675bfcf3e94dc9a4/weights.json
b23cb1818bbc4c1b76606826eabe74df8d1bcaa42920285bb3072697f0d6e205  coevo/gen-champions/ablation-run-c2-conviction-term/gen-6/1577942ba6435b20c9298dd2ce3c07af1135a70c55d69905675bfcf3e94dc9a4/weights.json.sha256
4af90eb6c1dc16f4497fd6551470753eb975142b082a6a53b8c6376e9e13883b  coevo/gen-champions/ablation-run-c2-conviction-term/gen-7/d688d29ad67ec48f6e2b79e595db4ffdd16afbb99db9f3eb31f8bc0110b553be/config.json
95804904f8028a067bc31e6d3270bbdb168ee2635079d0aed192c00dc23a9b8d  coevo/gen-champions/ablation-run-c2-conviction-term/gen-7/d688d29ad67ec48f6e2b79e595db4ffdd16afbb99db9f3eb31f8bc0110b553be/stamp.json
d688d29ad67ec48f6e2b79e595db4ffdd16afbb99db9f3eb31f8bc0110b553be  coevo/gen-champions/ablation-run-c2-conviction-term/gen-7/d688d29ad67ec48f6e2b79e595db4ffdd16afbb99db9f3eb31f8bc0110b553be/weights.json
8f37ad51b4aadbd49b07ca5a9fe39b8d294f395ff76e7d2e419f27244b087d79  coevo/gen-champions/ablation-run-c2-conviction-term/gen-7/d688d29ad67ec48f6e2b79e595db4ffdd16afbb99db9f3eb31f8bc0110b553be/weights.json.sha256
3175a4b25c97df96fb687959a6b60a19dc73cf057b6978aee201ff6e58ededb1  coevo/gen-champions/ablation-run-c2-conviction-term/gen-8/b07c2a3a56f275b53ce61a9cb4379810a83d2fcb4ce24d9289a45e5eb592cab9/config.json
fdc060ffffb78a30aedd8e7609d79198db9017f2a9e0ac76720925788811538e  coevo/gen-champions/ablation-run-c2-conviction-term/gen-8/b07c2a3a56f275b53ce61a9cb4379810a83d2fcb4ce24d9289a45e5eb592cab9/stamp.json
b07c2a3a56f275b53ce61a9cb4379810a83d2fcb4ce24d9289a45e5eb592cab9  coevo/gen-champions/ablation-run-c2-conviction-term/gen-8/b07c2a3a56f275b53ce61a9cb4379810a83d2fcb4ce24d9289a45e5eb592cab9/weights.json
5fb34ad926569b57a0e37cb1381636676d68f9fc523de3e5c31207c1be2df024  coevo/gen-champions/ablation-run-c2-conviction-term/gen-8/b07c2a3a56f275b53ce61a9cb4379810a83d2fcb4ce24d9289a45e5eb592cab9/weights.json.sha256
037e6908e79f2fa55c6c5e990a020b6d9d08dddd76dbb6a7155cf80fff114592  coevo/gen-champions/ablation-run-c2-conviction-term/gen-9/b07c2a3a56f275b53ce61a9cb4379810a83d2fcb4ce24d9289a45e5eb592cab9/config.json
eb3dbf6a849e8c682297f6c42ced29add401a5e6cc64147653739a124bced9f6  coevo/gen-champions/ablation-run-c2-conviction-term/gen-9/b07c2a3a56f275b53ce61a9cb4379810a83d2fcb4ce24d9289a45e5eb592cab9/stamp.json
b07c2a3a56f275b53ce61a9cb4379810a83d2fcb4ce24d9289a45e5eb592cab9  coevo/gen-champions/ablation-run-c2-conviction-term/gen-9/b07c2a3a56f275b53ce61a9cb4379810a83d2fcb4ce24d9289a45e5eb592cab9/weights.json
5fb34ad926569b57a0e37cb1381636676d68f9fc523de3e5c31207c1be2df024  coevo/gen-champions/ablation-run-c2-conviction-term/gen-9/b07c2a3a56f275b53ce61a9cb4379810a83d2fcb4ce24d9289a45e5eb592cab9/weights.json.sha256
792105800d7583c74888f657b21ab36c79b0b859809a5bdc606433eb094e8227  coevo/gen-champions/run-c1-crew-owned-tasks/gen-1/5eb3f040225411fa8ffdde37496979b6472b90f3920f28c6922ae316d6f226e5/config.json
98b173e61fa11a32a24ab76ff06691c7c88142893bbf70daa02d1694d1839c41  coevo/gen-champions/run-c1-crew-owned-tasks/gen-1/5eb3f040225411fa8ffdde37496979b6472b90f3920f28c6922ae316d6f226e5/stamp.json
5eb3f040225411fa8ffdde37496979b6472b90f3920f28c6922ae316d6f226e5  coevo/gen-champions/run-c1-crew-owned-tasks/gen-1/5eb3f040225411fa8ffdde37496979b6472b90f3920f28c6922ae316d6f226e5/weights.json
f25ea8fe4befeaedfaf0d14be82f69a60bba0201e783d77d7c6802ee92d4ea90  coevo/gen-champions/run-c1-crew-owned-tasks/gen-1/5eb3f040225411fa8ffdde37496979b6472b90f3920f28c6922ae316d6f226e5/weights.json.sha256
8aeed1b4bfd31ffe18ab37f2bee842acf22ceb99633bc05bb67b2249eb08e381  coevo/gen-champions/run-c1-crew-owned-tasks/gen-10/0ca3a382a0e3566dfb225d99cd72abd48e988709dba0cbae9fa5f96d68fa4f52/config.json
b1da904f06083b4c82248fcd91f71e62b4d8580fe66237b6290b796343d684bc  coevo/gen-champions/run-c1-crew-owned-tasks/gen-10/0ca3a382a0e3566dfb225d99cd72abd48e988709dba0cbae9fa5f96d68fa4f52/stamp.json
0ca3a382a0e3566dfb225d99cd72abd48e988709dba0cbae9fa5f96d68fa4f52  coevo/gen-champions/run-c1-crew-owned-tasks/gen-10/0ca3a382a0e3566dfb225d99cd72abd48e988709dba0cbae9fa5f96d68fa4f52/weights.json
8f344cdb6358193869a691db34d68cf40c5689af1fa4b2cc352c34f36d95d128  coevo/gen-champions/run-c1-crew-owned-tasks/gen-10/0ca3a382a0e3566dfb225d99cd72abd48e988709dba0cbae9fa5f96d68fa4f52/weights.json.sha256
86bb146f46fbb74657ffe076834aa538c30f9f63903b485cfa01bcaf011d226e  coevo/gen-champions/run-c1-crew-owned-tasks/gen-11/0ca3a382a0e3566dfb225d99cd72abd48e988709dba0cbae9fa5f96d68fa4f52/config.json
011f4d0bc627344904c289d7e9b7e7eb0b5f004c84ed344e66e3f187e0084f6c  coevo/gen-champions/run-c1-crew-owned-tasks/gen-11/0ca3a382a0e3566dfb225d99cd72abd48e988709dba0cbae9fa5f96d68fa4f52/stamp.json
0ca3a382a0e3566dfb225d99cd72abd48e988709dba0cbae9fa5f96d68fa4f52  coevo/gen-champions/run-c1-crew-owned-tasks/gen-11/0ca3a382a0e3566dfb225d99cd72abd48e988709dba0cbae9fa5f96d68fa4f52/weights.json
8f344cdb6358193869a691db34d68cf40c5689af1fa4b2cc352c34f36d95d128  coevo/gen-champions/run-c1-crew-owned-tasks/gen-11/0ca3a382a0e3566dfb225d99cd72abd48e988709dba0cbae9fa5f96d68fa4f52/weights.json.sha256
7330184cd2dfeb03c54fd81090f1f6e8f89d01f8254076c7312ecedec443069e  coevo/gen-champions/run-c1-crew-owned-tasks/gen-12/0ca3a382a0e3566dfb225d99cd72abd48e988709dba0cbae9fa5f96d68fa4f52/config.json
0c247233075bc91c85e5a825e041c42060f6bc6963d1c63ec1c2c7752cb84669  coevo/gen-champions/run-c1-crew-owned-tasks/gen-12/0ca3a382a0e3566dfb225d99cd72abd48e988709dba0cbae9fa5f96d68fa4f52/stamp.json
0ca3a382a0e3566dfb225d99cd72abd48e988709dba0cbae9fa5f96d68fa4f52  coevo/gen-champions/run-c1-crew-owned-tasks/gen-12/0ca3a382a0e3566dfb225d99cd72abd48e988709dba0cbae9fa5f96d68fa4f52/weights.json
8f344cdb6358193869a691db34d68cf40c5689af1fa4b2cc352c34f36d95d128  coevo/gen-champions/run-c1-crew-owned-tasks/gen-12/0ca3a382a0e3566dfb225d99cd72abd48e988709dba0cbae9fa5f96d68fa4f52/weights.json.sha256
ba83be191cd6196062e0376b22a7079a65bb2a4d2d1a862dcdd68b9689b733f2  coevo/gen-champions/run-c1-crew-owned-tasks/gen-2/a1fc26cc530534320ddeb7e750d5b4809310a67b1be34e5a9ce4abf44420ce42/config.json
0f85a699931b5bf208f2691fa39c06bb1eaf857041960f241281f77eb9faa288  coevo/gen-champions/run-c1-crew-owned-tasks/gen-2/a1fc26cc530534320ddeb7e750d5b4809310a67b1be34e5a9ce4abf44420ce42/stamp.json
a1fc26cc530534320ddeb7e750d5b4809310a67b1be34e5a9ce4abf44420ce42  coevo/gen-champions/run-c1-crew-owned-tasks/gen-2/a1fc26cc530534320ddeb7e750d5b4809310a67b1be34e5a9ce4abf44420ce42/weights.json
b6c806923a2234308de8845183b2160a2b1fee09f419ec4220e4cc298d4bb8b8  coevo/gen-champions/run-c1-crew-owned-tasks/gen-2/a1fc26cc530534320ddeb7e750d5b4809310a67b1be34e5a9ce4abf44420ce42/weights.json.sha256
215c4f44af3362a3fcf8fb7948f499cdbaec9fe8eeaf6d3ffe12ae0a66e75644  coevo/gen-champions/run-c1-crew-owned-tasks/gen-3/72adb41c9286d61d5a81ea4ed2bd347c0d7da52ad89ae6497f1dcbf2237ca4e5/config.json
5d7fa24ef16d20dd41b5357bcc61ef6a67fa58d891eb364b75212a53ae12efa5  coevo/gen-champions/run-c1-crew-owned-tasks/gen-3/72adb41c9286d61d5a81ea4ed2bd347c0d7da52ad89ae6497f1dcbf2237ca4e5/stamp.json
72adb41c9286d61d5a81ea4ed2bd347c0d7da52ad89ae6497f1dcbf2237ca4e5  coevo/gen-champions/run-c1-crew-owned-tasks/gen-3/72adb41c9286d61d5a81ea4ed2bd347c0d7da52ad89ae6497f1dcbf2237ca4e5/weights.json
e937d76813ced95a20e0e81fecdd650ebf774972eca5269d1e84cdbbbe385715  coevo/gen-champions/run-c1-crew-owned-tasks/gen-3/72adb41c9286d61d5a81ea4ed2bd347c0d7da52ad89ae6497f1dcbf2237ca4e5/weights.json.sha256
29824ba51cdac1ae905ba1c9e68ab80f685c4a770d5487cc27d456e3929589dc  coevo/gen-champions/run-c1-crew-owned-tasks/gen-4/0ca3a382a0e3566dfb225d99cd72abd48e988709dba0cbae9fa5f96d68fa4f52/config.json
59724732ce7a0acc54c7626ca8a9effd205d38dbe3dd8f16ef67a025f42841de  coevo/gen-champions/run-c1-crew-owned-tasks/gen-4/0ca3a382a0e3566dfb225d99cd72abd48e988709dba0cbae9fa5f96d68fa4f52/stamp.json
0ca3a382a0e3566dfb225d99cd72abd48e988709dba0cbae9fa5f96d68fa4f52  coevo/gen-champions/run-c1-crew-owned-tasks/gen-4/0ca3a382a0e3566dfb225d99cd72abd48e988709dba0cbae9fa5f96d68fa4f52/weights.json
8f344cdb6358193869a691db34d68cf40c5689af1fa4b2cc352c34f36d95d128  coevo/gen-champions/run-c1-crew-owned-tasks/gen-4/0ca3a382a0e3566dfb225d99cd72abd48e988709dba0cbae9fa5f96d68fa4f52/weights.json.sha256
b7a0997937fb2fbb8d2810fe8ac06a5952e786fe717072d65d0adb2ccd4095d7  coevo/gen-champions/run-c1-crew-owned-tasks/gen-5/0ca3a382a0e3566dfb225d99cd72abd48e988709dba0cbae9fa5f96d68fa4f52/config.json
dc3266c14e0a947596e1e43d30620a966e5126888a88cfa75c70fcda2f5d69b6  coevo/gen-champions/run-c1-crew-owned-tasks/gen-5/0ca3a382a0e3566dfb225d99cd72abd48e988709dba0cbae9fa5f96d68fa4f52/stamp.json
0ca3a382a0e3566dfb225d99cd72abd48e988709dba0cbae9fa5f96d68fa4f52  coevo/gen-champions/run-c1-crew-owned-tasks/gen-5/0ca3a382a0e3566dfb225d99cd72abd48e988709dba0cbae9fa5f96d68fa4f52/weights.json
8f344cdb6358193869a691db34d68cf40c5689af1fa4b2cc352c34f36d95d128  coevo/gen-champions/run-c1-crew-owned-tasks/gen-5/0ca3a382a0e3566dfb225d99cd72abd48e988709dba0cbae9fa5f96d68fa4f52/weights.json.sha256
3f415fee7ab9224c21d6a2f5829a24f1b1b5e0f2a1f5e253de516e60073e166f  coevo/gen-champions/run-c1-crew-owned-tasks/gen-6/0ca3a382a0e3566dfb225d99cd72abd48e988709dba0cbae9fa5f96d68fa4f52/config.json
6d64feee443f0300cc9703ec057f4f43c3d5e1655ee3741e377369b91945cd0a  coevo/gen-champions/run-c1-crew-owned-tasks/gen-6/0ca3a382a0e3566dfb225d99cd72abd48e988709dba0cbae9fa5f96d68fa4f52/stamp.json
0ca3a382a0e3566dfb225d99cd72abd48e988709dba0cbae9fa5f96d68fa4f52  coevo/gen-champions/run-c1-crew-owned-tasks/gen-6/0ca3a382a0e3566dfb225d99cd72abd48e988709dba0cbae9fa5f96d68fa4f52/weights.json
8f344cdb6358193869a691db34d68cf40c5689af1fa4b2cc352c34f36d95d128  coevo/gen-champions/run-c1-crew-owned-tasks/gen-6/0ca3a382a0e3566dfb225d99cd72abd48e988709dba0cbae9fa5f96d68fa4f52/weights.json.sha256
e77c5571f7cb4c824f6b0dce0fe59ac9c7f8ef6b9c6406b78f21d2d18023fedc  coevo/gen-champions/run-c1-crew-owned-tasks/gen-7/b8b35ef4bb7124b540aad336e03efe0d42d9e023fed0721e78533a358ac5e4a9/config.json
9679d658700a67ae0fadb78877e8a6ab676416ccc039ccef2b13929585d752ba  coevo/gen-champions/run-c1-crew-owned-tasks/gen-7/b8b35ef4bb7124b540aad336e03efe0d42d9e023fed0721e78533a358ac5e4a9/stamp.json
b8b35ef4bb7124b540aad336e03efe0d42d9e023fed0721e78533a358ac5e4a9  coevo/gen-champions/run-c1-crew-owned-tasks/gen-7/b8b35ef4bb7124b540aad336e03efe0d42d9e023fed0721e78533a358ac5e4a9/weights.json
1587ab9c358d294b249b2eda7557fb008f4bbd23b295714dbb34c4d65aa6db96  coevo/gen-champions/run-c1-crew-owned-tasks/gen-7/b8b35ef4bb7124b540aad336e03efe0d42d9e023fed0721e78533a358ac5e4a9/weights.json.sha256
ab3a1542697c556ad3cc31414a8c34f9075b4f387f508f21f7580f7bef81a22b  coevo/gen-champions/run-c1-crew-owned-tasks/gen-8/3a7e1c285fca5e15b7e6ab9e8fcbd4fc8cc824004cd4f1c57eff6edbc5a00001/config.json
5027386967a5979bce59dad854d0f02a7af7ef3b5d7cd54f6eaac37a6a81a29b  coevo/gen-champions/run-c1-crew-owned-tasks/gen-8/3a7e1c285fca5e15b7e6ab9e8fcbd4fc8cc824004cd4f1c57eff6edbc5a00001/stamp.json
3a7e1c285fca5e15b7e6ab9e8fcbd4fc8cc824004cd4f1c57eff6edbc5a00001  coevo/gen-champions/run-c1-crew-owned-tasks/gen-8/3a7e1c285fca5e15b7e6ab9e8fcbd4fc8cc824004cd4f1c57eff6edbc5a00001/weights.json
0f9fce92098540268d1e9e6e80d6ee458c9d21e6741ab2989bf035522f1f509b  coevo/gen-champions/run-c1-crew-owned-tasks/gen-8/3a7e1c285fca5e15b7e6ab9e8fcbd4fc8cc824004cd4f1c57eff6edbc5a00001/weights.json.sha256
5bf764f146612a1cf5efe90c88fb1a994757e1b52f395dbc96452b893c0e0c0d  coevo/gen-champions/run-c1-crew-owned-tasks/gen-9/0bf179b719a67c1b40f97377ba49bad6512d08932e0d944e4d024691f60e71df/config.json
a9e14c333e35afbc619ac89b8ed89368a701ff41302b340e3225f1e76357d26c  coevo/gen-champions/run-c1-crew-owned-tasks/gen-9/0bf179b719a67c1b40f97377ba49bad6512d08932e0d944e4d024691f60e71df/stamp.json
0bf179b719a67c1b40f97377ba49bad6512d08932e0d944e4d024691f60e71df  coevo/gen-champions/run-c1-crew-owned-tasks/gen-9/0bf179b719a67c1b40f97377ba49bad6512d08932e0d944e4d024691f60e71df/weights.json
4cb57a89e436030e962d07dc0f8893c60d8a6927dd1dd0983abcc66540a5732c  coevo/gen-champions/run-c1-crew-owned-tasks/gen-9/0bf179b719a67c1b40f97377ba49bad6512d08932e0d944e4d024691f60e71df/weights.json.sha256
efff0cc6a63ca54c818dd00ee348dcead093766f8e8a45d2595f8e23aba76418  coevo/gen-champions/run-c2-crew-general/gen-1/888046d082daf62853c9d10d25dde04e20691c042dcd6a6609492d554ed569bf/config.json
915e42f3f9bf47f758dcfef96fdbc386bfa97d5249e78a65b4ec05086dd6bda4  coevo/gen-champions/run-c2-crew-general/gen-1/888046d082daf62853c9d10d25dde04e20691c042dcd6a6609492d554ed569bf/stamp.json
888046d082daf62853c9d10d25dde04e20691c042dcd6a6609492d554ed569bf  coevo/gen-champions/run-c2-crew-general/gen-1/888046d082daf62853c9d10d25dde04e20691c042dcd6a6609492d554ed569bf/weights.json
3bc930aeefc9ee9b144959259c6375dde8873f7c6ab647f9806a8537300bd5e9  coevo/gen-champions/run-c2-crew-general/gen-1/888046d082daf62853c9d10d25dde04e20691c042dcd6a6609492d554ed569bf/weights.json.sha256
482ef21cadbe65db860e929137a02d2cc2c48a46459a329a89a451cb03458791  coevo/gen-champions/run-c2-crew-general/gen-10/e37b009b0febbf4fb6498e2cb0d8af946ac8878aaede90dcf74134fd668c1044/config.json
07158ce491a1a6da9579631eb5f776884643cd5c5aacda5c4add39403f58c654  coevo/gen-champions/run-c2-crew-general/gen-10/e37b009b0febbf4fb6498e2cb0d8af946ac8878aaede90dcf74134fd668c1044/stamp.json
e37b009b0febbf4fb6498e2cb0d8af946ac8878aaede90dcf74134fd668c1044  coevo/gen-champions/run-c2-crew-general/gen-10/e37b009b0febbf4fb6498e2cb0d8af946ac8878aaede90dcf74134fd668c1044/weights.json
60d1ddfb4ba6e847e742930483098bf6bc5daad69432532949a5595b693bd5ae  coevo/gen-champions/run-c2-crew-general/gen-10/e37b009b0febbf4fb6498e2cb0d8af946ac8878aaede90dcf74134fd668c1044/weights.json.sha256
a2faa3d9a951739b166b53047e713495861e420b82573cab184cc0b097ce7b47  coevo/gen-champions/run-c2-crew-general/gen-11/e37b009b0febbf4fb6498e2cb0d8af946ac8878aaede90dcf74134fd668c1044/config.json
702a01a5b2b50c575273b994e7ac3ecada7a3f810bbb115cc6ee08ceb85ba532  coevo/gen-champions/run-c2-crew-general/gen-11/e37b009b0febbf4fb6498e2cb0d8af946ac8878aaede90dcf74134fd668c1044/stamp.json
e37b009b0febbf4fb6498e2cb0d8af946ac8878aaede90dcf74134fd668c1044  coevo/gen-champions/run-c2-crew-general/gen-11/e37b009b0febbf4fb6498e2cb0d8af946ac8878aaede90dcf74134fd668c1044/weights.json
60d1ddfb4ba6e847e742930483098bf6bc5daad69432532949a5595b693bd5ae  coevo/gen-champions/run-c2-crew-general/gen-11/e37b009b0febbf4fb6498e2cb0d8af946ac8878aaede90dcf74134fd668c1044/weights.json.sha256
4a8297f4a8dd25f29f3f838e484c908b0d52145a9a07119019b433b70e0fa07c  coevo/gen-champions/run-c2-crew-general/gen-12/105f7a88d719bddbe094ebe05a9cac6ce096391562f38cb379ec73d87af4815a/config.json
edfef023ae5659d7b1069a13cb073ac7f9ed450693a267cd484916c6060109fd  coevo/gen-champions/run-c2-crew-general/gen-12/105f7a88d719bddbe094ebe05a9cac6ce096391562f38cb379ec73d87af4815a/stamp.json
105f7a88d719bddbe094ebe05a9cac6ce096391562f38cb379ec73d87af4815a  coevo/gen-champions/run-c2-crew-general/gen-12/105f7a88d719bddbe094ebe05a9cac6ce096391562f38cb379ec73d87af4815a/weights.json
932d111509646f2e7dcf3f35a3a4bcd862f50e3d56e1626da76278e65b4c1481  coevo/gen-champions/run-c2-crew-general/gen-12/105f7a88d719bddbe094ebe05a9cac6ce096391562f38cb379ec73d87af4815a/weights.json.sha256
2ab5f2e71d7f17b99e51256e02f223b8cffd220e10a1c3cace18805294795d74  coevo/gen-champions/run-c2-crew-general/gen-2/bd7770afb500087454504b78ee9a2520449faad7740078194e11a8961a56e534/config.json
c8d83f4dea1e5c4159cc862cc86f025fc9d0d26bce6ae88017ef86c99eff1cf2  coevo/gen-champions/run-c2-crew-general/gen-2/bd7770afb500087454504b78ee9a2520449faad7740078194e11a8961a56e534/stamp.json
bd7770afb500087454504b78ee9a2520449faad7740078194e11a8961a56e534  coevo/gen-champions/run-c2-crew-general/gen-2/bd7770afb500087454504b78ee9a2520449faad7740078194e11a8961a56e534/weights.json
65ddde3e13e6d88155415c7aaafc3f784fcd362782fd1c17c4e3d6b0d126f4e3  coevo/gen-champions/run-c2-crew-general/gen-2/bd7770afb500087454504b78ee9a2520449faad7740078194e11a8961a56e534/weights.json.sha256
1230dceb97d380a5a23fad649a670b112c1abae19197b6f1646ed024bfd65493  coevo/gen-champions/run-c2-crew-general/gen-3/7fa59718d8810a3c26214309eaf6b637a1afc66dc3ea923ab887152f4e985acd/config.json
8274bff66595bf6ed35cfa960bad47560d2dda477ec66b21470ee695a7bc527f  coevo/gen-champions/run-c2-crew-general/gen-3/7fa59718d8810a3c26214309eaf6b637a1afc66dc3ea923ab887152f4e985acd/stamp.json
7fa59718d8810a3c26214309eaf6b637a1afc66dc3ea923ab887152f4e985acd  coevo/gen-champions/run-c2-crew-general/gen-3/7fa59718d8810a3c26214309eaf6b637a1afc66dc3ea923ab887152f4e985acd/weights.json
24cfc15c56aa50abfab0f8edf021e5dcab03a3cf5bf514bd91cdc6a894bbe507  coevo/gen-champions/run-c2-crew-general/gen-3/7fa59718d8810a3c26214309eaf6b637a1afc66dc3ea923ab887152f4e985acd/weights.json.sha256
bfc006413cf8c177daacfbdfec56f91c54b876a87ff337efab4b7b615bc66d91  coevo/gen-champions/run-c2-crew-general/gen-4/1577942ba6435b20c9298dd2ce3c07af1135a70c55d69905675bfcf3e94dc9a4/config.json
b3e86b92ac3e4d5a6f1f18ea6395fa068f0513b5e4e674ebee4cc8ea0fe2a8a1  coevo/gen-champions/run-c2-crew-general/gen-4/1577942ba6435b20c9298dd2ce3c07af1135a70c55d69905675bfcf3e94dc9a4/stamp.json
1577942ba6435b20c9298dd2ce3c07af1135a70c55d69905675bfcf3e94dc9a4  coevo/gen-champions/run-c2-crew-general/gen-4/1577942ba6435b20c9298dd2ce3c07af1135a70c55d69905675bfcf3e94dc9a4/weights.json
b23cb1818bbc4c1b76606826eabe74df8d1bcaa42920285bb3072697f0d6e205  coevo/gen-champions/run-c2-crew-general/gen-4/1577942ba6435b20c9298dd2ce3c07af1135a70c55d69905675bfcf3e94dc9a4/weights.json.sha256
5bd8be7a7ad369c63305fdaa194fba38fec148c8183310eebb70c09f13832d9b  coevo/gen-champions/run-c2-crew-general/gen-5/1577942ba6435b20c9298dd2ce3c07af1135a70c55d69905675bfcf3e94dc9a4/config.json
e171e62261bd6a4876f22e33348f617cf0fbfbb0d1685f7ac32051332dbe86d2  coevo/gen-champions/run-c2-crew-general/gen-5/1577942ba6435b20c9298dd2ce3c07af1135a70c55d69905675bfcf3e94dc9a4/stamp.json
1577942ba6435b20c9298dd2ce3c07af1135a70c55d69905675bfcf3e94dc9a4  coevo/gen-champions/run-c2-crew-general/gen-5/1577942ba6435b20c9298dd2ce3c07af1135a70c55d69905675bfcf3e94dc9a4/weights.json
b23cb1818bbc4c1b76606826eabe74df8d1bcaa42920285bb3072697f0d6e205  coevo/gen-champions/run-c2-crew-general/gen-5/1577942ba6435b20c9298dd2ce3c07af1135a70c55d69905675bfcf3e94dc9a4/weights.json.sha256
d75241100ad7d4c7c86eaa69a1b0754db3ed0130a04fd9c71272ee99aa76e1ce  coevo/gen-champions/run-c2-crew-general/gen-6/1577942ba6435b20c9298dd2ce3c07af1135a70c55d69905675bfcf3e94dc9a4/config.json
383d50773f22efeb009ae34c3e94e8793ffdd6918877411c963bd9d420f1fcac  coevo/gen-champions/run-c2-crew-general/gen-6/1577942ba6435b20c9298dd2ce3c07af1135a70c55d69905675bfcf3e94dc9a4/stamp.json
1577942ba6435b20c9298dd2ce3c07af1135a70c55d69905675bfcf3e94dc9a4  coevo/gen-champions/run-c2-crew-general/gen-6/1577942ba6435b20c9298dd2ce3c07af1135a70c55d69905675bfcf3e94dc9a4/weights.json
b23cb1818bbc4c1b76606826eabe74df8d1bcaa42920285bb3072697f0d6e205  coevo/gen-champions/run-c2-crew-general/gen-6/1577942ba6435b20c9298dd2ce3c07af1135a70c55d69905675bfcf3e94dc9a4/weights.json.sha256
27347845c351d4d582c3f26457f159014af601269779770c909e7eaa629d177a  coevo/gen-champions/run-c2-crew-general/gen-7/18112eb81d9ff9e3ea87782c5cd2619ed79a316e65426fa7bf45f4ed96a60a9a/config.json
e3711baff371cc84d1a4decb4971fa2b90c6cba71431f9dbf71186643729673d  coevo/gen-champions/run-c2-crew-general/gen-7/18112eb81d9ff9e3ea87782c5cd2619ed79a316e65426fa7bf45f4ed96a60a9a/stamp.json
18112eb81d9ff9e3ea87782c5cd2619ed79a316e65426fa7bf45f4ed96a60a9a  coevo/gen-champions/run-c2-crew-general/gen-7/18112eb81d9ff9e3ea87782c5cd2619ed79a316e65426fa7bf45f4ed96a60a9a/weights.json
5e8d108c8aa287dd3e24bee49123eece474ee53d5c85f8d6958cb7332eca1a93  coevo/gen-champions/run-c2-crew-general/gen-7/18112eb81d9ff9e3ea87782c5cd2619ed79a316e65426fa7bf45f4ed96a60a9a/weights.json.sha256
fbd79fee69211bf963564d57d46fda7424749a2dfea377f94d65be19ef7bdbc2  coevo/gen-champions/run-c2-crew-general/gen-8/18112eb81d9ff9e3ea87782c5cd2619ed79a316e65426fa7bf45f4ed96a60a9a/config.json
cb495d8577832d6d8f752e4e6619abfbd3bcaea79f990abf837dc6a1b60e21be  coevo/gen-champions/run-c2-crew-general/gen-8/18112eb81d9ff9e3ea87782c5cd2619ed79a316e65426fa7bf45f4ed96a60a9a/stamp.json
18112eb81d9ff9e3ea87782c5cd2619ed79a316e65426fa7bf45f4ed96a60a9a  coevo/gen-champions/run-c2-crew-general/gen-8/18112eb81d9ff9e3ea87782c5cd2619ed79a316e65426fa7bf45f4ed96a60a9a/weights.json
5e8d108c8aa287dd3e24bee49123eece474ee53d5c85f8d6958cb7332eca1a93  coevo/gen-champions/run-c2-crew-general/gen-8/18112eb81d9ff9e3ea87782c5cd2619ed79a316e65426fa7bf45f4ed96a60a9a/weights.json.sha256
aa351c7bae6395afeee56c30dcf2c13f3cd90e85efedc4758ec8c928bce3164c  coevo/gen-champions/run-c2-crew-general/gen-9/515fc066f7aafc5d3603ab531adb9fe78cd496192c7565e9d8b4d3ff7b09a635/config.json
fab83ba67ae2fe120c1d18b55d9b84687427717300080155d402d981ebe95613  coevo/gen-champions/run-c2-crew-general/gen-9/515fc066f7aafc5d3603ab531adb9fe78cd496192c7565e9d8b4d3ff7b09a635/stamp.json
515fc066f7aafc5d3603ab531adb9fe78cd496192c7565e9d8b4d3ff7b09a635  coevo/gen-champions/run-c2-crew-general/gen-9/515fc066f7aafc5d3603ab531adb9fe78cd496192c7565e9d8b4d3ff7b09a635/weights.json
5ab7175099e0c0772e1b4480259decd294c4c8af5db72e8c97c325fb73fb3628  coevo/gen-champions/run-c2-crew-general/gen-9/515fc066f7aafc5d3603ab531adb9fe78cd496192c7565e9d8b4d3ff7b09a635/weights.json.sha256
73df542e87fcce6761d5bbfafe09998a1b2a017e2ac261ed06e6b6f4197295f9  coevo/intermediates/run-02-utility-lambda4/gen-1/dff6e472e00a0c23498164cec78c96f7a9b1cf29e065c65dce60edcc54d9ec7f/config.json
122c3d19999bd6932d90cb203557153620fa8cfc075c7ada93de2f20b8757e90  coevo/intermediates/run-02-utility-lambda4/gen-1/dff6e472e00a0c23498164cec78c96f7a9b1cf29e065c65dce60edcc54d9ec7f/stamp.json
dff6e472e00a0c23498164cec78c96f7a9b1cf29e065c65dce60edcc54d9ec7f  coevo/intermediates/run-02-utility-lambda4/gen-1/dff6e472e00a0c23498164cec78c96f7a9b1cf29e065c65dce60edcc54d9ec7f/weights.json
29ed120727cd2cb8bcaee99f94e9d2c41b4a6b68f7f9c1727f94aed792ea42c0  coevo/intermediates/run-02-utility-lambda4/gen-1/dff6e472e00a0c23498164cec78c96f7a9b1cf29e065c65dce60edcc54d9ec7f/weights.json.sha256
4db97102311e8b3b84a2288a89e1948404ae457a9c3ab82d70f20f3db5962200  coevo/intermediates/run-03-utility-bcanchor/gen-7/9bc30c15684e831d974c2dc35af20ec30f7e5ce2d295cfae327b605a625e069f/config.json
982ef7c138be12855f6a83884ae854049caac95e81c16f8d3f08b30b302e55cf  coevo/intermediates/run-03-utility-bcanchor/gen-7/9bc30c15684e831d974c2dc35af20ec30f7e5ce2d295cfae327b605a625e069f/stamp.json
9bc30c15684e831d974c2dc35af20ec30f7e5ce2d295cfae327b605a625e069f  coevo/intermediates/run-03-utility-bcanchor/gen-7/9bc30c15684e831d974c2dc35af20ec30f7e5ce2d295cfae327b605a625e069f/weights.json
5d091982dc1ca4365340007263cbbe77c66e7cd1c9c26ff31fe9e279f07c554f  coevo/intermediates/run-03-utility-bcanchor/gen-7/9bc30c15684e831d974c2dc35af20ec30f7e5ce2d295cfae327b605a625e069f/weights.json.sha256
1cdf43800f8484109d45606d01f497353f4eb12a2d74cfcaa143becd199692c6  coevo/intermediates/run-04-freepolicy-v3/gen-1/b775a7e6fd9e74c9618df6d020798c4051e0815c96b633ebe847f1cc4f6858ff/config.json
93c13c5f1662e281543a00e4e138c4fe14069904383eb50d8272ff155db3b586  coevo/intermediates/run-04-freepolicy-v3/gen-1/b775a7e6fd9e74c9618df6d020798c4051e0815c96b633ebe847f1cc4f6858ff/stamp.json
b775a7e6fd9e74c9618df6d020798c4051e0815c96b633ebe847f1cc4f6858ff  coevo/intermediates/run-04-freepolicy-v3/gen-1/b775a7e6fd9e74c9618df6d020798c4051e0815c96b633ebe847f1cc4f6858ff/weights.json
52d23b97364ca87ad616853b39d1209182a1cc00f6380f24d6758d4dd5cc0522  coevo/intermediates/run-04-freepolicy-v3/gen-1/b775a7e6fd9e74c9618df6d020798c4051e0815c96b633ebe847f1cc4f6858ff/weights.json.sha256
ca275a78677dd2a4a89c413b3d5221a4e0b5306ee44be1b2bfed69ee0815dbcd  coevo/intermediates/run-04-freepolicy-v3/gen-2/ee28facfba05f0b016662dcfe528241cea20cca2e46248bad7022143f4486a9a/config.json
c540406ff69b79699cb308e4d1a38104aabdf8a9084e8376fd33d7a862f244f0  coevo/intermediates/run-04-freepolicy-v3/gen-2/ee28facfba05f0b016662dcfe528241cea20cca2e46248bad7022143f4486a9a/stamp.json
ee28facfba05f0b016662dcfe528241cea20cca2e46248bad7022143f4486a9a  coevo/intermediates/run-04-freepolicy-v3/gen-2/ee28facfba05f0b016662dcfe528241cea20cca2e46248bad7022143f4486a9a/weights.json
d1e6356c910c336aadd0499e152597e93b35fdad1415ea2bc01d79c1314eab32  coevo/intermediates/run-04-freepolicy-v3/gen-2/ee28facfba05f0b016662dcfe528241cea20cca2e46248bad7022143f4486a9a/weights.json.sha256
a52ba708be4cddb0caca4c83adf9ceec12e22a74f68e11c77545a781b35d60bf  coevo/realpath-ablation/ablation-run-04-encoder-v3/prescreen-quotes-4000-4002.json
a52ba708be4cddb0caca4c83adf9ceec12e22a74f68e11c77545a781b35d60bf  coevo/realpath-ablation/ablation-run-04-encoder-v3/prescreen-quotes-4003-4005.json
28c8ade320f8e73076a79cb6b664cac77d691c5cfefd0f2250db6598fb3be3bc  coevo/realpath-ablation/ablation-run-04-encoder-v3/recordings-4000-4002/000-ablation-run-04-encoder-v3-gen9-bfa517676dd4/replay-seed-4000.jsonl
6b304046a54a2cf1680de110ace64a4953a54826fc95fb2def578ee71d34d76b  coevo/realpath-ablation/ablation-run-04-encoder-v3/recordings-4000-4002/000-ablation-run-04-encoder-v3-gen9-bfa517676dd4/replay-seed-4001.jsonl
851378e702984ed8c218c3f45f3e8ac8749631b78aa9355f66d5165a9b7343c8  coevo/realpath-ablation/ablation-run-04-encoder-v3/recordings-4000-4002/000-ablation-run-04-encoder-v3-gen9-bfa517676dd4/replay-seed-4002.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath-ablation/ablation-run-04-encoder-v3/recordings-4000-4002/000-ablation-run-04-encoder-v3-gen9-bfa517676dd4/roster.json
5c6384503fde839c8170f5ea2f7515889aa0dacb381e44e8b649944d8528e1a3  coevo/realpath-ablation/ablation-run-04-encoder-v3/recordings-4000-4002/001-ablation-run-04-encoder-v3-gen3-a4076d294a32/replay-seed-4000.jsonl
265178c1b6bdbeaf3b36cc3bb34d9b2907da6c58b83989fd1cba0e963850a86e  coevo/realpath-ablation/ablation-run-04-encoder-v3/recordings-4000-4002/001-ablation-run-04-encoder-v3-gen3-a4076d294a32/replay-seed-4001.jsonl
5f5750e2c597c45553fedcbc4d6c5fccc2adf39f5ccab6090a8efaef5e0bd002  coevo/realpath-ablation/ablation-run-04-encoder-v3/recordings-4000-4002/001-ablation-run-04-encoder-v3-gen3-a4076d294a32/replay-seed-4002.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath-ablation/ablation-run-04-encoder-v3/recordings-4000-4002/001-ablation-run-04-encoder-v3-gen3-a4076d294a32/roster.json
f2d3e5a0874d3234693a7e16c1733d75fa3934127e07b423f4c8df2be12d40db  coevo/realpath-ablation/ablation-run-04-encoder-v3/recordings-4003-4005/000-ablation-run-04-encoder-v3-gen9-bfa517676dd4/replay-seed-4003.jsonl
38a64d77e9042edaa38b7a4bda65732e717f65de5445c51bcb28a1d2764b4cfd  coevo/realpath-ablation/ablation-run-04-encoder-v3/recordings-4003-4005/000-ablation-run-04-encoder-v3-gen9-bfa517676dd4/replay-seed-4004.jsonl
f3bac4e12e938222406953471f6a954835bcf2f461ae0653e36c3da0e8fa807e  coevo/realpath-ablation/ablation-run-04-encoder-v3/recordings-4003-4005/000-ablation-run-04-encoder-v3-gen9-bfa517676dd4/replay-seed-4005.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath-ablation/ablation-run-04-encoder-v3/recordings-4003-4005/000-ablation-run-04-encoder-v3-gen9-bfa517676dd4/roster.json
72a959e88cb682c46d6c7b2f3a53867579aa206626ebcdaa9eb3c0d7b2bbc7ed  coevo/realpath-ablation/ablation-run-04-encoder-v3/recordings-4003-4005/001-ablation-run-04-encoder-v3-gen3-a4076d294a32/replay-seed-4003.jsonl
0cd5c2166d429bb328599f362e3ee3697496318aefa5cd6daff64a531838eb98  coevo/realpath-ablation/ablation-run-04-encoder-v3/recordings-4003-4005/001-ablation-run-04-encoder-v3-gen3-a4076d294a32/replay-seed-4004.jsonl
9b09d11710cd1f5e152416ddd0d6bc93bf7f4d478ed920d62acca60fde1075de  coevo/realpath-ablation/ablation-run-04-encoder-v3/recordings-4003-4005/001-ablation-run-04-encoder-v3-gen3-a4076d294a32/replay-seed-4005.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath-ablation/ablation-run-04-encoder-v3/recordings-4003-4005/001-ablation-run-04-encoder-v3-gen3-a4076d294a32/roster.json
7471feeb55184c6d0bdde34b3bc8caa7397d3791a1a0eabe014b49070c3f0474  coevo/realpath-ablation/ablation-run-04-encoder-v3/recordings-manifest-4003-4005.sha256
9c97d40ffed5371254b0f4ca373a7d60f2f12b5295ce2af419cf49fc84817487  coevo/realpath-ablation/ablation-run-04-encoder-v3/recordings-manifest.sha256
4b5e84cebe9267c4ac056977c63a9f9fc4460a35c416ac06e7c2f4873869d290  coevo/realpath-ablation/ablation-run-04-encoder-v3/sweep-4000-4002.json
422aad9e5950af3bc33c599d37b0b03a5014170bd49174b382e39c3e886ce0f5  coevo/realpath-backfill/recordings-manifest.sha256
40755b432fcc9957852db34f38f88e35401bb640618aae9f3e544c12dd91a771  coevo/realpath-backfill/run-02-utility-lambda4/prescreen-quotes-4000-4002.json
40755b432fcc9957852db34f38f88e35401bb640618aae9f3e544c12dd91a771  coevo/realpath-backfill/run-02-utility-lambda4/prescreen-quotes-4003-4005.json
d3bc2ab62bb56b47583265dfb81c9f38a32187d1451b3a7eb4bc085b44bca2cc  coevo/realpath-backfill/run-02-utility-lambda4/recordings-4000-4002/000-run-02-utility-lambda4-intermediate-gen1-dff6e472e00a/replay-seed-4000.jsonl
993bc65db0d418f4b0611bf15e1ef15d24841f94355cbdbbdafe0ea1a9df841f  coevo/realpath-backfill/run-02-utility-lambda4/recordings-4000-4002/000-run-02-utility-lambda4-intermediate-gen1-dff6e472e00a/replay-seed-4001.jsonl
9cd91da1d68e41f751c9a0feb7afac24f0de06259c1549a814a03aa68cdde632  coevo/realpath-backfill/run-02-utility-lambda4/recordings-4000-4002/000-run-02-utility-lambda4-intermediate-gen1-dff6e472e00a/replay-seed-4002.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath-backfill/run-02-utility-lambda4/recordings-4000-4002/000-run-02-utility-lambda4-intermediate-gen1-dff6e472e00a/roster.json
1afc2d1b77d6bcb1bc4b29501942cc0428623b66df1402e2d96b05fd23f46c58  coevo/realpath-backfill/run-02-utility-lambda4/recordings-4000-4002/001-run-02-utility-lambda4-intermediate-gen2-ea4bc955dfe0/replay-seed-4000.jsonl
2bcacb1cf3db61e18ea3d94b3aa1a1e62f6105a8d316f635e74e511b337edb54  coevo/realpath-backfill/run-02-utility-lambda4/recordings-4000-4002/001-run-02-utility-lambda4-intermediate-gen2-ea4bc955dfe0/replay-seed-4001.jsonl
1d92412382fe9e7de1ab976ec20e17371fb4ca7063d54af1764fa293bed2fc78  coevo/realpath-backfill/run-02-utility-lambda4/recordings-4000-4002/001-run-02-utility-lambda4-intermediate-gen2-ea4bc955dfe0/replay-seed-4002.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath-backfill/run-02-utility-lambda4/recordings-4000-4002/001-run-02-utility-lambda4-intermediate-gen2-ea4bc955dfe0/roster.json
44f53f83fc31865468668734013e0d4c366b98ebf020cc7a6d4badcb13a6511b  coevo/realpath-backfill/run-02-utility-lambda4/recordings-4003-4005/000-run-02-utility-lambda4-intermediate-gen1-dff6e472e00a/replay-seed-4003.jsonl
41ebf60d59463c66da79f2bf083365f2b7ba2e1dff15381237efce2a2dd93bc0  coevo/realpath-backfill/run-02-utility-lambda4/recordings-4003-4005/000-run-02-utility-lambda4-intermediate-gen1-dff6e472e00a/replay-seed-4004.jsonl
11b76ec7efe4ee3d346def85dd6b758b6e55fc0912b7da48cfecf33f8cd04e34  coevo/realpath-backfill/run-02-utility-lambda4/recordings-4003-4005/000-run-02-utility-lambda4-intermediate-gen1-dff6e472e00a/replay-seed-4005.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath-backfill/run-02-utility-lambda4/recordings-4003-4005/000-run-02-utility-lambda4-intermediate-gen1-dff6e472e00a/roster.json
846ca5cea2f9bd3ec9ff3b1fc299e0bd0a6f5899442bf9026e8bfd43aae331d6  coevo/realpath-backfill/run-02-utility-lambda4/recordings-4003-4005/001-run-02-utility-lambda4-intermediate-gen2-ea4bc955dfe0/replay-seed-4003.jsonl
789943d5aa811c87e6702d97c05f0de7b43c6473c691e63d92449906ca5dc31a  coevo/realpath-backfill/run-02-utility-lambda4/recordings-4003-4005/001-run-02-utility-lambda4-intermediate-gen2-ea4bc955dfe0/replay-seed-4004.jsonl
9e0979825e2acc64938b452735ff122e42fe4a0c5ae6591d9195b5a62db85338  coevo/realpath-backfill/run-02-utility-lambda4/recordings-4003-4005/001-run-02-utility-lambda4-intermediate-gen2-ea4bc955dfe0/replay-seed-4005.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath-backfill/run-02-utility-lambda4/recordings-4003-4005/001-run-02-utility-lambda4-intermediate-gen2-ea4bc955dfe0/roster.json
d23b8960a875c728b521b7138c43359122abbeaba0a834d119b2c5a9609139cc  coevo/realpath-backfill/run-02-utility-lambda4/sweep-4000-4002.json
5f37873730837a3d201f1d28cbcd1aae9e63fe3272988e0d2c7d18af94f4922d  coevo/realpath-backfill/run-02-utility-lambda4/sweep-4003-4005.json
4c889a62447413ee809eb6110dc81d65aba585ea0d63132801c3485d77d37241  coevo/realpath-backfill/run-03-utility-bcanchor/prescreen-quotes-4000-4002.json
4c889a62447413ee809eb6110dc81d65aba585ea0d63132801c3485d77d37241  coevo/realpath-backfill/run-03-utility-bcanchor/prescreen-quotes-4003-4005.json
7a1d432965d452222a0ff3f92a99f9419a9d276bb89b833404a3e1ba687ddab5  coevo/realpath-backfill/run-03-utility-bcanchor/recordings-4000-4002/000-run-03-utility-bcanchor-intermediate-gen7-9bc30c15684e/replay-seed-4000.jsonl
b76832841c872da87cb231c0860d54004ad5078d808a469d86d43afe3b382765  coevo/realpath-backfill/run-03-utility-bcanchor/recordings-4000-4002/000-run-03-utility-bcanchor-intermediate-gen7-9bc30c15684e/replay-seed-4001.jsonl
ae647cb875f4e6e89f0f4deb82452b3d46d2e199b28cebee7c3c89bda0d7780e  coevo/realpath-backfill/run-03-utility-bcanchor/recordings-4000-4002/000-run-03-utility-bcanchor-intermediate-gen7-9bc30c15684e/replay-seed-4002.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath-backfill/run-03-utility-bcanchor/recordings-4000-4002/000-run-03-utility-bcanchor-intermediate-gen7-9bc30c15684e/roster.json
730267a6ca377cb4d07a76a8eedd6253cae5286838f98b85c706770bcdb3cdbd  coevo/realpath-backfill/run-03-utility-bcanchor/recordings-4003-4005/000-run-03-utility-bcanchor-intermediate-gen7-9bc30c15684e/replay-seed-4003.jsonl
95ad5b024db33a81dff61736e2bf34557d6af931b47e968317d7ed3dd03b8119  coevo/realpath-backfill/run-03-utility-bcanchor/recordings-4003-4005/000-run-03-utility-bcanchor-intermediate-gen7-9bc30c15684e/replay-seed-4004.jsonl
c153dee0623e77e34b2c2cd4a16a6237e521fb6fe8c1be3eee35968f4f58bd0e  coevo/realpath-backfill/run-03-utility-bcanchor/recordings-4003-4005/000-run-03-utility-bcanchor-intermediate-gen7-9bc30c15684e/replay-seed-4005.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath-backfill/run-03-utility-bcanchor/recordings-4003-4005/000-run-03-utility-bcanchor-intermediate-gen7-9bc30c15684e/roster.json
dae3e74c4196288257387ab4b29132ce1782fb8381c73ee4cfc420842a914ecb  coevo/realpath-backfill/run-03-utility-bcanchor/sweep-4000-4002.json
54b7b30bc5d399c819a90ab384b316856bca357cf4a5192f02dba2cf5212707c  coevo/realpath-backfill/run-03-utility-bcanchor/sweep-4003-4005.json
ab15926a53c3e27d5b767512f9086aad354bddbac319c851686f747d79cb50e6  coevo/realpath-backfill/run-04-freepolicy-v3/prescreen-quotes-4000-4002.json
ab15926a53c3e27d5b767512f9086aad354bddbac319c851686f747d79cb50e6  coevo/realpath-backfill/run-04-freepolicy-v3/prescreen-quotes-4003-4005.json
d9316d08ee8962dfef834d3002c980c226447497891ba11d11d29281f879d14a  coevo/realpath-backfill/run-04-freepolicy-v3/recordings-4000-4002/000-run-04-freepolicy-v3-intermediate-gen1-b775a7e6fd9e/replay-seed-4000.jsonl
75265d7b051d1d9e82c57c05299e2d67453cd8a856b8e5c4a37fed5f90cadebb  coevo/realpath-backfill/run-04-freepolicy-v3/recordings-4000-4002/000-run-04-freepolicy-v3-intermediate-gen1-b775a7e6fd9e/replay-seed-4001.jsonl
5c555f1af8c298deb5b4cbf3dc227f528cc9493baaba789a3fe61fe53002161b  coevo/realpath-backfill/run-04-freepolicy-v3/recordings-4000-4002/000-run-04-freepolicy-v3-intermediate-gen1-b775a7e6fd9e/replay-seed-4002.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath-backfill/run-04-freepolicy-v3/recordings-4000-4002/000-run-04-freepolicy-v3-intermediate-gen1-b775a7e6fd9e/roster.json
61ea8ce4b08d1b427269928ad3d880567809c65f0501032533b3918c228f4e55  coevo/realpath-backfill/run-04-freepolicy-v3/recordings-4000-4002/001-run-04-freepolicy-v3-intermediate-gen2-ee28facfba05/replay-seed-4000.jsonl
50b09761f55de7726d78d3b8cceb7eb26967d9bf3c7a7c5be966537babc52a37  coevo/realpath-backfill/run-04-freepolicy-v3/recordings-4000-4002/001-run-04-freepolicy-v3-intermediate-gen2-ee28facfba05/replay-seed-4001.jsonl
e610c70810ce9f4c66fd1f215507365ef9cb51bafbfbe29e083410f20e52ef6b  coevo/realpath-backfill/run-04-freepolicy-v3/recordings-4000-4002/001-run-04-freepolicy-v3-intermediate-gen2-ee28facfba05/replay-seed-4002.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath-backfill/run-04-freepolicy-v3/recordings-4000-4002/001-run-04-freepolicy-v3-intermediate-gen2-ee28facfba05/roster.json
3f4562304f28dbf2ac215d2d67681b3c1774a7496fd2f9b41697e4f9d29274a3  coevo/realpath-backfill/run-04-freepolicy-v3/recordings-4003-4005/000-run-04-freepolicy-v3-intermediate-gen1-b775a7e6fd9e/replay-seed-4003.jsonl
42b90b672b1f43ec995d02d1b54fb75523cbb36601da71aa19aec7bc3580c84f  coevo/realpath-backfill/run-04-freepolicy-v3/recordings-4003-4005/000-run-04-freepolicy-v3-intermediate-gen1-b775a7e6fd9e/replay-seed-4004.jsonl
f2ead837d8857c52ecb1c9ce898d22671122b7a085d99da3d6ce22266c3f3aac  coevo/realpath-backfill/run-04-freepolicy-v3/recordings-4003-4005/000-run-04-freepolicy-v3-intermediate-gen1-b775a7e6fd9e/replay-seed-4005.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath-backfill/run-04-freepolicy-v3/recordings-4003-4005/000-run-04-freepolicy-v3-intermediate-gen1-b775a7e6fd9e/roster.json
581260285b1943a5611a80c4e10cb2b67ba0b4e5ad3d77f123c2e7ea9c759e4b  coevo/realpath-backfill/run-04-freepolicy-v3/recordings-4003-4005/001-run-04-freepolicy-v3-intermediate-gen2-ee28facfba05/replay-seed-4003.jsonl
15d99490edf4ccf28568bd71c68d6905c3beb9974bf75ed1f6820c7410ac3933  coevo/realpath-backfill/run-04-freepolicy-v3/recordings-4003-4005/001-run-04-freepolicy-v3-intermediate-gen2-ee28facfba05/replay-seed-4004.jsonl
083173658f041f5d3343334d6e2e3f1a065eadc813905c0ca4c1d7fdfcb7c91e  coevo/realpath-backfill/run-04-freepolicy-v3/recordings-4003-4005/001-run-04-freepolicy-v3-intermediate-gen2-ee28facfba05/replay-seed-4005.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath-backfill/run-04-freepolicy-v3/recordings-4003-4005/001-run-04-freepolicy-v3-intermediate-gen2-ee28facfba05/roster.json
b63dca0fccaff2426329043e1184f207a337970f2f4b41d6804b0e15e9167ed8  coevo/realpath-backfill/run-04-freepolicy-v3/sweep-4000-4002.json
cdb43fec02551ba241faac17b839f594f13bce33907d9763e972c9bb98de07f3  coevo/realpath-backfill/run-04-freepolicy-v3/sweep-4003-4005.json
cd7482ad2ec791c29238c005661ab8629125e72b5105b2aac12d3089d7615cf4  coevo/realpath-comparator/fsm-4000-4002/replay-seed-4000.jsonl
45ec72963c4f8129f8b4dd02331d74ece5611b274837f103b65f5e9304b046b8  coevo/realpath-comparator/fsm-4000-4002/replay-seed-4001.jsonl
9fe1bd47e74bf6fcf0fdb429b46a6be4a722a9c8a6b24a8109fcc7868c0bf8e1  coevo/realpath-comparator/fsm-4000-4002/replay-seed-4002.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath-comparator/fsm-4000-4002/roster.json
6933c79d260eb85fe8413b19ebca60cf64ed549a08f02da93891d39fdcf645c5  coevo/realpath-comparator/recordings-manifest.sha256
abdeb9aa00204d663fde8363a8869b2813d5829d935c043d86534ea970929eb9  coevo/realpath-comparator/sweep-4000-4002.json
7fc4b02815e2224289d12059cfe141d1be0da41892f235190bfc4fd13b74c5bb  coevo/realpath-crew/run-c1-crew-owned-tasks/measurement-stability-c1.json
003e69aacaf3587de75870a3fe311b22a2a711fc11224302e2aff380f1e638df  coevo/realpath-crew/run-c1-crew-owned-tasks/recordings-4000-4002/000-c1-gen0-owned-tasks-es/replay-seed-4000.jsonl
f0d93d428bec5daafed261392850d2b6dd8618e9575ecc28f6c95e725bed4c93  coevo/realpath-crew/run-c1-crew-owned-tasks/recordings-4000-4002/000-c1-gen0-owned-tasks-es/replay-seed-4001.jsonl
3267c386bea6d230928624e74a3f337b62f3f20080d7f908824464a9adbe2e94  coevo/realpath-crew/run-c1-crew-owned-tasks/recordings-4000-4002/000-c1-gen0-owned-tasks-es/replay-seed-4002.jsonl
242f79570d37c50deda87c684f5f031800f79622483435a16fa52d7e0f778385  coevo/realpath-crew/run-c1-crew-owned-tasks/recordings-4000-4002/000-c1-gen0-owned-tasks-es/roster.json
45a3085b96eb991c5a515ca1c573129693d371b484410953cc6f9ecf97ae957c  coevo/realpath-crew/run-c1-crew-owned-tasks/recordings-4000-4002/001-c1-swap0-champ-gen3/replay-seed-4000.jsonl
caa91cfae156af724ac9b5c5e8791a897894eeecf3c1e26fc0603656083d63b0  coevo/realpath-crew/run-c1-crew-owned-tasks/recordings-4000-4002/001-c1-swap0-champ-gen3/replay-seed-4001.jsonl
e14a30e9505b1046198324caed0bbc42ea26e303481490328316454b9cc04315  coevo/realpath-crew/run-c1-crew-owned-tasks/recordings-4000-4002/001-c1-swap0-champ-gen3/replay-seed-4002.jsonl
242f79570d37c50deda87c684f5f031800f79622483435a16fa52d7e0f778385  coevo/realpath-crew/run-c1-crew-owned-tasks/recordings-4000-4002/001-c1-swap0-champ-gen3/roster.json
a4feab4e1bd2fe13e8996acca299968b9163ecc2ec801eb31309a6df15625afe  coevo/realpath-crew/run-c1-crew-owned-tasks/recordings-4000-4002/002-c1-swap2-champ-gen9/replay-seed-4000.jsonl
bc9d533283b2f6008f596bd672cbd5b5fa0f318e880278cfc197c8059bcd5757  coevo/realpath-crew/run-c1-crew-owned-tasks/recordings-4000-4002/002-c1-swap2-champ-gen9/replay-seed-4001.jsonl
656a958aee7966b68c028f576aaf09f4a799f6a0d3bab573d005cbd51662dab7  coevo/realpath-crew/run-c1-crew-owned-tasks/recordings-4000-4002/002-c1-swap2-champ-gen9/replay-seed-4002.jsonl
242f79570d37c50deda87c684f5f031800f79622483435a16fa52d7e0f778385  coevo/realpath-crew/run-c1-crew-owned-tasks/recordings-4000-4002/002-c1-swap2-champ-gen9/roster.json
16d3ed0df89b39139343154d50e4970ac41fce713c07afcf5d0ae39e5f08e235  coevo/realpath-crew/run-c1-crew-owned-tasks/recordings-4000-4002/leg-4000-4002-000.json
c95a12169c356a9b650f7391ed66ad5e097ac10c29d56e4daf9c8e42e5fdaa39  coevo/realpath-crew/run-c1-crew-owned-tasks/recordings-4000-4002/leg-log.jsonl
80d273f95a709eaf35f909549b806dd0ce5dac4506e5c776107af4eb7261313e  coevo/realpath-crew/run-c1-crew-owned-tasks/recordings-4003-4005/000-c1-gen0-owned-tasks-es/replay-seed-4003.jsonl
78201ab43e29e4a546a4382e5dd0ddf081bcbc8221f70e0c6ddb352917c5fb3c  coevo/realpath-crew/run-c1-crew-owned-tasks/recordings-4003-4005/000-c1-gen0-owned-tasks-es/replay-seed-4004.jsonl
381217232b5ae62415a170a5f8dc9cccd9f1a8c5d25db4104c54003bf5c37d51  coevo/realpath-crew/run-c1-crew-owned-tasks/recordings-4003-4005/000-c1-gen0-owned-tasks-es/replay-seed-4005.jsonl
242f79570d37c50deda87c684f5f031800f79622483435a16fa52d7e0f778385  coevo/realpath-crew/run-c1-crew-owned-tasks/recordings-4003-4005/000-c1-gen0-owned-tasks-es/roster.json
a3f5b36cd2e71aebfa7e22ac54cf6746af7d4f66968ac91b79dbd2d68820b6b4  coevo/realpath-crew/run-c1-crew-owned-tasks/recordings-4003-4005/001-c1-swap0-champ-gen3/replay-seed-4003.jsonl
05ab42f11321f3a29a21d0508199ec8f032f157a957384245885243f5eac633f  coevo/realpath-crew/run-c1-crew-owned-tasks/recordings-4003-4005/001-c1-swap0-champ-gen3/replay-seed-4004.jsonl
4282cbc185b936dec23ea8436ab6f83e77919c4d21b1a5ba3e2f160a237b0de5  coevo/realpath-crew/run-c1-crew-owned-tasks/recordings-4003-4005/001-c1-swap0-champ-gen3/replay-seed-4005.jsonl
242f79570d37c50deda87c684f5f031800f79622483435a16fa52d7e0f778385  coevo/realpath-crew/run-c1-crew-owned-tasks/recordings-4003-4005/001-c1-swap0-champ-gen3/roster.json
869a92402303d9c38f633e30f078c887da578134765cdf2b1967cf558f95c687  coevo/realpath-crew/run-c1-crew-owned-tasks/recordings-4003-4005/002-c1-swap2-champ-gen9/replay-seed-4003.jsonl
3179314ad8a4efcbe16c0031de2e95ce35044bbb537c9733930a28ffac0e3423  coevo/realpath-crew/run-c1-crew-owned-tasks/recordings-4003-4005/002-c1-swap2-champ-gen9/replay-seed-4004.jsonl
10fb7f0af6a315532a495ed1ed68ca16ef96e60428da44cee7e1e2d5621cb618  coevo/realpath-crew/run-c1-crew-owned-tasks/recordings-4003-4005/002-c1-swap2-champ-gen9/replay-seed-4005.jsonl
242f79570d37c50deda87c684f5f031800f79622483435a16fa52d7e0f778385  coevo/realpath-crew/run-c1-crew-owned-tasks/recordings-4003-4005/002-c1-swap2-champ-gen9/roster.json
4f9f233929c2b62ed72b7e4d9e850ab910fd3c3ed947962ab4414011d51dbcb6  coevo/realpath-crew/run-c1-crew-owned-tasks/recordings-4003-4005/leg-4003-4005-000.json
5db0db7b9f7ab52faacfcba8d03a69b50a974e9695ac595584cda24f16f61795  coevo/realpath-crew/run-c1-crew-owned-tasks/recordings-4003-4005/leg-log.jsonl
4e9273ce302090e60951be720971b7c246891ec653d01240f43e7d32c86fcca7  coevo/realpath-crew/run-c1-crew-owned-tasks/recordings-manifest-4000-4002.sha256
00c93b892cb4536179046df27554a8618ee09388a309edccc9d1d583215155e5  coevo/realpath-crew/run-c1-crew-owned-tasks/recordings-manifest-4003-4005.sha256
12c6a9e81fe23f5abd2eefa097c4466806cb51d132ed3c97c3f38ff1605a43ff  coevo/realpath-crew/run-c1-crew-owned-tasks/sweep-4000-4002.json
14c6b57f76d93591de39d6683908bf7248d6643c82dc7abf019f8fb12b3cf643  coevo/realpath-crew/run-c1-crew-owned-tasks/sweep-4003-4005.json
018a8652c898d80a5e0c3fd4d0eebfaa109a5701d2056da0e158082570c04b5b  coevo/realpath-crew/run-c2-crew-general/measurement-stability-c2.json
b4f14015b8de0f08f0c49898b89d442fbd8f1af4da1f87819f25e4ae1e4da16d  coevo/realpath-crew/run-c2-crew-general/recordings-4000-4002/000-c2-gen0-utility-es/replay-seed-4000.jsonl
b1d53d7972ed1071656fc381a1388b19ff40bab47537809686b5554f1fc2ac5b  coevo/realpath-crew/run-c2-crew-general/recordings-4000-4002/000-c2-gen0-utility-es/replay-seed-4001.jsonl
167ee8f384299d3d183f613773ca44b27f4bc3536911bbd951f46fecbe6ac59f  coevo/realpath-crew/run-c2-crew-general/recordings-4000-4002/000-c2-gen0-utility-es/replay-seed-4002.jsonl
242f79570d37c50deda87c684f5f031800f79622483435a16fa52d7e0f778385  coevo/realpath-crew/run-c2-crew-general/recordings-4000-4002/000-c2-gen0-utility-es/roster.json
503018e9d5b6316a8169b45ca3187fbaf5028ad3d2a29b94fe9ad06bbcc4f5fd  coevo/realpath-crew/run-c2-crew-general/recordings-4000-4002/001-c2-swap0-champ-gen3/replay-seed-4000.jsonl
db7b7b9c1748ae9df74ab44d871f5ddd6ad0fce2125ecb502e012990b8a2a878  coevo/realpath-crew/run-c2-crew-general/recordings-4000-4002/001-c2-swap0-champ-gen3/replay-seed-4001.jsonl
1fb9cad040243c45d8d71d29f291bff90d5ce1864a7b3492bfb44a63c4f64204  coevo/realpath-crew/run-c2-crew-general/recordings-4000-4002/001-c2-swap0-champ-gen3/replay-seed-4002.jsonl
242f79570d37c50deda87c684f5f031800f79622483435a16fa52d7e0f778385  coevo/realpath-crew/run-c2-crew-general/recordings-4000-4002/001-c2-swap0-champ-gen3/roster.json
35a6d1930da926f585747b2588babb84d48e719a231cfee03adfa746740e39c5  coevo/realpath-crew/run-c2-crew-general/recordings-4000-4002/002-c2-swap2-champ-gen9/replay-seed-4000.jsonl
88b4ee2675e571827578e32ad225560e5b2bd0d35ea472a70204cecddb091713  coevo/realpath-crew/run-c2-crew-general/recordings-4000-4002/002-c2-swap2-champ-gen9/replay-seed-4001.jsonl
14770a2441fe21a37ef39ec1a1e3cbd2212f69842d7d7a5125bcf3a988eb0932  coevo/realpath-crew/run-c2-crew-general/recordings-4000-4002/002-c2-swap2-champ-gen9/replay-seed-4002.jsonl
242f79570d37c50deda87c684f5f031800f79622483435a16fa52d7e0f778385  coevo/realpath-crew/run-c2-crew-general/recordings-4000-4002/002-c2-swap2-champ-gen9/roster.json
a6bae6376d7efd4e6d4526948d66a03ba18249f8d9014b44f01e8c6d3fd68252  coevo/realpath-crew/run-c2-crew-general/recordings-4000-4002/leg-4000-4002-000.json
a0e8ff77bc62ae90aa82b4e0c85a91ecaf11611f1c816060074e7301516c0855  coevo/realpath-crew/run-c2-crew-general/recordings-4000-4002/leg-log.jsonl
8475e58aa0f493a3b763c830cd447a49cab3de5feec91cc859bb960986474936  coevo/realpath-crew/run-c2-crew-general/recordings-4003-4005/000-c2-gen0-utility-es/replay-seed-4003.jsonl
864a77852afe5476dd4e158ce68d01f1a51e605bd6a69a478afe8162c2773593  coevo/realpath-crew/run-c2-crew-general/recordings-4003-4005/000-c2-gen0-utility-es/replay-seed-4004.jsonl
bb35cecdb21e5a9048e33d0f673de7a73138e0d4150652d84ffc537043bb5a18  coevo/realpath-crew/run-c2-crew-general/recordings-4003-4005/000-c2-gen0-utility-es/replay-seed-4005.jsonl
242f79570d37c50deda87c684f5f031800f79622483435a16fa52d7e0f778385  coevo/realpath-crew/run-c2-crew-general/recordings-4003-4005/000-c2-gen0-utility-es/roster.json
7db6f6cf65f67f3f6aa6677387bd6631c949906ad93f78219c1622cbbc070dba  coevo/realpath-crew/run-c2-crew-general/recordings-4003-4005/001-c2-swap0-champ-gen3/replay-seed-4003.jsonl
59e22f19891e3f2cc68cc5354994833438129f2da2714fac55162cfd368f4204  coevo/realpath-crew/run-c2-crew-general/recordings-4003-4005/001-c2-swap0-champ-gen3/replay-seed-4004.jsonl
17cbd2ea5d0b7c4f0e4c1d811094865091499d83f66ea4c86fe5428446e3934a  coevo/realpath-crew/run-c2-crew-general/recordings-4003-4005/001-c2-swap0-champ-gen3/replay-seed-4005.jsonl
242f79570d37c50deda87c684f5f031800f79622483435a16fa52d7e0f778385  coevo/realpath-crew/run-c2-crew-general/recordings-4003-4005/001-c2-swap0-champ-gen3/roster.json
bba5fc1db80d34200ffd7a22dfb5262160306a27942f7a56d461a02c00dcd6f1  coevo/realpath-crew/run-c2-crew-general/recordings-4003-4005/002-c2-swap2-champ-gen9/replay-seed-4003.jsonl
3f9f21c4309679c8657bbc01a5bdd0bceed47e8cff9cf8940553e4788306ff20  coevo/realpath-crew/run-c2-crew-general/recordings-4003-4005/002-c2-swap2-champ-gen9/replay-seed-4004.jsonl
042513171ac8181529548e74c5fd5f0a5626b756f374e35b95751f8640e9bc5e  coevo/realpath-crew/run-c2-crew-general/recordings-4003-4005/002-c2-swap2-champ-gen9/replay-seed-4005.jsonl
242f79570d37c50deda87c684f5f031800f79622483435a16fa52d7e0f778385  coevo/realpath-crew/run-c2-crew-general/recordings-4003-4005/002-c2-swap2-champ-gen9/roster.json
67d3431a858e6a0f07d8a6b0eb4fd24d04be6bca8d19abac00678a7094e3c958  coevo/realpath-crew/run-c2-crew-general/recordings-4003-4005/leg-4003-4005-000.json
85ac6fc242eecd6b459218bea9eb9ec18707fa6f44f3cd16d6658e63147f5654  coevo/realpath-crew/run-c2-crew-general/recordings-4003-4005/leg-log.jsonl
3e8be192d8ba67790db9abf7e8e8cbcaaeb7ae59d39f19c0d98ad6a4e8d636b9  coevo/realpath-crew/run-c2-crew-general/recordings-manifest-4000-4002.sha256
a8da94533fe5fe6d49b8732360b00390ebd08c5cb1c9f905ba4e04fc024a949e  coevo/realpath-crew/run-c2-crew-general/recordings-manifest-4003-4005.sha256
3d51d6367644186271f6d5caf514fa8df5799ea70e248aac6e20d444563df4e6  coevo/realpath-crew/run-c2-crew-general/sweep-4000-4002.json
d0bf954346b1f61774e49b8683f3b998d03bcdd77d2ba04458348ee5d8d7ebf8  coevo/realpath-crew/run-c2-crew-general/sweep-4003-4005.json
7817fad2a169ef7d2ddcb31594e588ba3a5029b37a6936251bb965923aa99ecb  coevo/realpath-runnerups-gen3/run-02-utility-lambda4/prescreen-quotes-4000-4002.json
7817fad2a169ef7d2ddcb31594e588ba3a5029b37a6936251bb965923aa99ecb  coevo/realpath-runnerups-gen3/run-02-utility-lambda4/prescreen-quotes-4003-4005.json
0be758a31cd713b76d8184ee13e795d6c5a09401b827d22bfd19fa83dbd40f43  coevo/realpath-runnerups-gen3/run-02-utility-lambda4/recordings-4000-4002/000-run-02-utility-lambda4-runnerup-corrected-gen3-76400d720ca2/replay-seed-4000.jsonl
e18ed81f2cc2e9cb7d866f2b35b837d88897721d5e0fe0f414f285080ac3029c  coevo/realpath-runnerups-gen3/run-02-utility-lambda4/recordings-4000-4002/000-run-02-utility-lambda4-runnerup-corrected-gen3-76400d720ca2/replay-seed-4001.jsonl
a1d8df0d0ec13623bb3bb1c3a9e878c29f3161da23f41a4e96869a34006dce6e  coevo/realpath-runnerups-gen3/run-02-utility-lambda4/recordings-4000-4002/000-run-02-utility-lambda4-runnerup-corrected-gen3-76400d720ca2/replay-seed-4002.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath-runnerups-gen3/run-02-utility-lambda4/recordings-4000-4002/000-run-02-utility-lambda4-runnerup-corrected-gen3-76400d720ca2/roster.json
b5e32f4597bf76e1b04478063792591bdf5c6fc0de31dc3784c732eeeef05489  coevo/realpath-runnerups-gen3/run-02-utility-lambda4/recordings-4003-4005/000-run-02-utility-lambda4-runnerup-corrected-gen3-76400d720ca2/replay-seed-4003.jsonl
8f29a99406029ba0d97e1f6f803946d470698fe7bdbbbe4d2168127de6a40054  coevo/realpath-runnerups-gen3/run-02-utility-lambda4/recordings-4003-4005/000-run-02-utility-lambda4-runnerup-corrected-gen3-76400d720ca2/replay-seed-4004.jsonl
b404480416051a9a4f08498623acea2b5dafa675ff247d183e4dcf202e7b2489  coevo/realpath-runnerups-gen3/run-02-utility-lambda4/recordings-4003-4005/000-run-02-utility-lambda4-runnerup-corrected-gen3-76400d720ca2/replay-seed-4005.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath-runnerups-gen3/run-02-utility-lambda4/recordings-4003-4005/000-run-02-utility-lambda4-runnerup-corrected-gen3-76400d720ca2/roster.json
f981d68621ec2506214e4912fc2f9db486416a3ffddaa04d5ed35879c2d17f8c  coevo/realpath-runnerups-gen3/run-02-utility-lambda4/recordings-manifest-4000-4002.sha256
a1fcbcb887e86693478abf7c224b18aa05dac515c23cdffb9b55d9cf0498c270  coevo/realpath-runnerups-gen3/run-02-utility-lambda4/recordings-manifest-4003-4005.sha256
ce7b334afa59c2ec091cffededa47065d492ae47944197da99184e28edcbbec4  coevo/realpath-runnerups-gen3/run-02-utility-lambda4/sweep-4000-4002.json
dc1705d707bf5e198c4c395da4414b1d5b8d8b41060854f26be6b2299874e529  coevo/realpath-runnerups-gen3/run-02-utility-lambda4/sweep-4003-4005.json
d58a686462938a8fda68b857bdded75e6b64e4e715eec09d1730292415d592c1  coevo/realpath-runnerups/run-01-utility-champion/prescreen-quotes-4000-4002.json
14f6ccca01b5338765daab7a397032e865b746004bef94cd24a66e0e11ef7f3f  coevo/realpath-runnerups/run-01-utility-champion/recordings-4000-4002/000-run-01-utility-champion-runnerup-gen1-6cf5ffb68774/replay-seed-4000.jsonl
7860c0bd66ac0e1d28d576dfb50534ff100fe5ae0ebf78472a7975bc957dac1d  coevo/realpath-runnerups/run-01-utility-champion/recordings-4000-4002/000-run-01-utility-champion-runnerup-gen1-6cf5ffb68774/replay-seed-4001.jsonl
8d304a70c012f0955acafe1028bf9012766bac7d7ba23e7044a3993cce97eb52  coevo/realpath-runnerups/run-01-utility-champion/recordings-4000-4002/000-run-01-utility-champion-runnerup-gen1-6cf5ffb68774/replay-seed-4002.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath-runnerups/run-01-utility-champion/recordings-4000-4002/000-run-01-utility-champion-runnerup-gen1-6cf5ffb68774/roster.json
ee713ae7a1e2a913f3c88d373214df7079a01208000c011489af3aba10b9de9d  coevo/realpath-runnerups/run-01-utility-champion/recordings-4000-4002/001-run-01-utility-champion-runnerup-gen2-7c093a035369/replay-seed-4000.jsonl
65149ea8e6400bd39de9d66f22e0fe7c160a94a81e9b74625660af404709bfc5  coevo/realpath-runnerups/run-01-utility-champion/recordings-4000-4002/001-run-01-utility-champion-runnerup-gen2-7c093a035369/replay-seed-4001.jsonl
89593b9ed9c6dfbb26b320967227dc3b769abe85d139b8b648d4aeff0b7ae90c  coevo/realpath-runnerups/run-01-utility-champion/recordings-4000-4002/001-run-01-utility-champion-runnerup-gen2-7c093a035369/replay-seed-4002.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath-runnerups/run-01-utility-champion/recordings-4000-4002/001-run-01-utility-champion-runnerup-gen2-7c093a035369/roster.json
bd36077abdf8283e76ad0f7d9de9a6494d6d7e491f683de597c384fd0ae1ece1  coevo/realpath-runnerups/run-01-utility-champion/recordings-4000-4002/002-run-01-utility-champion-runnerup-gen3-11aa68637a8f/replay-seed-4000.jsonl
65e687744ae69599ff97cfd6f3f3d643f261ef71dc7c78995cb3b3863861331d  coevo/realpath-runnerups/run-01-utility-champion/recordings-4000-4002/002-run-01-utility-champion-runnerup-gen3-11aa68637a8f/replay-seed-4001.jsonl
770ab531c5e7add955b1d146f8f270a2c99848e45dd98747c92992ec607e5ae0  coevo/realpath-runnerups/run-01-utility-champion/recordings-4000-4002/002-run-01-utility-champion-runnerup-gen3-11aa68637a8f/replay-seed-4002.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath-runnerups/run-01-utility-champion/recordings-4000-4002/002-run-01-utility-champion-runnerup-gen3-11aa68637a8f/roster.json
28343ecaf2f1a8372fb4bb65bc95808e7ab7a1d94e0f577cf3331b91edb3ad7e  coevo/realpath-runnerups/run-01-utility-champion/recordings-4000-4002/003-run-01-utility-champion-runnerup-gen7-e531c1f9a704/replay-seed-4000.jsonl
d2b187ffa2fdf4fb177adf86a73b67e2a404ea484f41e0f1e6f92861cc5e592b  coevo/realpath-runnerups/run-01-utility-champion/recordings-4000-4002/003-run-01-utility-champion-runnerup-gen7-e531c1f9a704/replay-seed-4001.jsonl
eab29b9d27626d89723659715b4c3fa300d3b44520299e5e269f130923058b89  coevo/realpath-runnerups/run-01-utility-champion/recordings-4000-4002/003-run-01-utility-champion-runnerup-gen7-e531c1f9a704/replay-seed-4002.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath-runnerups/run-01-utility-champion/recordings-4000-4002/003-run-01-utility-champion-runnerup-gen7-e531c1f9a704/roster.json
28005a07e83fc9e3e7102f039b8a2563a407ce1de17096c734cd79e8d609e188  coevo/realpath-runnerups/run-01-utility-champion/recordings-4000-4002/004-run-01-utility-champion-runnerup-gen8-609ea9ce9e87/replay-seed-4000.jsonl
5f6437d31256611bb1062a11bde8e409edfa7b064955ee5c308442fa79b26362  coevo/realpath-runnerups/run-01-utility-champion/recordings-4000-4002/004-run-01-utility-champion-runnerup-gen8-609ea9ce9e87/replay-seed-4001.jsonl
f787d92eb993ae75e03b5e6ca966453571a7d7fde0c23d709fc4718a1b101902  coevo/realpath-runnerups/run-01-utility-champion/recordings-4000-4002/004-run-01-utility-champion-runnerup-gen8-609ea9ce9e87/replay-seed-4002.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath-runnerups/run-01-utility-champion/recordings-4000-4002/004-run-01-utility-champion-runnerup-gen8-609ea9ce9e87/roster.json
cd84a6295fb79a3809d6ce7d0f81961028adfb53d63d273387b64c7f15ff3572  coevo/realpath-runnerups/run-01-utility-champion/recordings-4000-4002/005-run-01-utility-champion-runnerup-gen9-1f5efd3c2f47/replay-seed-4000.jsonl
d418b9687ed954b5800fd01604e37af0f93061d773c2ddfbb94edcc0dcb70105  coevo/realpath-runnerups/run-01-utility-champion/recordings-4000-4002/005-run-01-utility-champion-runnerup-gen9-1f5efd3c2f47/replay-seed-4001.jsonl
2260e976722bd69f7375f05e2f6c5625aa03c91a08224444ea867a9023396c20  coevo/realpath-runnerups/run-01-utility-champion/recordings-4000-4002/005-run-01-utility-champion-runnerup-gen9-1f5efd3c2f47/replay-seed-4002.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath-runnerups/run-01-utility-champion/recordings-4000-4002/005-run-01-utility-champion-runnerup-gen9-1f5efd3c2f47/roster.json
2589983cf0f65b2fd6d89d413b570e9480635e126b70af06ea1b67a500a39f27  coevo/realpath-runnerups/run-01-utility-champion/recordings-manifest-4000-4002.sha256
dc7c25c9e56a73b6babc04b043d501113d0e597c11d5399caa73861e1f2e542e  coevo/realpath-runnerups/run-01-utility-champion/sweep-4000-4002.json
611a84c9e7c1125a16bf1d03aa396c3495ad16bbc48a93becd9e309126d9962e  coevo/realpath-runnerups/run-02-utility-lambda4/prescreen-quotes-4000-4002.json
611a84c9e7c1125a16bf1d03aa396c3495ad16bbc48a93becd9e309126d9962e  coevo/realpath-runnerups/run-02-utility-lambda4/prescreen-quotes-4003-4005.json
44b6a0163072fd366c1eb64af69e54490c8ee5fd5d27c69565e3f621c4bef238  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4000-4002/000-run-02-utility-lambda4-runnerup-gen1-3a89655f0ae7/replay-seed-4000.jsonl
3485458fc019b9f62a68ed4f6f080ee18e3d6cdc678b8418e3d2108d99c14d76  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4000-4002/000-run-02-utility-lambda4-runnerup-gen1-3a89655f0ae7/replay-seed-4001.jsonl
efaf09ca6510a04433a7ce500634490898c4ea8a538edc1cfb76844a95013395  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4000-4002/000-run-02-utility-lambda4-runnerup-gen1-3a89655f0ae7/replay-seed-4002.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4000-4002/000-run-02-utility-lambda4-runnerup-gen1-3a89655f0ae7/roster.json
d50346cee034b8cc4a52e8177512e0d3f7252a06aa99b692edda2d5cac8e20a0  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4000-4002/001-run-02-utility-lambda4-runnerup-gen2-2b40b2c1f1e8/replay-seed-4000.jsonl
5b03639459b4bee8b703b18f4ae15a1c1d0448c10fbd4330f6c838e86c4c9049  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4000-4002/001-run-02-utility-lambda4-runnerup-gen2-2b40b2c1f1e8/replay-seed-4001.jsonl
594f939a8fad2849363abbf3f5c585e5049d9999dd67177f1456432e6dc304b3  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4000-4002/001-run-02-utility-lambda4-runnerup-gen2-2b40b2c1f1e8/replay-seed-4002.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4000-4002/001-run-02-utility-lambda4-runnerup-gen2-2b40b2c1f1e8/roster.json
a7418fc0a885385ffb5e91c405054fcf9bd5b84e852d2e39b9bb357a7df61ba2  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4000-4002/002-run-02-utility-lambda4-runnerup-gen3-2bac4cfe8b72/replay-seed-4000.jsonl
f02d8be0490bb14819700160d1f8616cecb1d73c434c623407df53ca7ca5c641  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4000-4002/002-run-02-utility-lambda4-runnerup-gen3-2bac4cfe8b72/replay-seed-4001.jsonl
c42588220c6e7c490fdc05537d159ea3c3ef5b493fc7fc3449e144416b6a3eb8  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4000-4002/002-run-02-utility-lambda4-runnerup-gen3-2bac4cfe8b72/replay-seed-4002.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4000-4002/002-run-02-utility-lambda4-runnerup-gen3-2bac4cfe8b72/roster.json
ab5219a3003f76af066d5f7713678a534fba681a87881f21c2fb9f49c2ae442f  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4000-4002/003-run-02-utility-lambda4-runnerup-gen7-cb17deda3cf3/replay-seed-4000.jsonl
9a28ea38ada985acfd7c400278b1ebd83b21a1a43a8ec3ca33442425d59f6574  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4000-4002/003-run-02-utility-lambda4-runnerup-gen7-cb17deda3cf3/replay-seed-4001.jsonl
02c2134dc0a1377278ccead3f8b7bc43bb9be76901b969232389c05bad83cd4d  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4000-4002/003-run-02-utility-lambda4-runnerup-gen7-cb17deda3cf3/replay-seed-4002.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4000-4002/003-run-02-utility-lambda4-runnerup-gen7-cb17deda3cf3/roster.json
02806cf6d9bac36296d923a9706bf2411e4b1187dab86f7996fa11804e3d5421  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4000-4002/004-run-02-utility-lambda4-runnerup-gen8-f280962f179f/replay-seed-4000.jsonl
6569517e7561a4069e5b9a45e385cf9f189b5fe415b08528918d781386f9699a  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4000-4002/004-run-02-utility-lambda4-runnerup-gen8-f280962f179f/replay-seed-4001.jsonl
53f8c88eb27f15fa60f8f1f6ef509127520f4e409cf9d07808038e6e7eaf251f  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4000-4002/004-run-02-utility-lambda4-runnerup-gen8-f280962f179f/replay-seed-4002.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4000-4002/004-run-02-utility-lambda4-runnerup-gen8-f280962f179f/roster.json
3b8715fd489a8fcd1ccbdee09344399a775c293a863fb4b0d12a89560b21ca9c  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4000-4002/005-run-02-utility-lambda4-runnerup-gen9-bfd145cb4883/replay-seed-4000.jsonl
a20fb0fcfbd2bc2d789fbed967dba76fd2e36e59962cbbf30105e4fcf3815e38  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4000-4002/005-run-02-utility-lambda4-runnerup-gen9-bfd145cb4883/replay-seed-4001.jsonl
94ff1655167ce51fb3ddf4db86e2fa2d5455dc4ea1aff09162fc042f13ff50ad  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4000-4002/005-run-02-utility-lambda4-runnerup-gen9-bfd145cb4883/replay-seed-4002.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4000-4002/005-run-02-utility-lambda4-runnerup-gen9-bfd145cb4883/roster.json
11e662010792312752b9183efe485dd1a9462cb64fc080f33f7775e61b830f31  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4003-4005/000-run-02-utility-lambda4-runnerup-gen1-3a89655f0ae7/replay-seed-4003.jsonl
eb6181b779630dffdafbe6c8c601fd1d817d2f16e4ee9351e7df799aca59e7a7  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4003-4005/000-run-02-utility-lambda4-runnerup-gen1-3a89655f0ae7/replay-seed-4004.jsonl
accc98010376d90aeab9fcb7c2243dda41f54d14e62962b07497cfdea35908ac  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4003-4005/000-run-02-utility-lambda4-runnerup-gen1-3a89655f0ae7/replay-seed-4005.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4003-4005/000-run-02-utility-lambda4-runnerup-gen1-3a89655f0ae7/roster.json
ebdfe9a4e2379cede54507df764ff755190f1d2f6609039da76428cef2126d42  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4003-4005/001-run-02-utility-lambda4-runnerup-gen2-2b40b2c1f1e8/replay-seed-4003.jsonl
6a63d6a8d900fffee6af869c5c3fa5d68386974c5193336ba2efaecd27453f68  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4003-4005/001-run-02-utility-lambda4-runnerup-gen2-2b40b2c1f1e8/replay-seed-4004.jsonl
a97fb81f29ec34403f27bc6733216a272365092c848236b2dfa3303958534c08  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4003-4005/001-run-02-utility-lambda4-runnerup-gen2-2b40b2c1f1e8/replay-seed-4005.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4003-4005/001-run-02-utility-lambda4-runnerup-gen2-2b40b2c1f1e8/roster.json
cdcc16558c515fdc4e880c458fbef3a604ba34b81a8869e628aef415dc42e9fe  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4003-4005/002-run-02-utility-lambda4-runnerup-gen3-2bac4cfe8b72/replay-seed-4003.jsonl
e0dc96b4fb19634ebb43716b120303d7e4850b9051e27e4377b527ef7cd9eacd  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4003-4005/002-run-02-utility-lambda4-runnerup-gen3-2bac4cfe8b72/replay-seed-4004.jsonl
7f3afcb76bc15f680ebc2647f12d9defa1e1e3a4f9d01c6d0cf3e99f5efc674d  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4003-4005/002-run-02-utility-lambda4-runnerup-gen3-2bac4cfe8b72/replay-seed-4005.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4003-4005/002-run-02-utility-lambda4-runnerup-gen3-2bac4cfe8b72/roster.json
122acc981b1fc254c5737656d61c92c3fa03e592c0a23d090f08412913849048  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4003-4005/003-run-02-utility-lambda4-runnerup-gen7-cb17deda3cf3/replay-seed-4003.jsonl
1879c3ed844c72f5c120e535db204c0b3e395cff50a7550aa5a96d87a7e8df6e  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4003-4005/003-run-02-utility-lambda4-runnerup-gen7-cb17deda3cf3/replay-seed-4004.jsonl
216479fa8ef7d8ffc1bc7b8ae5e0c9da04397aff579653e001fc3bafd237a940  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4003-4005/003-run-02-utility-lambda4-runnerup-gen7-cb17deda3cf3/replay-seed-4005.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4003-4005/003-run-02-utility-lambda4-runnerup-gen7-cb17deda3cf3/roster.json
b5966e12395530a078b5635f09599ed7abc5c9dfb35d591624cc83e278d9fb81  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4003-4005/004-run-02-utility-lambda4-runnerup-gen8-f280962f179f/replay-seed-4003.jsonl
b7eb8e3e78595e28d8e14cfb2a777d7e88b8ec9ebf479d1bcdeb840f68b05888  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4003-4005/004-run-02-utility-lambda4-runnerup-gen8-f280962f179f/replay-seed-4004.jsonl
18afb2b1257240f7f5caa510170f2b4b4e5500a82e156c7d39f7d938ea49505d  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4003-4005/004-run-02-utility-lambda4-runnerup-gen8-f280962f179f/replay-seed-4005.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4003-4005/004-run-02-utility-lambda4-runnerup-gen8-f280962f179f/roster.json
3e0a2eb1b2a18addda924837d3a2d478f0271310c83a15620d5e55fb9a9c3b81  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4003-4005/005-run-02-utility-lambda4-runnerup-gen9-bfd145cb4883/replay-seed-4003.jsonl
def4e72f8e2abdcba24ae91ae0574f8a2bd07becb3bb0850c2b2f3a2a2cb6e83  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4003-4005/005-run-02-utility-lambda4-runnerup-gen9-bfd145cb4883/replay-seed-4004.jsonl
8eb8d154459fb7934f90453ba7c9735d3c8753718f46910434b39a151e0207d2  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4003-4005/005-run-02-utility-lambda4-runnerup-gen9-bfd145cb4883/replay-seed-4005.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-4003-4005/005-run-02-utility-lambda4-runnerup-gen9-bfd145cb4883/roster.json
a261c3709336ce95b374db21ed4162adf4da5f092ccb80f3ed733be3c147afe6  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-manifest-4000-4002.sha256
e0b85f67d01e0b150858c562409976c1042b4b9e439383016cf23d9df454fc07  coevo/realpath-runnerups/run-02-utility-lambda4/recordings-manifest-4003-4005.sha256
c2627d860b79e1ee0d0de4064869f79201347ea213e367ebcef5725d8665b872  coevo/realpath-runnerups/run-02-utility-lambda4/sweep-4000-4002.json
4d583c70c44d8914c0b22f82703697f5c7ca4f1cafb9e62193012db7d686c006  coevo/realpath-runnerups/run-02-utility-lambda4/sweep-4003-4005.json
5e92043f904743b849de361d11cdc4068f2b79d948e66f734a0f14ef612b5132  coevo/realpath-runnerups/run-03-utility-bcanchor/prescreen-quotes-4000-4002.json
1e33f2af2408b31db10cc685255f55bccd33e676611907254942aafe46e98760  coevo/realpath-runnerups/run-03-utility-bcanchor/recordings-4000-4002/000-run-03-utility-bcanchor-runnerup-gen1-98171e870e74/replay-seed-4000.jsonl
d3d23b3a4a66ac98508d919a386274193d7b9bcb1e841cc08219c577b60df8ea  coevo/realpath-runnerups/run-03-utility-bcanchor/recordings-4000-4002/000-run-03-utility-bcanchor-runnerup-gen1-98171e870e74/replay-seed-4001.jsonl
09fb1f25394e216c8474b4ec825a39705271028b57ae8bfd7a758c9b00ccc9ae  coevo/realpath-runnerups/run-03-utility-bcanchor/recordings-4000-4002/000-run-03-utility-bcanchor-runnerup-gen1-98171e870e74/replay-seed-4002.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath-runnerups/run-03-utility-bcanchor/recordings-4000-4002/000-run-03-utility-bcanchor-runnerup-gen1-98171e870e74/roster.json
2992dad6e0744d3e1b64d5b76deb991c51b4aea75ad50f80c9ab95ac8971b3f8  coevo/realpath-runnerups/run-03-utility-bcanchor/recordings-4000-4002/001-run-03-utility-bcanchor-runnerup-gen2-62499b47ca73/replay-seed-4000.jsonl
7314e01cda5679932d27576334e9013d5eb4a1c38e42e2fc70ba6a0f80eb5e97  coevo/realpath-runnerups/run-03-utility-bcanchor/recordings-4000-4002/001-run-03-utility-bcanchor-runnerup-gen2-62499b47ca73/replay-seed-4001.jsonl
6999998c0e545a8e5994fe8fd12cda0d680dc5ae7fd938f06822f6cef7524e21  coevo/realpath-runnerups/run-03-utility-bcanchor/recordings-4000-4002/001-run-03-utility-bcanchor-runnerup-gen2-62499b47ca73/replay-seed-4002.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath-runnerups/run-03-utility-bcanchor/recordings-4000-4002/001-run-03-utility-bcanchor-runnerup-gen2-62499b47ca73/roster.json
ddd20dfc5ee6692a733206ceed6db37a837478b14293d2732fc24bf204e4b21c  coevo/realpath-runnerups/run-03-utility-bcanchor/recordings-4000-4002/002-run-03-utility-bcanchor-runnerup-gen3-b1c8f9147845/replay-seed-4000.jsonl
9406b3dda855f993cd41dd0569eb5081e229241bf1875cc1c51ca0049a4ca627  coevo/realpath-runnerups/run-03-utility-bcanchor/recordings-4000-4002/002-run-03-utility-bcanchor-runnerup-gen3-b1c8f9147845/replay-seed-4001.jsonl
ac26a8f86463072605c3097f4fc86ae97c32b6830cd35a211fc8d39ebba366da  coevo/realpath-runnerups/run-03-utility-bcanchor/recordings-4000-4002/002-run-03-utility-bcanchor-runnerup-gen3-b1c8f9147845/replay-seed-4002.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath-runnerups/run-03-utility-bcanchor/recordings-4000-4002/002-run-03-utility-bcanchor-runnerup-gen3-b1c8f9147845/roster.json
1d34c8ec19469096674e328b203d0d40f79bd0e19bb02b19b81d768cff7a2f7a  coevo/realpath-runnerups/run-03-utility-bcanchor/recordings-4000-4002/003-run-03-utility-bcanchor-runnerup-gen7-f07bfa9fb89d/replay-seed-4000.jsonl
ec343bc992ef4126bed59c171516ce51b2a22c61433a9d611bb42d0a43ff868f  coevo/realpath-runnerups/run-03-utility-bcanchor/recordings-4000-4002/003-run-03-utility-bcanchor-runnerup-gen7-f07bfa9fb89d/replay-seed-4001.jsonl
b9b35f506f882b159727b1ad5a49326a1f3fc61ccb26d40a5b8cfa8e528b388f  coevo/realpath-runnerups/run-03-utility-bcanchor/recordings-4000-4002/003-run-03-utility-bcanchor-runnerup-gen7-f07bfa9fb89d/replay-seed-4002.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath-runnerups/run-03-utility-bcanchor/recordings-4000-4002/003-run-03-utility-bcanchor-runnerup-gen7-f07bfa9fb89d/roster.json
2af825f9125f472a1bd5b866c0722663791132664347da81bfda78b9b4b635a2  coevo/realpath-runnerups/run-03-utility-bcanchor/recordings-4000-4002/004-run-03-utility-bcanchor-runnerup-gen8-7f73929d5b91/replay-seed-4000.jsonl
1f04459b18ed7082ee85d1d86a0dba00e85f86d75bc7db9224b6aa9fc8d62042  coevo/realpath-runnerups/run-03-utility-bcanchor/recordings-4000-4002/004-run-03-utility-bcanchor-runnerup-gen8-7f73929d5b91/replay-seed-4001.jsonl
e35225f1e021f2fb4ad43238a2e4d6aaf9f587a5bb2fc905dcfe11ec4d0bcedb  coevo/realpath-runnerups/run-03-utility-bcanchor/recordings-4000-4002/004-run-03-utility-bcanchor-runnerup-gen8-7f73929d5b91/replay-seed-4002.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath-runnerups/run-03-utility-bcanchor/recordings-4000-4002/004-run-03-utility-bcanchor-runnerup-gen8-7f73929d5b91/roster.json
8e36215b08b7d341947d601b31f2b857b96ee2e438459df3a654b91c50f60b06  coevo/realpath-runnerups/run-03-utility-bcanchor/recordings-4000-4002/005-run-03-utility-bcanchor-runnerup-gen9-0c7a75b47b85/replay-seed-4000.jsonl
93a1c997896b480a6a76b71b022f888ffbda0f19fada97465f004483feb58033  coevo/realpath-runnerups/run-03-utility-bcanchor/recordings-4000-4002/005-run-03-utility-bcanchor-runnerup-gen9-0c7a75b47b85/replay-seed-4001.jsonl
c4322b83f69d9c01b34d8f30d0d995c517c9ed6d049a1dfd4426ab7baae39e43  coevo/realpath-runnerups/run-03-utility-bcanchor/recordings-4000-4002/005-run-03-utility-bcanchor-runnerup-gen9-0c7a75b47b85/replay-seed-4002.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath-runnerups/run-03-utility-bcanchor/recordings-4000-4002/005-run-03-utility-bcanchor-runnerup-gen9-0c7a75b47b85/roster.json
7bd97ed46ed7a88655b9f2703239a8a0002f9d7d1d1232eaf86ecd822635bba6  coevo/realpath-runnerups/run-03-utility-bcanchor/recordings-manifest-4000-4002.sha256
92bc5f83530b8f58c40ca9f4afa4e7dd58d8b277e02d29e8cde95156ada74b0a  coevo/realpath-runnerups/run-03-utility-bcanchor/sweep-4000-4002.json
b4fa862d0516bebf6258ed9fc2826941881ad6a698fbf00b242c01a7799128bd  coevo/realpath/baseline-cells-corpus.json
ce49e15f7db151e37f008b111b22566f97c9ecc34840e0fc845b0866b6439801  coevo/realpath/recordings-manifest.sha256
528a82c0bd01cb1d2148166ee355020632473304e167e73915ed1a3da4902cd6  coevo/realpath/run-01-utility-champion/prescreen-quotes.json
2c0dd626b858ee44db988ba5721ccf3479cb39ed78448cd58d7405c61b7d809f  coevo/realpath/run-01-utility-champion/recordings-4000-4002/000-run-01-utility-champion-alternating-freeze-champion-gen9-8ac3652a74f8/replay-seed-4000.jsonl
8b8f28221998e3f2fd94872453a999472f1afbe9288576110f68557f514fdbee  coevo/realpath/run-01-utility-champion/recordings-4000-4002/000-run-01-utility-champion-alternating-freeze-champion-gen9-8ac3652a74f8/replay-seed-4001.jsonl
fc7995eef3e3a3ff1fd8274ea1d786f01dc9e460a75b6d5c038245b9b93598d4  coevo/realpath/run-01-utility-champion/recordings-4000-4002/000-run-01-utility-champion-alternating-freeze-champion-gen9-8ac3652a74f8/replay-seed-4002.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath/run-01-utility-champion/recordings-4000-4002/000-run-01-utility-champion-alternating-freeze-champion-gen9-8ac3652a74f8/roster.json
274e1e41bd6f14cdbafc6bd0cd00b3ea58d85638d78c147411dc045d7df81b0b  coevo/realpath/run-01-utility-champion/recordings-4000-4002/001-run-01-utility-champion-alternating-freeze-champion-gen3-6d327dcbde94/replay-seed-4000.jsonl
1255165e642f426ad07084bb308bacb0a38661e25b8b8802cf183ebbeff0f3d8  coevo/realpath/run-01-utility-champion/recordings-4000-4002/001-run-01-utility-champion-alternating-freeze-champion-gen3-6d327dcbde94/replay-seed-4001.jsonl
95509dd101dde58658b047d9e1723ccbe1faff855801a69eb952de801eb8b2da  coevo/realpath/run-01-utility-champion/recordings-4000-4002/001-run-01-utility-champion-alternating-freeze-champion-gen3-6d327dcbde94/replay-seed-4002.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath/run-01-utility-champion/recordings-4000-4002/001-run-01-utility-champion-alternating-freeze-champion-gen3-6d327dcbde94/roster.json
b33768a9a543227f557ba662c6b7376d19fa8d811fa4a19a32889a5712238d26  coevo/realpath/run-01-utility-champion/recordings-4003-4005/000-run-01-utility-champion-alternating-freeze-champion-gen9-8ac3652a74f8/replay-seed-4003.jsonl
0c6288ae97bb5c1c5b20cd4c8b16b8b0ef678554359620cc103c165ee424205c  coevo/realpath/run-01-utility-champion/recordings-4003-4005/000-run-01-utility-champion-alternating-freeze-champion-gen9-8ac3652a74f8/replay-seed-4004.jsonl
6ed708ab4b5a00829468134d30d93eb18d968f21a5cf96308020dd58ab342cb6  coevo/realpath/run-01-utility-champion/recordings-4003-4005/000-run-01-utility-champion-alternating-freeze-champion-gen9-8ac3652a74f8/replay-seed-4005.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath/run-01-utility-champion/recordings-4003-4005/000-run-01-utility-champion-alternating-freeze-champion-gen9-8ac3652a74f8/roster.json
f43802efc8a42b2f0012ad09cb62000d63292b6f64589b33c5294e553009c374  coevo/realpath/run-01-utility-champion/recordings-4003-4005/001-run-01-utility-champion-alternating-freeze-champion-gen3-6d327dcbde94/replay-seed-4003.jsonl
efa19bfb68f75f9e2832e730b080a785b490782cbfb39aea1b83e0c898ce6ff6  coevo/realpath/run-01-utility-champion/recordings-4003-4005/001-run-01-utility-champion-alternating-freeze-champion-gen3-6d327dcbde94/replay-seed-4004.jsonl
c31972cff77d22fa98e0814832499c4a72c7442664d9c0ed1099df15496d8ff2  coevo/realpath/run-01-utility-champion/recordings-4003-4005/001-run-01-utility-champion-alternating-freeze-champion-gen3-6d327dcbde94/replay-seed-4005.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath/run-01-utility-champion/recordings-4003-4005/001-run-01-utility-champion-alternating-freeze-champion-gen3-6d327dcbde94/roster.json
49ef2a977dfd3e72c2f73ad2395ccbb927d7b868c576f788b5283ee5dc5e8c3a  coevo/realpath/run-01-utility-champion/sweep-4000-4002.json
e771913cfde5971cb569bfcc34c27acfba1543e5047ebed05846226778b1c339  coevo/realpath/run-01-utility-champion/sweep-4003-4005.json
df637a2629ce8797ce628022cbaa2ec90a1f50e87e2130cb9f932aa531d74fa8  coevo/realpath/run-02-utility-lambda4/prescreen-quotes.json
0169c297207d5c062bd3d2b87c9555c6e60de761484e71e4e2ee7aec0ecd8e39  coevo/realpath/run-02-utility-lambda4/recordings-4000-4002/000-run-02-utility-lambda4-alternating-freeze-champion-gen9-2ca474514b86/replay-seed-4000.jsonl
92cd7860a6e22d9067c1602d657977d7022c36e1e6bf7a754e35315e92d88983  coevo/realpath/run-02-utility-lambda4/recordings-4000-4002/000-run-02-utility-lambda4-alternating-freeze-champion-gen9-2ca474514b86/replay-seed-4001.jsonl
04445f4262b9aabb379f7a45c766a8f4cc6026e92f7c5e021daaef4272a29d63  coevo/realpath/run-02-utility-lambda4/recordings-4000-4002/000-run-02-utility-lambda4-alternating-freeze-champion-gen9-2ca474514b86/replay-seed-4002.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath/run-02-utility-lambda4/recordings-4000-4002/000-run-02-utility-lambda4-alternating-freeze-champion-gen9-2ca474514b86/roster.json
1ba932cc36ca2574dbcecc7bc54201688326e420d2cb8b549081bed10a669aea  coevo/realpath/run-02-utility-lambda4/recordings-4000-4002/001-run-02-utility-lambda4-alternating-freeze-champion-gen3-10c1f9f3c0a2/replay-seed-4000.jsonl
58339d038c5bcd2d400602db80687c6d29cc68efd104d64ba6777d3ac7148ddc  coevo/realpath/run-02-utility-lambda4/recordings-4000-4002/001-run-02-utility-lambda4-alternating-freeze-champion-gen3-10c1f9f3c0a2/replay-seed-4001.jsonl
f4873eea58e706f9e0e52a879761e924dedbb96a17b97c179866b3dbdb68718d  coevo/realpath/run-02-utility-lambda4/recordings-4000-4002/001-run-02-utility-lambda4-alternating-freeze-champion-gen3-10c1f9f3c0a2/replay-seed-4002.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath/run-02-utility-lambda4/recordings-4000-4002/001-run-02-utility-lambda4-alternating-freeze-champion-gen3-10c1f9f3c0a2/roster.json
f688ba52e6aea8cfd677bbc63eb00dd94c86de9cfe67bf9241848aba37109f88  coevo/realpath/run-02-utility-lambda4/recordings-4003-4005/000-run-02-utility-lambda4-alternating-freeze-champion-gen9-2ca474514b86/replay-seed-4003.jsonl
562e4be733614dce213b96d7a4ca476a92bf50b1ea1a665fd64e58bdddcbd839  coevo/realpath/run-02-utility-lambda4/recordings-4003-4005/000-run-02-utility-lambda4-alternating-freeze-champion-gen9-2ca474514b86/replay-seed-4004.jsonl
1de404bcdb63bb6a6c4e971bf496609a9c05db60d049d16a1163d91075fcf08e  coevo/realpath/run-02-utility-lambda4/recordings-4003-4005/000-run-02-utility-lambda4-alternating-freeze-champion-gen9-2ca474514b86/replay-seed-4005.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath/run-02-utility-lambda4/recordings-4003-4005/000-run-02-utility-lambda4-alternating-freeze-champion-gen9-2ca474514b86/roster.json
d822753e1172cb704fbb1b3065b9fa20c71ee0d9284d0a826c55846eb6f4d428  coevo/realpath/run-02-utility-lambda4/recordings-4003-4005/001-run-02-utility-lambda4-alternating-freeze-champion-gen3-10c1f9f3c0a2/replay-seed-4003.jsonl
b6c1d9380dd94a739f8c6041681e843895c6eb0a83bd8ba1d67c260fd897795e  coevo/realpath/run-02-utility-lambda4/recordings-4003-4005/001-run-02-utility-lambda4-alternating-freeze-champion-gen3-10c1f9f3c0a2/replay-seed-4004.jsonl
91f04ee2ce29fb8a36e4e6d0938f3bf4f353d78d727be0ad000c2678af8a4e35  coevo/realpath/run-02-utility-lambda4/recordings-4003-4005/001-run-02-utility-lambda4-alternating-freeze-champion-gen3-10c1f9f3c0a2/replay-seed-4005.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath/run-02-utility-lambda4/recordings-4003-4005/001-run-02-utility-lambda4-alternating-freeze-champion-gen3-10c1f9f3c0a2/roster.json
df3f397ccdf4b873763793ce5d4212ed15f356fc94afda51641a39928026ed52  coevo/realpath/run-02-utility-lambda4/sweep-4000-4002.json
9f364f8c2ab42f60d7556dc0dca005742b825d36bcfea42af3433fc59ad954b9  coevo/realpath/run-02-utility-lambda4/sweep-4003-4005.json
9a5030e4f927e1dd558cbe4b6e3b271958d2eb981dc9233afa18acfc3efb930e  coevo/realpath/run-03-utility-bcanchor/prescreen-quotes.json
cc95759694cf25382fab99d4ab6899c3af4f1c8995889974234c6a9a77966642  coevo/realpath/run-03-utility-bcanchor/recordings-4000-4002/000-run-03-utility-bcanchor-alternating-freeze-champion-gen9-a89be618bfbb/replay-seed-4000.jsonl
6cad792fdb617eee0900ca6014cf7e97d5298bbe56a69e3883a6df7567228006  coevo/realpath/run-03-utility-bcanchor/recordings-4000-4002/000-run-03-utility-bcanchor-alternating-freeze-champion-gen9-a89be618bfbb/replay-seed-4001.jsonl
152a923924bfcb94e09a2d041ab73209ce5610c196aab183f21d7eceae7bc036  coevo/realpath/run-03-utility-bcanchor/recordings-4000-4002/000-run-03-utility-bcanchor-alternating-freeze-champion-gen9-a89be618bfbb/replay-seed-4002.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath/run-03-utility-bcanchor/recordings-4000-4002/000-run-03-utility-bcanchor-alternating-freeze-champion-gen9-a89be618bfbb/roster.json
eb385c3d98af7a82f9881d0fc1e4d295dd5a4f1480e5905d6dfea64280c49a60  coevo/realpath/run-03-utility-bcanchor/recordings-4000-4002/001-run-03-utility-bcanchor-alternating-freeze-champion-gen3-6d327dcbde94/replay-seed-4000.jsonl
bde1fb407915afe56eda299a5df53e40dfdb613a15b7be0dee277a8cead72903  coevo/realpath/run-03-utility-bcanchor/recordings-4000-4002/001-run-03-utility-bcanchor-alternating-freeze-champion-gen3-6d327dcbde94/replay-seed-4001.jsonl
196862fb256e1e76f04a4e24c261ed77b412c9a6c9164de0c3ec2ea6d66c7db5  coevo/realpath/run-03-utility-bcanchor/recordings-4000-4002/001-run-03-utility-bcanchor-alternating-freeze-champion-gen3-6d327dcbde94/replay-seed-4002.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath/run-03-utility-bcanchor/recordings-4000-4002/001-run-03-utility-bcanchor-alternating-freeze-champion-gen3-6d327dcbde94/roster.json
d7aaa6f09ba4001168390639b4726cc1e72b1b20ce9cafc6206d4883920f66dc  coevo/realpath/run-03-utility-bcanchor/recordings-4003-4005/000-run-03-utility-bcanchor-alternating-freeze-champion-gen9-a89be618bfbb/replay-seed-4003.jsonl
899e33d40bd53373db1a48ac442a141810ea7721946dbed3a0707a212f95f501  coevo/realpath/run-03-utility-bcanchor/recordings-4003-4005/000-run-03-utility-bcanchor-alternating-freeze-champion-gen9-a89be618bfbb/replay-seed-4004.jsonl
e1be2612a4925bd40d3a60a17f645bfde81adc65a0b063fde4bbc74242dcac97  coevo/realpath/run-03-utility-bcanchor/recordings-4003-4005/000-run-03-utility-bcanchor-alternating-freeze-champion-gen9-a89be618bfbb/replay-seed-4005.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath/run-03-utility-bcanchor/recordings-4003-4005/000-run-03-utility-bcanchor-alternating-freeze-champion-gen9-a89be618bfbb/roster.json
d5d24ffa86e4c32f3dd8e37e550dede37c85ca571211177bcbdab458d477ea83  coevo/realpath/run-03-utility-bcanchor/recordings-4003-4005/001-run-03-utility-bcanchor-alternating-freeze-champion-gen3-6d327dcbde94/replay-seed-4003.jsonl
6a7e5d7cfecd5b8e5738333e5528721180684d47959c83661a6dba6fb13ca497  coevo/realpath/run-03-utility-bcanchor/recordings-4003-4005/001-run-03-utility-bcanchor-alternating-freeze-champion-gen3-6d327dcbde94/replay-seed-4004.jsonl
eaf92ee762a05299804b3cda8cca6c0134f51d39414a4c034dd27364fb6ce29f  coevo/realpath/run-03-utility-bcanchor/recordings-4003-4005/001-run-03-utility-bcanchor-alternating-freeze-champion-gen3-6d327dcbde94/replay-seed-4005.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath/run-03-utility-bcanchor/recordings-4003-4005/001-run-03-utility-bcanchor-alternating-freeze-champion-gen3-6d327dcbde94/roster.json
dd48f92e432ce72cc0ca04b6851690c50625108e5a8a546b0264545db3da785a  coevo/realpath/run-03-utility-bcanchor/sweep-4000-4002.json
d32cb94acc03964b6ccf9dc5a244c003736e145aef74d5b691e189a5850b40a2  coevo/realpath/run-03-utility-bcanchor/sweep-4003-4005.json
22c72cf0e2470dc72254befc06dd6d3c6927e52df255eaf0da9254268cfd84fb  coevo/realpath/run-04-freepolicy-v3/prescreen-quotes.json
ebfe1a754c687ff37fbf52cd4bb63ca496c67eca0944877f0291f7103a5c254a  coevo/realpath/run-04-freepolicy-v3/recordings-4000-4002/000-run-04-freepolicy-v3-alternating-freeze-champion-gen9-27f852fe0919/replay-seed-4000.jsonl
fd1ebb6e1ca5eab109cfe4e06c173a0275a0adf8cf77103780ade7dcb22f5eb9  coevo/realpath/run-04-freepolicy-v3/recordings-4000-4002/000-run-04-freepolicy-v3-alternating-freeze-champion-gen9-27f852fe0919/replay-seed-4001.jsonl
7472fe2dbd0dd07a93ec5a5d61b6f41e0209374eaf4a6ab5d73007c0f2dfbdd8  coevo/realpath/run-04-freepolicy-v3/recordings-4000-4002/000-run-04-freepolicy-v3-alternating-freeze-champion-gen9-27f852fe0919/replay-seed-4002.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath/run-04-freepolicy-v3/recordings-4000-4002/000-run-04-freepolicy-v3-alternating-freeze-champion-gen9-27f852fe0919/roster.json
3ed8aa8aa7605ed8e458fe10b72a754b00538d462767a1cbb7d0bcd9ef22fa52  coevo/realpath/run-04-freepolicy-v3/recordings-4000-4002/001-run-04-freepolicy-v3-alternating-freeze-champion-gen3-348df066e0db/replay-seed-4000.jsonl
710f43ef22df95f137d97d2e7d1012247d54267c2c18cc0769b73f065dbaa565  coevo/realpath/run-04-freepolicy-v3/recordings-4000-4002/001-run-04-freepolicy-v3-alternating-freeze-champion-gen3-348df066e0db/replay-seed-4001.jsonl
fe5f353778caa755cace161cb528f1a6f3b914501f33f8a4e179e5ff9c2a8b1c  coevo/realpath/run-04-freepolicy-v3/recordings-4000-4002/001-run-04-freepolicy-v3-alternating-freeze-champion-gen3-348df066e0db/replay-seed-4002.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath/run-04-freepolicy-v3/recordings-4000-4002/001-run-04-freepolicy-v3-alternating-freeze-champion-gen3-348df066e0db/roster.json
126c66c197bd7ee29bea7a106d064d6c1dd8b9960b921c4a40533905d35ede7f  coevo/realpath/run-04-freepolicy-v3/recordings-4003-4005/000-run-04-freepolicy-v3-alternating-freeze-champion-gen9-27f852fe0919/replay-seed-4003.jsonl
643b90039f77cdc0998f358f852068abb388f0e50d6832416b25cdb443a210fa  coevo/realpath/run-04-freepolicy-v3/recordings-4003-4005/000-run-04-freepolicy-v3-alternating-freeze-champion-gen9-27f852fe0919/replay-seed-4004.jsonl
7bbf4912319ab0bb6cbcb6aa5669254c3f8d329e8025647521b920e13b470fdf  coevo/realpath/run-04-freepolicy-v3/recordings-4003-4005/000-run-04-freepolicy-v3-alternating-freeze-champion-gen9-27f852fe0919/replay-seed-4005.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath/run-04-freepolicy-v3/recordings-4003-4005/000-run-04-freepolicy-v3-alternating-freeze-champion-gen9-27f852fe0919/roster.json
472450a5ec44ce7b5818c7ec50ca70ffdae7d444b0a998c55332786869e7ac44  coevo/realpath/run-04-freepolicy-v3/recordings-4003-4005/001-run-04-freepolicy-v3-alternating-freeze-champion-gen3-348df066e0db/replay-seed-4003.jsonl
9c054b05b02b78d3f2c0d58f3f438a40f9cee8866ff561f353dbbbf21cd9210c  coevo/realpath/run-04-freepolicy-v3/recordings-4003-4005/001-run-04-freepolicy-v3-alternating-freeze-champion-gen3-348df066e0db/replay-seed-4004.jsonl
278801317275900be50dd770f21602c7565ee6734f52608d99ad340e5f27428a  coevo/realpath/run-04-freepolicy-v3/recordings-4003-4005/001-run-04-freepolicy-v3-alternating-freeze-champion-gen3-348df066e0db/replay-seed-4005.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath/run-04-freepolicy-v3/recordings-4003-4005/001-run-04-freepolicy-v3-alternating-freeze-champion-gen3-348df066e0db/roster.json
1ffdbb45eaad6da85d335d8016642551b054bbcb7f593590c7cd23e7a19f6c78  coevo/realpath/run-04-freepolicy-v3/sweep-4000-4002.json
2ac505828049426aff350b9c04c02067b451c01f2ef98964eed43ee80a944403  coevo/realpath/run-04-freepolicy-v3/sweep-4003-4005.json
46a6e65f8ee74106a807fb62003752f2ff7c581e278b25b34f13a9e217481eeb  coevo/realpath/run-05-freepolicy-v2-founders/prescreen-quotes.json
717a753722ac070ae7a0ac2863e8901ca5e1cdad9136d6d10f04c4ab1d0afcec  coevo/realpath/run-05-freepolicy-v2-founders/recordings-4000-4002/000-run-05-freepolicy-v2-founders-alternating-freeze-champion-gen2-43b113ec7ebd/replay-seed-4000.jsonl
71079e3b304cda03d98de83792e4a1445152286f7acaaf6b6353e9bf4c6c6a3a  coevo/realpath/run-05-freepolicy-v2-founders/recordings-4000-4002/000-run-05-freepolicy-v2-founders-alternating-freeze-champion-gen2-43b113ec7ebd/replay-seed-4001.jsonl
3931c43189f5ef5d9fd5b40afac265c4401d23398b7bbd5583110b0a19d49d12  coevo/realpath/run-05-freepolicy-v2-founders/recordings-4000-4002/000-run-05-freepolicy-v2-founders-alternating-freeze-champion-gen2-43b113ec7ebd/replay-seed-4002.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath/run-05-freepolicy-v2-founders/recordings-4000-4002/000-run-05-freepolicy-v2-founders-alternating-freeze-champion-gen2-43b113ec7ebd/roster.json
6d0a3b89c2e28895aff117ed38eb2fd0251d0f9f8da5b70b1986d284afaa6ee5  coevo/realpath/run-05-freepolicy-v2-founders/recordings-4000-4002/001-run-05-freepolicy-v2-founders-exploiter-probe-gen3-119e5374b4af/replay-seed-4000.jsonl
a492392b29cfc2e091d3fe88fbd9b8c783a6728618dc0901de6915f4c65adf1c  coevo/realpath/run-05-freepolicy-v2-founders/recordings-4000-4002/001-run-05-freepolicy-v2-founders-exploiter-probe-gen3-119e5374b4af/replay-seed-4001.jsonl
97e9884ff6f5cfaf36e95a37b97cf87824068be60d58bedaf87b69b66f5f919b  coevo/realpath/run-05-freepolicy-v2-founders/recordings-4000-4002/001-run-05-freepolicy-v2-founders-exploiter-probe-gen3-119e5374b4af/replay-seed-4002.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath/run-05-freepolicy-v2-founders/recordings-4000-4002/001-run-05-freepolicy-v2-founders-exploiter-probe-gen3-119e5374b4af/roster.json
6e1cafaf17393b58c5938fbefd453ef79c0c5f58ddc2c53cfbe744770a101a81  coevo/realpath/run-05-freepolicy-v2-founders/recordings-4003-4005/000-run-05-freepolicy-v2-founders-alternating-freeze-champion-gen2-43b113ec7ebd/replay-seed-4003.jsonl
20c6182d2b3e0f1cfcba5ffaefc86eb9b363e472fb6ab53d537085898a7e67c8  coevo/realpath/run-05-freepolicy-v2-founders/recordings-4003-4005/000-run-05-freepolicy-v2-founders-alternating-freeze-champion-gen2-43b113ec7ebd/replay-seed-4004.jsonl
8cefb470162e9cdbf530608ec8511a218edc8cd285bc3418019b51ce614a0591  coevo/realpath/run-05-freepolicy-v2-founders/recordings-4003-4005/000-run-05-freepolicy-v2-founders-alternating-freeze-champion-gen2-43b113ec7ebd/replay-seed-4005.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath/run-05-freepolicy-v2-founders/recordings-4003-4005/000-run-05-freepolicy-v2-founders-alternating-freeze-champion-gen2-43b113ec7ebd/roster.json
0ddda5608d98e66807a1d39c8d45a9cb88fbf45fb0ead906eb8b0f5dfb35f5a5  coevo/realpath/run-05-freepolicy-v2-founders/recordings-4003-4005/001-run-05-freepolicy-v2-founders-exploiter-probe-gen3-119e5374b4af/replay-seed-4003.jsonl
82d3908872de331177768cc47559ecd3798e1049283235fb81c8973d501573f4  coevo/realpath/run-05-freepolicy-v2-founders/recordings-4003-4005/001-run-05-freepolicy-v2-founders-exploiter-probe-gen3-119e5374b4af/replay-seed-4004.jsonl
e470086f64dcf51788f3d9f9420d58eb5df61e36cc704168245df256507e9430  coevo/realpath/run-05-freepolicy-v2-founders/recordings-4003-4005/001-run-05-freepolicy-v2-founders-exploiter-probe-gen3-119e5374b4af/replay-seed-4005.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  coevo/realpath/run-05-freepolicy-v2-founders/recordings-4003-4005/001-run-05-freepolicy-v2-founders-exploiter-probe-gen3-119e5374b4af/roster.json
33722a961a6c75b45beebd8b45e2fe83cc68d8a857ee0357a9e0ce0f0590c942  coevo/realpath/run-05-freepolicy-v2-founders/sweep-4000-4002.json
255eb97549f1ce9091d9d693a9788a0e57f0712f6a78055a6a0f0a042a76aa4c  coevo/realpath/run-05-freepolicy-v2-founders/sweep-4003-4005.json
20ac096ee0b0a96e4fff0a4f6599fa79cb15e7d6461d33d9d12ff5cf22a744cb  coevo/run-01-utility-champion/crew/gen-12/31ca14b5a05c017d543e76c3ec78d42556515b1e123ac22b16a2e0680b79f119/config.json
afb05921b071f407aa6c0fef06c95e4bcd2677fd9c070ea4f3e17352bfe59714  coevo/run-01-utility-champion/crew/gen-12/31ca14b5a05c017d543e76c3ec78d42556515b1e123ac22b16a2e0680b79f119/stamp.json
31ca14b5a05c017d543e76c3ec78d42556515b1e123ac22b16a2e0680b79f119  coevo/run-01-utility-champion/crew/gen-12/31ca14b5a05c017d543e76c3ec78d42556515b1e123ac22b16a2e0680b79f119/weights.json
ee317a0651fa3574cbf6c8446f370c2f68079a71b2b5f37004627f5b5b1fa75e  coevo/run-01-utility-champion/crew/gen-12/31ca14b5a05c017d543e76c3ec78d42556515b1e123ac22b16a2e0680b79f119/weights.json.sha256
17976d6ab7df3a3732243cb4388df7124581486b89e0306c8720e01a47941a0c  coevo/run-01-utility-champion/crew/gen-6/22c9707e0ddcea03f7f4ab1fbe179cc1be7d00bcba5df8eb9ce93b69d97e8971/config.json
623650c2448fb0aa7fbcbc5b3f301ea27c6176ace450772d8218411fcf593d86  coevo/run-01-utility-champion/crew/gen-6/22c9707e0ddcea03f7f4ab1fbe179cc1be7d00bcba5df8eb9ce93b69d97e8971/stamp.json
22c9707e0ddcea03f7f4ab1fbe179cc1be7d00bcba5df8eb9ce93b69d97e8971  coevo/run-01-utility-champion/crew/gen-6/22c9707e0ddcea03f7f4ab1fbe179cc1be7d00bcba5df8eb9ce93b69d97e8971/weights.json
1f61a5436018c0c2d31c0236013acbf479d6a494dcd24efab68c9455d195baf2  coevo/run-01-utility-champion/crew/gen-6/22c9707e0ddcea03f7f4ab1fbe179cc1be7d00bcba5df8eb9ce93b69d97e8971/weights.json.sha256
a38332776a5c2fe0b8ad4d39068e00c8bd08c1043b82fe97223e4526350416c9  coevo/run-01-utility-champion/crew/gen-9/31c01b9ae1ac47b3fe9fdf7707f1b0f1cd9c80a7065a71bb0a8cc155a7520b24/config.json
8c9c06e14822993575dc7a019fc9a5491a276e9f215858cfc38d8916f25640f4  coevo/run-01-utility-champion/crew/gen-9/31c01b9ae1ac47b3fe9fdf7707f1b0f1cd9c80a7065a71bb0a8cc155a7520b24/stamp.json
31c01b9ae1ac47b3fe9fdf7707f1b0f1cd9c80a7065a71bb0a8cc155a7520b24  coevo/run-01-utility-champion/crew/gen-9/31c01b9ae1ac47b3fe9fdf7707f1b0f1cd9c80a7065a71bb0a8cc155a7520b24/weights.json
41e75b047dcad0d61bd4f0c3d9f5bdf0e1b58cd376e97c443e9ebe2953fd8901  coevo/run-01-utility-champion/crew/gen-9/31c01b9ae1ac47b3fe9fdf7707f1b0f1cd9c80a7065a71bb0a8cc155a7520b24/weights.json.sha256
296670858273f69a4c121c8161ad4efe6a3aa2b725c09e35316ebe376a28c79c  coevo/run-01-utility-champion/crew/hall_of_fame.json
48138df6f983ac23fd5a727a8e61ba0a61bfa7011eab5e414852e805346bf125  coevo/run-01-utility-champion/impostor/gen-10/46ee734a3319145dd8b12021e3d444c997dc0942798e6b0ee2c9539f82d5eb1f/config.json
e5663e9fd689ace06b3541938d8451557f5a0a70d72a31f9d31a5877bb421768  coevo/run-01-utility-champion/impostor/gen-10/46ee734a3319145dd8b12021e3d444c997dc0942798e6b0ee2c9539f82d5eb1f/stamp.json
46ee734a3319145dd8b12021e3d444c997dc0942798e6b0ee2c9539f82d5eb1f  coevo/run-01-utility-champion/impostor/gen-10/46ee734a3319145dd8b12021e3d444c997dc0942798e6b0ee2c9539f82d5eb1f/weights.json
10331ff284663c3ffbb514397eddf59d9cab0fcfa61d785f1ff2ae14f815d7cc  coevo/run-01-utility-champion/impostor/gen-10/46ee734a3319145dd8b12021e3d444c997dc0942798e6b0ee2c9539f82d5eb1f/weights.json.sha256
de0d0e0dc0100d836c1c2b5fe185b851711a8c79f56ee5f41b4021e759534288  coevo/run-01-utility-champion/impostor/gen-11/8615871f77cf097bbd8839b01b3c0e9c71dcc463206e890f261dd4f62f31cc2b/config.json
c8533e070b73c91ad25fb0337fa7243986d62fa2bd013fbae24a38dcac47e028  coevo/run-01-utility-champion/impostor/gen-11/8615871f77cf097bbd8839b01b3c0e9c71dcc463206e890f261dd4f62f31cc2b/stamp.json
8615871f77cf097bbd8839b01b3c0e9c71dcc463206e890f261dd4f62f31cc2b  coevo/run-01-utility-champion/impostor/gen-11/8615871f77cf097bbd8839b01b3c0e9c71dcc463206e890f261dd4f62f31cc2b/weights.json
2fdf7055c51d8bf1abb4d74f0b18944530586807082dad6b59b3a355cd167230  coevo/run-01-utility-champion/impostor/gen-11/8615871f77cf097bbd8839b01b3c0e9c71dcc463206e890f261dd4f62f31cc2b/weights.json.sha256
f3a2bcbe4af5b5b6a3a7f0b37d4bdc1badc28d50ccbcacae21028b36f8c51f97  coevo/run-01-utility-champion/impostor/gen-12/7ffd56f635017c4aaf51a3325fedb18e7e5d96efc5af7ade9d78c8bdae3db47c/config.json
76c073ec96d3125beb1821af8db2910a228e98a4ae2006655989637cfd86aac8  coevo/run-01-utility-champion/impostor/gen-12/7ffd56f635017c4aaf51a3325fedb18e7e5d96efc5af7ade9d78c8bdae3db47c/stamp.json
7ffd56f635017c4aaf51a3325fedb18e7e5d96efc5af7ade9d78c8bdae3db47c  coevo/run-01-utility-champion/impostor/gen-12/7ffd56f635017c4aaf51a3325fedb18e7e5d96efc5af7ade9d78c8bdae3db47c/weights.json
d7e581f2168d2bf9fa0ac71d4d110bdf9e715ab1eca6cf4d0ebfcd647d77d009  coevo/run-01-utility-champion/impostor/gen-12/7ffd56f635017c4aaf51a3325fedb18e7e5d96efc5af7ade9d78c8bdae3db47c/weights.json.sha256
284feb9a4778aa48787679ab70f916c978a84cdfbb7f1c481cd2df94e2d3475a  coevo/run-01-utility-champion/impostor/gen-4/a88f726205c8e75d5220a59dde205347a1cfd62411fd426a957e2295021c0aad/config.json
3e6ec76a671d594d5d8621eb64595fc6dee7777dd69e4fbaed73bf595736dda1  coevo/run-01-utility-champion/impostor/gen-4/a88f726205c8e75d5220a59dde205347a1cfd62411fd426a957e2295021c0aad/stamp.json
a88f726205c8e75d5220a59dde205347a1cfd62411fd426a957e2295021c0aad  coevo/run-01-utility-champion/impostor/gen-4/a88f726205c8e75d5220a59dde205347a1cfd62411fd426a957e2295021c0aad/weights.json
43fbbbe27783cec0517d75b754a5a9d24b7ec5e3bed9379ac4ac3be1c085dc08  coevo/run-01-utility-champion/impostor/gen-4/a88f726205c8e75d5220a59dde205347a1cfd62411fd426a957e2295021c0aad/weights.json.sha256
36638a04c3f84e976b816ff717086a8c72145708c8ce4881e3fc4212a4ec1dd0  coevo/run-01-utility-champion/impostor/gen-5/ec9de936c1f78996c072922e9c590fc6292949f5d8a20235319bdb044a00fd96/config.json
b97d2afc72059d2ee22bb09dd6b7dca449819033300d79372c93815fb0ba3ca0  coevo/run-01-utility-champion/impostor/gen-5/ec9de936c1f78996c072922e9c590fc6292949f5d8a20235319bdb044a00fd96/stamp.json
ec9de936c1f78996c072922e9c590fc6292949f5d8a20235319bdb044a00fd96  coevo/run-01-utility-champion/impostor/gen-5/ec9de936c1f78996c072922e9c590fc6292949f5d8a20235319bdb044a00fd96/weights.json
2118e13df0386972c39e26f9ec8ea471b5629f5134cc566f9e005df859b26f25  coevo/run-01-utility-champion/impostor/gen-5/ec9de936c1f78996c072922e9c590fc6292949f5d8a20235319bdb044a00fd96/weights.json.sha256
d105a4b68358a226af84b955295764487dab52e3d279ac480d745f8d9a72bec4  coevo/run-01-utility-champion/impostor/gen-6/472f93b8716d839ee974c7c1081fc509bad7438da2a7dc9ae8ac6757f198677d/config.json
5b61156f1987ad41cec2d84af4f0afec6efe79564c0b46bdadd3c71b9c84455c  coevo/run-01-utility-champion/impostor/gen-6/472f93b8716d839ee974c7c1081fc509bad7438da2a7dc9ae8ac6757f198677d/stamp.json
472f93b8716d839ee974c7c1081fc509bad7438da2a7dc9ae8ac6757f198677d  coevo/run-01-utility-champion/impostor/gen-6/472f93b8716d839ee974c7c1081fc509bad7438da2a7dc9ae8ac6757f198677d/weights.json
70f262799933a481e126b764930110f6641a84055091b51b3edc81f3fb17e4ce  coevo/run-01-utility-champion/impostor/gen-6/472f93b8716d839ee974c7c1081fc509bad7438da2a7dc9ae8ac6757f198677d/weights.json.sha256
634d72de275591d61e471be65a984f332d821e1a9401e72f587fc9316a8c0b41  coevo/run-01-utility-champion/impostor/gen-9/8ac3652a74f81e72440f960a68fa8ae258dd033451d9982592fb48daaa1a7d45/config.json
f384c9867e133b3eb096daca2cc87aa4c20effe2684eda6baa6f8236661f8a11  coevo/run-01-utility-champion/impostor/gen-9/8ac3652a74f81e72440f960a68fa8ae258dd033451d9982592fb48daaa1a7d45/stamp.json
8ac3652a74f81e72440f960a68fa8ae258dd033451d9982592fb48daaa1a7d45  coevo/run-01-utility-champion/impostor/gen-9/8ac3652a74f81e72440f960a68fa8ae258dd033451d9982592fb48daaa1a7d45/weights.json
dd5402fd45d519d455dd4980a0292ae947006079ec3ced59741ce767de61e4c9  coevo/run-01-utility-champion/impostor/gen-9/8ac3652a74f81e72440f960a68fa8ae258dd033451d9982592fb48daaa1a7d45/weights.json.sha256
1bbbb7cfb3f6834c82b7dd17f92e854d24f65b348bd434dec13fb940655b64d3  coevo/run-01-utility-champion/impostor/hall_of_fame.json
3d19cba122146c91220bb58060b4120d1f0f343a834692fdc85ca41102283e82  coevo/run-02-utility-lambda4/crew/gen-1/d15a5e12284a3bbac3971c63b9ddd81a4e95316c978afd54d69a0ef206bab8b4/config.json
baca20eb296f5fb8d4ce55e91dc673dc84d5c5f6e29eb28f11f14830c8417e76  coevo/run-02-utility-lambda4/crew/gen-1/d15a5e12284a3bbac3971c63b9ddd81a4e95316c978afd54d69a0ef206bab8b4/stamp.json
d15a5e12284a3bbac3971c63b9ddd81a4e95316c978afd54d69a0ef206bab8b4  coevo/run-02-utility-lambda4/crew/gen-1/d15a5e12284a3bbac3971c63b9ddd81a4e95316c978afd54d69a0ef206bab8b4/weights.json
8cdae8dd53c9ad203aeaf5386f19f9aa55666e5962dbaa6db47270ba163cbda6  coevo/run-02-utility-lambda4/crew/gen-1/d15a5e12284a3bbac3971c63b9ddd81a4e95316c978afd54d69a0ef206bab8b4/weights.json.sha256
937811eb487e64228003d6b9c2a5bb22854af2d5db2f25ca1cfbdf1c855aea8a  coevo/run-02-utility-lambda4/crew/gen-12/53d755165fa0b2ca2a627ac053dd3048e4f584ebcd061331eb68fd33832e05db/config.json
59adf1514be5a35f725fb585da88814ce9599c9f80ea98deefaeee8536d189c8  coevo/run-02-utility-lambda4/crew/gen-12/53d755165fa0b2ca2a627ac053dd3048e4f584ebcd061331eb68fd33832e05db/stamp.json
53d755165fa0b2ca2a627ac053dd3048e4f584ebcd061331eb68fd33832e05db  coevo/run-02-utility-lambda4/crew/gen-12/53d755165fa0b2ca2a627ac053dd3048e4f584ebcd061331eb68fd33832e05db/weights.json
22e3a39f10d29c13be238e34b849de3ad65192e55698d6200c455f1ca9cec27c  coevo/run-02-utility-lambda4/crew/gen-12/53d755165fa0b2ca2a627ac053dd3048e4f584ebcd061331eb68fd33832e05db/weights.json.sha256
93f062bef4358a6168b252e546b8e4cb8f7f7597352145d2d65a5b5f0ca25db6  coevo/run-02-utility-lambda4/crew/gen-2/11bde07828e63d9dc8102ac3621d4a5591e8a44864cfd235aab4c47f5a51e4ea/config.json
228d6ff9d1cb654e0fcac38d1eb37e9f128f4ef3e1c76bf8b366759e33365858  coevo/run-02-utility-lambda4/crew/gen-2/11bde07828e63d9dc8102ac3621d4a5591e8a44864cfd235aab4c47f5a51e4ea/stamp.json
11bde07828e63d9dc8102ac3621d4a5591e8a44864cfd235aab4c47f5a51e4ea  coevo/run-02-utility-lambda4/crew/gen-2/11bde07828e63d9dc8102ac3621d4a5591e8a44864cfd235aab4c47f5a51e4ea/weights.json
57475d5b5becbee12c802cdc4cf0d1719cc5635801e0cfb1c73be04962d8beb3  coevo/run-02-utility-lambda4/crew/gen-2/11bde07828e63d9dc8102ac3621d4a5591e8a44864cfd235aab4c47f5a51e4ea/weights.json.sha256
11a54a8262c208c5e71748efea8fc3d73c201faa0d4f98fa858dba8739e3db24  coevo/run-02-utility-lambda4/crew/gen-3/fa870c58d290cfecb39149272f6c43ca373d44534891dd8e8777588fb8bfa6a4/config.json
f830a972e2d378d2678c3c2893e11972c0623b56116b93566e45ccb1ff1947fe  coevo/run-02-utility-lambda4/crew/gen-3/fa870c58d290cfecb39149272f6c43ca373d44534891dd8e8777588fb8bfa6a4/stamp.json
fa870c58d290cfecb39149272f6c43ca373d44534891dd8e8777588fb8bfa6a4  coevo/run-02-utility-lambda4/crew/gen-3/fa870c58d290cfecb39149272f6c43ca373d44534891dd8e8777588fb8bfa6a4/weights.json
fba26c3566a22c37dac366699356a301d8cf2daae0304460204c1c67f38cb086  coevo/run-02-utility-lambda4/crew/gen-3/fa870c58d290cfecb39149272f6c43ca373d44534891dd8e8777588fb8bfa6a4/weights.json.sha256
18abeddd58e7e704d9bc69b817c9f87f154d677949c292a4ffb79b5ce7a8a3ce  coevo/run-02-utility-lambda4/crew/gen-6/1baf6fefec590c1fef6e5570846b0633c4090391b7fb264f9324ab62238c06fa/config.json
bd2605d9b8197cbebefc1a824cc41b7524ece008dd9429db199c6e18fa43c9ea  coevo/run-02-utility-lambda4/crew/gen-6/1baf6fefec590c1fef6e5570846b0633c4090391b7fb264f9324ab62238c06fa/stamp.json
1baf6fefec590c1fef6e5570846b0633c4090391b7fb264f9324ab62238c06fa  coevo/run-02-utility-lambda4/crew/gen-6/1baf6fefec590c1fef6e5570846b0633c4090391b7fb264f9324ab62238c06fa/weights.json
9b0b97a4ddb044ee9aeecba4f847a370da5b1f426b1de98f4fa6aad94ee8a73b  coevo/run-02-utility-lambda4/crew/gen-6/1baf6fefec590c1fef6e5570846b0633c4090391b7fb264f9324ab62238c06fa/weights.json.sha256
bb7b7d1e912cc176d927efd3251a33e355321602d1a4329e00dcec330bc48e04  coevo/run-02-utility-lambda4/crew/gen-7/47909077c7b1bc9bed75d8ae76ae0eeff27ceb84930250757368425d6272b723/config.json
e2c5646337b91ca9c7ebf3090541dbcb8cf4d1dca5c64a7a7c410cd71b8a8894  coevo/run-02-utility-lambda4/crew/gen-7/47909077c7b1bc9bed75d8ae76ae0eeff27ceb84930250757368425d6272b723/stamp.json
47909077c7b1bc9bed75d8ae76ae0eeff27ceb84930250757368425d6272b723  coevo/run-02-utility-lambda4/crew/gen-7/47909077c7b1bc9bed75d8ae76ae0eeff27ceb84930250757368425d6272b723/weights.json
be4688cb71f32dad609bf443e8027ecbdaddeac99d59786c6cf63fdbf289a169  coevo/run-02-utility-lambda4/crew/gen-7/47909077c7b1bc9bed75d8ae76ae0eeff27ceb84930250757368425d6272b723/weights.json.sha256
e796f844cd8728221c9f780bb27c9e1d802ddaf2ddd73d40630ba68b3fe6f089  coevo/run-02-utility-lambda4/crew/gen-8/658a0fbff4e01758763eb9805a9ee2df338f71df88529fa8f36bfb8e8a815092/config.json
7474bfa283d003cc4a1519bb642f756c811f388d207c87421f5e4071cc917421  coevo/run-02-utility-lambda4/crew/gen-8/658a0fbff4e01758763eb9805a9ee2df338f71df88529fa8f36bfb8e8a815092/stamp.json
658a0fbff4e01758763eb9805a9ee2df338f71df88529fa8f36bfb8e8a815092  coevo/run-02-utility-lambda4/crew/gen-8/658a0fbff4e01758763eb9805a9ee2df338f71df88529fa8f36bfb8e8a815092/weights.json
717b1007eace16c8a9bd28341e28249449de177225e47a0ddce5a27c176fed5d  coevo/run-02-utility-lambda4/crew/gen-8/658a0fbff4e01758763eb9805a9ee2df338f71df88529fa8f36bfb8e8a815092/weights.json.sha256
5c9a3237572ae6e50f96160cd19042f741573f6969540e0372367f6fa51ecd95  coevo/run-02-utility-lambda4/crew/gen-9/50aa0e961da98e1f3a7b509ae49840c0e2cf9c3cadd0b5655bedd97b623918e1/config.json
5b534687c1f54550627ac56c14336962d66d876f5930b69aa94bdae26ba1b2c1  coevo/run-02-utility-lambda4/crew/gen-9/50aa0e961da98e1f3a7b509ae49840c0e2cf9c3cadd0b5655bedd97b623918e1/stamp.json
50aa0e961da98e1f3a7b509ae49840c0e2cf9c3cadd0b5655bedd97b623918e1  coevo/run-02-utility-lambda4/crew/gen-9/50aa0e961da98e1f3a7b509ae49840c0e2cf9c3cadd0b5655bedd97b623918e1/weights.json
ae910b2f1604ba1e17c8a5f814b87adb769245e9e7dfd37748bebaca16435fcb  coevo/run-02-utility-lambda4/crew/gen-9/50aa0e961da98e1f3a7b509ae49840c0e2cf9c3cadd0b5655bedd97b623918e1/weights.json.sha256
a39009c753d7b43e72c1a57529933b3233a865b93146a608d54f0b7c37ee5aa7  coevo/run-02-utility-lambda4/crew/hall_of_fame.json
58ec54bd3fea2d7f16cc7e661b15b39f7801566bcbd574fe0e29ad19908ba189  coevo/run-02-utility-lambda4/impostor/gen-10/d2aba2ba32030da9a65b1c1f21fe00470f30c949edaca63f07b7833ba3197e04/config.json
4b4db3c5ca82dbd216a1a132d3abc44998b94189d0ba30809578fe5f6b19d7eb  coevo/run-02-utility-lambda4/impostor/gen-10/d2aba2ba32030da9a65b1c1f21fe00470f30c949edaca63f07b7833ba3197e04/stamp.json
d2aba2ba32030da9a65b1c1f21fe00470f30c949edaca63f07b7833ba3197e04  coevo/run-02-utility-lambda4/impostor/gen-10/d2aba2ba32030da9a65b1c1f21fe00470f30c949edaca63f07b7833ba3197e04/weights.json
c41aa33a29007cffe8253903aa42a024509206126f2c2800a088e3bdc67d4bb5  coevo/run-02-utility-lambda4/impostor/gen-10/d2aba2ba32030da9a65b1c1f21fe00470f30c949edaca63f07b7833ba3197e04/weights.json.sha256
d73c27033cf7663ea2017b1a681ad59f055f8b793f2a0110366b1e889d839d21  coevo/run-02-utility-lambda4/impostor/gen-11/d00cd283a70af65db1bcac0f02bea1237554d372039a40659c98863f7f5caae2/config.json
edf7b973403011801598c193d6a1dc7eef1a3f37bf638fa99de939f6c1d1a7f3  coevo/run-02-utility-lambda4/impostor/gen-11/d00cd283a70af65db1bcac0f02bea1237554d372039a40659c98863f7f5caae2/stamp.json
d00cd283a70af65db1bcac0f02bea1237554d372039a40659c98863f7f5caae2  coevo/run-02-utility-lambda4/impostor/gen-11/d00cd283a70af65db1bcac0f02bea1237554d372039a40659c98863f7f5caae2/weights.json
62f1561b2ec7b0876fc6639c8a4397755b2cac5c49455335ff35b1e90ea2bc02  coevo/run-02-utility-lambda4/impostor/gen-11/d00cd283a70af65db1bcac0f02bea1237554d372039a40659c98863f7f5caae2/weights.json.sha256
6a19a01e19334a23008a31bfb2ad2c70b4a19efe703873f7879fbc043dda04d4  coevo/run-02-utility-lambda4/impostor/gen-12/975048e7dcc56c2dce986a76fb89b5bcc61b881f9294c31954e88e49416afb18/config.json
68f2df0528ebb103035888486d9beadead9073d57dc849c47c3756d675db0f96  coevo/run-02-utility-lambda4/impostor/gen-12/975048e7dcc56c2dce986a76fb89b5bcc61b881f9294c31954e88e49416afb18/stamp.json
975048e7dcc56c2dce986a76fb89b5bcc61b881f9294c31954e88e49416afb18  coevo/run-02-utility-lambda4/impostor/gen-12/975048e7dcc56c2dce986a76fb89b5bcc61b881f9294c31954e88e49416afb18/weights.json
3796b0f5a8fd3c582573e0a30452595579aa8a1e2c97482ba5921edf3baa8f8d  coevo/run-02-utility-lambda4/impostor/gen-12/975048e7dcc56c2dce986a76fb89b5bcc61b881f9294c31954e88e49416afb18/weights.json.sha256
c92a9dd1a2ebdb3e70a1fc2af2e685d18906147d87bfe192541f5c106080d013  coevo/run-02-utility-lambda4/impostor/gen-3/10c1f9f3c0a263d9175f6e249b8083d6a24f2eb70238cb5bc623cc8ba47574e7/config.json
a3bf10f15c64be2dfb38ac282265f74e93c93680f8887794ac52787d18a16bae  coevo/run-02-utility-lambda4/impostor/gen-3/10c1f9f3c0a263d9175f6e249b8083d6a24f2eb70238cb5bc623cc8ba47574e7/stamp.json
10c1f9f3c0a263d9175f6e249b8083d6a24f2eb70238cb5bc623cc8ba47574e7  coevo/run-02-utility-lambda4/impostor/gen-3/10c1f9f3c0a263d9175f6e249b8083d6a24f2eb70238cb5bc623cc8ba47574e7/weights.json
40cc379855902d6612a1914121154620d07fce608f2f2b37ffb1cc68c6e93516  coevo/run-02-utility-lambda4/impostor/gen-3/10c1f9f3c0a263d9175f6e249b8083d6a24f2eb70238cb5bc623cc8ba47574e7/weights.json.sha256
e5ebabced87c93a71e035b68b651ef7656cff0d028fa2e437f9de93a2dc99f0f  coevo/run-02-utility-lambda4/impostor/gen-6/f9a26c912d34fd3e31dbbf541236f272eec9841a9c6ae9e4b437779d0672cdd6/config.json
8ebd817d932e12db8306397cf17aac0e016aa9cef03f7e47b5bc9920d896df4c  coevo/run-02-utility-lambda4/impostor/gen-6/f9a26c912d34fd3e31dbbf541236f272eec9841a9c6ae9e4b437779d0672cdd6/stamp.json
f9a26c912d34fd3e31dbbf541236f272eec9841a9c6ae9e4b437779d0672cdd6  coevo/run-02-utility-lambda4/impostor/gen-6/f9a26c912d34fd3e31dbbf541236f272eec9841a9c6ae9e4b437779d0672cdd6/weights.json
565a9712c86c999e4062d194e2d39263b0af49202c457bd4995b12a6838eba23  coevo/run-02-utility-lambda4/impostor/gen-6/f9a26c912d34fd3e31dbbf541236f272eec9841a9c6ae9e4b437779d0672cdd6/weights.json.sha256
9eeabe18ca29032b2dd08af60f7a0706ede233aa91c15e11cd8d1f822307dcf7  coevo/run-02-utility-lambda4/impostor/gen-9/2ca474514b86cb8e2e47ef90dd552c34e7076371e97611f7a47fbc387826d4e0/config.json
49faee2623b253b96c7bda1a93560e07a6f234352a82b026d273ad9f9909a69a  coevo/run-02-utility-lambda4/impostor/gen-9/2ca474514b86cb8e2e47ef90dd552c34e7076371e97611f7a47fbc387826d4e0/stamp.json
2ca474514b86cb8e2e47ef90dd552c34e7076371e97611f7a47fbc387826d4e0  coevo/run-02-utility-lambda4/impostor/gen-9/2ca474514b86cb8e2e47ef90dd552c34e7076371e97611f7a47fbc387826d4e0/weights.json
f85ecde03a31b10631788790d16dd7e690e22336aaa5cf468f462329d20b870c  coevo/run-02-utility-lambda4/impostor/gen-9/2ca474514b86cb8e2e47ef90dd552c34e7076371e97611f7a47fbc387826d4e0/weights.json.sha256
d88ebe04e51a2245800b75e657f77df15879859874932cebcee1ebb0f72db11f  coevo/run-02-utility-lambda4/impostor/hall_of_fame.json
60bffd5740ab153b603c1554972f353119e3214d690752fcf28aa2107c3fd1e5  coevo/run-03-utility-bcanchor/crew/gen-12/706c6c1f38c89e0e0a9c480d4e7ce699b8c211ce9046d4379785bf01f4cb7422/config.json
43f21b3f61f4ee3f10801d136092b589e40b677b67cbc1afd1db24346f9298c8  coevo/run-03-utility-bcanchor/crew/gen-12/706c6c1f38c89e0e0a9c480d4e7ce699b8c211ce9046d4379785bf01f4cb7422/stamp.json
706c6c1f38c89e0e0a9c480d4e7ce699b8c211ce9046d4379785bf01f4cb7422  coevo/run-03-utility-bcanchor/crew/gen-12/706c6c1f38c89e0e0a9c480d4e7ce699b8c211ce9046d4379785bf01f4cb7422/weights.json
f2a1d5600efb2615930b344d49bc909f3c198e476be3b0510184e643eba1a385  coevo/run-03-utility-bcanchor/crew/gen-12/706c6c1f38c89e0e0a9c480d4e7ce699b8c211ce9046d4379785bf01f4cb7422/weights.json.sha256
2ecdb5c27ffd33bbb78b6eb67e1facaef79bbac90b5d6b2f86b29a0dc59b7fbb  coevo/run-03-utility-bcanchor/crew/gen-3/bb9d1602f1c8cf15c509fdd108d6a6cc654bee3a88cd4886c4eabde5868ff8fc/config.json
cad24118fd9fb6fdeac4bd111dd219a5fd3e6ade361a7e27678b97452996b1ac  coevo/run-03-utility-bcanchor/crew/gen-3/bb9d1602f1c8cf15c509fdd108d6a6cc654bee3a88cd4886c4eabde5868ff8fc/stamp.json
bb9d1602f1c8cf15c509fdd108d6a6cc654bee3a88cd4886c4eabde5868ff8fc  coevo/run-03-utility-bcanchor/crew/gen-3/bb9d1602f1c8cf15c509fdd108d6a6cc654bee3a88cd4886c4eabde5868ff8fc/weights.json
f12e386c744adebeaab835a6a30ba66db3545165bd706437285e507b26c96a90  coevo/run-03-utility-bcanchor/crew/gen-3/bb9d1602f1c8cf15c509fdd108d6a6cc654bee3a88cd4886c4eabde5868ff8fc/weights.json.sha256
2ddf18530b43808f968d2bec7b9fdbe95a5a6c4753f9aa9bc427dd31f01a0acd  coevo/run-03-utility-bcanchor/crew/gen-6/1ae4883b4293d0481ed7939648a2e690b029a3ac2352d4b9e60127a55e50fc3d/config.json
98349414c635ec59543d4209bcc08dc535f131eb98758f7a638f031b771d0d34  coevo/run-03-utility-bcanchor/crew/gen-6/1ae4883b4293d0481ed7939648a2e690b029a3ac2352d4b9e60127a55e50fc3d/stamp.json
1ae4883b4293d0481ed7939648a2e690b029a3ac2352d4b9e60127a55e50fc3d  coevo/run-03-utility-bcanchor/crew/gen-6/1ae4883b4293d0481ed7939648a2e690b029a3ac2352d4b9e60127a55e50fc3d/weights.json
8235fd67b477dede15add3ee785b633238718b7e8ed60b0d96a46ceda49bfcd4  coevo/run-03-utility-bcanchor/crew/gen-6/1ae4883b4293d0481ed7939648a2e690b029a3ac2352d4b9e60127a55e50fc3d/weights.json.sha256
8a9e9c510ee15105c16fa50e8e09d63dda22db81a6e1b45a43222d522162e7dc  coevo/run-03-utility-bcanchor/crew/gen-7/b27c1ad0f973426ef5e4e05f5b641bfa59a1cd48809554ff9b3b985f1f5b4f3e/config.json
e14fe8c4da4f26520b11b5271570d45a0d874eff5de319b5640334ea2c41dfc8  coevo/run-03-utility-bcanchor/crew/gen-7/b27c1ad0f973426ef5e4e05f5b641bfa59a1cd48809554ff9b3b985f1f5b4f3e/stamp.json
b27c1ad0f973426ef5e4e05f5b641bfa59a1cd48809554ff9b3b985f1f5b4f3e  coevo/run-03-utility-bcanchor/crew/gen-7/b27c1ad0f973426ef5e4e05f5b641bfa59a1cd48809554ff9b3b985f1f5b4f3e/weights.json
a0684eda74e33b76c4d0d7c5717a4683b72ba2b783a685c8b5f63706322e5ad5  coevo/run-03-utility-bcanchor/crew/gen-7/b27c1ad0f973426ef5e4e05f5b641bfa59a1cd48809554ff9b3b985f1f5b4f3e/weights.json.sha256
b6f235fdc1fc9b392e65dcc21981c18078627db5ea18f7feffe4db87f40e9457  coevo/run-03-utility-bcanchor/crew/gen-8/5cf62887f3704feca3f31ebe3eb17c76a2218b60931089c805327fb39777a5a1/config.json
ac01f1774ee2250808820787cec5717334662e8ba18852e40fb1ab0ebb2ffa18  coevo/run-03-utility-bcanchor/crew/gen-8/5cf62887f3704feca3f31ebe3eb17c76a2218b60931089c805327fb39777a5a1/stamp.json
5cf62887f3704feca3f31ebe3eb17c76a2218b60931089c805327fb39777a5a1  coevo/run-03-utility-bcanchor/crew/gen-8/5cf62887f3704feca3f31ebe3eb17c76a2218b60931089c805327fb39777a5a1/weights.json
23b7c8ac72a5ddd4725d48352ca6022f270f885f52d0609234312457c96e0b76  coevo/run-03-utility-bcanchor/crew/gen-8/5cf62887f3704feca3f31ebe3eb17c76a2218b60931089c805327fb39777a5a1/weights.json.sha256
bec23c971bd59e7c01da5f4f976cfbd8fa1ea6f850dac637304b90d9f4fd97c0  coevo/run-03-utility-bcanchor/crew/hall_of_fame.json
a7765cc52381c41f03e554161dcdd24cc6af0d88f1c12ad4319d750b346b7c42  coevo/run-03-utility-bcanchor/impostor/gen-10/4a491aa43489551026811ed105c8f0d05ab1ef54c201cd014e839e5961f8bd48/config.json
a63ee80146e918d8158440ad3bffab77f2cca3a0147f6194d29d8ab00240fc36  coevo/run-03-utility-bcanchor/impostor/gen-10/4a491aa43489551026811ed105c8f0d05ab1ef54c201cd014e839e5961f8bd48/stamp.json
4a491aa43489551026811ed105c8f0d05ab1ef54c201cd014e839e5961f8bd48  coevo/run-03-utility-bcanchor/impostor/gen-10/4a491aa43489551026811ed105c8f0d05ab1ef54c201cd014e839e5961f8bd48/weights.json
61e4a210be7a1c289c16f1a7c39dff0395307352704160a7edd41f2278ba3407  coevo/run-03-utility-bcanchor/impostor/gen-10/4a491aa43489551026811ed105c8f0d05ab1ef54c201cd014e839e5961f8bd48/weights.json.sha256
25db29bf99098b21fb5d0bf27a641e1fe19c5448e6caafbb6debffa0e3534aa0  coevo/run-03-utility-bcanchor/impostor/gen-11/312f0eda1d02098db5d6c2dc248568745d35365558e750c2653e2b4a9db9970f/config.json
e1904a9e6a316571c91294c627dd8a2255f3dcd3daea37f597b5510c4818afcb  coevo/run-03-utility-bcanchor/impostor/gen-11/312f0eda1d02098db5d6c2dc248568745d35365558e750c2653e2b4a9db9970f/stamp.json
312f0eda1d02098db5d6c2dc248568745d35365558e750c2653e2b4a9db9970f  coevo/run-03-utility-bcanchor/impostor/gen-11/312f0eda1d02098db5d6c2dc248568745d35365558e750c2653e2b4a9db9970f/weights.json
c8f10a8919434273dc62ee61a4d9f9bb3623798baba5e2227e084573beffd007  coevo/run-03-utility-bcanchor/impostor/gen-11/312f0eda1d02098db5d6c2dc248568745d35365558e750c2653e2b4a9db9970f/weights.json.sha256
92347d1f9d5d420e8eef3518867bbe0be8c411f9ed4d6e9514f31e8dcd6ee547  coevo/run-03-utility-bcanchor/impostor/gen-12/41e960b3921b14e67c3a3aa4c8016c1c71283f1145e37fa657bda14fd820c1ed/config.json
59ad1e66c12bc817a8e3e976161046ea430f7d8069635742d22de6a33b53e19c  coevo/run-03-utility-bcanchor/impostor/gen-12/41e960b3921b14e67c3a3aa4c8016c1c71283f1145e37fa657bda14fd820c1ed/stamp.json
41e960b3921b14e67c3a3aa4c8016c1c71283f1145e37fa657bda14fd820c1ed  coevo/run-03-utility-bcanchor/impostor/gen-12/41e960b3921b14e67c3a3aa4c8016c1c71283f1145e37fa657bda14fd820c1ed/weights.json
653a133614822aba8e3109e19e35a2f30362a2976078e6ab8894fae9cf831b67  coevo/run-03-utility-bcanchor/impostor/gen-12/41e960b3921b14e67c3a3aa4c8016c1c71283f1145e37fa657bda14fd820c1ed/weights.json.sha256
8c1458b298803d805d71af01ae1119f604880cee065e10fd1024cae51f19314f  coevo/run-03-utility-bcanchor/impostor/gen-3/6d327dcbde940a5ee1bb4f9e22ff91fbbc4d74c0ddb33797043fdff69fef71d0/config.json
e5c5d876cfa28a31d673675e8f8621054bc9c9be97e539eee584b76e0b0cdaf1  coevo/run-03-utility-bcanchor/impostor/gen-3/6d327dcbde940a5ee1bb4f9e22ff91fbbc4d74c0ddb33797043fdff69fef71d0/stamp.json
6d327dcbde940a5ee1bb4f9e22ff91fbbc4d74c0ddb33797043fdff69fef71d0  coevo/run-03-utility-bcanchor/impostor/gen-3/6d327dcbde940a5ee1bb4f9e22ff91fbbc4d74c0ddb33797043fdff69fef71d0/weights.json
f893500dcbadee64f134260391e0d9f7afbc87c98b830e476eab4cb99d770037  coevo/run-03-utility-bcanchor/impostor/gen-3/6d327dcbde940a5ee1bb4f9e22ff91fbbc4d74c0ddb33797043fdff69fef71d0/weights.json.sha256
2a246a8acc619ad00d4a561ce81fb5546a84649e1f24d5db1d72eb1a61d12e27  coevo/run-03-utility-bcanchor/impostor/gen-4/56a8e5b956e10c157c6b04f908faec90e1ea777451e30e0ea5d2898c593c97c8/config.json
cedfc70b645df978ddfb755dc19afbf5418094f51d1897fbedc410598c54d0f8  coevo/run-03-utility-bcanchor/impostor/gen-4/56a8e5b956e10c157c6b04f908faec90e1ea777451e30e0ea5d2898c593c97c8/stamp.json
56a8e5b956e10c157c6b04f908faec90e1ea777451e30e0ea5d2898c593c97c8  coevo/run-03-utility-bcanchor/impostor/gen-4/56a8e5b956e10c157c6b04f908faec90e1ea777451e30e0ea5d2898c593c97c8/weights.json
2b31d65f327c10c15de133e8d33958907d51b5848bf61d93722f3a2e6924b7b1  coevo/run-03-utility-bcanchor/impostor/gen-4/56a8e5b956e10c157c6b04f908faec90e1ea777451e30e0ea5d2898c593c97c8/weights.json.sha256
46caca9e7fb68d6586a8f1c519b82223e11c3cf94ffdef972b89e40b24d2d14f  coevo/run-03-utility-bcanchor/impostor/gen-5/4cce01320886781bdfafa0e3fa02732bcb14ef251eecdc2e612a198c646d4639/config.json
58a6a66206d64f8f1233b0c8bb507b7de2f4a8f608eb9c1205649b3798182d8c  coevo/run-03-utility-bcanchor/impostor/gen-5/4cce01320886781bdfafa0e3fa02732bcb14ef251eecdc2e612a198c646d4639/stamp.json
4cce01320886781bdfafa0e3fa02732bcb14ef251eecdc2e612a198c646d4639  coevo/run-03-utility-bcanchor/impostor/gen-5/4cce01320886781bdfafa0e3fa02732bcb14ef251eecdc2e612a198c646d4639/weights.json
0422b8ed0ce9f128109348c3ac057a9f0723bc89c9d080bbb5cbf820e0d0b859  coevo/run-03-utility-bcanchor/impostor/gen-5/4cce01320886781bdfafa0e3fa02732bcb14ef251eecdc2e612a198c646d4639/weights.json.sha256
118c2b2698c16779c0c037d1e764e5c8671863368109ac1b490bcdba7ec47f90  coevo/run-03-utility-bcanchor/impostor/gen-6/112b6c9e3d21242e29937cecd227a2e1e401e0d40790684eda23483dd43d07df/config.json
69c7dc985502c93a753f97c4c4be9848e6930f95bdbc4ed9be0b90c36ff4fb0f  coevo/run-03-utility-bcanchor/impostor/gen-6/112b6c9e3d21242e29937cecd227a2e1e401e0d40790684eda23483dd43d07df/stamp.json
112b6c9e3d21242e29937cecd227a2e1e401e0d40790684eda23483dd43d07df  coevo/run-03-utility-bcanchor/impostor/gen-6/112b6c9e3d21242e29937cecd227a2e1e401e0d40790684eda23483dd43d07df/weights.json
127b6d3897fb57c4baa611dc32d9227e04db8ba67a73db4dfd0433a88215c9ba  coevo/run-03-utility-bcanchor/impostor/gen-6/112b6c9e3d21242e29937cecd227a2e1e401e0d40790684eda23483dd43d07df/weights.json.sha256
17f6045553139fe17c845cacdce51a39fba1afa538c4baadfd8809b820c4dff6  coevo/run-03-utility-bcanchor/impostor/gen-9/a89be618bfbbd2a73941d1de9ead774b588206c513b58393b1f1747b1a68386e/config.json
e010605fa61b372dd95a56813ff54622724d9b622609d27939e5fd7fc693ec98  coevo/run-03-utility-bcanchor/impostor/gen-9/a89be618bfbbd2a73941d1de9ead774b588206c513b58393b1f1747b1a68386e/stamp.json
a89be618bfbbd2a73941d1de9ead774b588206c513b58393b1f1747b1a68386e  coevo/run-03-utility-bcanchor/impostor/gen-9/a89be618bfbbd2a73941d1de9ead774b588206c513b58393b1f1747b1a68386e/weights.json
c1982bfded2a80cd5daee961d24d8994accc19c5d5eaa35be612ea1febbd0dcc  coevo/run-03-utility-bcanchor/impostor/gen-9/a89be618bfbbd2a73941d1de9ead774b588206c513b58393b1f1747b1a68386e/weights.json.sha256
e5a2d574365568c87fb792090b5af0e4d9b22ca6ad0e1007915f80f0afd49a17  coevo/run-03-utility-bcanchor/impostor/hall_of_fame.json
3741ef25d92a108be24fbbdebf26d85ee8fd78ad2bc9a73c434a9d87b1525207  coevo/run-04-freepolicy-v3/crew/gen-1/76a0e8c542a8bda8d87e5e1192403abf74385bc9b8ea1892e7c86cfe75644054/config.json
2a2246c1cddae6dd0339273704c39c44ce3403e28f9c256973a3429df0c33ee9  coevo/run-04-freepolicy-v3/crew/gen-1/76a0e8c542a8bda8d87e5e1192403abf74385bc9b8ea1892e7c86cfe75644054/stamp.json
76a0e8c542a8bda8d87e5e1192403abf74385bc9b8ea1892e7c86cfe75644054  coevo/run-04-freepolicy-v3/crew/gen-1/76a0e8c542a8bda8d87e5e1192403abf74385bc9b8ea1892e7c86cfe75644054/weights.json
0f059094ddbbaa781003fd9875660ed88dbc3f8ec691db832b9a1d83596a9c5c  coevo/run-04-freepolicy-v3/crew/gen-1/76a0e8c542a8bda8d87e5e1192403abf74385bc9b8ea1892e7c86cfe75644054/weights.json.sha256
dd896fe53ed39f70482a60beecc589350f0c060a331a9a7c2ac4701a3d19c93f  coevo/run-04-freepolicy-v3/crew/gen-12/9dc8432fe4fd69a2c5951887d83b82356d0e19609ced204afe07b10f72e715c9/config.json
f3a57287f0731729ab9e3060302902b3f7e6e8b11a8acabec1346ce0cbf35448  coevo/run-04-freepolicy-v3/crew/gen-12/9dc8432fe4fd69a2c5951887d83b82356d0e19609ced204afe07b10f72e715c9/stamp.json
9dc8432fe4fd69a2c5951887d83b82356d0e19609ced204afe07b10f72e715c9  coevo/run-04-freepolicy-v3/crew/gen-12/9dc8432fe4fd69a2c5951887d83b82356d0e19609ced204afe07b10f72e715c9/weights.json
001865d1db8002f089af46a2e899318279de84a2711c0b6383888171c8c7177b  coevo/run-04-freepolicy-v3/crew/gen-12/9dc8432fe4fd69a2c5951887d83b82356d0e19609ced204afe07b10f72e715c9/weights.json.sha256
d1b5440694c7f79407a91b11ef84f01b3b9d7430f77ab6ecc57a1344699e4b0d  coevo/run-04-freepolicy-v3/crew/gen-2/ba09557be65fa5f2bbfcdf28f41db103ab8798bfe764cfb9d2c4a15dfe166e94/config.json
631c3cb8996cd7e9451e10be188a2e58108572d9b8c1a88a8ba1bbcdb868f534  coevo/run-04-freepolicy-v3/crew/gen-2/ba09557be65fa5f2bbfcdf28f41db103ab8798bfe764cfb9d2c4a15dfe166e94/stamp.json
ba09557be65fa5f2bbfcdf28f41db103ab8798bfe764cfb9d2c4a15dfe166e94  coevo/run-04-freepolicy-v3/crew/gen-2/ba09557be65fa5f2bbfcdf28f41db103ab8798bfe764cfb9d2c4a15dfe166e94/weights.json
f69c45ee72e4bee8eb53aecdcbc057a384337ddb258d8e903fefab32b920e7ce  coevo/run-04-freepolicy-v3/crew/gen-2/ba09557be65fa5f2bbfcdf28f41db103ab8798bfe764cfb9d2c4a15dfe166e94/weights.json.sha256
d9f588094467efc15c8972f15695a56dd9ec72e529b59719832700d15b4e0d92  coevo/run-04-freepolicy-v3/crew/gen-3/20a00ebb51026a62be9f0261bfe6c6e6c51524e29e919a9efbb3103ea3398acc/config.json
95cf44ce47fa9f6ea1006a585f70ad21d3d0a0a42b19325969e1937e1aba09a3  coevo/run-04-freepolicy-v3/crew/gen-3/20a00ebb51026a62be9f0261bfe6c6e6c51524e29e919a9efbb3103ea3398acc/stamp.json
20a00ebb51026a62be9f0261bfe6c6e6c51524e29e919a9efbb3103ea3398acc  coevo/run-04-freepolicy-v3/crew/gen-3/20a00ebb51026a62be9f0261bfe6c6e6c51524e29e919a9efbb3103ea3398acc/weights.json
60ddbe471e210dde44d14cb65893999e569fcdec3ad409a0f47fbde2dce05d06  coevo/run-04-freepolicy-v3/crew/gen-3/20a00ebb51026a62be9f0261bfe6c6e6c51524e29e919a9efbb3103ea3398acc/weights.json.sha256
c8b53eeb9bcfd8399813931fd354df9edff80237c327cb97bd8291c490cd9701  coevo/run-04-freepolicy-v3/crew/gen-6/43e5b8696e7710ce4377446a66bf57e18d86d7fb2d871b225cb1a652c58bb13f/config.json
c54985be53379cbba84137090002dd36efbd259469e772250230139a55fe5d9a  coevo/run-04-freepolicy-v3/crew/gen-6/43e5b8696e7710ce4377446a66bf57e18d86d7fb2d871b225cb1a652c58bb13f/stamp.json
43e5b8696e7710ce4377446a66bf57e18d86d7fb2d871b225cb1a652c58bb13f  coevo/run-04-freepolicy-v3/crew/gen-6/43e5b8696e7710ce4377446a66bf57e18d86d7fb2d871b225cb1a652c58bb13f/weights.json
6258bda39b1b1803fed9082cc108878baacaf6791ae18174deecc309cedffe7e  coevo/run-04-freepolicy-v3/crew/gen-6/43e5b8696e7710ce4377446a66bf57e18d86d7fb2d871b225cb1a652c58bb13f/weights.json.sha256
887baadca74136b6152e9c657628fce1377a7883f14ad6f8d6c16ab35f62ff58  coevo/run-04-freepolicy-v3/crew/gen-8/0f0f16aa0743d768cd289a4dca6e0f83bdcf4741bf3660167c8f9e748ad68c93/config.json
63adf70d07d6a11ec4c5a3d73d8765a54c93834f44c561432e012a9d6adcb6ea  coevo/run-04-freepolicy-v3/crew/gen-8/0f0f16aa0743d768cd289a4dca6e0f83bdcf4741bf3660167c8f9e748ad68c93/stamp.json
0f0f16aa0743d768cd289a4dca6e0f83bdcf4741bf3660167c8f9e748ad68c93  coevo/run-04-freepolicy-v3/crew/gen-8/0f0f16aa0743d768cd289a4dca6e0f83bdcf4741bf3660167c8f9e748ad68c93/weights.json
1b28950eb227d422987601bc7ed1e5456b4a403bb18aad2f2be7e694896e36d7  coevo/run-04-freepolicy-v3/crew/gen-8/0f0f16aa0743d768cd289a4dca6e0f83bdcf4741bf3660167c8f9e748ad68c93/weights.json.sha256
a402675982e2c177ebf753ccf85db1e20d154b92b4ab7c8d047b5a092e6fd93d  coevo/run-04-freepolicy-v3/crew/gen-9/b953b0099267e40eb428e5208281f217bc151b2cfe3a7640e7a1ac6316bc064f/config.json
a8200c4acfdff006a77327001d2a1e44a95a9e610ac58c1b7d85fd41c070dd2f  coevo/run-04-freepolicy-v3/crew/gen-9/b953b0099267e40eb428e5208281f217bc151b2cfe3a7640e7a1ac6316bc064f/stamp.json
b953b0099267e40eb428e5208281f217bc151b2cfe3a7640e7a1ac6316bc064f  coevo/run-04-freepolicy-v3/crew/gen-9/b953b0099267e40eb428e5208281f217bc151b2cfe3a7640e7a1ac6316bc064f/weights.json
08da8ea096a865c5f03e1e94409264bbe3bf92753e2de14fb637561a2cf3ec25  coevo/run-04-freepolicy-v3/crew/gen-9/b953b0099267e40eb428e5208281f217bc151b2cfe3a7640e7a1ac6316bc064f/weights.json.sha256
a66cec0d297f38126ec4aea2563346f5592494fbb18ecf041c16f42b65b6fb20  coevo/run-04-freepolicy-v3/crew/hall_of_fame.json
21779229a8aa082ad80f62bdd8d7e94400e185a7f3d11307eb8ea6e6f27fbc3b  coevo/run-04-freepolicy-v3/impostor/gen-3/348df066e0db6e255b4ce58eaffd0875771dedd1b1154d669111545674456768/config.json
185f6152ee47b7fde021d6166c8c9756e5c08cb841799497beade40b801155a5  coevo/run-04-freepolicy-v3/impostor/gen-3/348df066e0db6e255b4ce58eaffd0875771dedd1b1154d669111545674456768/stamp.json
348df066e0db6e255b4ce58eaffd0875771dedd1b1154d669111545674456768  coevo/run-04-freepolicy-v3/impostor/gen-3/348df066e0db6e255b4ce58eaffd0875771dedd1b1154d669111545674456768/weights.json
45def44770055bf4fe6302e2e08f9832c29308bf671eb1e329a8058bcc3aa850  coevo/run-04-freepolicy-v3/impostor/gen-3/348df066e0db6e255b4ce58eaffd0875771dedd1b1154d669111545674456768/weights.json.sha256
901fb4775d3d34af6aa74341b43c5399f972b1819cf8efa3a6293a8516692a3c  coevo/run-04-freepolicy-v3/impostor/gen-9/27f852fe0919bed6035ecd7317dea08f7a9b90c16ba1331336cb5df80df0a474/config.json
f6fa432c0a3cfcd9da1526782dca04527eae4e99459e1375183bfbefafd9b772  coevo/run-04-freepolicy-v3/impostor/gen-9/27f852fe0919bed6035ecd7317dea08f7a9b90c16ba1331336cb5df80df0a474/stamp.json
27f852fe0919bed6035ecd7317dea08f7a9b90c16ba1331336cb5df80df0a474  coevo/run-04-freepolicy-v3/impostor/gen-9/27f852fe0919bed6035ecd7317dea08f7a9b90c16ba1331336cb5df80df0a474/weights.json
7f92e13bbbb2104494bfb596566b3ad6e5bae6e3991459eeda7cb36cff730c64  coevo/run-04-freepolicy-v3/impostor/gen-9/27f852fe0919bed6035ecd7317dea08f7a9b90c16ba1331336cb5df80df0a474/weights.json.sha256
c0e173f2b9e5a78e5297281fc7b738ad6c5ad5753359634541d1617e5b0ebfa1  coevo/run-04-freepolicy-v3/impostor/hall_of_fame.json
cf77a5892876825a0518c85ea28634d2668b61c760e0b5a14b7090217d3438e0  coevo/run-05-freepolicy-v2-founders/crew/gen-1/11edd676172c001369f1d42802bf49975dcc861580eefdc3e1d222c90f47256c/config.json
791f63a9527c09247fd707a10a2f4e760e43fb5acaf9daf993f685ade127e312  coevo/run-05-freepolicy-v2-founders/crew/gen-1/11edd676172c001369f1d42802bf49975dcc861580eefdc3e1d222c90f47256c/stamp.json
11edd676172c001369f1d42802bf49975dcc861580eefdc3e1d222c90f47256c  coevo/run-05-freepolicy-v2-founders/crew/gen-1/11edd676172c001369f1d42802bf49975dcc861580eefdc3e1d222c90f47256c/weights.json
83956368c36e12cc25f1913cc283076bcddaf9122f9533449a1935e45d21316f  coevo/run-05-freepolicy-v2-founders/crew/gen-1/11edd676172c001369f1d42802bf49975dcc861580eefdc3e1d222c90f47256c/weights.json.sha256
85d0c4a72a6bc26e0c38ccf86a67f74de8af1c4c485d18e2c6355d0581e36efc  coevo/run-05-freepolicy-v2-founders/crew/gen-2/38274bf2316827a73fd9fccd2d3c9815db6fb8b625c3e7a3b8de45e0d1e62c16/config.json
7870ecc88cd2a8bba64e0fcffde535e6a4361399e92a07a42b2782fbbbec3669  coevo/run-05-freepolicy-v2-founders/crew/gen-2/38274bf2316827a73fd9fccd2d3c9815db6fb8b625c3e7a3b8de45e0d1e62c16/stamp.json
38274bf2316827a73fd9fccd2d3c9815db6fb8b625c3e7a3b8de45e0d1e62c16  coevo/run-05-freepolicy-v2-founders/crew/gen-2/38274bf2316827a73fd9fccd2d3c9815db6fb8b625c3e7a3b8de45e0d1e62c16/weights.json
eae8bab0a9070efe57d9e8b62f5c73215a170c54037030ab5e0014999aa0b80f  coevo/run-05-freepolicy-v2-founders/crew/gen-2/38274bf2316827a73fd9fccd2d3c9815db6fb8b625c3e7a3b8de45e0d1e62c16/weights.json.sha256
ef59dc599e6e01e7e94502740ead78db9c07e1c1980f10bc2ec2777944c4996f  coevo/run-05-freepolicy-v2-founders/crew/gen-4/3921f86a8435795c259221a228ee346a494d792cbcf71e388f087f6181f09665/config.json
30e48d43b5053338cdb0a7d3d51d45eaeb8780219f4da394fa5a9214a21130a4  coevo/run-05-freepolicy-v2-founders/crew/gen-4/3921f86a8435795c259221a228ee346a494d792cbcf71e388f087f6181f09665/stamp.json
3921f86a8435795c259221a228ee346a494d792cbcf71e388f087f6181f09665  coevo/run-05-freepolicy-v2-founders/crew/gen-4/3921f86a8435795c259221a228ee346a494d792cbcf71e388f087f6181f09665/weights.json
dcf416b373ecd27cc297f6b7526510020fb0fa8db4766956d122757f5de23579  coevo/run-05-freepolicy-v2-founders/crew/gen-4/3921f86a8435795c259221a228ee346a494d792cbcf71e388f087f6181f09665/weights.json.sha256
48496fabd939544ee024a89e6ed0690a396aa90b83603daea79ff34a58755842  coevo/run-05-freepolicy-v2-founders/crew/hall_of_fame.json
1669b07b676f796e04d948c2bda160befdf2bb4cfdc034aef270b3e9ad9a3fc0  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/026f222d15f4fe65566bad3d2b6fbe211f5deea537c280aa58ec890731e78a51/config.json
cd7b5d30b9348cb496ff25a7d83b4fa5d893417189f2376e5d88e35decd81dfc  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/026f222d15f4fe65566bad3d2b6fbe211f5deea537c280aa58ec890731e78a51/stamp.json
026f222d15f4fe65566bad3d2b6fbe211f5deea537c280aa58ec890731e78a51  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/026f222d15f4fe65566bad3d2b6fbe211f5deea537c280aa58ec890731e78a51/weights.json
d314b9cfcab13ed92d78c11588005fe34bc765107dd732215a42d82633ce28fa  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/026f222d15f4fe65566bad3d2b6fbe211f5deea537c280aa58ec890731e78a51/weights.json.sha256
dd8fb6236ed1a27cf1dc2e1a333f789cadf6a5b88b0fc532911b00a170d7f118  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/1f68554cf0fb7b55b171d38ef3be602be0ed700ecb680f7107e7fa80f2e1d8b8/config.json
761d96483ae0be25396d010bd3643da688d0000bb2efd85b3bd47d9849ba5bd0  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/1f68554cf0fb7b55b171d38ef3be602be0ed700ecb680f7107e7fa80f2e1d8b8/stamp.json
1f68554cf0fb7b55b171d38ef3be602be0ed700ecb680f7107e7fa80f2e1d8b8  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/1f68554cf0fb7b55b171d38ef3be602be0ed700ecb680f7107e7fa80f2e1d8b8/weights.json
6ce2aa3c2e4b98d436fb7576efa2c1f1123e61b49283ae8c95e4431c2c08554f  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/1f68554cf0fb7b55b171d38ef3be602be0ed700ecb680f7107e7fa80f2e1d8b8/weights.json.sha256
0dee7c38152da5e9c067677a2f4b4db92baddd77bad0d8f50104dd769ac96512  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/4154ac84c116148fb1b4dad40ed9096f8c44000cc8ff0eaf159ef44da094abe9/config.json
2f0dc412af0e4e0d7842b2ed679f0ebdf814011062072b57a486c036fd3341cc  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/4154ac84c116148fb1b4dad40ed9096f8c44000cc8ff0eaf159ef44da094abe9/stamp.json
4154ac84c116148fb1b4dad40ed9096f8c44000cc8ff0eaf159ef44da094abe9  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/4154ac84c116148fb1b4dad40ed9096f8c44000cc8ff0eaf159ef44da094abe9/weights.json
913d67737ee742f5ea8acb68fd7bb7d7c4d2ddabb04fe65bbee163cf78cdcb41  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/4154ac84c116148fb1b4dad40ed9096f8c44000cc8ff0eaf159ef44da094abe9/weights.json.sha256
dfcf5cacc97d8b1c61e36c609570f6441b10fa2a81f0bf91253f41e7dcfb3e5f  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/55d986c01976818d7566fbd9a627793fb33d1b5545920b50a78db07724eb3c96/config.json
88d9307a881c20ee82a5a4a2f1350a42cbdb228f4d2b60b17fd58208489a88c3  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/55d986c01976818d7566fbd9a627793fb33d1b5545920b50a78db07724eb3c96/stamp.json
55d986c01976818d7566fbd9a627793fb33d1b5545920b50a78db07724eb3c96  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/55d986c01976818d7566fbd9a627793fb33d1b5545920b50a78db07724eb3c96/weights.json
aac239dbb3aaf2d7740bbabc32b4a30ad223035e5407c8c1522c05bf5a17d752  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/55d986c01976818d7566fbd9a627793fb33d1b5545920b50a78db07724eb3c96/weights.json.sha256
f4aa525262d04aa523ca00a2a0844da9cf2baf9abbd2cd92bf632642ec3ba8ff  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/58ded2b224f1490610e7d5a63fad4566152a20e03c105f5ac0ad7612206c99e4/config.json
9048e9cc72c48e6e96718a6fcfa7c99be939242f2767b3fc7f4abeaed0e7eb1e  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/58ded2b224f1490610e7d5a63fad4566152a20e03c105f5ac0ad7612206c99e4/stamp.json
58ded2b224f1490610e7d5a63fad4566152a20e03c105f5ac0ad7612206c99e4  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/58ded2b224f1490610e7d5a63fad4566152a20e03c105f5ac0ad7612206c99e4/weights.json
b639f94cc709b59441b8ab77859508c7b9247c0aba53b8b9af81c95d564314c6  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/58ded2b224f1490610e7d5a63fad4566152a20e03c105f5ac0ad7612206c99e4/weights.json.sha256
3437ec2d589b39d5231bef89425f81840d4ea7426948f10f73c2bee7748c7527  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/63035d8bf6fae8df59a673d0309939fdd52d239a14d5966b36128c6356b4490c/config.json
cc715664d3a2f54155887bdb072d9ebed4370321b1d6a284cbc15c0efa097a8a  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/63035d8bf6fae8df59a673d0309939fdd52d239a14d5966b36128c6356b4490c/stamp.json
63035d8bf6fae8df59a673d0309939fdd52d239a14d5966b36128c6356b4490c  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/63035d8bf6fae8df59a673d0309939fdd52d239a14d5966b36128c6356b4490c/weights.json
0f0344978a1f0fe3ebba572de34675fd9ea21d2a5faaa3967e6458222814f23e  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/63035d8bf6fae8df59a673d0309939fdd52d239a14d5966b36128c6356b4490c/weights.json.sha256
fa9d944140ef20c441e3ccf92ecf6ee6adfe32bb9863d0920be654becc8d4626  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/727de6d4e6f3b7e6331d2c32991d339bf85e98d2877703503c185c81c23e7203/config.json
f6ed8ba279b16dc45d507f28afd55352e31221159d11347860e78d04418d16c7  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/727de6d4e6f3b7e6331d2c32991d339bf85e98d2877703503c185c81c23e7203/stamp.json
727de6d4e6f3b7e6331d2c32991d339bf85e98d2877703503c185c81c23e7203  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/727de6d4e6f3b7e6331d2c32991d339bf85e98d2877703503c185c81c23e7203/weights.json
5449311a968f7f254f82a8f31148adf38db9af0539de44508b3d318ba9be42c5  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/727de6d4e6f3b7e6331d2c32991d339bf85e98d2877703503c185c81c23e7203/weights.json.sha256
3e9acd73e7a38e82fe6def8c2601d52b7eb0eb94370ca668822060798056953c  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/80ffbc2a0c4f1754f86e58e380c738ce0ef00344aecf1bf19daa3529a5307a55/config.json
436128c00103bba1fa4409fef99939eccc0ffa5fa50f67103b07fbb5775f07fd  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/80ffbc2a0c4f1754f86e58e380c738ce0ef00344aecf1bf19daa3529a5307a55/stamp.json
80ffbc2a0c4f1754f86e58e380c738ce0ef00344aecf1bf19daa3529a5307a55  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/80ffbc2a0c4f1754f86e58e380c738ce0ef00344aecf1bf19daa3529a5307a55/weights.json
84c0d254d9124abbc1d1b8256b8ced629eb6ba304f7c613b1a0185056b7e6bf9  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/80ffbc2a0c4f1754f86e58e380c738ce0ef00344aecf1bf19daa3529a5307a55/weights.json.sha256
ad1d5f7f249c3505c6c7038dc65609ba3d6623e5af374169cbdfa60ffe0607fa  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/8354585374e2ce82766d69a5c07d45571d90e2df9fba3bcab08f67e7d491ae3e/config.json
a9235b0b43b996134d087e8bb66d7e024546d169b9f51044a7aff9c5a99ebf8c  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/8354585374e2ce82766d69a5c07d45571d90e2df9fba3bcab08f67e7d491ae3e/stamp.json
8354585374e2ce82766d69a5c07d45571d90e2df9fba3bcab08f67e7d491ae3e  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/8354585374e2ce82766d69a5c07d45571d90e2df9fba3bcab08f67e7d491ae3e/weights.json
005e33044e0814bc421aae2aea6c7fefe98169b5d71ffe18e030b59e79ebcc64  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/8354585374e2ce82766d69a5c07d45571d90e2df9fba3bcab08f67e7d491ae3e/weights.json.sha256
b441de5f583cee4b90267bac5d6a07a77f5492926fedef14e98d1e937b6bc94c  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/85b926a42aa3f39174c69ce152df1e207e1441a96595c59e485a3a9af42594bd/config.json
656806a3dc53e71ecaf642aab3d2c22c56ee830500841e0d4f8d6ae869438515  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/85b926a42aa3f39174c69ce152df1e207e1441a96595c59e485a3a9af42594bd/stamp.json
85b926a42aa3f39174c69ce152df1e207e1441a96595c59e485a3a9af42594bd  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/85b926a42aa3f39174c69ce152df1e207e1441a96595c59e485a3a9af42594bd/weights.json
ad8686437884807bee848523c74dde30e17aa2c1e46d434f4d1537c5160b03f7  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/85b926a42aa3f39174c69ce152df1e207e1441a96595c59e485a3a9af42594bd/weights.json.sha256
8ccf5feb4ffee266a730d4d90a6059f95a5f47208047816fe2de7e6940b55b53  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/9eac92e5961de9fa27574afd62392f1c891e5fdd54173131338ff783ca692649/config.json
3d74f920d2c1abcaa4a7989ee81f6f3d6db71e89b904a3d53e1deb4d7aee2341  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/9eac92e5961de9fa27574afd62392f1c891e5fdd54173131338ff783ca692649/stamp.json
9eac92e5961de9fa27574afd62392f1c891e5fdd54173131338ff783ca692649  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/9eac92e5961de9fa27574afd62392f1c891e5fdd54173131338ff783ca692649/weights.json
c86976c83f242f6d4ac813561c20855e89d1050f3110595baa52af0b9e0f842a  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/9eac92e5961de9fa27574afd62392f1c891e5fdd54173131338ff783ca692649/weights.json.sha256
92c7a5a5d5d7d8561a9cc1c54cdc03b4ecb2513017bc25faad65844b6e9bf8e8  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/a25dc4cd7ee8ab588f9493aa4ed60916e440b0f2b4dd81135291b8c6acef6a26/config.json
de02326d6686d8e96c59fba340e546bfe7ef470932abe4ddfc36af2488b8b256  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/a25dc4cd7ee8ab588f9493aa4ed60916e440b0f2b4dd81135291b8c6acef6a26/stamp.json
a25dc4cd7ee8ab588f9493aa4ed60916e440b0f2b4dd81135291b8c6acef6a26  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/a25dc4cd7ee8ab588f9493aa4ed60916e440b0f2b4dd81135291b8c6acef6a26/weights.json
4f8be26137ae31adc1b73e30b22a9e9c3d2f712011a03d5b26094c79a9e7294c  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/a25dc4cd7ee8ab588f9493aa4ed60916e440b0f2b4dd81135291b8c6acef6a26/weights.json.sha256
c7711c21faa27bfebee67b1e3000342fa8a024499363cd2035f08c7b78ecf146  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/afac2713dafd72f120b0b9d9a10c642b14075a456d46637f91a5e4a0927e7276/config.json
3ecfeb22a7c4ddd33f210d75e6cfb350bdd4db8d82bdc64bec4a27a478b0ecb0  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/afac2713dafd72f120b0b9d9a10c642b14075a456d46637f91a5e4a0927e7276/stamp.json
afac2713dafd72f120b0b9d9a10c642b14075a456d46637f91a5e4a0927e7276  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/afac2713dafd72f120b0b9d9a10c642b14075a456d46637f91a5e4a0927e7276/weights.json
601f013f97c1ae90249ec469e9115f8d33296d5f95701a89f05f064de548eae9  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/afac2713dafd72f120b0b9d9a10c642b14075a456d46637f91a5e4a0927e7276/weights.json.sha256
4a39bedb042840f2deb23d9e096bfcc4b8932d2a07b8fd3f3085091c4d702bbb  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/b23771eb90f54d66286b1897a686b73003862f05a289f17b5a462f98698df350/config.json
5526740b44486e2c1fdb120afb8af40f6fb57f6e36151da5cff025c3e749a8c6  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/b23771eb90f54d66286b1897a686b73003862f05a289f17b5a462f98698df350/stamp.json
b23771eb90f54d66286b1897a686b73003862f05a289f17b5a462f98698df350  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/b23771eb90f54d66286b1897a686b73003862f05a289f17b5a462f98698df350/weights.json
08a6bc95b7cb679091891f8ea7e54c2832eb01f853f03e695958923c6d0e1317  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/b23771eb90f54d66286b1897a686b73003862f05a289f17b5a462f98698df350/weights.json.sha256
5f32b5b64ba1e2eb913ed8d108bc0356e33ccdffdc228d021374cc8bed263cfa  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/b4469dec6f95def6ba53b9ca37b81b4285b02501374047f290c6a579de0f84bb/config.json
82c64a529f67f68b8a0837e8526a09f36fd105b078549b7b69aa4f39cc6067fb  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/b4469dec6f95def6ba53b9ca37b81b4285b02501374047f290c6a579de0f84bb/stamp.json
b4469dec6f95def6ba53b9ca37b81b4285b02501374047f290c6a579de0f84bb  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/b4469dec6f95def6ba53b9ca37b81b4285b02501374047f290c6a579de0f84bb/weights.json
323909584111a3063f1298641408aac0d21f2f2a0e0880f9d28d9ad60161d6b6  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/b4469dec6f95def6ba53b9ca37b81b4285b02501374047f290c6a579de0f84bb/weights.json.sha256
d4b8ababaa54735e352b81f7b56cd3191fae3ceb3a82861702faef6e3ec4dffb  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/b974f0ec8940907f149c57723c2d8bb8f7b55152714fe79ea97e7a59418cab06/config.json
837424af4aa37a89f328eb180bf6b791be00ded061dd6fdc47c865a71c75ae6c  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/b974f0ec8940907f149c57723c2d8bb8f7b55152714fe79ea97e7a59418cab06/stamp.json
b974f0ec8940907f149c57723c2d8bb8f7b55152714fe79ea97e7a59418cab06  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/b974f0ec8940907f149c57723c2d8bb8f7b55152714fe79ea97e7a59418cab06/weights.json
f8b5f9ce25cf879cb35a2a9c3db6c4515ba7c1904dc83dea5eba8a1876c3abbd  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/b974f0ec8940907f149c57723c2d8bb8f7b55152714fe79ea97e7a59418cab06/weights.json.sha256
c90c082d5c00c9e7a52b6a219463d5d58b3c92eefd40af5a6d082ca837419e94  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/bb032e461d4c57f73d55fffc9ba5b2f8232fb64a7de38fee6c88c2ec58b22cd9/config.json
ee7d037f0df50c10e5ee2b65151c426afe51af985b572530f2baf2c710e5c1f8  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/bb032e461d4c57f73d55fffc9ba5b2f8232fb64a7de38fee6c88c2ec58b22cd9/stamp.json
bb032e461d4c57f73d55fffc9ba5b2f8232fb64a7de38fee6c88c2ec58b22cd9  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/bb032e461d4c57f73d55fffc9ba5b2f8232fb64a7de38fee6c88c2ec58b22cd9/weights.json
c6715a31bc20ea8ecd7919aa4c271d1885f22386a8dd1378796370c9ce057eda  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/bb032e461d4c57f73d55fffc9ba5b2f8232fb64a7de38fee6c88c2ec58b22cd9/weights.json.sha256
3b6ff346bdf84907cdd86569a835cc8bb5f688ec3ba05adb63b87353350e6adf  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/bb12b0e98e355f05c0e1d2f47ec2ca46299d5ed7146a507e3395bbfcd71b49b8/config.json
88a99ebc244f15f72605dcfe34eb815813e1beb2a3acf33cf08b70ac36191f7b  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/bb12b0e98e355f05c0e1d2f47ec2ca46299d5ed7146a507e3395bbfcd71b49b8/stamp.json
bb12b0e98e355f05c0e1d2f47ec2ca46299d5ed7146a507e3395bbfcd71b49b8  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/bb12b0e98e355f05c0e1d2f47ec2ca46299d5ed7146a507e3395bbfcd71b49b8/weights.json
0afa47b682ec2817c9b616ec947ed268d8fa29994faf8ed76a98db73ce86cd5d  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/bb12b0e98e355f05c0e1d2f47ec2ca46299d5ed7146a507e3395bbfcd71b49b8/weights.json.sha256
3aa0c39ec2710063f2d4c0c7fe7a332c3622527686aafe8ed13055296df759e1  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/c20bb4c46e259fcc79b70ae6e30a98020b0a0a05de4ff9ec6b116aed952177bc/config.json
b7af2ca5fc068b97873b2e2f68e5078f932d964f4cadc9e353064bf881fa538b  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/c20bb4c46e259fcc79b70ae6e30a98020b0a0a05de4ff9ec6b116aed952177bc/stamp.json
c20bb4c46e259fcc79b70ae6e30a98020b0a0a05de4ff9ec6b116aed952177bc  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/c20bb4c46e259fcc79b70ae6e30a98020b0a0a05de4ff9ec6b116aed952177bc/weights.json
a9a59a7a384c6ee6d90165a6d95bb00d4f95d006d87ae0b43993aa89f776cde5  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/c20bb4c46e259fcc79b70ae6e30a98020b0a0a05de4ff9ec6b116aed952177bc/weights.json.sha256
bc35af6d4397e698b5bd563f3a7c91051b891d3744d0a4d19a8f6a3d896d382c  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/d94d6cb9e57396dd32dbb6639c2cac55514dbffd785cff998e0ed3bdf1878676/config.json
7b1f9c82e2fc8d2e4164cbfb2a207cd974dcf902884f13b1e867c71d7552ba77  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/d94d6cb9e57396dd32dbb6639c2cac55514dbffd785cff998e0ed3bdf1878676/stamp.json
d94d6cb9e57396dd32dbb6639c2cac55514dbffd785cff998e0ed3bdf1878676  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/d94d6cb9e57396dd32dbb6639c2cac55514dbffd785cff998e0ed3bdf1878676/weights.json
0535020f7dc3b9bcf3289c2cd39c53259b3cfa4bea9418b994791ccfdb950704  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/d94d6cb9e57396dd32dbb6639c2cac55514dbffd785cff998e0ed3bdf1878676/weights.json.sha256
803339c55457d088985a1f52ef4c2c75e14da6c93997ec0ae2fbb35bfd5ff808  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/da97ca4c2e02b44d8ef3db17ecda100c82e209c8b98b34823b47093f9f8f06c3/config.json
7658f5868422d189f0028329aa5814cee0a26290fcd3fb389fa37d6ff2296aed  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/da97ca4c2e02b44d8ef3db17ecda100c82e209c8b98b34823b47093f9f8f06c3/stamp.json
da97ca4c2e02b44d8ef3db17ecda100c82e209c8b98b34823b47093f9f8f06c3  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/da97ca4c2e02b44d8ef3db17ecda100c82e209c8b98b34823b47093f9f8f06c3/weights.json
3f489d8adc85e8736bf0365403659ab9430a1c4fcddac03b81811916ca61cdce  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/da97ca4c2e02b44d8ef3db17ecda100c82e209c8b98b34823b47093f9f8f06c3/weights.json.sha256
5b0cf1f0a8c13de408b0f6e71529e25806a05baf3313f28d92fa989175c46bd8  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/e05a99363da1d881308b2d206d4d0bd75aa4078b1adf3f6377562048cead24ed/config.json
274a51f2a7a930c254c9cd7b9c13a7cfc19357e7688da457767b40f3b1c35714  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/e05a99363da1d881308b2d206d4d0bd75aa4078b1adf3f6377562048cead24ed/stamp.json
e05a99363da1d881308b2d206d4d0bd75aa4078b1adf3f6377562048cead24ed  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/e05a99363da1d881308b2d206d4d0bd75aa4078b1adf3f6377562048cead24ed/weights.json
85c8595839b96956b8d69cf90da75f132853216f11309c37af7d5145bef3e897  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/e05a99363da1d881308b2d206d4d0bd75aa4078b1adf3f6377562048cead24ed/weights.json.sha256
761c61142d48a0ad2e36e883fa8458b046a47df4ae0487484bb9bf262c6d48c8  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/e454385fcc664423928e18fe463a4e7c77d2e3dd9f1355def02fbc4e2585efed/config.json
0991ee411ebdb3a479096038092dc26f0536fa41ffc355f0e4c9e55e9cec05ac  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/e454385fcc664423928e18fe463a4e7c77d2e3dd9f1355def02fbc4e2585efed/stamp.json
e454385fcc664423928e18fe463a4e7c77d2e3dd9f1355def02fbc4e2585efed  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/e454385fcc664423928e18fe463a4e7c77d2e3dd9f1355def02fbc4e2585efed/weights.json
1a61ae9dff40b0e31616aef2c472f7b1d3c01e010a2dd6a7c6c5720c1666b04d  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/e454385fcc664423928e18fe463a4e7c77d2e3dd9f1355def02fbc4e2585efed/weights.json.sha256
268ce1a59ee05fb4b04bebc6759905c1ddcf08881ebca86e8ee4eeb856f059ca  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/e6285a503213a0cd40bba6ea19faf1c28b2a2c6fe9517e72b4a430da7c239eaf/config.json
47715da119e9d86d7ea864507031302056062fe75ac9bc24a4f5855f4b56093a  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/e6285a503213a0cd40bba6ea19faf1c28b2a2c6fe9517e72b4a430da7c239eaf/stamp.json
e6285a503213a0cd40bba6ea19faf1c28b2a2c6fe9517e72b4a430da7c239eaf  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/e6285a503213a0cd40bba6ea19faf1c28b2a2c6fe9517e72b4a430da7c239eaf/weights.json
29faae4bc2ea78e9b20b032709e03c44c6a1eb4b1ce0e2aa9ef79a209072280a  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/e6285a503213a0cd40bba6ea19faf1c28b2a2c6fe9517e72b4a430da7c239eaf/weights.json.sha256
83aa7a76c50db275d35dac2fd7638eee31d2d3b582cc01f496a50c9c02f87058  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/e8f49993e79de0a896cacaad02f63c7bb561088503f6ec2b6033568b7ff789b1/config.json
e15382a375ce1ecbaef5c0b70775437f6a730a4db35375ff6897abcb8a8b7e4c  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/e8f49993e79de0a896cacaad02f63c7bb561088503f6ec2b6033568b7ff789b1/stamp.json
e8f49993e79de0a896cacaad02f63c7bb561088503f6ec2b6033568b7ff789b1  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/e8f49993e79de0a896cacaad02f63c7bb561088503f6ec2b6033568b7ff789b1/weights.json
d4613074afa3dd0eebea5cd3bc4082e122b091303a8aac5dfb6cbc2c573f49cc  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/e8f49993e79de0a896cacaad02f63c7bb561088503f6ec2b6033568b7ff789b1/weights.json.sha256
f6664bed136bd934f0153b9a4d5cac8e6912acd0ce6e726a826a0ea367a995b9  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/e956c9ec6ab6dd4307ffe36c80df01f23c46b1d44d1e4d6ba40046c4110b7b83/config.json
68c7e40f470a0e27997a45194bc0073546e269487441b2664bfbb30f13c8f2bc  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/e956c9ec6ab6dd4307ffe36c80df01f23c46b1d44d1e4d6ba40046c4110b7b83/stamp.json
e956c9ec6ab6dd4307ffe36c80df01f23c46b1d44d1e4d6ba40046c4110b7b83  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/e956c9ec6ab6dd4307ffe36c80df01f23c46b1d44d1e4d6ba40046c4110b7b83/weights.json
45ad72a28172f0b03da8c6a54814d8628be9fcd8d0509fe4a9cb7445abe4aec5  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/e956c9ec6ab6dd4307ffe36c80df01f23c46b1d44d1e4d6ba40046c4110b7b83/weights.json.sha256
5c8a7aaceba733d37775ff3597c3d5a4dca6edff4f5ff92ef576be86bb1a5efc  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/f0c14ec9e60cf19108f41829620d07746a81729b5ca1329863d033cf8a06ebff/config.json
976849ee5bde84b4f1048b3b10f8fce11c468d8381a8a74bcdf3b0a24167b836  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/f0c14ec9e60cf19108f41829620d07746a81729b5ca1329863d033cf8a06ebff/stamp.json
f0c14ec9e60cf19108f41829620d07746a81729b5ca1329863d033cf8a06ebff  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/f0c14ec9e60cf19108f41829620d07746a81729b5ca1329863d033cf8a06ebff/weights.json
c60c1239f66282701cf5d76e0619d75cb7031bc6680a44831e75a7fad06565b1  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/f0c14ec9e60cf19108f41829620d07746a81729b5ca1329863d033cf8a06ebff/weights.json.sha256
8154202b6a583c7c7502c6f8732adc021179ab8170f2f1340261f5d7fc0158c0  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/f1dee083f5e19c1979c4e7abbede176ffa915ff53af41eaea8d5291b67eaeda7/config.json
be7b6d39b1b0d64bc5a50f7323cc0d9202fb2455ef01e9e69f67da5ba8369547  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/f1dee083f5e19c1979c4e7abbede176ffa915ff53af41eaea8d5291b67eaeda7/stamp.json
f1dee083f5e19c1979c4e7abbede176ffa915ff53af41eaea8d5291b67eaeda7  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/f1dee083f5e19c1979c4e7abbede176ffa915ff53af41eaea8d5291b67eaeda7/weights.json
d1bde93045e26906b42b6626c0149cf2e0d528cc369e345620a680d62ce2ac6e  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/f1dee083f5e19c1979c4e7abbede176ffa915ff53af41eaea8d5291b67eaeda7/weights.json.sha256
ff304e1f15c14db2817d8776b2aba3ed50ba5d016da16d8fe61a69d5c7e2c2fc  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/f4ed45d3810e30aa8fad0e2ddbff35be9a17408fd2d2cefbc02309aaabb31f5b/config.json
40b7e9443513769b76d45b2ff06cab5319bdac23f3a35ba905103ad319d40c12  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/f4ed45d3810e30aa8fad0e2ddbff35be9a17408fd2d2cefbc02309aaabb31f5b/stamp.json
f4ed45d3810e30aa8fad0e2ddbff35be9a17408fd2d2cefbc02309aaabb31f5b  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/f4ed45d3810e30aa8fad0e2ddbff35be9a17408fd2d2cefbc02309aaabb31f5b/weights.json
4f1593ac0963c52413bcc74c77c491d9a5010aa074cd2339e89632d41691bf0d  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/f4ed45d3810e30aa8fad0e2ddbff35be9a17408fd2d2cefbc02309aaabb31f5b/weights.json.sha256
b0b20b04bc253b93cbbf300483d0d466f697c9019d324788f15ef4cc29313778  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/f597ba18d14b4c6a7aab793e8758e356368f1ce751a57d43c8d469531afa04ad/config.json
db04652165ce18a8fffebcd44954b962d48a54b02ca0a45a0a501c7ab0150376  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/f597ba18d14b4c6a7aab793e8758e356368f1ce751a57d43c8d469531afa04ad/stamp.json
f597ba18d14b4c6a7aab793e8758e356368f1ce751a57d43c8d469531afa04ad  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/f597ba18d14b4c6a7aab793e8758e356368f1ce751a57d43c8d469531afa04ad/weights.json
52cf8a4237b9086444d180f731bc683ebc8cbf8479ba3a96e22651dc649b0d81  coevo/run-05-freepolicy-v2-founders/impostor/gen-0/f597ba18d14b4c6a7aab793e8758e356368f1ce751a57d43c8d469531afa04ad/weights.json.sha256
43c63935d8b14c562e2e96c5175dccef6b97414af8ff029bdae84d45c6f64317  coevo/run-05-freepolicy-v2-founders/impostor/gen-2/43b113ec7ebd911b1720401884ca7e0e0cf452e611f01904ae41cb6e3c3d68d9/config.json
dc9fc9966bb44d2d6575ae1bdf4eb50149b3c49eb3935d82b877004c7e3d912d  coevo/run-05-freepolicy-v2-founders/impostor/gen-2/43b113ec7ebd911b1720401884ca7e0e0cf452e611f01904ae41cb6e3c3d68d9/stamp.json
43b113ec7ebd911b1720401884ca7e0e0cf452e611f01904ae41cb6e3c3d68d9  coevo/run-05-freepolicy-v2-founders/impostor/gen-2/43b113ec7ebd911b1720401884ca7e0e0cf452e611f01904ae41cb6e3c3d68d9/weights.json
57721d962fbdbe7134f238647b442c512fbe46a017a5dd2c154aa7d6d06c0ed1  coevo/run-05-freepolicy-v2-founders/impostor/gen-2/43b113ec7ebd911b1720401884ca7e0e0cf452e611f01904ae41cb6e3c3d68d9/weights.json.sha256
7c3f94ad542b4c52ef646256f91236b6f2df600f27ac938433c7feaf22a61ea4  coevo/run-05-freepolicy-v2-founders/impostor/gen-3/119e5374b4afb9c64f0463483b0cbc9457fc589737abafb24838798703692f2c/config.json
904a60cb52e82fbb257a23beba1aa1a8c6e90cf2b439698d37b755143577e57d  coevo/run-05-freepolicy-v2-founders/impostor/gen-3/119e5374b4afb9c64f0463483b0cbc9457fc589737abafb24838798703692f2c/stamp.json
119e5374b4afb9c64f0463483b0cbc9457fc589737abafb24838798703692f2c  coevo/run-05-freepolicy-v2-founders/impostor/gen-3/119e5374b4afb9c64f0463483b0cbc9457fc589737abafb24838798703692f2c/weights.json
6dd42d85bcb0a030c050df859802f953c093fc87df1b04029003638ac7c4c50a  coevo/run-05-freepolicy-v2-founders/impostor/gen-3/119e5374b4afb9c64f0463483b0cbc9457fc589737abafb24838798703692f2c/weights.json.sha256
b59de4097b4fa3cd9a7cc336588a3224b809296693590e709a891f70b791acfb  coevo/run-05-freepolicy-v2-founders/impostor/gen-4/9b60588c80d826417e312b7a88b08be77840101968fded02b1e4b8a7d24e94da/config.json
e4134b6c5c0e46d65a89631c263c5bcdae106a5327c8ac089996f33723f22a38  coevo/run-05-freepolicy-v2-founders/impostor/gen-4/9b60588c80d826417e312b7a88b08be77840101968fded02b1e4b8a7d24e94da/stamp.json
9b60588c80d826417e312b7a88b08be77840101968fded02b1e4b8a7d24e94da  coevo/run-05-freepolicy-v2-founders/impostor/gen-4/9b60588c80d826417e312b7a88b08be77840101968fded02b1e4b8a7d24e94da/weights.json
1953d3106337f7fb02153e2706772704280d69ae5ba5dab5d5e71a7a0353f1a0  coevo/run-05-freepolicy-v2-founders/impostor/gen-4/9b60588c80d826417e312b7a88b08be77840101968fded02b1e4b8a7d24e94da/weights.json.sha256
dc7c93ba05a2bb63e19ce60f3c611238623a519a258fc6f1b56ec7ff728ad60c  coevo/run-05-freepolicy-v2-founders/impostor/hall_of_fame.json
88f74ea14dec6e91321556884be5934723f0c1e646f6e2f0ba75e6e656f36f37  coevo/run-c1-crew-owned-tasks/crew/gen-10/02f900e8479addc6ec8749e81b35fd54d07d40c5d1b6f08863f515718c1f693f/config.json
35b4931ed4363c892ee3c5df5792e93d089355b0c131c19418afa85b23d6de7f  coevo/run-c1-crew-owned-tasks/crew/gen-10/02f900e8479addc6ec8749e81b35fd54d07d40c5d1b6f08863f515718c1f693f/stamp.json
02f900e8479addc6ec8749e81b35fd54d07d40c5d1b6f08863f515718c1f693f  coevo/run-c1-crew-owned-tasks/crew/gen-10/02f900e8479addc6ec8749e81b35fd54d07d40c5d1b6f08863f515718c1f693f/weights.json
abd1ebff38611eca88601a413f416f83e7bc9b0eda4c99a9bacb55c23cebc365  coevo/run-c1-crew-owned-tasks/crew/gen-10/02f900e8479addc6ec8749e81b35fd54d07d40c5d1b6f08863f515718c1f693f/weights.json.sha256
47fa671fe5600013bbfaf2bfe38d2bd396aa4cfc429695bb3bf229d0ee975b75  coevo/run-c1-crew-owned-tasks/crew/gen-11/2cf6c29c3c4132006382b70ba069dc0d6509346d19341aa4487a3ca661f37809/config.json
6676661ff85643c9d374fb60dc2597a532d8c32562cbf4b255c5ec6f60ac2575  coevo/run-c1-crew-owned-tasks/crew/gen-11/2cf6c29c3c4132006382b70ba069dc0d6509346d19341aa4487a3ca661f37809/stamp.json
2cf6c29c3c4132006382b70ba069dc0d6509346d19341aa4487a3ca661f37809  coevo/run-c1-crew-owned-tasks/crew/gen-11/2cf6c29c3c4132006382b70ba069dc0d6509346d19341aa4487a3ca661f37809/weights.json
7bfd159cd032d78d900ce21b63beb7cd9cc46d8ff9b0b5bfab6c4bda4769f8b4  coevo/run-c1-crew-owned-tasks/crew/gen-11/2cf6c29c3c4132006382b70ba069dc0d6509346d19341aa4487a3ca661f37809/weights.json.sha256
6b007bff349ca20656259b4598e214eb4699de260406f53ff5256c7cf46e024e  coevo/run-c1-crew-owned-tasks/crew/gen-12/83d1c22c44fd1d58012b34d8f1f48ac33ea98039522141bf47dcdee87e092ae6/config.json
e3d6e02b449e57d26c7eb6218002c8f9cc099badacd83f637e024f67c6c4db75  coevo/run-c1-crew-owned-tasks/crew/gen-12/83d1c22c44fd1d58012b34d8f1f48ac33ea98039522141bf47dcdee87e092ae6/stamp.json
83d1c22c44fd1d58012b34d8f1f48ac33ea98039522141bf47dcdee87e092ae6  coevo/run-c1-crew-owned-tasks/crew/gen-12/83d1c22c44fd1d58012b34d8f1f48ac33ea98039522141bf47dcdee87e092ae6/weights.json
9c6bf5436754cd32a717f298a8ae09f785c71ecde41cbe02fe323428eca8168c  coevo/run-c1-crew-owned-tasks/crew/gen-12/83d1c22c44fd1d58012b34d8f1f48ac33ea98039522141bf47dcdee87e092ae6/weights.json.sha256
ba73de7b7886fdedf3a5ac3fa20eedf956aca1b533c5a183c1df597ed5ba5494  coevo/run-c1-crew-owned-tasks/crew/gen-3/72adb41c9286d61d5a81ea4ed2bd347c0d7da52ad89ae6497f1dcbf2237ca4e5/config.json
f09ec32f06454937c5a6c152dcc522fc87eca582b185dea55520b57f12dad38f  coevo/run-c1-crew-owned-tasks/crew/gen-3/72adb41c9286d61d5a81ea4ed2bd347c0d7da52ad89ae6497f1dcbf2237ca4e5/stamp.json
72adb41c9286d61d5a81ea4ed2bd347c0d7da52ad89ae6497f1dcbf2237ca4e5  coevo/run-c1-crew-owned-tasks/crew/gen-3/72adb41c9286d61d5a81ea4ed2bd347c0d7da52ad89ae6497f1dcbf2237ca4e5/weights.json
e937d76813ced95a20e0e81fecdd650ebf774972eca5269d1e84cdbbbe385715  coevo/run-c1-crew-owned-tasks/crew/gen-3/72adb41c9286d61d5a81ea4ed2bd347c0d7da52ad89ae6497f1dcbf2237ca4e5/weights.json.sha256
4271f6992f0409863a36f541b0d3d5ded3d6290ae0d6d0e5f7dc28bc79f1f7c4  coevo/run-c1-crew-owned-tasks/crew/gen-4/26636fab45e3025d54f8948db12f0a08fea9dec73e21876e4031540845cb3bbc/config.json
e1dc67590a8f82bd063baf2ff9dc350c72a83f6e99b009dfbd952f3b264843fd  coevo/run-c1-crew-owned-tasks/crew/gen-4/26636fab45e3025d54f8948db12f0a08fea9dec73e21876e4031540845cb3bbc/stamp.json
26636fab45e3025d54f8948db12f0a08fea9dec73e21876e4031540845cb3bbc  coevo/run-c1-crew-owned-tasks/crew/gen-4/26636fab45e3025d54f8948db12f0a08fea9dec73e21876e4031540845cb3bbc/weights.json
be613d1d026ae2b268144e580653ee93503da9983e028765f2c571afb1ea6adf  coevo/run-c1-crew-owned-tasks/crew/gen-4/26636fab45e3025d54f8948db12f0a08fea9dec73e21876e4031540845cb3bbc/weights.json.sha256
649ba2f7edf9b5fc81945433975f00e321b49fb120cdc3138ff84b7d205e83eb  coevo/run-c1-crew-owned-tasks/crew/hall_of_fame.json
7648b8a9a2cb655febb64e365b823aa85f9d894cdc05afb6918b806cceb6b2fc  coevo/run-c1-crew-owned-tasks/impostor/gen-1/d8afecd74e2a8aa048c561e569409d5e6a9c0c0d77eb97fca4997b198f85a92f/config.json
c2a491a72ac2394d435757eb225cee406b4a365b8a160ef683667c833c395027  coevo/run-c1-crew-owned-tasks/impostor/gen-1/d8afecd74e2a8aa048c561e569409d5e6a9c0c0d77eb97fca4997b198f85a92f/stamp.json
d8afecd74e2a8aa048c561e569409d5e6a9c0c0d77eb97fca4997b198f85a92f  coevo/run-c1-crew-owned-tasks/impostor/gen-1/d8afecd74e2a8aa048c561e569409d5e6a9c0c0d77eb97fca4997b198f85a92f/weights.json
c0f944ca29706dd7803df1423521317c4e4fb9bbfa19c444fae5e6280dedaf8a  coevo/run-c1-crew-owned-tasks/impostor/gen-1/d8afecd74e2a8aa048c561e569409d5e6a9c0c0d77eb97fca4997b198f85a92f/weights.json.sha256
e71f669892abe41695915bbca7a2170f9b5b68ad85b9f66942459e0cf31123c9  coevo/run-c1-crew-owned-tasks/impostor/gen-2/00716018dd5e9b90357183e47b3647722a75041218a9002fac80c8c2b6c0b6fd/config.json
558afc4733e385f93734d500e34d2850e2e373cd0cdca8fe4c7d1827ab8797b9  coevo/run-c1-crew-owned-tasks/impostor/gen-2/00716018dd5e9b90357183e47b3647722a75041218a9002fac80c8c2b6c0b6fd/stamp.json
00716018dd5e9b90357183e47b3647722a75041218a9002fac80c8c2b6c0b6fd  coevo/run-c1-crew-owned-tasks/impostor/gen-2/00716018dd5e9b90357183e47b3647722a75041218a9002fac80c8c2b6c0b6fd/weights.json
636b769dffb2111abc734c0a187d26250c51dd38336b476ead2141ad6969c665  coevo/run-c1-crew-owned-tasks/impostor/gen-2/00716018dd5e9b90357183e47b3647722a75041218a9002fac80c8c2b6c0b6fd/weights.json.sha256
eefcf7395d1ab44f2e3037df47061f1b84d5e7e5b179c0013496a9a762d3fe54  coevo/run-c1-crew-owned-tasks/impostor/gen-3/5faa43e93122eb95060eaf2153486e7775adc1a2569e18c7e4236268b3f67056/config.json
06e540fe00a123da96fca51f1a201da45362e59588e9b2ca9c7b294cb209bf8a  coevo/run-c1-crew-owned-tasks/impostor/gen-3/5faa43e93122eb95060eaf2153486e7775adc1a2569e18c7e4236268b3f67056/stamp.json
5faa43e93122eb95060eaf2153486e7775adc1a2569e18c7e4236268b3f67056  coevo/run-c1-crew-owned-tasks/impostor/gen-3/5faa43e93122eb95060eaf2153486e7775adc1a2569e18c7e4236268b3f67056/weights.json
222d70fcc3dfa1051a0150473425fc8cc646faa50aad8ddb04e2c94ab56f634d  coevo/run-c1-crew-owned-tasks/impostor/gen-3/5faa43e93122eb95060eaf2153486e7775adc1a2569e18c7e4236268b3f67056/weights.json.sha256
4587bda78e49dafbc23b343803e2e44aa969b97a4a5eae5510f251e281965276  coevo/run-c1-crew-owned-tasks/impostor/gen-6/0ca3a382a0e3566dfb225d99cd72abd48e988709dba0cbae9fa5f96d68fa4f52/config.json
138fac2dfb1d2ece67274fa71977c9397baa1d8439b483d2accfa81607b8c421  coevo/run-c1-crew-owned-tasks/impostor/gen-6/0ca3a382a0e3566dfb225d99cd72abd48e988709dba0cbae9fa5f96d68fa4f52/stamp.json
0ca3a382a0e3566dfb225d99cd72abd48e988709dba0cbae9fa5f96d68fa4f52  coevo/run-c1-crew-owned-tasks/impostor/gen-6/0ca3a382a0e3566dfb225d99cd72abd48e988709dba0cbae9fa5f96d68fa4f52/weights.json
8f344cdb6358193869a691db34d68cf40c5689af1fa4b2cc352c34f36d95d128  coevo/run-c1-crew-owned-tasks/impostor/gen-6/0ca3a382a0e3566dfb225d99cd72abd48e988709dba0cbae9fa5f96d68fa4f52/weights.json.sha256
82e2833dbaaf9197115d5039c6d7af3390692c4348690e992a2b475b6ac0c0d2  coevo/run-c1-crew-owned-tasks/impostor/gen-7/005850f0531519f6e2fe78a0b85ca229392c54a4e62f96ab71c059dca49b9397/config.json
e107c89b4ded2877f86c1f3ffb674177ac67db25ccc8f378e9d6baae5fb96060  coevo/run-c1-crew-owned-tasks/impostor/gen-7/005850f0531519f6e2fe78a0b85ca229392c54a4e62f96ab71c059dca49b9397/stamp.json
005850f0531519f6e2fe78a0b85ca229392c54a4e62f96ab71c059dca49b9397  coevo/run-c1-crew-owned-tasks/impostor/gen-7/005850f0531519f6e2fe78a0b85ca229392c54a4e62f96ab71c059dca49b9397/weights.json
d5a7fff6eb44b25223db43eb33200653010031102d5ce807d5ff6e9bbaeb27aa  coevo/run-c1-crew-owned-tasks/impostor/gen-7/005850f0531519f6e2fe78a0b85ca229392c54a4e62f96ab71c059dca49b9397/weights.json.sha256
eddd9d481f79fd4060afe64cc51c3fcd6bbe58d212d922561c0de539b9079ae8  coevo/run-c1-crew-owned-tasks/impostor/gen-8/cf544e5c6b2715505fad370fc60d2251d9e9f3cf7f412dafe1da305063217be1/config.json
6aef009cb415cdfd6bbbc1596c912abe687d6238b1b087dc8f659cfab75c0a8d  coevo/run-c1-crew-owned-tasks/impostor/gen-8/cf544e5c6b2715505fad370fc60d2251d9e9f3cf7f412dafe1da305063217be1/stamp.json
cf544e5c6b2715505fad370fc60d2251d9e9f3cf7f412dafe1da305063217be1  coevo/run-c1-crew-owned-tasks/impostor/gen-8/cf544e5c6b2715505fad370fc60d2251d9e9f3cf7f412dafe1da305063217be1/weights.json
2e11ae4645b52603013309734adde29bd8c9b3b2cadaace646f97e1f55076363  coevo/run-c1-crew-owned-tasks/impostor/gen-8/cf544e5c6b2715505fad370fc60d2251d9e9f3cf7f412dafe1da305063217be1/weights.json.sha256
b2932286e41e6c7fb7bab87e9e8f0660d1226942c2d5b6cd7eebbbff2975b1f9  coevo/run-c1-crew-owned-tasks/impostor/gen-9/098a017395d6d0a9a36393db98dcc8f6726a7fe00b36f1b809a018f2590c781a/config.json
1f31bc46dc83da82d217e7535fe44e5a256effb780e76b4f0544058e49699011  coevo/run-c1-crew-owned-tasks/impostor/gen-9/098a017395d6d0a9a36393db98dcc8f6726a7fe00b36f1b809a018f2590c781a/stamp.json
098a017395d6d0a9a36393db98dcc8f6726a7fe00b36f1b809a018f2590c781a  coevo/run-c1-crew-owned-tasks/impostor/gen-9/098a017395d6d0a9a36393db98dcc8f6726a7fe00b36f1b809a018f2590c781a/weights.json
c86a7cce5e82f0a8c99bf48c2347b5723c804c887916b041f4310810a8acd21f  coevo/run-c1-crew-owned-tasks/impostor/gen-9/098a017395d6d0a9a36393db98dcc8f6726a7fe00b36f1b809a018f2590c781a/weights.json.sha256
13c6e5d8baa256ff8854fc3cfe803a85511ec07628667b6305df571b1c9015c2  coevo/run-c1-crew-owned-tasks/impostor/hall_of_fame.json
08e1ed86877c4a5ffc0d1321d0898ba4561a39de226313631ff994c077d0ff4d  coevo/run-c2-crew-general/crew/gen-10/1916d3ad3e432dfcc5ec43c1c506d4a0659ae1b18fe5785f2bacf2810c0b9d7b/config.json
4a460a83ae9875ebf2bca8534b6ca05ff4ba980a286dd70f7ff82b2fd6a2bb67  coevo/run-c2-crew-general/crew/gen-10/1916d3ad3e432dfcc5ec43c1c506d4a0659ae1b18fe5785f2bacf2810c0b9d7b/stamp.json
1916d3ad3e432dfcc5ec43c1c506d4a0659ae1b18fe5785f2bacf2810c0b9d7b  coevo/run-c2-crew-general/crew/gen-10/1916d3ad3e432dfcc5ec43c1c506d4a0659ae1b18fe5785f2bacf2810c0b9d7b/weights.json
44eb8e9b5d1b7cb504c70c73595a31705aef8de286e29f23c1f51b094c505ed9  coevo/run-c2-crew-general/crew/gen-10/1916d3ad3e432dfcc5ec43c1c506d4a0659ae1b18fe5785f2bacf2810c0b9d7b/weights.json.sha256
995570e005d8447aeb451cbf5f27643e0481027fb233a407a9f7975d3e0d1c51  coevo/run-c2-crew-general/crew/gen-11/0641baba7257ac8b03fd0c32405347899bfe32470c3830a3f80500f55b1ba5bb/config.json
694897e401f82c99dd2de1126f9f6575b337af0fe055333b3b1be1c4d1f315de  coevo/run-c2-crew-general/crew/gen-11/0641baba7257ac8b03fd0c32405347899bfe32470c3830a3f80500f55b1ba5bb/stamp.json
0641baba7257ac8b03fd0c32405347899bfe32470c3830a3f80500f55b1ba5bb  coevo/run-c2-crew-general/crew/gen-11/0641baba7257ac8b03fd0c32405347899bfe32470c3830a3f80500f55b1ba5bb/weights.json
f9a4987de07fdd944ec554e8d20b73f250b51f5f013cafa8a05f93c03c9814d3  coevo/run-c2-crew-general/crew/gen-11/0641baba7257ac8b03fd0c32405347899bfe32470c3830a3f80500f55b1ba5bb/weights.json.sha256
225c95594568272f34f1cfddfbcb469065fa4de5d435379a11d0e3f20ed3a4fc  coevo/run-c2-crew-general/crew/gen-12/d761c08ce0c8ff6d24a72ec0eddcf980f40a697384e401aeb4b03ff9c6de8955/config.json
6062ea334f05396c41e1ec9b5e6ad30070f70d3435b0f10d32f5c6dd0bc492c6  coevo/run-c2-crew-general/crew/gen-12/d761c08ce0c8ff6d24a72ec0eddcf980f40a697384e401aeb4b03ff9c6de8955/stamp.json
d761c08ce0c8ff6d24a72ec0eddcf980f40a697384e401aeb4b03ff9c6de8955  coevo/run-c2-crew-general/crew/gen-12/d761c08ce0c8ff6d24a72ec0eddcf980f40a697384e401aeb4b03ff9c6de8955/weights.json
3de02174b18f4bce331474099e4d0242b309feb894e6602bb0010dce706f5549  coevo/run-c2-crew-general/crew/gen-12/d761c08ce0c8ff6d24a72ec0eddcf980f40a697384e401aeb4b03ff9c6de8955/weights.json.sha256
3206053eff75dd20fd43b0c3715a27c52f0175cbd8f857aed406c06004283d89  coevo/run-c2-crew-general/crew/gen-3/7fa59718d8810a3c26214309eaf6b637a1afc66dc3ea923ab887152f4e985acd/config.json
eb634492cb9aecac2e7c7669e8764fd7c92a53223bc89fd6be2b2735e8c9981c  coevo/run-c2-crew-general/crew/gen-3/7fa59718d8810a3c26214309eaf6b637a1afc66dc3ea923ab887152f4e985acd/stamp.json
7fa59718d8810a3c26214309eaf6b637a1afc66dc3ea923ab887152f4e985acd  coevo/run-c2-crew-general/crew/gen-3/7fa59718d8810a3c26214309eaf6b637a1afc66dc3ea923ab887152f4e985acd/weights.json
24cfc15c56aa50abfab0f8edf021e5dcab03a3cf5bf514bd91cdc6a894bbe507  coevo/run-c2-crew-general/crew/gen-3/7fa59718d8810a3c26214309eaf6b637a1afc66dc3ea923ab887152f4e985acd/weights.json.sha256
e10c1b7dba952f7575062baf9b9c2a87fe06b3c1249184d55909522df59849f7  coevo/run-c2-crew-general/crew/gen-4/c7347d92c3e9e59a4766a2237f10afbb875803108f77c17f3ea78cd939bfab7d/config.json
a967a63cdb752f1eb1d83c7018431796b24d4a3e1a590501b216a1be48b3bed4  coevo/run-c2-crew-general/crew/gen-4/c7347d92c3e9e59a4766a2237f10afbb875803108f77c17f3ea78cd939bfab7d/stamp.json
c7347d92c3e9e59a4766a2237f10afbb875803108f77c17f3ea78cd939bfab7d  coevo/run-c2-crew-general/crew/gen-4/c7347d92c3e9e59a4766a2237f10afbb875803108f77c17f3ea78cd939bfab7d/weights.json
addbde96c462d762c62f80099908b769118ef53642a5b89cfc302ff89b94aee5  coevo/run-c2-crew-general/crew/gen-4/c7347d92c3e9e59a4766a2237f10afbb875803108f77c17f3ea78cd939bfab7d/weights.json.sha256
215695d984e3b60ac5ac5afd061aa37c60a99307b9dd9e08e9a67b7c161ccd10  coevo/run-c2-crew-general/crew/gen-5/933d8e1ab855f7b6e567882fb4c1b4a91e48347e02089be7776c146ffae49d24/config.json
172aae8385a0daf436d2d048b2f3a0eec23992e388ab7c5ed3c942b611c34b40  coevo/run-c2-crew-general/crew/gen-5/933d8e1ab855f7b6e567882fb4c1b4a91e48347e02089be7776c146ffae49d24/stamp.json
933d8e1ab855f7b6e567882fb4c1b4a91e48347e02089be7776c146ffae49d24  coevo/run-c2-crew-general/crew/gen-5/933d8e1ab855f7b6e567882fb4c1b4a91e48347e02089be7776c146ffae49d24/weights.json
7be19a05b492beb64e3cba797b31b8049cf3104e9464d72ded59e0e936cc7ccf  coevo/run-c2-crew-general/crew/gen-5/933d8e1ab855f7b6e567882fb4c1b4a91e48347e02089be7776c146ffae49d24/weights.json.sha256
b73e72c63aa0dbddbccb7f22927dd0db151d7c468718dd05e73950484a0209bf  coevo/run-c2-crew-general/crew/hall_of_fame.json
ebc9627102b6c31ee7e0a9398cec89d2ca29410641a859944b50b4216bd3d2ad  coevo/run-c2-crew-general/impostor/gen-1/c5671ccab33bb27393e37ae3879b062e6199011688140f9329007e66afe07b8f/config.json
5c227f515599bda46856c1d040a1163ee5f8bbb3e92413b64b7f59d254fb56b8  coevo/run-c2-crew-general/impostor/gen-1/c5671ccab33bb27393e37ae3879b062e6199011688140f9329007e66afe07b8f/stamp.json
c5671ccab33bb27393e37ae3879b062e6199011688140f9329007e66afe07b8f  coevo/run-c2-crew-general/impostor/gen-1/c5671ccab33bb27393e37ae3879b062e6199011688140f9329007e66afe07b8f/weights.json
c1f8e821cadeb7605021edcf00ee30cf55d1ddefa943298eb0de26a2ecb75a13  coevo/run-c2-crew-general/impostor/gen-1/c5671ccab33bb27393e37ae3879b062e6199011688140f9329007e66afe07b8f/weights.json.sha256
d9722c9428002162ad4a91ca33ae0a0a85c57d7dae2793cba2c3387fcfd320f6  coevo/run-c2-crew-general/impostor/gen-12/105f7a88d719bddbe094ebe05a9cac6ce096391562f38cb379ec73d87af4815a/config.json
3da735d10099c8d49bc4642fe367a74861fa4589f05f60370f6657e816c24215  coevo/run-c2-crew-general/impostor/gen-12/105f7a88d719bddbe094ebe05a9cac6ce096391562f38cb379ec73d87af4815a/stamp.json
105f7a88d719bddbe094ebe05a9cac6ce096391562f38cb379ec73d87af4815a  coevo/run-c2-crew-general/impostor/gen-12/105f7a88d719bddbe094ebe05a9cac6ce096391562f38cb379ec73d87af4815a/weights.json
932d111509646f2e7dcf3f35a3a4bcd862f50e3d56e1626da76278e65b4c1481  coevo/run-c2-crew-general/impostor/gen-12/105f7a88d719bddbe094ebe05a9cac6ce096391562f38cb379ec73d87af4815a/weights.json.sha256
3ddfb5eb90b44ee00782e366c2117771df6169bb55540b394c009edea7eda4d4  coevo/run-c2-crew-general/impostor/gen-2/d5ad5bb40e7d1c6343b88a7bccc4678d258e3678cea48d5cdbf47db4276b635b/config.json
064219d9640d0f6e0554edcb890191b123ec890c79a0fb6dcf862ac12f8ae7a3  coevo/run-c2-crew-general/impostor/gen-2/d5ad5bb40e7d1c6343b88a7bccc4678d258e3678cea48d5cdbf47db4276b635b/stamp.json
d5ad5bb40e7d1c6343b88a7bccc4678d258e3678cea48d5cdbf47db4276b635b  coevo/run-c2-crew-general/impostor/gen-2/d5ad5bb40e7d1c6343b88a7bccc4678d258e3678cea48d5cdbf47db4276b635b/weights.json
71e8b703db9ea032e6972163279d03fa559c2b80576f29be3ea0e1c2e13a7f8f  coevo/run-c2-crew-general/impostor/gen-2/d5ad5bb40e7d1c6343b88a7bccc4678d258e3678cea48d5cdbf47db4276b635b/weights.json.sha256
975e1ef9dd82842515363f9087cc3e725ffb56ec72e65a640f793d3e541cc028  coevo/run-c2-crew-general/impostor/gen-3/7e5fe988f2cdc91328ead651ba1da9d75e81c6b0169c58b18db6dbe35c6fba7f/config.json
befcfa91a02b5b1f04d65aa06e8ce4d1d5f2a1aec59b43c9a30fcb806203aed2  coevo/run-c2-crew-general/impostor/gen-3/7e5fe988f2cdc91328ead651ba1da9d75e81c6b0169c58b18db6dbe35c6fba7f/stamp.json
7e5fe988f2cdc91328ead651ba1da9d75e81c6b0169c58b18db6dbe35c6fba7f  coevo/run-c2-crew-general/impostor/gen-3/7e5fe988f2cdc91328ead651ba1da9d75e81c6b0169c58b18db6dbe35c6fba7f/weights.json
62fb0baf2b690e795337e9c03c91780bda351033a79fa36b941bd43f41892bc8  coevo/run-c2-crew-general/impostor/gen-3/7e5fe988f2cdc91328ead651ba1da9d75e81c6b0169c58b18db6dbe35c6fba7f/weights.json.sha256
9058d053dcd1b3c28110051f38b82441439cf6053fd90e67aa9a4fc91a50251a  coevo/run-c2-crew-general/impostor/gen-6/1577942ba6435b20c9298dd2ce3c07af1135a70c55d69905675bfcf3e94dc9a4/config.json
d3852acd7692c8e7e58f42ae4f223c33d4925dcdee4a8fe170603ddbd00bf0c2  coevo/run-c2-crew-general/impostor/gen-6/1577942ba6435b20c9298dd2ce3c07af1135a70c55d69905675bfcf3e94dc9a4/stamp.json
1577942ba6435b20c9298dd2ce3c07af1135a70c55d69905675bfcf3e94dc9a4  coevo/run-c2-crew-general/impostor/gen-6/1577942ba6435b20c9298dd2ce3c07af1135a70c55d69905675bfcf3e94dc9a4/weights.json
b23cb1818bbc4c1b76606826eabe74df8d1bcaa42920285bb3072697f0d6e205  coevo/run-c2-crew-general/impostor/gen-6/1577942ba6435b20c9298dd2ce3c07af1135a70c55d69905675bfcf3e94dc9a4/weights.json.sha256
d18c49712c6148da6c76cbbbc91c560ec99bb8038531436c91f99cd1acf18c3b  coevo/run-c2-crew-general/impostor/gen-7/216d4664d6acc1d41b1b0edbfa029ec85614925cfc613c0ebd05971be35fce02/config.json
d96e6e83d4ac80091c01d5e3623a9aab16826f90ac2e8c4793ed196e24eb0b9e  coevo/run-c2-crew-general/impostor/gen-7/216d4664d6acc1d41b1b0edbfa029ec85614925cfc613c0ebd05971be35fce02/stamp.json
216d4664d6acc1d41b1b0edbfa029ec85614925cfc613c0ebd05971be35fce02  coevo/run-c2-crew-general/impostor/gen-7/216d4664d6acc1d41b1b0edbfa029ec85614925cfc613c0ebd05971be35fce02/weights.json
ed091d4fd51a28405b74e4c742646693c007244f3bd965695a1582fd6b630fa8  coevo/run-c2-crew-general/impostor/gen-7/216d4664d6acc1d41b1b0edbfa029ec85614925cfc613c0ebd05971be35fce02/weights.json.sha256
58a4ca10f0b0e3d6c18801adfe490ddf9fd106ae101ec7c0e5010eca14637622  coevo/run-c2-crew-general/impostor/gen-8/5df1d71903444333d404a77d42e0ac8ae412e11fc63041bfda0329a2df0eee45/config.json
b50b9b6fbadb86dda13132e7bf31e9f20d52456073c47d01a68f084c496fbafa  coevo/run-c2-crew-general/impostor/gen-8/5df1d71903444333d404a77d42e0ac8ae412e11fc63041bfda0329a2df0eee45/stamp.json
5df1d71903444333d404a77d42e0ac8ae412e11fc63041bfda0329a2df0eee45  coevo/run-c2-crew-general/impostor/gen-8/5df1d71903444333d404a77d42e0ac8ae412e11fc63041bfda0329a2df0eee45/weights.json
fcdf7fd01379efc3e01270f1fb588ce9766df022cc8326733d63529e4f44182a  coevo/run-c2-crew-general/impostor/gen-8/5df1d71903444333d404a77d42e0ac8ae412e11fc63041bfda0329a2df0eee45/weights.json.sha256
48b37115a1b0cc8eef0a8816f302bc8ffa1bb9f2503c90022c56265349faff00  coevo/run-c2-crew-general/impostor/gen-9/a0eb02dc9e7c69fb6afd6bd99e83b9be33bd425057ce3b8a2e7a442ac9e0de27/config.json
919b41c287b6237d4856575f43f77ce0474e05e6e192db03da47783a34d24041  coevo/run-c2-crew-general/impostor/gen-9/a0eb02dc9e7c69fb6afd6bd99e83b9be33bd425057ce3b8a2e7a442ac9e0de27/stamp.json
a0eb02dc9e7c69fb6afd6bd99e83b9be33bd425057ce3b8a2e7a442ac9e0de27  coevo/run-c2-crew-general/impostor/gen-9/a0eb02dc9e7c69fb6afd6bd99e83b9be33bd425057ce3b8a2e7a442ac9e0de27/weights.json
a332643fb1e15e0da7a8bfc43a8aed91c5db152af945427961cd1dcf8d1b26c0  coevo/run-c2-crew-general/impostor/gen-9/a0eb02dc9e7c69fb6afd6bd99e83b9be33bd425057ce3b8a2e7a442ac9e0de27/weights.json.sha256
64e8a2fdd1e5af2aa7c25e1efdd387258175565158761df5cdb84027fbf2a1df  coevo/run-c2-crew-general/impostor/hall_of_fame.json
521abe4afbe4cb6cf1be28a4c6439d4bc8315cb324f5f82875315677b718570e  coevo/runnerups-gen3/run-02-utility-lambda4/gen-3/76400d720ca26df69c402e96d167472222b4b3645a738c26b55283d94dd5507f/config.json
6116c53f3709e2f1022a47117a891683b3f59bf3f9b3a9c2c834790e556222e1  coevo/runnerups-gen3/run-02-utility-lambda4/gen-3/76400d720ca26df69c402e96d167472222b4b3645a738c26b55283d94dd5507f/stamp.json
76400d720ca26df69c402e96d167472222b4b3645a738c26b55283d94dd5507f  coevo/runnerups-gen3/run-02-utility-lambda4/gen-3/76400d720ca26df69c402e96d167472222b4b3645a738c26b55283d94dd5507f/weights.json
76feeb5cb7eea9bb2264c8c8f8ccff7f8914e39bc67d1c5e38d71639fdb0207a  coevo/runnerups-gen3/run-02-utility-lambda4/gen-3/76400d720ca26df69c402e96d167472222b4b3645a738c26b55283d94dd5507f/weights.json.sha256
bd16ba367ff9b9e05caa14c75cda0f65d6011715130ec6fe82b82fb67366fdda  coevo/runnerups/run-01-utility-champion/exact-rescore.json
a3852964c7527f87478f4a8ccaf2f9e37638be398bf1bbc98e5f65277ad12811  coevo/runnerups/run-01-utility-champion/gen-1/6cf5ffb687746790b2124ff12de6cbbbc5dab7f61d9987cd6affcd9ad8abd580/config.json
5e68d34e9e6ca03a904dac52cfb3275cbbf54ddd3e61f1dbe2606fe9b6245392  coevo/runnerups/run-01-utility-champion/gen-1/6cf5ffb687746790b2124ff12de6cbbbc5dab7f61d9987cd6affcd9ad8abd580/stamp.json
6cf5ffb687746790b2124ff12de6cbbbc5dab7f61d9987cd6affcd9ad8abd580  coevo/runnerups/run-01-utility-champion/gen-1/6cf5ffb687746790b2124ff12de6cbbbc5dab7f61d9987cd6affcd9ad8abd580/weights.json
f9e3cd7c9d636d1621485fc959fad2869469385ccb6728788de99f52f5fb52f4  coevo/runnerups/run-01-utility-champion/gen-1/6cf5ffb687746790b2124ff12de6cbbbc5dab7f61d9987cd6affcd9ad8abd580/weights.json.sha256
f3323492a844d7af1689355649e173f3ec4c7a0cd0634ad2e2637764220c4df8  coevo/runnerups/run-01-utility-champion/gen-2/7c093a035369826920ba9aea96a83d60cea8d595387bc72832c43dc18bd2daec/config.json
462a97521a05c49ef091d6afb40b812b0b1594181e501263f2234bff25d8ee27  coevo/runnerups/run-01-utility-champion/gen-2/7c093a035369826920ba9aea96a83d60cea8d595387bc72832c43dc18bd2daec/stamp.json
7c093a035369826920ba9aea96a83d60cea8d595387bc72832c43dc18bd2daec  coevo/runnerups/run-01-utility-champion/gen-2/7c093a035369826920ba9aea96a83d60cea8d595387bc72832c43dc18bd2daec/weights.json
70a13849c5e7ac11b52be081312e84d85be198a26276a955c566d5e774f213cb  coevo/runnerups/run-01-utility-champion/gen-2/7c093a035369826920ba9aea96a83d60cea8d595387bc72832c43dc18bd2daec/weights.json.sha256
dbd7f2794af83dc863d71f355e09fa6f5dcafa2d64347a182a0af72f1d4fce82  coevo/runnerups/run-01-utility-champion/gen-3/11aa68637a8f12e53780db29cabffb7f88af437f0635db9af3aacdc1014260c4/config.json
1fed225324721880a567038923d86ac7b724a6955a2ed8c701f181e40d2320e0  coevo/runnerups/run-01-utility-champion/gen-3/11aa68637a8f12e53780db29cabffb7f88af437f0635db9af3aacdc1014260c4/stamp.json
11aa68637a8f12e53780db29cabffb7f88af437f0635db9af3aacdc1014260c4  coevo/runnerups/run-01-utility-champion/gen-3/11aa68637a8f12e53780db29cabffb7f88af437f0635db9af3aacdc1014260c4/weights.json
bf0983e5b1b1da689036e3c94d4aa5cdba260634b2e703427d30722f200c8821  coevo/runnerups/run-01-utility-champion/gen-3/11aa68637a8f12e53780db29cabffb7f88af437f0635db9af3aacdc1014260c4/weights.json.sha256
511574cbd56f2c377aebaea6ab778e4c3e38e68ec9652c938afb6b17e7c415cb  coevo/runnerups/run-01-utility-champion/gen-7/e531c1f9a704a5011b4ff0150e6f263422d5295c7954ed3b5165d2ad9d16ad26/config.json
72be22909331afeaebe9673f20d548cf88204f5593e3dd0d4d28a50399f60818  coevo/runnerups/run-01-utility-champion/gen-7/e531c1f9a704a5011b4ff0150e6f263422d5295c7954ed3b5165d2ad9d16ad26/stamp.json
e531c1f9a704a5011b4ff0150e6f263422d5295c7954ed3b5165d2ad9d16ad26  coevo/runnerups/run-01-utility-champion/gen-7/e531c1f9a704a5011b4ff0150e6f263422d5295c7954ed3b5165d2ad9d16ad26/weights.json
500f5bffc26bcaaa6deef20bab35487bdd5fc42f1633f3ee40f8973bf185f615  coevo/runnerups/run-01-utility-champion/gen-7/e531c1f9a704a5011b4ff0150e6f263422d5295c7954ed3b5165d2ad9d16ad26/weights.json.sha256
a3c827565ee691b5f7ff3a937962c7951c0438da55f738dc77da53d0f821d70d  coevo/runnerups/run-01-utility-champion/gen-8/609ea9ce9e878cded117da0b20a24ee6b4fbc47c66dec5344ded0defb581876c/config.json
7e5ce8309803439531fbe5d791deb5e4b5170838d9160d04227bd06764abeaa2  coevo/runnerups/run-01-utility-champion/gen-8/609ea9ce9e878cded117da0b20a24ee6b4fbc47c66dec5344ded0defb581876c/stamp.json
609ea9ce9e878cded117da0b20a24ee6b4fbc47c66dec5344ded0defb581876c  coevo/runnerups/run-01-utility-champion/gen-8/609ea9ce9e878cded117da0b20a24ee6b4fbc47c66dec5344ded0defb581876c/weights.json
a2c2a072e91d3efe344ef269ab5b5555bbc0a43a3c4e70729b685dfaccf2d22b  coevo/runnerups/run-01-utility-champion/gen-8/609ea9ce9e878cded117da0b20a24ee6b4fbc47c66dec5344ded0defb581876c/weights.json.sha256
c93351a5834ef6a38aacd5020afd1655e723a0a99a58b15e511ac0090a890d7b  coevo/runnerups/run-01-utility-champion/gen-9/1f5efd3c2f47462c4373ca2e051e12007d60aa9dfc222173821099cfa258c26f/config.json
74f7f6f1dc7e5d90fe828e359c74f77d5eded8ca879f6eeecde5617e033a57de  coevo/runnerups/run-01-utility-champion/gen-9/1f5efd3c2f47462c4373ca2e051e12007d60aa9dfc222173821099cfa258c26f/stamp.json
1f5efd3c2f47462c4373ca2e051e12007d60aa9dfc222173821099cfa258c26f  coevo/runnerups/run-01-utility-champion/gen-9/1f5efd3c2f47462c4373ca2e051e12007d60aa9dfc222173821099cfa258c26f/weights.json
ded3479867aa164c8b830230eceebb7ffab7eb00849df63e8da1eacacbfd26b6  coevo/runnerups/run-01-utility-champion/gen-9/1f5efd3c2f47462c4373ca2e051e12007d60aa9dfc222173821099cfa258c26f/weights.json.sha256
f7c82421776e8c96891baa71f690a50a3521d07647c9ad60120f470799782d56  coevo/runnerups/run-01-utility-champion/index.json
1c0b3fcda5c7e133bfd92846b5fada3ccb131440589afb71b89209e0123b8039  coevo/runnerups/run-02-utility-lambda4/exact-rescore.json
ac557acd5553056a489e5d17cbd9bf9849b8d2218737eca01b6959ec1c9e5713  coevo/runnerups/run-02-utility-lambda4/gen-1/3a89655f0ae78e389046778ad0735bddba5a8ac555f9bd1f8bb92d0cb4e2f482/config.json
3727a6b876087eafb433a0555c5258951ce34d13f4fe6af028ceb54fd0dd6dc6  coevo/runnerups/run-02-utility-lambda4/gen-1/3a89655f0ae78e389046778ad0735bddba5a8ac555f9bd1f8bb92d0cb4e2f482/stamp.json
3a89655f0ae78e389046778ad0735bddba5a8ac555f9bd1f8bb92d0cb4e2f482  coevo/runnerups/run-02-utility-lambda4/gen-1/3a89655f0ae78e389046778ad0735bddba5a8ac555f9bd1f8bb92d0cb4e2f482/weights.json
228b8c8e62dbb513853bb6f5dc1a04ee1965731a3e5bb763bb8e2bd81f65081f  coevo/runnerups/run-02-utility-lambda4/gen-1/3a89655f0ae78e389046778ad0735bddba5a8ac555f9bd1f8bb92d0cb4e2f482/weights.json.sha256
91cef7a6abc73b33e539591cf66306617fefd876bfbfadf5a5d175ecff0b162c  coevo/runnerups/run-02-utility-lambda4/gen-2/2b40b2c1f1e83b1e4b156cf5fd7c524e04129028b314f984afc0e064296e54e2/config.json
407ea3e2dde633f5ad8986f1d0e45e45d7418f679effdb40357437c929c56f45  coevo/runnerups/run-02-utility-lambda4/gen-2/2b40b2c1f1e83b1e4b156cf5fd7c524e04129028b314f984afc0e064296e54e2/stamp.json
2b40b2c1f1e83b1e4b156cf5fd7c524e04129028b314f984afc0e064296e54e2  coevo/runnerups/run-02-utility-lambda4/gen-2/2b40b2c1f1e83b1e4b156cf5fd7c524e04129028b314f984afc0e064296e54e2/weights.json
1dd435813e974f2170bcff4f5123e507e0db11fe5f817521e5ff5b0a5f4bfb48  coevo/runnerups/run-02-utility-lambda4/gen-2/2b40b2c1f1e83b1e4b156cf5fd7c524e04129028b314f984afc0e064296e54e2/weights.json.sha256
137144a6473442fdf393484629cf95e950c7476c9e214192682679ef04d642db  coevo/runnerups/run-02-utility-lambda4/gen-3/76400d720ca26df69c402e96d167472222b4b3645a738c26b55283d94dd5507f/config.json
97fffbc1dbbd11b29cc4adeeca0e60cd531bcbf0417f2d142fc0101d54a5db55  coevo/runnerups/run-02-utility-lambda4/gen-3/76400d720ca26df69c402e96d167472222b4b3645a738c26b55283d94dd5507f/stamp.json
76400d720ca26df69c402e96d167472222b4b3645a738c26b55283d94dd5507f  coevo/runnerups/run-02-utility-lambda4/gen-3/76400d720ca26df69c402e96d167472222b4b3645a738c26b55283d94dd5507f/weights.json
76feeb5cb7eea9bb2264c8c8f8ccff7f8914e39bc67d1c5e38d71639fdb0207a  coevo/runnerups/run-02-utility-lambda4/gen-3/76400d720ca26df69c402e96d167472222b4b3645a738c26b55283d94dd5507f/weights.json.sha256
2bac4cfe8b7269c8bfa2f0bdfbde56f527981f7de517d1555c102baa696813a4  coevo/runnerups/run-02-utility-lambda4/gen-3/SUPERSEDED-2bac4cfe8b7269c8bfa2f0bdfbde56f527981f7de517d1555c102baa696813a4/weights.json
883268e71f738d854fdd9b8286862f10fe8df73febc2cde924914bbc4cceb335  coevo/runnerups/run-02-utility-lambda4/gen-3/SUPERSEDED-2bac4cfe8b7269c8bfa2f0bdfbde56f527981f7de517d1555c102baa696813a4/weights.json.sha256
d2a27c0ad7ec8d514bd504d5d2ebd52078eb6bb23d4963ce0b236b8f751e65a6  coevo/runnerups/run-02-utility-lambda4/gen-7/cb17deda3cf34708ebd8d14d5cd49da06ef6c00023cc81efeeb16047807cbc33/config.json
c25fb8e7d21781829c862f3e73ab40162ed37a6163f176416c40f33f0ad35499  coevo/runnerups/run-02-utility-lambda4/gen-7/cb17deda3cf34708ebd8d14d5cd49da06ef6c00023cc81efeeb16047807cbc33/stamp.json
cb17deda3cf34708ebd8d14d5cd49da06ef6c00023cc81efeeb16047807cbc33  coevo/runnerups/run-02-utility-lambda4/gen-7/cb17deda3cf34708ebd8d14d5cd49da06ef6c00023cc81efeeb16047807cbc33/weights.json
7ed6b05e8e839c8c5896d733dbceb60689dd653eae9b5e2553f5da5ad31e8cfe  coevo/runnerups/run-02-utility-lambda4/gen-7/cb17deda3cf34708ebd8d14d5cd49da06ef6c00023cc81efeeb16047807cbc33/weights.json.sha256
87f361ee8e2a3179bd335fb3f204a2a0ace6e4d9ab8e6ef28dd0e5f2269be8b9  coevo/runnerups/run-02-utility-lambda4/gen-8/f280962f179fd11c4df2f98cb1daf24a3367222396c03a97b18fdee0d5418d10/config.json
659a4fedb1dd4d1febdaf094e00edd9cfc34bd0344c22f8840b81c98f51d409c  coevo/runnerups/run-02-utility-lambda4/gen-8/f280962f179fd11c4df2f98cb1daf24a3367222396c03a97b18fdee0d5418d10/stamp.json
f280962f179fd11c4df2f98cb1daf24a3367222396c03a97b18fdee0d5418d10  coevo/runnerups/run-02-utility-lambda4/gen-8/f280962f179fd11c4df2f98cb1daf24a3367222396c03a97b18fdee0d5418d10/weights.json
d323150596d4dd0dea1bb73aef1e82d7dec96af8459a54176ef1d50fdf6f28b5  coevo/runnerups/run-02-utility-lambda4/gen-8/f280962f179fd11c4df2f98cb1daf24a3367222396c03a97b18fdee0d5418d10/weights.json.sha256
671111ddcd9f191b35037f3a5114fe65720786d0d1e76e8eb282e3338ca17925  coevo/runnerups/run-02-utility-lambda4/index.json
bfec2714764ed52bed22dfb097efc0946dbd2cd5ca6de832a63d45736d654cf4  coevo/runnerups/run-03-utility-bcanchor/exact-rescore.json
4326f42aa5281fec38f2b05e4b0aab765c7b4b9c8a8cf61045abdf4dad5028c5  coevo/runnerups/run-03-utility-bcanchor/gen-1/98171e870e74d62fb181ef7face49f8bf7b3fdbad30bb6d133f94cd366abf6e0/config.json
fcc34461238540ef24cddf9ee40455b7c33f20a6a0eb293c947a716eff91528a  coevo/runnerups/run-03-utility-bcanchor/gen-1/98171e870e74d62fb181ef7face49f8bf7b3fdbad30bb6d133f94cd366abf6e0/stamp.json
98171e870e74d62fb181ef7face49f8bf7b3fdbad30bb6d133f94cd366abf6e0  coevo/runnerups/run-03-utility-bcanchor/gen-1/98171e870e74d62fb181ef7face49f8bf7b3fdbad30bb6d133f94cd366abf6e0/weights.json
00bb87e8f6540011ebab13ceeb414430fdffc37112a90db299e188d80d8dbd9e  coevo/runnerups/run-03-utility-bcanchor/gen-1/98171e870e74d62fb181ef7face49f8bf7b3fdbad30bb6d133f94cd366abf6e0/weights.json.sha256
d1aaa64ba31d7b5e03b94303992cf630871408b273dab308243209a77dbac462  coevo/runnerups/run-03-utility-bcanchor/gen-2/62499b47ca73db000fb0ac6c9e8af37655ba672506421f8de1031646e3422461/config.json
e8a3ddc70d28e138311ef2f769be6f504c0ec956b270ff7bff6206367806e555  coevo/runnerups/run-03-utility-bcanchor/gen-2/62499b47ca73db000fb0ac6c9e8af37655ba672506421f8de1031646e3422461/stamp.json
62499b47ca73db000fb0ac6c9e8af37655ba672506421f8de1031646e3422461  coevo/runnerups/run-03-utility-bcanchor/gen-2/62499b47ca73db000fb0ac6c9e8af37655ba672506421f8de1031646e3422461/weights.json
a6a486656f263987f42ee5b5f0c32446eb0657df3e9adb3c90ce1e4bda8c0aea  coevo/runnerups/run-03-utility-bcanchor/gen-2/62499b47ca73db000fb0ac6c9e8af37655ba672506421f8de1031646e3422461/weights.json.sha256
06c0168e981aec6ef951b76b0673ba68b9617e8e8f6ae803f7e07282d337e6ac  coevo/runnerups/run-03-utility-bcanchor/gen-3/b1c8f9147845d526a4d6fc699385aa67981d1e0ba67ec8110448a936058dc34a/config.json
c3818d1922c4f453e9e71e4516aad8e881bcc143593c5d2cf8ca4309751b5578  coevo/runnerups/run-03-utility-bcanchor/gen-3/b1c8f9147845d526a4d6fc699385aa67981d1e0ba67ec8110448a936058dc34a/stamp.json
b1c8f9147845d526a4d6fc699385aa67981d1e0ba67ec8110448a936058dc34a  coevo/runnerups/run-03-utility-bcanchor/gen-3/b1c8f9147845d526a4d6fc699385aa67981d1e0ba67ec8110448a936058dc34a/weights.json
498b4bb9ad8e388d4f99affea57993c22af74694f40a71fccb6a6282696fa8a2  coevo/runnerups/run-03-utility-bcanchor/gen-3/b1c8f9147845d526a4d6fc699385aa67981d1e0ba67ec8110448a936058dc34a/weights.json.sha256
8123014326422a78f239a5a25179684066da9646b15acbded204557c646a28a5  coevo/runnerups/run-03-utility-bcanchor/gen-7/f07bfa9fb89d5b63cae3ccdd993ddbb933f4ba100f52c503d6b58eca5e2f8d76/config.json
451c46b2dd926cb05aa166e470edf65c89906dea4811540fdc163f61db73d864  coevo/runnerups/run-03-utility-bcanchor/gen-7/f07bfa9fb89d5b63cae3ccdd993ddbb933f4ba100f52c503d6b58eca5e2f8d76/stamp.json
f07bfa9fb89d5b63cae3ccdd993ddbb933f4ba100f52c503d6b58eca5e2f8d76  coevo/runnerups/run-03-utility-bcanchor/gen-7/f07bfa9fb89d5b63cae3ccdd993ddbb933f4ba100f52c503d6b58eca5e2f8d76/weights.json
4067d3830bd4d52609a18c5ebd68f9fe4a72455df2860b41a4100c5c68d1e71e  coevo/runnerups/run-03-utility-bcanchor/gen-7/f07bfa9fb89d5b63cae3ccdd993ddbb933f4ba100f52c503d6b58eca5e2f8d76/weights.json.sha256
f7f9900adf046a09868b84c085963b0a6a485636543e68b13abd7fadd460a1cb  coevo/runnerups/run-03-utility-bcanchor/gen-9/0c7a75b47b85fc50992ddbee01a3cedc8a8012ef6157e6963e0b7b743dc92279/config.json
55d538f88898178fcaf222a9c3e49cfcfb572736cf52b07b03dbdac278d9b37f  coevo/runnerups/run-03-utility-bcanchor/gen-9/0c7a75b47b85fc50992ddbee01a3cedc8a8012ef6157e6963e0b7b743dc92279/stamp.json
0c7a75b47b85fc50992ddbee01a3cedc8a8012ef6157e6963e0b7b743dc92279  coevo/runnerups/run-03-utility-bcanchor/gen-9/0c7a75b47b85fc50992ddbee01a3cedc8a8012ef6157e6963e0b7b743dc92279/weights.json
0ff1ce1940f8f65e24382ef072f92699fa1dbf3086bc7dc5dd3c851f3d985f65  coevo/runnerups/run-03-utility-bcanchor/gen-9/0c7a75b47b85fc50992ddbee01a3cedc8a8012ef6157e6963e0b7b743dc92279/weights.json.sha256
8c294519344edbc05c735376c8fa2550c00269b21b15f87833928fb57d47da89  coevo/runnerups/run-03-utility-bcanchor/index.json
```

## 8. sha-256 — the `finalist-eval-raw/` payload (1,569 files)

**Delegated, not duplicated.** Those 1,569 digests already have an in-tree
owner: `training/reports/_finalist_eval_raw/MANIFEST.md` §7, written by Task
19.21. Copying them here would create a second copy of one fact, which is the
drift class this project spends its audits cleaning. The rows are identical up
to the path prefix — verified row for row when this commit was built:

```bash
awk '/^```sha256$/{f=1;next} /^```$/{f=0} f' \
  training/reports/_finalist_eval_raw/MANIFEST.md \
  | sed 's#  \./#  finalist-eval-raw/#'
```

is exactly the missing block, and that is the transformation
`scripts/fetch_evidence.sh --verify` applies. Together with §7, every one of
the evidence commit's 2,953 files carries a digest.
