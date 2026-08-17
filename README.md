# `evidence/phase-18-coevo` — the ONE immutable evidence commit

**This branch is one commit and stays one commit.** Its sha is pinned in
`training/artifacts/coevo/EVIDENCE-MANIFEST.md` on the default branch, and
`scripts/fetch_evidence.sh` fetches **by that sha, never by this branch name** —
the pin *is* the immutability guarantee. Adding a commit here does not corrupt
anything; it just makes the new commit unreachable by every consumer. Don't.

Created by **Task 19.22** (`tasks/phase-19.md`) — artifact classes + the coevo
prune + the fast-clone path — implementing Phase 19 **locked decision 5**
(*"artifact retention: prune coevo only"*).

## What is here

| tree | files | MiB | what it is |
|---|---|---|---|
| `coevo/` | 1,383 | 101.097 | the **class-(c)** bytes pruned from `training/artifacts/coevo/` at 19.22 — every byte no test pins: the realpath\* per-seed recordings and their rosters, the unpinned genome directories (`config.json` + `stamp.json` + `weights.json` + `weights.json.sha256`), the per-tranche `recordings-manifest*.sha256`, the campaign plans/rows and hall-of-fame files |
| `finalist-eval-raw/` | 1,569 | 298.157 | the **Phase-18 finalist raw slate** — the 449-game event-level lineage behind the Phase-18 adoption decision, recovered at Task 19.21 and folded here from the (now retired) `evidence/raw-slate-staging` ref @ `c27ab7b5f5e7e10bfab5c6dc752362b137862cac` |
| `README.md` | 1 | — | this file |
| **total** | **2,953** | **399.254** | the two payload trees (418,648,282 bytes); this file adds ~2 KiB on top |

Paths under `coevo/` are relative to `training/artifacts/coevo/`:
`scripts/fetch_evidence.sh` restores `coevo/<x>` to `training/artifacts/coevo/<x>`
and `finalist-eval-raw/<x>` to `training/reports/_finalist_eval_raw/<x>`.

## The authority is the in-tree manifest, not this branch

`training/artifacts/coevo/EVIDENCE-MANIFEST.md` on the default branch is the
manifest commit for these bytes. It carries a **sha-256 for every file here**
(this README included), pins this commit's sha, and records which in-tree paths
stayed behind and which test pins each one. Where this README and that manifest
disagree, **the manifest wins** — see the errata below for exactly why that
sentence is here.

Restore and verify in one command:

```bash
bash scripts/fetch_evidence.sh          # fetch by the pinned sha + restore + verify
bash scripts/fetch_evidence.sh --verify # verify what is already restored
```

## Errata carried forward from the retired staging ref

`evidence/raw-slate-staging` carried a ref-root `README.md`
(sha-256 `ea4e4ff1f50ecaae88000b69f707f9a478ec96eb7065a39ade1d48d5bad3b8fb`,
1,841 bytes) — the **one** staged file no committed sha covered, as
`training/reports/_finalist_eval_raw/MANIFEST.md` §2 declared openly. It is not
carried forward verbatim, because two of its figures disagree with the bytes it
described. Both were re-checked against those bytes when this commit was built:

| the staging README said | the bytes say |
|---|---|
| `1,569 files, 297.8 MiB` | 1,569 files, **298.157 MiB** (312,640,280 bytes) — which the in-tree `MANIFEST.md` states correctly as 298.2 |
| recorded `2026-07-29 → 2026-08-01` | `2026-07-29T07:17:48Z → `**`2026-07-31T18:00:06Z`** — the last timestamp anywhere in the slate; no `2026-08` timestamp exists in it |

Its digest above is recorded so the one uncovered staged byte is on the record;
its two numbers are not repeated anywhere in this tree.

## What is not here

The **1,433 split-view symlinks** under `scoring/<arm>/<view>/`. Every one
resolved to a raw recording that *is* here, their targets are absolute
owner-machine paths (so they dangle off that machine), and dereferencing them
would have written 612.3 MiB of duplicate bytes. Their membership — which seeds
each view held — is tabulated in `training/reports/_finalist_eval_raw/MANIFEST.md`
§4, so every view is reconstructible.

## Nothing was re-recorded

These are the original bytes. The slate's price is **57.1589 busy hours**
(`training/reports/report-finalist-eval.md` §14), named and declined by the
Phase-19 charter. The recordings are real-provider (Featherless
`Qwen/Qwen3.6-27B`) draws: preserving the bytes makes the lineage auditable, it
does not make the run re-runnable.
