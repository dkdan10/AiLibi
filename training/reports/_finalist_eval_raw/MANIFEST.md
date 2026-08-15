# The Phase-18 finalist raw slate — the content-addressed manifest

> **Task:** 19.21 (`tasks/phase-19.md`) — the finalist raw slate: recover or
> label (owner). **Anchor:** `audits/audit-phase-19-triage.md` §7 item 22
> \[C; VERIFIED §8 row 11\] — *"Recover/content-address the finalist raw slate
> if it still exists; otherwise mark event-level lineage non-reproducible. Do
> not re-record."*
> **Ruling, 2026-08-15: RECOVERED.** The owner-machine check found
> `~/ailibi-campaign-1826/` intact — **1,569 files, 298.2 MiB**,
> including all **449** raw per-seed recordings. Every one is sha-256'd in §7
> below and staged on `evidence/raw-slate-staging`.
> **Consumer:** Task 19.22 folds the staged bytes into the ONE immutable
> evidence commit (`evidence/phase-18-coevo`) and retires the staging ref.
> **Nothing was re-recorded** (§6).

## 1. What this slate is

The **449-game finalist eval** behind the Phase-18 adoption decision: nine arms
recorded on the locked baseline-6 substrate over
`2026-07-29T07:17:48Z → 2026-07-31T18:00:06Z`
(`training/reports/report-finalist-eval.md` §14), scored into the JSON that
§16's evidence tables are read from cell by cell.

The report states the provenance separation at §2 (:115-118):

> the raw recordings are working artifacts — they live **outside** the repo
> tree, do NOT join `replays/samples/` or `replays/ml_corpus/`, and are
> re-recordable from this recipe. What is committed is their **measurement**
> (§3, the jsonl).

and §16 (:1066-1070) names the external source of every recorded cell:

> Every cell below is read from a committed `~/ailibi-campaign-1826/scoring/<arm>/`
> JSON (`summary.json`, `validity.json`, `core.json`, `watchability*.json`,
> `split-half.json`, `instruments.json`, `stamp-proof.json`, `duration.json`,
> `row.json`)

The triage's finding is what those two sentences add up to: the flattened rows
in `training/reports/results-finalist-eval.jsonl` are committed, but the
**event-level lineage under them was repo-external and uncommitted** —
`git ls-files training/reports/_finalist_eval_raw` returned nothing. This
manifest closes that gap for the bytes, and §5 states exactly what it does and
does not buy.

**§2's separation still holds.** These bytes do **not** join
`replays/samples/` or `replays/ml_corpus/`, and they do not land in the working
tree at all: they become **class-(c) large immutable evidence** on the evidence
branch (`docs/artifacts.md`, Task 19.22), reachable by pinned sha and fetched on
demand.

## 2. Where the bytes are

| | location | durability |
|---|---|---|
| **source** | `~/ailibi-campaign-1826/` (the owner's machine) | **none** — one machine, no backup; this manifest exists because that was the whole problem |
| **staged** | `evidence/raw-slate-staging` @ `c27ab7b5f5e7e10bfab5c6dc752362b137862cac` | **temporary** — pushed 2026-08-15 by this task, retired by 19.22 after the fold |
| **destination** | `evidence/phase-18-coevo`, the ONE immutable evidence commit | **the durable home**; its tip sha is pinned in 19.22's in-tree manifest and `scripts/fetch_evidence.sh` fetches BY that sha |

The staging ref reproduces the campaign root **verbatim** under
`finalist-eval-raw/`, minus the 1,433 split-view symlinks (§4), plus one
ref-local `README.md` at the ref root. That `README.md` is the **only** file on
the ref not covered by §7 — it is ref metadata written by this task, not slate
bytes.

## 3. The census — what "449" means

| arm | raw recordings | audit sidecars | forensics files | note |
|---|---|---|---|---|
| `p18-crew-c1-gen0` | 50 | 50 | 0 | — |
| `p18-crew-c1-gen9` | 50 | 50 | 0 | — |
| `p18-crew-c2-gen0` | 50 | 50 | 0 | — |
| `p18-crew-c2-gen9` | 50 | 50 | 0 | — |
| `p18-fsm-comparator` | 50 | 50 | 4 | — |
| `p18-imp-6d327dcb` | 50 | 50 | 0 | — |
| `p18-imp-7f73929d` | 49 | 50 | 6 | seed 35 excluded |
| `p18-imp-bfd145cb` | 50 | 50 | 0 | — |
| `p18-imp-ea4bc955` | 50 | 50 | 0 | — |
| **total** | **449** | **450** | **10** | **449 = 8 × 50 + 49** |

**449, not 450.** `p18-imp-7f73929d` seed 35 never recorded clean — the report
records it at :935 as *"excluded, forensics kept"* after **14 logged attempts,
every one rc 99**, and carries the arm at **n=49** in every §16 cell. Its raw
replay is therefore absent by construction, while its **audit sidecar survives**
(both in `scoring/` and as a copy in the arm dir) and six forensics recordings
of the failed attempts are kept. `p18-fsm-comparator` seed 5 is the mirror case
— pure on attempt 14, scored at the full n=50, four impure attempts kept in
`forensics/`.

An absent seed-35 raw replay is **the recorded state of the slate**, not a loss
introduced here.

## 4. The inventory

| class | paths | files | MiB |
|---|---|---|---|
| raw per-seed recordings — **the 449 games** | `<arm>/replay-seed-N.jsonl` | 449 | 182.1 |
| audit sidecars — the stamp==sidecar evidence | `scoring/<arm>/audit-sidecars/replay-seed-N.audit.jsonl` | 450 | 105.5 |
| the excluded seed's retained sidecar | `p18-imp-7f73929d/replay-seed-35.audit.jsonl` | 1 | 0.3 |
| scoring measurement JSON — **what §16's cells are read from** | `scoring/<arm>/*.json` | 112 | 3.0 |
| per-arm roster + tournament report | `<arm>/roster.json`, `<arm>/tournament-eval-report.json` | 18 | 2.9 |
| split-view rosters | `scoring/<arm>/<view>/roster.json` | 61 | 0.0 |
| forensics — the excluded/impure attempts | `forensics/*.jsonl` | 10 | 4.0 |
| operator leg logs | `leg-log-*.jsonl` | 10 | 0.1 |
| operator per-seed stdout | `stdout-<arm>-seed-N.log` | 450 | 0.2 |
| the scoring/assembly scripts + the 18.26 owner brief | `*.py`, `*.sh`, `*.pdf` | 8 | 0.1 |
| **total** | | **1,569** | **298.2** |

### The 1,433 split-view symlinks — recorded, not duplicated

`scoring/<arm>/` also holds 61 **view directories** of symlinks —
`split-h1`/`split-h2`, the `mod5` train/val/test splits, the f13 and 49-seed
intersection views — 1,433 links in total. Every one was verified to be
non-dangling, to point at a `replay-seed-N.jsonl` **in its own arm**, and to
carry the same basename as its target: they are views into raw recordings that
§7 already covers. Dereferencing them would have written **612.3 MiB** of
duplicate bytes — the same 449 recordings copied once per view they appear in —
to add nothing. Staging them as symlinks was the other wrong answer: their
targets are absolute owner-machine paths, so every one dangles off this machine.

What the links *carry* is their **membership** — which seeds each view held —
and that is evidence, so it is tabulated here rather than dropped. Each view is
reconstructible from this table plus the raw recordings.

| view directory | seeds | membership |
|---|---|---|
| `scoring/p18-crew-c1-gen0/instruments-view` | 49 | 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49 |
| `scoring/p18-crew-c1-gen0/split-h1` | 25 | 0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48 |
| `scoring/p18-crew-c1-gen0/split-h2` | 25 | 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 37, 39, 41, 43, 45, 47, 49 |
| `scoring/p18-crew-c1-gen0/split-test_mod5_4` | 10 | 4, 9, 14, 19, 24, 29, 34, 39, 44, 49 |
| `scoring/p18-crew-c1-gen0/split-train_mod5_012` | 29 | 0, 1, 2, 5, 6, 7, 10, 11, 12, 15, 16, 17, 21, 22, 25, 26, 27, 30, 31, 32, 35, 36, 37, 40, 41, 42, 45, 46, 47 |
| `scoring/p18-crew-c1-gen0/split-val_mod5_3` | 10 | 3, 8, 13, 18, 23, 28, 33, 38, 43, 48 |
| `scoring/p18-crew-c1-gen9/rider-intersection-view` | 49 | 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49 |
| `scoring/p18-crew-c1-gen9/split-h1` | 25 | 0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48 |
| `scoring/p18-crew-c1-gen9/split-h2` | 25 | 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 37, 39, 41, 43, 45, 47, 49 |
| `scoring/p18-crew-c1-gen9/split-test_mod5_4` | 10 | 4, 9, 14, 19, 24, 29, 34, 39, 44, 49 |
| `scoring/p18-crew-c1-gen9/split-train_mod5_012` | 30 | 0, 1, 2, 5, 6, 7, 10, 11, 12, 15, 16, 17, 20, 21, 22, 25, 26, 27, 30, 31, 32, 35, 36, 37, 40, 41, 42, 45, 46, 47 |
| `scoring/p18-crew-c1-gen9/split-val_mod5_3` | 10 | 3, 8, 13, 18, 23, 28, 33, 38, 43, 48 |
| `scoring/p18-crew-c2-gen0/split-h1` | 25 | 0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48 |
| `scoring/p18-crew-c2-gen0/split-h2` | 25 | 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 37, 39, 41, 43, 45, 47, 49 |
| `scoring/p18-crew-c2-gen0/split-test_mod5_4` | 10 | 4, 9, 14, 19, 24, 29, 34, 39, 44, 49 |
| `scoring/p18-crew-c2-gen0/split-train_mod5_012` | 30 | 0, 1, 2, 5, 6, 7, 10, 11, 12, 15, 16, 17, 20, 21, 22, 25, 26, 27, 30, 31, 32, 35, 36, 37, 40, 41, 42, 45, 46, 47 |
| `scoring/p18-crew-c2-gen0/split-val_mod5_3` | 10 | 3, 8, 13, 18, 23, 28, 33, 38, 43, 48 |
| `scoring/p18-crew-c2-gen9/instruments-view` | 48 | 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49 |
| `scoring/p18-crew-c2-gen9/split-h1` | 25 | 0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48 |
| `scoring/p18-crew-c2-gen9/split-h2` | 25 | 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 37, 39, 41, 43, 45, 47, 49 |
| `scoring/p18-crew-c2-gen9/split-test_mod5_4` | 9 | 4, 9, 14, 24, 29, 34, 39, 44, 49 |
| `scoring/p18-crew-c2-gen9/split-train_mod5_012` | 29 | 0, 1, 2, 5, 6, 7, 10, 11, 12, 15, 16, 17, 21, 22, 25, 26, 27, 30, 31, 32, 35, 36, 37, 40, 41, 42, 45, 46, 47 |
| `scoring/p18-crew-c2-gen9/split-val_mod5_3` | 10 | 3, 8, 13, 18, 23, 28, 33, 38, 43, 48 |
| `scoring/p18-fsm-comparator/instruments-49-view` | 49 | 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49 |
| `scoring/p18-fsm-comparator/split-h1` | 25 | 0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48 |
| `scoring/p18-fsm-comparator/split-h2` | 25 | 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 37, 39, 41, 43, 45, 47, 49 |
| `scoring/p18-fsm-comparator/split-test_mod5_4` | 10 | 4, 9, 14, 19, 24, 29, 34, 39, 44, 49 |
| `scoring/p18-fsm-comparator/split-train_mod5_012` | 30 | 0, 1, 2, 5, 6, 7, 10, 11, 12, 15, 16, 17, 20, 21, 22, 25, 26, 27, 30, 31, 32, 35, 36, 37, 40, 41, 42, 45, 46, 47 |
| `scoring/p18-fsm-comparator/split-val_mod5_3` | 10 | 3, 8, 13, 18, 23, 28, 33, 38, 43, 48 |
| `scoring/p18-fsm-comparator/split49-test_mod5_4` | 10 | 4, 9, 14, 19, 24, 29, 34, 39, 44, 49 |
| `scoring/p18-fsm-comparator/split49-train_mod5_012` | 29 | 0, 1, 2, 5, 6, 7, 10, 11, 12, 15, 16, 17, 20, 21, 22, 25, 26, 27, 30, 31, 32, 36, 37, 40, 41, 42, 45, 46, 47 |
| `scoring/p18-fsm-comparator/split49-val_mod5_3` | 10 | 3, 8, 13, 18, 23, 28, 33, 38, 43, 48 |
| `scoring/p18-imp-6d327dcb/f13-intersection-view` | 49 | 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49 |
| `scoring/p18-imp-6d327dcb/f13-split-h1` | 25 | 0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48 |
| `scoring/p18-imp-6d327dcb/f13-split-h2` | 24 | 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 37, 39, 41, 43, 45, 47, 49 |
| `scoring/p18-imp-6d327dcb/split-h1` | 25 | 0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48 |
| `scoring/p18-imp-6d327dcb/split-h2` | 25 | 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 37, 39, 41, 43, 45, 47, 49 |
| `scoring/p18-imp-6d327dcb/split-test_mod5_4` | 10 | 4, 9, 14, 19, 24, 29, 34, 39, 44, 49 |
| `scoring/p18-imp-6d327dcb/split-train_mod5_012` | 30 | 0, 1, 2, 5, 6, 7, 10, 11, 12, 15, 16, 17, 20, 21, 22, 25, 26, 27, 30, 31, 32, 35, 36, 37, 40, 41, 42, 45, 46, 47 |
| `scoring/p18-imp-6d327dcb/split-val_mod5_3` | 10 | 3, 8, 13, 18, 23, 28, 33, 38, 43, 48 |
| `scoring/p18-imp-7f73929d/split-h1` | 25 | 0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48 |
| `scoring/p18-imp-7f73929d/split-h2` | 24 | 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 37, 39, 41, 43, 45, 47, 49 |
| `scoring/p18-imp-7f73929d/split-test_mod5_4` | 10 | 4, 9, 14, 19, 24, 29, 34, 39, 44, 49 |
| `scoring/p18-imp-7f73929d/split-train_mod5_012` | 29 | 0, 1, 2, 5, 6, 7, 10, 11, 12, 15, 16, 17, 20, 21, 22, 25, 26, 27, 30, 31, 32, 36, 37, 40, 41, 42, 45, 46, 47 |
| `scoring/p18-imp-7f73929d/split-val_mod5_3` | 10 | 3, 8, 13, 18, 23, 28, 33, 38, 43, 48 |
| `scoring/p18-imp-bfd145cb/f13-intersection-view` | 49 | 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49 |
| `scoring/p18-imp-bfd145cb/f13-split-h1` | 25 | 0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48 |
| `scoring/p18-imp-bfd145cb/f13-split-h2` | 24 | 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 37, 39, 41, 43, 45, 47, 49 |
| `scoring/p18-imp-bfd145cb/split-h1` | 25 | 0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48 |
| `scoring/p18-imp-bfd145cb/split-h2` | 25 | 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 37, 39, 41, 43, 45, 47, 49 |
| `scoring/p18-imp-bfd145cb/split-test_mod5_4` | 10 | 4, 9, 14, 19, 24, 29, 34, 39, 44, 49 |
| `scoring/p18-imp-bfd145cb/split-train_mod5_012` | 30 | 0, 1, 2, 5, 6, 7, 10, 11, 12, 15, 16, 17, 20, 21, 22, 25, 26, 27, 30, 31, 32, 35, 36, 37, 40, 41, 42, 45, 46, 47 |
| `scoring/p18-imp-bfd145cb/split-val_mod5_3` | 10 | 3, 8, 13, 18, 23, 28, 33, 38, 43, 48 |
| `scoring/p18-imp-ea4bc955/f13-intersection-view` | 49 | 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49 |
| `scoring/p18-imp-ea4bc955/f13-split-h1` | 25 | 0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48 |
| `scoring/p18-imp-ea4bc955/f13-split-h2` | 24 | 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 37, 39, 41, 43, 45, 47, 49 |
| `scoring/p18-imp-ea4bc955/split-h1` | 25 | 0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48 |
| `scoring/p18-imp-ea4bc955/split-h2` | 25 | 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 37, 39, 41, 43, 45, 47, 49 |
| `scoring/p18-imp-ea4bc955/split-test_mod5_4` | 10 | 4, 9, 14, 19, 24, 29, 34, 39, 44, 49 |
| `scoring/p18-imp-ea4bc955/split-train_mod5_012` | 30 | 0, 1, 2, 5, 6, 7, 10, 11, 12, 15, 16, 17, 20, 21, 22, 25, 26, 27, 30, 31, 32, 35, 36, 37, 40, 41, 42, 45, 46, 47 |
| `scoring/p18-imp-ea4bc955/split-val_mod5_3` | 10 | 3, 8, 13, 18, 23, 28, 33, 38, 43, 48 |

## 5. Verify

Peel §7's fenced block into a `shasum -c` file, fetch the staged ref, and check:

````
awk '/^```sha256$/{f=1;next} /^```$/{f=0} f' \
  training/reports/_finalist_eval_raw/MANIFEST.md > /tmp/slate.sha256

git fetch --depth 1 https://github.com/dkdan10/AiLibi.git \
  refs/heads/evidence/raw-slate-staging
test "$(git rev-parse FETCH_HEAD)" = c27ab7b5f5e7e10bfab5c6dc752362b137862cac
mkdir -p /tmp/slate && git archive FETCH_HEAD | tar -x -C /tmp/slate

cd /tmp/slate/finalist-eval-raw && shasum -a 256 -c /tmp/slate.sha256
````

The same block checks the owner's disk from `~/ailibi-campaign-1826/`, and —
after 19.22 folds these bytes and retires the staging ref — the evidence commit
restored by `scripts/fetch_evidence.sh`.

The hashes were computed from the owner's disk and then checked three times by
this task, at **1,569/1,569 OK, 0 failures** each: against the staged
copy, against the tree extracted from the staging commit, and against a fresh
**anonymous** fetch of the pushed ref (`git rev-parse FETCH_HEAD` =
`c27ab7b5f5e7e10bfab5c6dc752362b137862cac`).

### What content-addressing buys — and what it does not

- **It buys:** the exact bytes behind every §16 cell, hash-pinned, so a reader
  can re-derive the flattened rows from the events, audit the stamp==sidecar
  claim game by game, and prove the recovered bytes are the recorded ones.
- **It does not buy reproducibility of the recording.** These are real-provider
  (Featherless `Qwen/Qwen3.6-27B`) recordings; a seed alone does not regenerate
  them, and the recording *is* the determinism boundary (README, the
  reproducibility scopes). Preserving the bytes is what makes the lineage
  auditable — it does not make the run re-runnable.
- **It does not re-open any verdict.** No cell, table, or ruling in
  `report-finalist-eval.md` moves because of this recovery.

## 6. Not re-recorded

Nothing here was re-run, and no re-recording is scheduled. The slate's price is
recorded in §14 of the report — a **58.705 h** span, **57.1589 busy hours** —
and Phase 19's charter names and declines it. These are the original 2026-07-29
→ 2026-07-31 bytes.

## 7. sha-256 — every one of the 1,569 files

Paths are relative to the slate root (`~/ailibi-campaign-1826/` on the owner's
machine; `finalist-eval-raw/` on the evidence ref). `shasum -a 256 -c`-compatible,
matching the `recordings-manifest.sha256` idiom under `training/artifacts/coevo/`.

```sha256
b128c6adaa11ae1866bb587dbc5f170ae66c5945f23a40395a1dd23ab79d5d5d  ./AiLibi-18.26-owner-brief.pdf
9e4fdff525f99ab4bedb8b7534430b23acfcf75743fbf894ff6d6388fb3c583e  ./assemble-row.py
57352ec88e36ff203e47f98ef8335c661ee467fe1db13238ac02e5e52c38e230  ./forensics/p18-fsm-comparator-seed-5-063243.jsonl
7b2c26097c9943490534d1008f29647a37b2b268b2d3a2ab251924d6ab4022b3  ./forensics/p18-fsm-comparator-seed-5-065753.jsonl
3e77b3cd39e77ba463415c6346767a41a619ca1712749fe7540fde38dee73c42  ./forensics/p18-fsm-comparator-seed-5-071804.jsonl
830011cdbb7a1258b092bf73ee795710ca8a778777500c0bf38e0927ad91d400  ./forensics/p18-fsm-comparator-seed-5-074141.jsonl
299f411889d46b04446936101c685ac3b692b7e266ce312f047b539289fc9a9c  ./forensics/p18-imp-7f73929d-seed-35-064353.jsonl
fb1812967697fb02d604a08a5048bbb10fdc5d9109967fe540358b1ffd009608  ./forensics/p18-imp-7f73929d-seed-35-070939.jsonl
287c396faa4e1388dc821025559cb04c7960d4d2081fb7129ced328869ac87ad  ./forensics/p18-imp-7f73929d-seed-35-072947.jsonl
260352de12ebf67af4c8a0ca3968051ca5bea13539f6f5eaa3c49b881d455e53  ./forensics/p18-imp-7f73929d-seed-35-075415.jsonl
856d0b5776e3a5409a15650c3593e754723aa4f8dd35a940cee7dd08d294944e  ./forensics/p18-imp-7f73929d-seed-35-082204.jsonl
a51843191bb2ccd0fd5cf30ed70c2f558ee09320d91fa71d4bee5cfda180e25c  ./forensics/p18-imp-7f73929d-seed-35-083309.jsonl
db47e247e61963416349c6140ee1b5fbfe51f96e6d1bf6708a2410791cb8f479  ./leg-log-p18-crew-c1-gen0.jsonl
21e3534e7a75dd02766a353c5b4463344c0bda1f353d82554efcd9b49f427d2d  ./leg-log-p18-crew-c1-gen9.jsonl
b5c8d1729e0a7f20519611d0ee04bb21751e808c5bb446d71ea9f7b596a5613a  ./leg-log-p18-crew-c2-gen0.jsonl
cb7c964ddf556e1576cf0acb5b8f96604f89b7720ef65b8479dffe501f3b7297  ./leg-log-p18-crew-c2-gen9.jsonl
0453b057e1e028e222de62a6a3c81bd2f28faa38f4b3e441a0bfacc6755be3af  ./leg-log-p18-fsm-comparator.jsonl
f2ec1deaa4c78549b98049400c5b6d07f1c977a12b3b654cf0536c59b9ef4dc5  ./leg-log-p18-imp-6d327dcb.jsonl
fe20fbf105427a17c6b6bcb35dd27bf5af7d262163510f6a62bad39affc9e7f8  ./leg-log-p18-imp-7f73929d.jsonl
8768da7b8bc1ed0d3f26180d141fd28e404538afa10f41bfd607ea405abaa41b  ./leg-log-p18-imp-bfd145cb.jsonl
0c3875e86481d18c182fcec02be459b8a32607c0aa8e1c6f02ec15141766b868  ./leg-log-p18-imp-ea4bc955.jsonl
65fa5ea75ad805468c1df37328dbd29ce82b7ff07e7029977eb90f5bf3f364b2  ./leg-log-stubborn.jsonl
25e388b2f994905527ef7f0ab19fa9b75fcb74dd7fdb9396de90963e8e249fcb  ./leg-runner-v2.sh
b6b56bc9825e76a5ae49eb110697959b7b8fbad39e02579e7e8fdc7e57f7104d  ./leg-runner.sh
33aabec38d13cff197a206ead5014c03689338c56af6d0c44550ad56c450d9f0  ./make-owner-brief.py
4c431bc6b44859d31a203708e13b6aee7907af362b1adbda978792c57108c103  ./p18-crew-c1-gen0/replay-seed-0.jsonl
c899ce399bdf7f009395c59a8bedbac045e3066efb5e17a2d51f9311f73687db  ./p18-crew-c1-gen0/replay-seed-1.jsonl
cb60f11e7b5bc735494312dfc5c12b0efe17a0c8154ba7b9ec56320e59cb3631  ./p18-crew-c1-gen0/replay-seed-10.jsonl
ce2aa70c4f222a6eb5b3bac27eb711ec0a068f2067c7052e82b93d9555e98d9d  ./p18-crew-c1-gen0/replay-seed-11.jsonl
47df69e73597f7369602bc69404b38128b2b11dac1287df71c7f382049d2ad0a  ./p18-crew-c1-gen0/replay-seed-12.jsonl
e7b4b687cd6318291dc976a0db40a8dd11dba73cbc443397888c23af22ec9751  ./p18-crew-c1-gen0/replay-seed-13.jsonl
e036c84f89de6d2f55fa1eacf2b62f82bae6d7b06cd2f05332aa585440939c7f  ./p18-crew-c1-gen0/replay-seed-14.jsonl
260e135938eec9306df31c62deada561393d8adec87b86f5da6b16ed16afe657  ./p18-crew-c1-gen0/replay-seed-15.jsonl
d15396f8480c97c2be1615b38b2287a76f2f2b5164058e90e2df13444666af20  ./p18-crew-c1-gen0/replay-seed-16.jsonl
9f1a665681e9491bf12fa1591ba92a3c27094dd8cd90d2e503ca386b8dc464c9  ./p18-crew-c1-gen0/replay-seed-17.jsonl
c324f1cc7e41f1d8d513d81179a04ae67571f1de01c604054ed72ee8722d7adb  ./p18-crew-c1-gen0/replay-seed-18.jsonl
2c38a9520443ff46117362d9d1fd7ce89512cec8240a3ee4a03e97312d28c79c  ./p18-crew-c1-gen0/replay-seed-19.jsonl
73910a4852af3b1e5c83d5c91529f1e6deba56a408ad1b519cd2cc2de8184b00  ./p18-crew-c1-gen0/replay-seed-2.jsonl
a8c4fda06555193858b42ad4ed6226712157f7e13300f3f46a12def00a20aca9  ./p18-crew-c1-gen0/replay-seed-20.jsonl
2c9f0e1e369bc82e55acb33d048671bba0fea3671a34acecb98129fcc3aa3652  ./p18-crew-c1-gen0/replay-seed-21.jsonl
6a9d22d67bc45dbbf5ed7d48ac0d3fae63d5097036a90dacacdce78ce2b8270d  ./p18-crew-c1-gen0/replay-seed-22.jsonl
f4b28df3c6ba7e413298480b4ac0e9b014e456793d40466ce14d4b3a73890588  ./p18-crew-c1-gen0/replay-seed-23.jsonl
09e46491c60a839144c5243d2142027ca0bcce0937660996e45b907953413240  ./p18-crew-c1-gen0/replay-seed-24.jsonl
371c29d915efb57fd2865ba2917c16315ca5b9751f84008f605776787c6f58c8  ./p18-crew-c1-gen0/replay-seed-25.jsonl
1a0e13793b1908424dc60ed7202225fbb979148b03dea0fdf20e1fe6b080f7f8  ./p18-crew-c1-gen0/replay-seed-26.jsonl
da1316c6d52bd06683419d33b71a1fc4d4420d8898f27ce57a5cb3c337fed305  ./p18-crew-c1-gen0/replay-seed-27.jsonl
618a2d30021c1590dfab4ce5c7f2f9752a8058b5e7b75f7654a9790c58ba8541  ./p18-crew-c1-gen0/replay-seed-28.jsonl
c705036b8fcf47b3f6f8b7ceecc29b2797cf8658f6bd0a0158bfb0a82542e40a  ./p18-crew-c1-gen0/replay-seed-29.jsonl
ad0a31fffb007802bb23052f10a607206383c8fb7dd39e1c5696ff03c7a3e7dd  ./p18-crew-c1-gen0/replay-seed-3.jsonl
eb4181a10ba887ce8b4825deabd6f7f15dc760bd6e0a0991a3d98d71b6552793  ./p18-crew-c1-gen0/replay-seed-30.jsonl
658d8600d10dcba0de1cb6199b82eb0bf5ab1f79a8eaca8e296e1ac9fb00f214  ./p18-crew-c1-gen0/replay-seed-31.jsonl
219307434b75a97fdcc91801e8a855d787013926aa79873f0be8699cb44f6cc9  ./p18-crew-c1-gen0/replay-seed-32.jsonl
74b68a4f0d401f1c5699616342265405c400700f7c717485e43cdf9130e03192  ./p18-crew-c1-gen0/replay-seed-33.jsonl
0d234fe84504302c0d0b68857e33d5210b60311a0f47ce3605a8f9dd53ac970c  ./p18-crew-c1-gen0/replay-seed-34.jsonl
868b11edac23c5d28bec2e3dbdf9b26cb8d64abcaa8ac36566908fbeea94aa13  ./p18-crew-c1-gen0/replay-seed-35.jsonl
8d15297c08ead79226f2f68471acea580d41f9bec40e97a8cbc81b80dd1a1819  ./p18-crew-c1-gen0/replay-seed-36.jsonl
a172b120c38d9dc2ee501457e7aff4a5065a64465ab487ddb759ff8d3fac49b8  ./p18-crew-c1-gen0/replay-seed-37.jsonl
3ef9ce42be729ef4b87722608a80de712a335ecc5ff53f2de5060e6c578a69d8  ./p18-crew-c1-gen0/replay-seed-38.jsonl
59d2e95dcf79ed0a53d9d15bacb43d41cce0afc9c522458b1fc584be27960868  ./p18-crew-c1-gen0/replay-seed-39.jsonl
395cc2794e4df47dcd0256b8c63600b084dbef6328c5e4ef57cd567f65a48090  ./p18-crew-c1-gen0/replay-seed-4.jsonl
0bd4aa6d20b83fc71b43434ef36f7e6ee9d37efa5049803cfb8dc49af56d284d  ./p18-crew-c1-gen0/replay-seed-40.jsonl
f421bb77ca76d3fa481aa0b4a290b59a03ea0dab831a0c4a5a1eef144c0cf199  ./p18-crew-c1-gen0/replay-seed-41.jsonl
9c272d36402266c0dbb5dd416bef40c327732767ba5795e70a88dee26965671f  ./p18-crew-c1-gen0/replay-seed-42.jsonl
3fc2afb020730cac1fd6d8c4f41ee0ed42c2c2693d2fc35e4588df8c92b09166  ./p18-crew-c1-gen0/replay-seed-43.jsonl
f6f0623325a5eb483a846e6ce1e4546234df5e9b2b0d30096e28bc036e060840  ./p18-crew-c1-gen0/replay-seed-44.jsonl
a98c248d9f964a1f9af13f02ebcfc46e7a7dbd2c4b31a40168a9f22a48a3b5a8  ./p18-crew-c1-gen0/replay-seed-45.jsonl
dcefd7a10fa1f35846dd6f0cfb175a078cc3c53b06dd23847064b83e30f4745b  ./p18-crew-c1-gen0/replay-seed-46.jsonl
e27f760838568ca8df1cc310bf488738dd9734966d6182e372ffa7bc52f004dc  ./p18-crew-c1-gen0/replay-seed-47.jsonl
315d8dd19f89d75782129ed5b9384bb0d7be46872d811ee8d7b5d758d0abd755  ./p18-crew-c1-gen0/replay-seed-48.jsonl
64d09dc6312dc687fc006f792b0b2fdf28650f84771beb62299eb41e56056819  ./p18-crew-c1-gen0/replay-seed-49.jsonl
b3bf91e53214bcd2cb84b892f4f9d99d8b3f60cd90a1c8c3ee65213b1fa969ef  ./p18-crew-c1-gen0/replay-seed-5.jsonl
90d7aa7b336e94521fb041927bebe3132a635ec9e097c9adf7652575c53ac255  ./p18-crew-c1-gen0/replay-seed-6.jsonl
8014bb4b7d8d678a7e61c12efb7039be10cbfd3a272b54b2a910c16e1d720c69  ./p18-crew-c1-gen0/replay-seed-7.jsonl
0659b387209236ad4f4b143f352e783e81f9f67858a6f2e2ab2cb9e4984bab83  ./p18-crew-c1-gen0/replay-seed-8.jsonl
7f7d4823b90e09748c7a91233f39e9fec2846b605b389e8ffedc73f6ebc3ecb4  ./p18-crew-c1-gen0/replay-seed-9.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./p18-crew-c1-gen0/roster.json
220872ba389fd94f80cda892935bcc70073c4386796c259b8b7ac6ada9981c8b  ./p18-crew-c1-gen0/tournament-eval-report.json
628ceeac4157a5e613071a5ab29b04199de6985fcb615b6e6db5c90541044a74  ./p18-crew-c1-gen9/replay-seed-0.jsonl
261fa4cf00f5c0883e1139abc95821000b01bf796c63c4e6985edfc3d2de3106  ./p18-crew-c1-gen9/replay-seed-1.jsonl
6d4f1487ab006d2fef95e066be06608b37c6d021c937035fcb46e5d15e022b53  ./p18-crew-c1-gen9/replay-seed-10.jsonl
f0a4590a1c30ccd90d417d4ffe3a29b5d05c5669f91237629c6a9e7dc2bc7294  ./p18-crew-c1-gen9/replay-seed-11.jsonl
83403e51a00ce101a08f225de53744d53ae95b38a846d76f774ab0576c4d4336  ./p18-crew-c1-gen9/replay-seed-12.jsonl
eca40800658b5a429922895878564fb4b262100b03ae52f76ffba93401d5c3b1  ./p18-crew-c1-gen9/replay-seed-13.jsonl
b3f9c697e6d4c9e2b7f2a4ed4217d72fea5fa5ab81b5c1f16c49b5676157381a  ./p18-crew-c1-gen9/replay-seed-14.jsonl
6883b6f3f25205a77b602bbdb91c9a4b660b0b45f1383bdbe0c296ca0c64e975  ./p18-crew-c1-gen9/replay-seed-15.jsonl
9f74abe9bcd88347840a6c1830d83c2f650448d80485a552d9c4c4ec56939884  ./p18-crew-c1-gen9/replay-seed-16.jsonl
025b75fe33bf17a6715c79d549184a37625ac43217951b940f00319e3318385e  ./p18-crew-c1-gen9/replay-seed-17.jsonl
42587e2b262cba75ecbbffdb3adeb170483d44fa5084a0e318b8a20a59fa6c18  ./p18-crew-c1-gen9/replay-seed-18.jsonl
eb13086a7d272b5ec5f99e4063bf53e80030a35ba6bdf2c51ba39c8059aaea61  ./p18-crew-c1-gen9/replay-seed-19.jsonl
4c5216459cb0e01f7b89956ac2c8f4131b4cac1e04d4bb5d0e4e7f80d9f0bfc5  ./p18-crew-c1-gen9/replay-seed-2.jsonl
44b0f264b1b5d40ca68461f487599dae161df175af3e5d767291ed8742487243  ./p18-crew-c1-gen9/replay-seed-20.jsonl
e587ed24d2f489178a74efec14951ac0884ff1e2461051dd3176714da8ebad2c  ./p18-crew-c1-gen9/replay-seed-21.jsonl
c5a320bb9df12555d264ddf7c1d18854ed7965d4735bb84b3e75e0bfcd45e2b5  ./p18-crew-c1-gen9/replay-seed-22.jsonl
c5298d112e081f436dbc16b7fc1b48ba9c7d13783aa8122174a88fa192654296  ./p18-crew-c1-gen9/replay-seed-23.jsonl
d795f93605fb73bad682931fba20e74f5c174b36e9410279a25be57612fae6cd  ./p18-crew-c1-gen9/replay-seed-24.jsonl
d02527a57aeb2f6f1c7c7b7e1f9527c5af8195dcec5421a13caf967e686229a8  ./p18-crew-c1-gen9/replay-seed-25.jsonl
e5f8072b6d8e6e4498aa6ef79cbaa4b320ed8ce29b4fbe549537d5bf72a4524c  ./p18-crew-c1-gen9/replay-seed-26.jsonl
a5dba0ee0a2fbb11a07022527c808911c56f35aaf7179f48ef0d52bc1edfb707  ./p18-crew-c1-gen9/replay-seed-27.jsonl
8c0db1cc62b3512ed7c040c5a4a892790b7fae9e680b473dd1df4d8b19c95ff2  ./p18-crew-c1-gen9/replay-seed-28.jsonl
3bce536d427480f8601f74a7f7e752917c4ab4a789ca32b1939f44d16b829b23  ./p18-crew-c1-gen9/replay-seed-29.jsonl
364576387206b83be9ca5ca4c75a4f909abe241157a35429bed7e937b10ba2c7  ./p18-crew-c1-gen9/replay-seed-3.jsonl
ca2b01e5571dde53b7070e4997d5e814a9380a041eed9348424b72bdce754580  ./p18-crew-c1-gen9/replay-seed-30.jsonl
5fd2b0c532a72b2073f7aaa4f36727dfbdad82aedf2aae8e479363295138bddc  ./p18-crew-c1-gen9/replay-seed-31.jsonl
a8411ac71a6d225a9a735cf4d5e0675c15800c646b12f54015cfcabd2f2a154c  ./p18-crew-c1-gen9/replay-seed-32.jsonl
ccd115dc1fdb2a14c84251ed530c2b530e3955ae1b74401a208cfcdb1dbb99c0  ./p18-crew-c1-gen9/replay-seed-33.jsonl
4bf028d66a502278ec920af2620b83c4f1d4667f888ed3d77fbd13275c7fd140  ./p18-crew-c1-gen9/replay-seed-34.jsonl
be181bc6e3e6d2848fd82b2477019ea73a56a4c2b6af0a73b301210ba7e7620a  ./p18-crew-c1-gen9/replay-seed-35.jsonl
6b89f4fe912c775104d5bbde41b2c7ce398bdbf9e8377346f1b7e325a337c3b3  ./p18-crew-c1-gen9/replay-seed-36.jsonl
9ca2d3455474b30df94792fff755a5818397bd64295f8e487ab49908c6d2dfdf  ./p18-crew-c1-gen9/replay-seed-37.jsonl
9b3d4822230a6dd9d12bb6e420d4659914308bb560bd32ae96488ee25d7a6ea3  ./p18-crew-c1-gen9/replay-seed-38.jsonl
ba46956524d601a07b2be50a599ee40a49f9b71e9ca4e26cd3d5ba3e1eb0787e  ./p18-crew-c1-gen9/replay-seed-39.jsonl
52ac73b183b918578e83c557371538211eba4d21d38459d9e74ff6d208c8840c  ./p18-crew-c1-gen9/replay-seed-4.jsonl
1cab2088125087553d622bb062ca293803d4ae88f2873d537228775c47097b33  ./p18-crew-c1-gen9/replay-seed-40.jsonl
89e796f966cef7ded2d4b74d1cf839a064d1b9476ebd24eba41c49b8965aed62  ./p18-crew-c1-gen9/replay-seed-41.jsonl
2e820472506c831bb21d53fd13c70ea9ff729397e38aa41d04d8b84e3f01b1f8  ./p18-crew-c1-gen9/replay-seed-42.jsonl
65bbd53d601fbf45a14a88e2f93d41130db508c60d860eb3db94d74aef2bf87d  ./p18-crew-c1-gen9/replay-seed-43.jsonl
852167e7d08940e177d27c1d7293611ff1018bc4cf82487c4a8fee4984a6e73d  ./p18-crew-c1-gen9/replay-seed-44.jsonl
d78a7e0c0a168f04a9381b51d6f0c85d8b0763c3195e528161edd30529f0a252  ./p18-crew-c1-gen9/replay-seed-45.jsonl
d12458805a6518ce2e58258616dca0732c3a1d9bb9558ed6f889a4d7b89f6516  ./p18-crew-c1-gen9/replay-seed-46.jsonl
c97775c7e698d271b92d8bdd38aa7d6275c352c01b50f3b21533eca6c76206ac  ./p18-crew-c1-gen9/replay-seed-47.jsonl
fe0b376cf71b6cda73b0dcc96162c27c8174a9ae0228c03ca902ad6e7f16af4e  ./p18-crew-c1-gen9/replay-seed-48.jsonl
16da8c210efbffa8255260361a14079da41b7702978a62267a4775688b71ab57  ./p18-crew-c1-gen9/replay-seed-49.jsonl
8d8ea580317329baea21c674322793ec64b808a42db17f0320f959d212e0a6c0  ./p18-crew-c1-gen9/replay-seed-5.jsonl
1f8311e074b3083940e79e5036ed4919abf0b32f469be44d75c9ced009a76512  ./p18-crew-c1-gen9/replay-seed-6.jsonl
5e03987b699ae8d504cbcf72f8822785a6e927cd371420fe889eba0d732200f7  ./p18-crew-c1-gen9/replay-seed-7.jsonl
e93d56780fb18d976aa1664b209cf021b2ed6930c3d35780a9e65f9115a4ce5b  ./p18-crew-c1-gen9/replay-seed-8.jsonl
84aab6d1598e14c2fd418fa397f83cf546bab692b5f3203f917b61462ceb7d33  ./p18-crew-c1-gen9/replay-seed-9.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./p18-crew-c1-gen9/roster.json
d5ca27fa5e65514894082f4672f79c41b85ddb9a606b60afdaf9784decfe6f30  ./p18-crew-c1-gen9/tournament-eval-report.json
b6310ccae3301225e2c023b354f8fdfad7758e05ef53a475dce365b79eba6f95  ./p18-crew-c2-gen0/replay-seed-0.jsonl
17343b4152cb8537201387ed52748bbb9fbc394cc7f061c05c2416a14052f394  ./p18-crew-c2-gen0/replay-seed-1.jsonl
4aa89b669bf13e27cb70640e98849cdf1c4dd1720549b6d61fa8bf4930cf2f4d  ./p18-crew-c2-gen0/replay-seed-10.jsonl
456cc3b733f23fca9179f24811a484a870a6f57787691b20b95739996c729d39  ./p18-crew-c2-gen0/replay-seed-11.jsonl
94a9930a1a68ffa7477dd6e2fe7c48ac3e12855f4eed9bf1243fceb9669f1037  ./p18-crew-c2-gen0/replay-seed-12.jsonl
82642222d229b5de3a4cf5278a130bc540d434f2e6b2ff8768d9a5379940b69e  ./p18-crew-c2-gen0/replay-seed-13.jsonl
5eea216c263c4abab34dc4d6e3856a8cc68fd1a1017ddf2de63e4fafb80c83d4  ./p18-crew-c2-gen0/replay-seed-14.jsonl
811b79c9801b9ef23e190bc51d53f3018cc7cad3445cd6490bb6f8fd06921ce1  ./p18-crew-c2-gen0/replay-seed-15.jsonl
8740e777a09a25a3969d8e0b126fe9ff4201e3f18e237a87bf84c22ef822ed84  ./p18-crew-c2-gen0/replay-seed-16.jsonl
4fde29336c97359996d5d8849543b95a49513ba8cb293668292d27475a6a5f58  ./p18-crew-c2-gen0/replay-seed-17.jsonl
7574eac11de92deff10078bdecb525b9b97649b918ea3117d8bd78ddbde3deee  ./p18-crew-c2-gen0/replay-seed-18.jsonl
9f05fe1da83bef548df17c5dd63e7c0f4c3f36e5c2fdfa2bc09392c2da608e07  ./p18-crew-c2-gen0/replay-seed-19.jsonl
5d0ad7c56177b9f8d52921e15c534ba011e50115f97a73d605e76674b57bb174  ./p18-crew-c2-gen0/replay-seed-2.jsonl
363f2eb9aa992d6ec5a00a90de43fa34b67b4d55bb9cf1a767e4332e5275991c  ./p18-crew-c2-gen0/replay-seed-20.jsonl
8e4c667f389cd1f0fa098f47b46e79207ffeb0ef34a52924ba5b8200045abf54  ./p18-crew-c2-gen0/replay-seed-21.jsonl
0fe9b848f679074a5d7fc047a000086f1f3c0afff49ffc3d98fd9abe7518fd80  ./p18-crew-c2-gen0/replay-seed-22.jsonl
9dee071c3c870cf77720b3a4cbdb941a33be9ffad76ed0b2e14cbf552f66d29b  ./p18-crew-c2-gen0/replay-seed-23.jsonl
380fad8511e4a0aeecd9c276c0dcd6ff11f4fd3cd12c834ffb1a0cb5cb870a5e  ./p18-crew-c2-gen0/replay-seed-24.jsonl
74f26f216fce98d87dcea6e18c487fc2587eb342ebeac42a3385b740e1b963e7  ./p18-crew-c2-gen0/replay-seed-25.jsonl
9938bb1c176c6909a25db58c415491ce8c2a2e5fccd31d4c4b91786ea7cde973  ./p18-crew-c2-gen0/replay-seed-26.jsonl
f617540a9373c230555acb55aee33c50c4eac853e3bb25577855051070697d44  ./p18-crew-c2-gen0/replay-seed-27.jsonl
25bc71e2c9c7b0af8fb280d5e15b1a661cd452948a679689f5d52b990a0446db  ./p18-crew-c2-gen0/replay-seed-28.jsonl
575cd5da8b46993c3b687c4da261fa2eb945fc7c6848da53cefcb20726b00834  ./p18-crew-c2-gen0/replay-seed-29.jsonl
2f2092b2306deb957f52e29e0a1cca622bd8b09292a9d3fabadb2b80dc498a3f  ./p18-crew-c2-gen0/replay-seed-3.jsonl
2e23665cd0bd930d20667749ff7a96eebe069b93f6874fa369f3f3a17bc527f7  ./p18-crew-c2-gen0/replay-seed-30.jsonl
89c3fa5b49db9d73a06c8bff3595c6a1a6d95d00901a2f45b07262743c255bf0  ./p18-crew-c2-gen0/replay-seed-31.jsonl
3f9b6a620e8001a36d6288044c8328a85c026a79dc51eeca3c97aa87b94274a5  ./p18-crew-c2-gen0/replay-seed-32.jsonl
f7368c95a273593fa1b4f8fc1a46c761509e6ca7d247df749609f4ea0f410d3a  ./p18-crew-c2-gen0/replay-seed-33.jsonl
3f8e14d402f606f2ebe7d6dc8fad94a6ec432d559b80469540a82e7a4712ae91  ./p18-crew-c2-gen0/replay-seed-34.jsonl
5fbfd715e3ca1f4d5db45db62887bb416db795e4ba42525afc17cf7c588cc3db  ./p18-crew-c2-gen0/replay-seed-35.jsonl
e75b7f9df0863479c9be76509f9f481b373fb096df7e981533b56c5a0e4e790b  ./p18-crew-c2-gen0/replay-seed-36.jsonl
1a271f7478c920e875eb1060a1ce21fe17fef6fa2f3bfb397f29308472ed2e97  ./p18-crew-c2-gen0/replay-seed-37.jsonl
50ff639adbb1e21ab47fdcf9763965be919cbe61ed5c214087c53e332367ae13  ./p18-crew-c2-gen0/replay-seed-38.jsonl
6efb757ed31f87a96e849c4e33c7906352474a69577f3af86f28536819a7d92e  ./p18-crew-c2-gen0/replay-seed-39.jsonl
1ad4d12b611132934aa10862254c4720b17f791e8e1e3af5c0a80744c604aff1  ./p18-crew-c2-gen0/replay-seed-4.jsonl
4cf022d08715dc41f055ed8f1b4e7692b2aaac4d3b5041102778239451611ab0  ./p18-crew-c2-gen0/replay-seed-40.jsonl
b533f91c571baab433e6d263e741657edd07ae0f01f27d1ec5731e4a11a6babf  ./p18-crew-c2-gen0/replay-seed-41.jsonl
505d00269eb5f67b428ef2a16092b9f8f08a9628b4042913a8aca34ba3f2b671  ./p18-crew-c2-gen0/replay-seed-42.jsonl
75aadcba5f06918bb687e902b3ef803b24aeca92cecd3202ca8ce244bee96f25  ./p18-crew-c2-gen0/replay-seed-43.jsonl
c40bc94f973e2d2d35bda097060ca36d06f3a566333041db4d6a6cbb6fbc3d4f  ./p18-crew-c2-gen0/replay-seed-44.jsonl
ed6d53f3be8010db02ac9da56896fadb424222a996749ef312482ae27fb4ee9a  ./p18-crew-c2-gen0/replay-seed-45.jsonl
2920d65247b97336a997967337b9381ac222156f825b07e975b3ed94ef5c4441  ./p18-crew-c2-gen0/replay-seed-46.jsonl
a47a430554d0b64eea9099b92115f5a56a2ee7e3178b0bf27ad741c7f5832fb0  ./p18-crew-c2-gen0/replay-seed-47.jsonl
dcf248ce62928e86a82d2b2d23ded81b82bcfd6272cb9a528dba164554bc6715  ./p18-crew-c2-gen0/replay-seed-48.jsonl
3957b18741900e548d4e93342758b9094e778e17a2f33df927c16704ce52eb3c  ./p18-crew-c2-gen0/replay-seed-49.jsonl
4fd1079637cbb5db5d21194211898af5e8fbc277e135cc968cc7d59abfa9b970  ./p18-crew-c2-gen0/replay-seed-5.jsonl
fc073e54531db4201ee048da175bc06352e886a6a3844ae2536b83544b673073  ./p18-crew-c2-gen0/replay-seed-6.jsonl
2d1e1869c0c012f51fd85234a7541eebc60271b98af5d48562deb40ccd83ef41  ./p18-crew-c2-gen0/replay-seed-7.jsonl
8598969726987789d9741392ef07df02e33a55ce53d21b9f49a3ab1ddf2f8925  ./p18-crew-c2-gen0/replay-seed-8.jsonl
22542b15edf33b556abb036276d5dcfeeb513373238b6a38cca3247be3a17f68  ./p18-crew-c2-gen0/replay-seed-9.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./p18-crew-c2-gen0/roster.json
1741ad2a4b6c2c7dd06537d8610710505e86399a5403f86ef471833ac523794c  ./p18-crew-c2-gen0/tournament-eval-report.json
9a6960c4280d7abb5f58ceae4c3756ea49421a3a1fae2c2c022e0e187f125449  ./p18-crew-c2-gen9/replay-seed-0.jsonl
d1852e6c906314a3df1f86e28c23ef16e6a2e3d9947033559f277d287af74d9f  ./p18-crew-c2-gen9/replay-seed-1.jsonl
66cfd3561809b6214a07c8f0d5e5586af513cc1f84eed9c731ec78b0b46606ab  ./p18-crew-c2-gen9/replay-seed-10.jsonl
9b57e1df7f5bc354c075c5a3a5c1481aa4383854816a893969fa9890efc08cef  ./p18-crew-c2-gen9/replay-seed-11.jsonl
5eeadec38468ebe7261b700f6bdf9124002f1dc4116f854714177a017586df49  ./p18-crew-c2-gen9/replay-seed-12.jsonl
a9d7fd41e6ad505af01093725531e6ffe9beeb07759a943c2e156269498a8baf  ./p18-crew-c2-gen9/replay-seed-13.jsonl
a7e52f6b10a8a8b146a50daa11cce389f6252a0a14bb0b07c4b57b494745543f  ./p18-crew-c2-gen9/replay-seed-14.jsonl
cfd82f19653bad1e4bb625b64a84690f37b0deb0208a286b414fe1c02bb1ce41  ./p18-crew-c2-gen9/replay-seed-15.jsonl
079e2d2640084ef8b8d99c0b0657385460d8f4dffa4ff5be34c2cc7b6969dca1  ./p18-crew-c2-gen9/replay-seed-16.jsonl
0e4421225646779fc7d11c609769d041d9c4c21872fa72ffa36a23f6bbee17fa  ./p18-crew-c2-gen9/replay-seed-17.jsonl
61cdc2157d8dc391ba521f376338dcab3df232d01fa86ad27e35c796eaad2f1c  ./p18-crew-c2-gen9/replay-seed-18.jsonl
fb3758a39770216b4fadc3e120eff21fa5d8684015b02d487503a9233add7447  ./p18-crew-c2-gen9/replay-seed-19.jsonl
fd2dfd1647abc080d62b239d7938d2ab5c1169e5b3629dfdcd22eb399104adb8  ./p18-crew-c2-gen9/replay-seed-2.jsonl
08b8fc03f105fa3f9c597c32bd2aef6999b91d839cf693d308d97790208c5eaa  ./p18-crew-c2-gen9/replay-seed-20.jsonl
76399ba8b2ac15e0cfe62b90e743d311fbf212134501b9b52bd3fab443be6f72  ./p18-crew-c2-gen9/replay-seed-21.jsonl
c428eb6cb1e93f04fd0d429acc257c21cf19634b9dd09dc09900d7c17322cc60  ./p18-crew-c2-gen9/replay-seed-22.jsonl
d89501d01026464aabe2dd1ae80cacb621437652a80131851e76bffc6ca8abc3  ./p18-crew-c2-gen9/replay-seed-23.jsonl
21f283f8a2806fe374cfbdd8b2a96730324cbc2fe1a4ddd3798e7666c725a79b  ./p18-crew-c2-gen9/replay-seed-24.jsonl
ca8791880e1946b26d8fb270aebbab7e1297473c69c5b4cf68e61fc840a29b0c  ./p18-crew-c2-gen9/replay-seed-25.jsonl
0e17eaf619e74aa99899b46acac16ccca76b8b553e493d117e7f5f9500fa2b3d  ./p18-crew-c2-gen9/replay-seed-26.jsonl
e53dd04ddd915a2a0513d947ae0601545c4396d54a226559dc649fbe75d8d2c6  ./p18-crew-c2-gen9/replay-seed-27.jsonl
676fe341a19895c0fc03ac306bc30f9f70fefdba6670cea0942d98c4606aad60  ./p18-crew-c2-gen9/replay-seed-28.jsonl
dbe514fee1c08fe4f2c785b5bfe016591fa2163729628a2d6ad6f9becdd861fc  ./p18-crew-c2-gen9/replay-seed-29.jsonl
9f2db5a7277d09826a045780d5fec2e0614786db8e04f3758a0957f05e183b5e  ./p18-crew-c2-gen9/replay-seed-3.jsonl
b99f9edfb81b6a3127c86778f2b3221af80afeda05552d51ee4ea592a8491958  ./p18-crew-c2-gen9/replay-seed-30.jsonl
05f9253f3476cf3fc8a89d7ae9506898f7d8ab430c426e86c80bde17389d595e  ./p18-crew-c2-gen9/replay-seed-31.jsonl
be73316b0ac402da0d5e06d9ad3a349cecd7d4e761d178df113c9274ab63ed1f  ./p18-crew-c2-gen9/replay-seed-32.jsonl
444f76ef13f29d37b9df5583109935efdf5c457bbf958edbd3f0c2a8625e73e0  ./p18-crew-c2-gen9/replay-seed-33.jsonl
85e7eddd66b3b5c96a9a0b4640c65d0ec8b4e4984b6a2eae7e7f81c3139ae5bf  ./p18-crew-c2-gen9/replay-seed-34.jsonl
469653651c5903aebbb4cf8d27ec350dda8403aea025d4bfa644ae9bb686f814  ./p18-crew-c2-gen9/replay-seed-35.jsonl
f0ecdd85813a218b78574325c74bf1beec7e87eb3dc7c7e8ea30aaabdc524145  ./p18-crew-c2-gen9/replay-seed-36.jsonl
1d75bae75a2e735d41a7f26895f44ce1b0460a04d7a7acce882e2528e665195f  ./p18-crew-c2-gen9/replay-seed-37.jsonl
96cd5521d911b4a1ab47ea6a00c09ef7376e87a6b9fd13417043149cff7e71fc  ./p18-crew-c2-gen9/replay-seed-38.jsonl
f5bb6e824076ce800af554eebb47ed5521175c284116950505c0b757344896d5  ./p18-crew-c2-gen9/replay-seed-39.jsonl
e664f68c3a7f528ae2471e51dfe8803283626a5abbd7be79455b701dac353dfa  ./p18-crew-c2-gen9/replay-seed-4.jsonl
1ca5fc740849f5c4753fa9aab21c683aa7b9df83ffda1cc56ae83bb378cfec9e  ./p18-crew-c2-gen9/replay-seed-40.jsonl
150fa268b078dfdd7900b57939ba77b00cb3370bb15fb258a69f04abfe54ea82  ./p18-crew-c2-gen9/replay-seed-41.jsonl
b390d57babe4a16104f8774a02ca57a00f69112d89dbdead4b4ff52bda9a562b  ./p18-crew-c2-gen9/replay-seed-42.jsonl
19df8f2ba6a79da852411fb02cb088e76da1657a877ead24e725e4ef52085977  ./p18-crew-c2-gen9/replay-seed-43.jsonl
52fab37cadf08cb4a0a72986c1deb3f5cc00662da32147ed297f731b5a99a96b  ./p18-crew-c2-gen9/replay-seed-44.jsonl
5eacded9d45e702db0091d72f6b8a4439e617de6859032674273be645a4c1502  ./p18-crew-c2-gen9/replay-seed-45.jsonl
a79feec0c53533f965963d15f78fb92b42db3c51be23b3a65754edbf70592e1b  ./p18-crew-c2-gen9/replay-seed-46.jsonl
f5f9e58a4777f7d2ebde0f88e4d5cf9d2aef546b78fb24df77e0c83b44215c56  ./p18-crew-c2-gen9/replay-seed-47.jsonl
5170814ab9511845c6dfd03d9a7fc46ac22b57e7bfd26eb5e46f52728559386e  ./p18-crew-c2-gen9/replay-seed-48.jsonl
6b7b6d3e25029c87d30c0c58c8f76252da0ec6f558f4799ec00588a36c6d21c0  ./p18-crew-c2-gen9/replay-seed-49.jsonl
09c9b8d92707a4ebad9a10de04fab54ee6953e67556ec374e828e875f18e927d  ./p18-crew-c2-gen9/replay-seed-5.jsonl
cc9701eb6ca3ae90d5f54edd6b2cd5d110a3f6402253958dc019523b2141893c  ./p18-crew-c2-gen9/replay-seed-6.jsonl
a190865d62b2f45c3ea59643e7cc02b3a7919d2e93f0179b2a879eecabbd1344  ./p18-crew-c2-gen9/replay-seed-7.jsonl
66977c7b55f2b6e8db2e35c760282410dfb031f8068b2d2db9f9c44aaab0429a  ./p18-crew-c2-gen9/replay-seed-8.jsonl
2548fae8eef79fd95ddce311d26ebeebcbae6348c05fd6c4d972a8a7714eb617  ./p18-crew-c2-gen9/replay-seed-9.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./p18-crew-c2-gen9/roster.json
a9201a510844941d3eab0a157686e0d90f012b329db1004c242a89d61fe1665a  ./p18-crew-c2-gen9/tournament-eval-report.json
a4a198f32cc879edf7cad6cfd1c606366b6761ee4dd41b0be9ce27672b59da67  ./p18-fsm-comparator/replay-seed-0.jsonl
4db39da6097c9cbc4434a38105437a7208c4784978f4b65efa6310d9a6486019  ./p18-fsm-comparator/replay-seed-1.jsonl
0fc14ff5c929cffd06abd2d40e9b62a792a24fc8f6480c18c677c51b50505a8d  ./p18-fsm-comparator/replay-seed-10.jsonl
7dd3af1b7f24878d2088911d4312e250b6f54bf952cb1d7f1d67b6d041898b1e  ./p18-fsm-comparator/replay-seed-11.jsonl
e0565d5744b2572d8a67a72385139110227a01f0881ea9761430104fda122c30  ./p18-fsm-comparator/replay-seed-12.jsonl
b4bb47866112cb3f32b9a7413db7f8eea11d54f37688494c24bac18ccec260de  ./p18-fsm-comparator/replay-seed-13.jsonl
1139056200b358c11a95fc127853bf0276a0d02dd06b5807b42cd78116761e92  ./p18-fsm-comparator/replay-seed-14.jsonl
fd54d31f4cc73521dcb8f0d8d32e279c4c738a564d65235e037bc5bd19c3241b  ./p18-fsm-comparator/replay-seed-15.jsonl
aff8711916c03271c2317a777d98e9bf5a4e608c88a2e4e8f2ea8ca57c8929f8  ./p18-fsm-comparator/replay-seed-16.jsonl
2e9b5a7fef0e06223308e582d771686d09b30ee4bb7113945805a1b25b72f40f  ./p18-fsm-comparator/replay-seed-17.jsonl
293701dfdec60b3da5a6134113dfd3a94d71a47fc9bec365c4899aa89284e0a0  ./p18-fsm-comparator/replay-seed-18.jsonl
003014de64fedcf2b8dc46371a75c2edd47829ae658ca70570c2043af6f77729  ./p18-fsm-comparator/replay-seed-19.jsonl
1b5c4cc018016464cbe31310d625ba6fbef96862c5e22ac9dc76304e777f5337  ./p18-fsm-comparator/replay-seed-2.jsonl
d4a98ad2d2685e057777acaf5e1331d495a3222d720def4c83fb44e80d484961  ./p18-fsm-comparator/replay-seed-20.jsonl
d28082087ac008f8563a1da9fe87d4989f044363caf5f8d2c892fce2ae7921c4  ./p18-fsm-comparator/replay-seed-21.jsonl
57dc62c1eb142e6ed78c77669ea148ffbc6790e55f2f66888ab1397be7fdef57  ./p18-fsm-comparator/replay-seed-22.jsonl
c97d91080455aacef0c0bf0882a2f55bf55d77dfbbc9e69330149d24a6fdf95d  ./p18-fsm-comparator/replay-seed-23.jsonl
0a0d153c985b12a14e4c7420164ebd11f02f47b4abd52796673b1cb0738a45b3  ./p18-fsm-comparator/replay-seed-24.jsonl
a0e5661571061a00bc6699e0bbdb0b6fbe23e02a33163466d09f7b1970af2295  ./p18-fsm-comparator/replay-seed-25.jsonl
ea89aee66c485495df97ee4d6e19a347645a5ac6b88b010cb1bfedb412efb2eb  ./p18-fsm-comparator/replay-seed-26.jsonl
83ad629370480a9cc3abdac922c731790e6a83fdcd74b4ee01e02c3521bf4de5  ./p18-fsm-comparator/replay-seed-27.jsonl
742396a1c49a166e0169dd798b8552849984b3ae9e059d2203736559136bc42e  ./p18-fsm-comparator/replay-seed-28.jsonl
88aa728088d5d916bafd48f5b7a792aae91f136ce39837ee55e63adecd916584  ./p18-fsm-comparator/replay-seed-29.jsonl
bb5375891ed2925906964cebdda1e70872bb751d864b6aaeeb68f59dd2dd8f62  ./p18-fsm-comparator/replay-seed-3.jsonl
df936bb08d94ec257b39455aa88c6f7166f4d88b7faede0577d8680e9206a04f  ./p18-fsm-comparator/replay-seed-30.jsonl
50710121dc7d5cadb3e3f61b49e1efad229dd47f396144e0b1392c4fd7394819  ./p18-fsm-comparator/replay-seed-31.jsonl
ef2034b14f385a2bc13da90bc035bee4b52ccab41048deea7acb7cc34d4b5b7e  ./p18-fsm-comparator/replay-seed-32.jsonl
d12c53aa46c1b68ab1924d0546853b2a994ee5ce435e6ecff9b72fe0d56d2060  ./p18-fsm-comparator/replay-seed-33.jsonl
de1f948d1a89794b744ebc58918e1d50cde08fd56565ac2e0ee28b9cad894da5  ./p18-fsm-comparator/replay-seed-34.jsonl
7b11499de6a1de5fbc4ad9021be8c7bc86bcdc2cf6a2e4fe5db7f287277f8f85  ./p18-fsm-comparator/replay-seed-35.jsonl
c2d83ea7c60264c612901b9c695077d231584a643d3cc637b988d7b9c1bb6f62  ./p18-fsm-comparator/replay-seed-36.jsonl
f1f4a18fb5e240a73e62ca04f97900f890451048d9c66a8019f4d6f79bc16611  ./p18-fsm-comparator/replay-seed-37.jsonl
4b25a7f4692a17963588f3477e6bc9796c90232f064b3243773d03ea1ec1883f  ./p18-fsm-comparator/replay-seed-38.jsonl
6f550ef1b3eb333bed699c04ff596768261c2c110e89124464ab6db87300f90d  ./p18-fsm-comparator/replay-seed-39.jsonl
3ec78e416ef64d95becf7935fcdd73a20411ccbdb682ed8d2dcf716b2ae00b38  ./p18-fsm-comparator/replay-seed-4.jsonl
e9e2ddc25a61832091f486c6177de9eef8e3bd05787e53483029855aefddc2cb  ./p18-fsm-comparator/replay-seed-40.jsonl
2b1c61144592931efb5ec388b028cf59856521818ccac41e78e5ba143a8a9cc1  ./p18-fsm-comparator/replay-seed-41.jsonl
2c57b09a2719100a25ed1f4cfa31e1cc9385e245f5d47d6a71a713c6ebcd8789  ./p18-fsm-comparator/replay-seed-42.jsonl
2c6f92a8d8f26a79b31cf15c4535c79f9da9ef7cfe4a7220bb5db8f36c06acfe  ./p18-fsm-comparator/replay-seed-43.jsonl
33a0120ae92c8a14acb967c677fff5d7400196278107e5e022f7627752dd3569  ./p18-fsm-comparator/replay-seed-44.jsonl
f1d49c1125f79886fa7637937dddb03ab3eb1dea5cd93357bb37e5f0ba9239ea  ./p18-fsm-comparator/replay-seed-45.jsonl
64b3cfb7d7d364e323a8de1de9be47228f488f01246559f985f2901a1bc234bf  ./p18-fsm-comparator/replay-seed-46.jsonl
9d2c005e120c99626de9d686c03a8a220edb7b58bf61f16c4ab14432dbc413ef  ./p18-fsm-comparator/replay-seed-47.jsonl
767ff3e73d62a93551982791362d3fd72ed6a378d0509bb429a4954c20860f28  ./p18-fsm-comparator/replay-seed-48.jsonl
7753a7065c93934cb6e14d2e1c1e4b712abd8988c40b6c8a274fe6bb693320d6  ./p18-fsm-comparator/replay-seed-49.jsonl
95973bb06dfa73d5d2f7fede1032d4cbc61bccb8278b2710156ee3a3cec45203  ./p18-fsm-comparator/replay-seed-5.jsonl
6412ffd1b038866bf143aa3872e8be536a74f4d3560f14d6768c531164714c8a  ./p18-fsm-comparator/replay-seed-6.jsonl
684d4e1e5bd4a702b2da9bb152597ac04f45d9720860f9388892fe72b8e9daba  ./p18-fsm-comparator/replay-seed-7.jsonl
da542e599f6974108e2539f681d616f007dec3ed174e3318604803f794219b2f  ./p18-fsm-comparator/replay-seed-8.jsonl
30ec0e29e288b54a07a91f32339c4fd1c08a6d93388031de7e8c37ee23371f86  ./p18-fsm-comparator/replay-seed-9.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./p18-fsm-comparator/roster.json
4308554773ace40b6efbb02019b6bc9b0da3e6539967d297dbf068ea6f449b6e  ./p18-fsm-comparator/tournament-eval-report.json
dd49755d1509410b0afb1c1e759eb6b3a9377fad2aaceb211a725de09fabeff2  ./p18-imp-6d327dcb/replay-seed-0.jsonl
7fe0e12dc2c5de06083495dcddfeba6e96d0e74ad52e5855309d86a1d7f4bec1  ./p18-imp-6d327dcb/replay-seed-1.jsonl
cb1c40bb86cb64840a7648c1915972e538e77219bcd3203f2a33a80e62c89967  ./p18-imp-6d327dcb/replay-seed-10.jsonl
3a6a387d510e3edb157023df23c46c642ad8be9e88cb76f94cf9e6c8b9e30913  ./p18-imp-6d327dcb/replay-seed-11.jsonl
7fa99f3a2e953b041e759fb702ad214c9474ae0df7c6e1847d7e60d9acd3dfb8  ./p18-imp-6d327dcb/replay-seed-12.jsonl
a5174c3b83123a07e0732f27d4ff6b5ff59968c21f97ac0d514f40a3a5dba2f7  ./p18-imp-6d327dcb/replay-seed-13.jsonl
d9f0910fcd6503cb2f6c8dca666b3d9f0196f3d66dc494af70daa459549595af  ./p18-imp-6d327dcb/replay-seed-14.jsonl
ae7335f2687e6b8fb32f83532760ba9ea3661eb7102165a9dffd2a1b39c6fee7  ./p18-imp-6d327dcb/replay-seed-15.jsonl
a957a91b2c0f853b635cf48316036989408fd8c9498d860b818d6e3424a16f5c  ./p18-imp-6d327dcb/replay-seed-16.jsonl
268003de39207e91498dd52228a66d5e9621c001e55878823c534c992faa5149  ./p18-imp-6d327dcb/replay-seed-17.jsonl
c3b887f3f597029314c4866a09ddc33b759d2ab3176f10b19b504cbbbc03ead3  ./p18-imp-6d327dcb/replay-seed-18.jsonl
3d1dae85108880e943aeee8896206910450b44de5d4cdb5b6271f9238f579af9  ./p18-imp-6d327dcb/replay-seed-19.jsonl
dd8f5acbc3f7efee626748067fbd1c08f170507069b50755505ff6d9d4407aa6  ./p18-imp-6d327dcb/replay-seed-2.jsonl
92ea297f50138c03c76f6858472af1b4f1733a1f73406b5cc3f607f33a866d75  ./p18-imp-6d327dcb/replay-seed-20.jsonl
cf97ca6461eb33d7bc19bc415233d46373f70d833c6f9d9393ce9901e3f2c2d3  ./p18-imp-6d327dcb/replay-seed-21.jsonl
8284884487661b486c38e6659868e290aecb0cd3b65c980f2e1929d48dde3539  ./p18-imp-6d327dcb/replay-seed-22.jsonl
4dfcc2d69ba6f32a55c841780853e73d44815f7eaaf465422798b4b7bc60f4e8  ./p18-imp-6d327dcb/replay-seed-23.jsonl
fc6f9b78e3be73307367e6ad4c8a718fba6a382185643f7a9bc13e6745d5d2c2  ./p18-imp-6d327dcb/replay-seed-24.jsonl
43945a8f6a3d1f6e3013eed56c51d99d02423d23c05592c29ce6df43b2f9d37b  ./p18-imp-6d327dcb/replay-seed-25.jsonl
619f5f6f86bd7e1b90462fdeb8ae4a29a4f2ab0b0524c32fb61f66c5059b93b5  ./p18-imp-6d327dcb/replay-seed-26.jsonl
495a929713ba8099be00828dd44c32029c15c487a926edb19525d4c37affd957  ./p18-imp-6d327dcb/replay-seed-27.jsonl
00c5e8c6b3c3f0b4bf940f0bd12bb8c97c487ad6bdc510466aa477f1bbb88ef7  ./p18-imp-6d327dcb/replay-seed-28.jsonl
1bdc87e0d62d3a2041c14a0637adbfea4dcf95ab66bbc768600c242a4ea2d679  ./p18-imp-6d327dcb/replay-seed-29.jsonl
afa034496f357a1510347c6c458ee01d096cb1bbc7ea8f21aaa282511b169a05  ./p18-imp-6d327dcb/replay-seed-3.jsonl
8a6533e46530fa2d3d5606cb4c1dd4645370af8741cf96a9dd8ff2fc500cd81c  ./p18-imp-6d327dcb/replay-seed-30.jsonl
fd0a263f557b77528a52dc724c2a5b513b79da088fb3ed9f41b056c1ad33c50b  ./p18-imp-6d327dcb/replay-seed-31.jsonl
2b903e9ffea6ae63e9e3f64126bb80f69ac249ed427dc6202bac463ebe420d78  ./p18-imp-6d327dcb/replay-seed-32.jsonl
c2e3f8b5dca4c9809fd5330f378989b01b14194f332fd9950de39f6e4bd53959  ./p18-imp-6d327dcb/replay-seed-33.jsonl
24f20a32f27ef7f0f5c777afbc011138d5ac128d9fabf6733f1d4880273bb8fc  ./p18-imp-6d327dcb/replay-seed-34.jsonl
4c1ee287c58f3ea3a911509b45359a86c600768bddc26cea45967d51ac5693f7  ./p18-imp-6d327dcb/replay-seed-35.jsonl
c55cd278c3c514eaa92078b06590be8ac0939fc8dd79dcb99473e39c5fa7d52e  ./p18-imp-6d327dcb/replay-seed-36.jsonl
7b2b94a3fe1cf1e5a5c9568593b72ec44736403bccf39efedbf98e597883a681  ./p18-imp-6d327dcb/replay-seed-37.jsonl
8d3cfe01ba39ac4fa67569097c3e677624e8345ab91a37ac35eb64df6ec12996  ./p18-imp-6d327dcb/replay-seed-38.jsonl
981dfd068f913c083063cacec78b84c41701c43ed13a2faa619bccc4e70bd31c  ./p18-imp-6d327dcb/replay-seed-39.jsonl
b7cc1707d9445b088855c1f95a3cb26cf7e190743f1407c42a5a9f3c74dde0f1  ./p18-imp-6d327dcb/replay-seed-4.jsonl
3bc55f6179b22760a578ffec585e5f22493b6d640dc5c372a283f19f96922417  ./p18-imp-6d327dcb/replay-seed-40.jsonl
61952999dc413a09d50608c5cf573c9cca582290fce7c2716a513e3685df713e  ./p18-imp-6d327dcb/replay-seed-41.jsonl
89b95ecb7dbbfb03b27c81ca2128b6f2c046f45ac9263ab8db35a4341ae1db6e  ./p18-imp-6d327dcb/replay-seed-42.jsonl
58fc8687df6938846a6782c50bea7b3e13493355b1c25da8fc5db38cba574c8d  ./p18-imp-6d327dcb/replay-seed-43.jsonl
d8e85b56f0be996919640a6e61f303719a1292993cca792c8bcb6b34e8fcad3f  ./p18-imp-6d327dcb/replay-seed-44.jsonl
2a08253c53d5610fc9503421c871c4c42abc1da188e73b59cb6c447c3e82e9dd  ./p18-imp-6d327dcb/replay-seed-45.jsonl
1c23be34181c82aa1f841abb930a0413d264472e88c2ea88d35578827aaf7802  ./p18-imp-6d327dcb/replay-seed-46.jsonl
94ea5950de79a5bcbd3f85c7aae0b274b1bdc5a21486cd430e19ded558a18b75  ./p18-imp-6d327dcb/replay-seed-47.jsonl
2cdaaecf225c30faa871e50945f14620616b4d639f87886738d06cab1522d719  ./p18-imp-6d327dcb/replay-seed-48.jsonl
a8fcb28c67772d52a7e61e6d2bbbf69c6d88e677e9931ffdf9dc6364b55804c3  ./p18-imp-6d327dcb/replay-seed-49.jsonl
47a8bb0b2ff7d7207eb2c5f6d29f6b09a146a74f637a802fa46b36e427d297a3  ./p18-imp-6d327dcb/replay-seed-5.jsonl
a6c8b5eeb47ee0e5aa5994b6709d984e32ab616bce126f293161b9d384f5ffff  ./p18-imp-6d327dcb/replay-seed-6.jsonl
e64a85ba1ad43345250eedc71dc5433e997bb209029e8cef74dccf61ae74fd12  ./p18-imp-6d327dcb/replay-seed-7.jsonl
a3a22263c546067508f1c14188d5ae398c5dfa716cd924b59179a2a09a54579d  ./p18-imp-6d327dcb/replay-seed-8.jsonl
47879628e5e04cfe93a15bc007ed53f38091cb1b64a9487c09fb70c8ffc1f4d5  ./p18-imp-6d327dcb/replay-seed-9.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./p18-imp-6d327dcb/roster.json
b35afbf94c0025148db4f975457946669ac310f9f5357b0356988c7b443442ba  ./p18-imp-6d327dcb/tournament-eval-report.json
5518ceed1476e253f3d31601216512313fe30ed51d698a99e3ee346c71297462  ./p18-imp-7f73929d/replay-seed-0.jsonl
fcdbbe27351f7e2f7ec6cecfd36026a12202bf9d2604e6c8f762f9d15e674076  ./p18-imp-7f73929d/replay-seed-1.jsonl
be9723586f5d3184ba2c77411d91faa9d856e5f48a89284603aadbe5c15eef61  ./p18-imp-7f73929d/replay-seed-10.jsonl
3cb0b998891ffee3d05f104cd4dac78e10f265f988b53a27b3d4ac1bfd0b72ca  ./p18-imp-7f73929d/replay-seed-11.jsonl
e287bd1b27d582c56b20b264ba8048d211c84016eaada37b89f7773aab619d68  ./p18-imp-7f73929d/replay-seed-12.jsonl
caeeb76fc8aa250e71be06d5d21d4a960f087596b4622b670e9977a783cb0976  ./p18-imp-7f73929d/replay-seed-13.jsonl
260d7978ddf0710f9bec71ec3ea12539d84f7bedbcc02242570e8250256e08a1  ./p18-imp-7f73929d/replay-seed-14.jsonl
f0a285312fdebde2e93c266b758e2029327291e09c6b1a6767cad964ea7d5e56  ./p18-imp-7f73929d/replay-seed-15.jsonl
9a7ca2adb7b68f867d6b71d9b28cad4e8dbd040f82bfb4d6a976c2dbb34a4828  ./p18-imp-7f73929d/replay-seed-16.jsonl
f668b189823f30df824b3e1924aeb59d7c479f5c697198cf368b0760c8a5e152  ./p18-imp-7f73929d/replay-seed-17.jsonl
39301d2eb07c02a8a430205b5c49773360ca6338f12527bb7797cd196e3da4b3  ./p18-imp-7f73929d/replay-seed-18.jsonl
6da78369120803b4b42a3b03a7bc76b0b81270e70daa6a050dc9b0c276847d3a  ./p18-imp-7f73929d/replay-seed-19.jsonl
47c847c7ddf5e11ed16eb4e9ec17f89c188968a8655c415ecad87ae94b652fea  ./p18-imp-7f73929d/replay-seed-2.jsonl
701629860b87c478a495edd0f00f68a27714f3545bc8d371d13baffcfe71a279  ./p18-imp-7f73929d/replay-seed-20.jsonl
01faaab96bc96e77e5fcefa66451c14431a2a2dfec7a2eba17439d5b549a939f  ./p18-imp-7f73929d/replay-seed-21.jsonl
3f414dc332816e45145a2a97cf799d5af4431704e3adf6d2d530c844d2e4a110  ./p18-imp-7f73929d/replay-seed-22.jsonl
1c8214614483430f6351469234a81f11dd8b2b4be861c10283ca10aae399c993  ./p18-imp-7f73929d/replay-seed-23.jsonl
02cd14557b1838073da378448563f2e9829d8556a8011f3f39e53fdace70f839  ./p18-imp-7f73929d/replay-seed-24.jsonl
8930653b37f0fe01064e988bcdc8a602c3f929af988c5ad11ea60f155754ae3c  ./p18-imp-7f73929d/replay-seed-25.jsonl
10c133d516b227c6086156c4baeab7d5b475b0fc55c8fffa7856bd407e2967e4  ./p18-imp-7f73929d/replay-seed-26.jsonl
ff5552122ecc82af61a3702b24318987827ef0ca2e6d6491bd6c7eae00f23214  ./p18-imp-7f73929d/replay-seed-27.jsonl
0b6b7e7611692366e0c7b575d0950e5007678b85c7ed3a5a66bf75eae782ef1c  ./p18-imp-7f73929d/replay-seed-28.jsonl
357424f027af1865862e352eacf4041c6cdcd93ac3b87390ed09721ec41f7046  ./p18-imp-7f73929d/replay-seed-29.jsonl
e28100cedca0e989d54ea8a35e409944923ad2ed1a8c6f324da93ac635c2244f  ./p18-imp-7f73929d/replay-seed-3.jsonl
61b0daae5758c44d95443940a1dd9e4172aba4acacfd096eb3b0b9b9abf94e5c  ./p18-imp-7f73929d/replay-seed-30.jsonl
537b57109d1e55ffd7911a967fe2501be2231fbc26b3810b6e9c296e6a667c8f  ./p18-imp-7f73929d/replay-seed-31.jsonl
ea32122284124e21ec8334b207fb2483232f3ac10d2879105c47cf668abbaa15  ./p18-imp-7f73929d/replay-seed-32.jsonl
f42e283fabc2b5bdbc79f1e7e702b754a42db52a4cc2081609e6ff1949acd878  ./p18-imp-7f73929d/replay-seed-33.jsonl
7b44b1379035e8bf760d5e78866863737c26b43a85fab8d94b419907b19f47a1  ./p18-imp-7f73929d/replay-seed-34.jsonl
7ea0d7bce2a058e6eb5f0353b13ea7399d588e781bc31ffd202498bd259e2053  ./p18-imp-7f73929d/replay-seed-35.audit.jsonl
59585ce7e0ac097948e2df8f3c8bbf5f9f8e38caf1e94ba9de34c14b55197fe3  ./p18-imp-7f73929d/replay-seed-36.jsonl
88f38fc64391b0006dd0b2c735db5a95972abfddf84171b9450dccd498fc47aa  ./p18-imp-7f73929d/replay-seed-37.jsonl
a52e27e200240f9cf2c30b7b3d9cfd28bd96afbec1cad24d6d72a7316cb095f8  ./p18-imp-7f73929d/replay-seed-38.jsonl
f97c9c759ce0bed05945d4ce7a7b94519c485b4082e3f162328fb6777fa05698  ./p18-imp-7f73929d/replay-seed-39.jsonl
4b07e2b07ce5ecea797d9b8ae0ee7c6beeca516a05e9fa0c1b085769a4dc5795  ./p18-imp-7f73929d/replay-seed-4.jsonl
a5ffcdf33d664306fc6bb88ff63caee88d243b31eb4209c4d78a87a961b8e265  ./p18-imp-7f73929d/replay-seed-40.jsonl
754bf1bc7931ad610e3c48cdbf2308c5d64a897e41f8aaeb22b9adad5ce88d98  ./p18-imp-7f73929d/replay-seed-41.jsonl
052cba454598ba6cea0b85907932d652b80f61adbcab7ae8102cf4bfdd30e5d5  ./p18-imp-7f73929d/replay-seed-42.jsonl
c2a6f64a45a6194edad64bf3187852846749f135174425a62dfa01948528b181  ./p18-imp-7f73929d/replay-seed-43.jsonl
99fa617d904a15279dea4ff48c3d4477f00a3f58f61edbd6688a9c9ca96c1b33  ./p18-imp-7f73929d/replay-seed-44.jsonl
938b55508430dec9697d08c2e520273b70c5b651afb7052dfc0ffdd29022a826  ./p18-imp-7f73929d/replay-seed-45.jsonl
7aa7ad4635dd1dc84552b04cd5b679b6311f78ee5c070770ce0589e36ecf3692  ./p18-imp-7f73929d/replay-seed-46.jsonl
3ed660a68be8fcdc80d42b7f07c8b05a8b64bbc1a7ea9b3d16cfcff8f92888ff  ./p18-imp-7f73929d/replay-seed-47.jsonl
ada99409bd3af1be591536ef31ecd60c950147a2e434b3a24c2b7c5cb7d6ef30  ./p18-imp-7f73929d/replay-seed-48.jsonl
c17df64b8e325f9489aab26597a5b7b739f7ea6a999abc92d8b8a214acd644df  ./p18-imp-7f73929d/replay-seed-49.jsonl
c204a3bc748a3d972a5ec0bc575d2937498c39240e5fa8e092d3ce96b45dfb44  ./p18-imp-7f73929d/replay-seed-5.jsonl
63a6df56257be698e79b61124fb66554594d85af7fa12168ea4651bc645a4e45  ./p18-imp-7f73929d/replay-seed-6.jsonl
8c0b21aea3126297c2230fc586362a865859352b3abe4c6fd89064f867e263aa  ./p18-imp-7f73929d/replay-seed-7.jsonl
115a8d6c4871da8471b0619324efbd436df0a0e8fd5916601a6e297ee2d4508a  ./p18-imp-7f73929d/replay-seed-8.jsonl
d24c8296b59f8fda7c2fbb79d611e6a1ef9f513fa34b1644c265b70547c53e78  ./p18-imp-7f73929d/replay-seed-9.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./p18-imp-7f73929d/roster.json
f61b629f9c94bf7e7b71dcc9c17eef4ce6a595ad61eb167f4e6ed1f9eeb3f1dd  ./p18-imp-7f73929d/tournament-eval-report.json
60a9a02d2980032a829ac6d447461a58c9e6e839e70d498d0de485a4fe18878c  ./p18-imp-bfd145cb/replay-seed-0.jsonl
d1eecfedc44b35b6032f7bfc208f492f55c35d5d7785b50cdba59770ec634cfd  ./p18-imp-bfd145cb/replay-seed-1.jsonl
95cb0366f8d3f7b1d2ef7d61036f349bf2e6c8caf4231679d531f1135b38f1a9  ./p18-imp-bfd145cb/replay-seed-10.jsonl
e63aca98de2afc0549b882b577b37eeabbc41785ac2783fcda7e35c7b29326c1  ./p18-imp-bfd145cb/replay-seed-11.jsonl
e4ba919dd77a49f4f80b0bfd9386629740e868a5d0ae0c8cfc90879b23296f21  ./p18-imp-bfd145cb/replay-seed-12.jsonl
502512bd32da8876eea6fd553c23b9b6970477a22cd218acf64f8b266df4b902  ./p18-imp-bfd145cb/replay-seed-13.jsonl
49ad2404bbbcb097eeb4667f90b4adb227b5e7908cc3738b86a7489a4a25d93b  ./p18-imp-bfd145cb/replay-seed-14.jsonl
2c81187f8d578d10934826874bd9520ea40221c394982c378e5fff3c68155f84  ./p18-imp-bfd145cb/replay-seed-15.jsonl
7a2614cfadfb59c671588452608190dd0419869a3308ab793c6f57d138f1488d  ./p18-imp-bfd145cb/replay-seed-16.jsonl
f294ae420ffcfd153146abaa41787a545d584a7b0c1ef052d7b8f4956d54c2fa  ./p18-imp-bfd145cb/replay-seed-17.jsonl
194a0dd78959c5d89f4c25d8c7c7b6bfc39199b746ce47e0af9ee55c173f90db  ./p18-imp-bfd145cb/replay-seed-18.jsonl
35e15131942f40c666120d8eb51d9614a891fc8a04ea9a602245813b2ddc930e  ./p18-imp-bfd145cb/replay-seed-19.jsonl
707911e99c550bd75c8cd2deaefc5f79994f0fba3f9b544bfad6dbe1beb3fc9f  ./p18-imp-bfd145cb/replay-seed-2.jsonl
459d2ae2d099e13ebdc860e441eef0faa6a757d4436d34e10e6f3332dbdc2578  ./p18-imp-bfd145cb/replay-seed-20.jsonl
5a807db9ed1a41265c40016dba27be97bf9969329cbb929630e9bba66d7be93e  ./p18-imp-bfd145cb/replay-seed-21.jsonl
badcdd3994bf34fce66ba7c682f3aa36ece0fb735c7734263fa0f954074d5a38  ./p18-imp-bfd145cb/replay-seed-22.jsonl
199c621777393d22d67d9c42047ff9ad3dadf9a0933ceaa21b5a3020600e00a4  ./p18-imp-bfd145cb/replay-seed-23.jsonl
f5c8eabd96ca136edc109dd5ebb52bbf72608dfe8779ce60ce8d5115004f7d77  ./p18-imp-bfd145cb/replay-seed-24.jsonl
41dcfddf02d49f6dd67afda19287d7b084ca98adace5c2ff71b81c9f1e3fc4c2  ./p18-imp-bfd145cb/replay-seed-25.jsonl
f295100867a7e6c6341182c143697a33f5e589201c4e921df1cb345afaa9ad87  ./p18-imp-bfd145cb/replay-seed-26.jsonl
0d093d953c6a990ae5dc3d46e03afe48e169e44d0eec78edad2a16f4287b9e1d  ./p18-imp-bfd145cb/replay-seed-27.jsonl
9dca2f7160a2e1bb0c7929ed72b9722a797a263d2406ad14e872e9d26b4b8bce  ./p18-imp-bfd145cb/replay-seed-28.jsonl
6c7a742dd2f1dd353a9a48733cc2f52e3e5fc278d294578f722b550ff39ffc82  ./p18-imp-bfd145cb/replay-seed-29.jsonl
e6927be82bdef35b875ba702e163af223b831c6fb16ad46d5c67c5c8fe9dce91  ./p18-imp-bfd145cb/replay-seed-3.jsonl
e605ab6d9dd58608b80e495b912d8ccc64d15ea55405109c3337be41ab757ca3  ./p18-imp-bfd145cb/replay-seed-30.jsonl
8ec5cdc933dbbcccc3f657c3aab582f48b6a62848cf2186b836dad7915cce533  ./p18-imp-bfd145cb/replay-seed-31.jsonl
ef4335f3f768d93a79e53a9803c92cafdcc274af29a25b7397a5d13366e73d09  ./p18-imp-bfd145cb/replay-seed-32.jsonl
765467e2e18e34841b820e1e097ee37553e711cff5cdae82dbcae13b928397f8  ./p18-imp-bfd145cb/replay-seed-33.jsonl
43a7d1a9359741704c1142479c7c998de5588f30dc63c0529665f997e08bbb8f  ./p18-imp-bfd145cb/replay-seed-34.jsonl
abf2d18fffaf80a01530790a9be7fdcbc96e1ed8ae1c64b8d2f22007bc796acf  ./p18-imp-bfd145cb/replay-seed-35.jsonl
5da35f272e5ddfc61f10e2bf01716bd784f553f9d15d7080ba097f1497705856  ./p18-imp-bfd145cb/replay-seed-36.jsonl
9eb5292a16dea9d908eacbf5ff81ce4b460b5d056a22cdc8ce8076dfdf1fd253  ./p18-imp-bfd145cb/replay-seed-37.jsonl
58904bd0e329ed9c3b1a7872c4344ee2f32da01176ffcc7207ed827e50efea14  ./p18-imp-bfd145cb/replay-seed-38.jsonl
2d7fbbee6ee11be7a0832711846dab1362cf472423ae09f8933a7f27e2bef4d7  ./p18-imp-bfd145cb/replay-seed-39.jsonl
0b70820e624cd2b02e13091fa2ba35365186b7edb4f52526a785945c7121864c  ./p18-imp-bfd145cb/replay-seed-4.jsonl
83f6f1d4dd104edc74806bfef2f205091102b212eab5d3aed5fc977e213ad271  ./p18-imp-bfd145cb/replay-seed-40.jsonl
fb72b6932450bab78c135432ba113b0a1ca38cc9343b06b7a0e544938822e404  ./p18-imp-bfd145cb/replay-seed-41.jsonl
c4d9878bb086de1ba7c2e93e1e808f37b8153fe4cc76781fdcb6ac57fb8fc80b  ./p18-imp-bfd145cb/replay-seed-42.jsonl
2f3d5ca77b68feaec623c7f405e3c65639d11216e9e2333e8e1dfbfa51814be7  ./p18-imp-bfd145cb/replay-seed-43.jsonl
52314933a7756d627f290dac06f8dfb48ab4d6dc57a29eff6e7dfc860dc97c1a  ./p18-imp-bfd145cb/replay-seed-44.jsonl
c9dcdca60234e4593b3c1048fc75829cd654d2263df7a84077ddad295ecd0f34  ./p18-imp-bfd145cb/replay-seed-45.jsonl
5959567090689ad9b3b0d64746238ee25cc01db79e0ea55ae473e292ebc0ff2d  ./p18-imp-bfd145cb/replay-seed-46.jsonl
90e92cf358759eddd2f8970073bd2e6a11e4c7576e21444526c639acac0cbc09  ./p18-imp-bfd145cb/replay-seed-47.jsonl
b39eafbf7b6ab4d434240e6f892fcf58bd2f4d14e671e9b54b0df82a8dfefd4c  ./p18-imp-bfd145cb/replay-seed-48.jsonl
ab8356a8ea58e28fa91d6ed14e9dd839bf0ae89cd4639d9543cc3e8f6df54f19  ./p18-imp-bfd145cb/replay-seed-49.jsonl
16142ee6d4f113b0d430e2d392fa0296a3a953d1921ac6324205a2be79e1c61b  ./p18-imp-bfd145cb/replay-seed-5.jsonl
e5cb0820be15a6e0c2fe688db4cd91e687f3e816d802cecee627e0bf5610f666  ./p18-imp-bfd145cb/replay-seed-6.jsonl
91551bcfad36984fabed6bbf472d9c519bda519dd1a89acf032e86b8f93e053e  ./p18-imp-bfd145cb/replay-seed-7.jsonl
e9516b06f9716bd80f53ef859486a76bd31106bbf028c9002463d59f766f7b48  ./p18-imp-bfd145cb/replay-seed-8.jsonl
1bc1b8ca1be5d4b0b7b586a46419fbdd33a36e64e1e0e5758f0ac83906bedee1  ./p18-imp-bfd145cb/replay-seed-9.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./p18-imp-bfd145cb/roster.json
6c46d443b814cd516109f896acdf6e0b244372fd6a77cad0ae7e32ca465516b1  ./p18-imp-bfd145cb/tournament-eval-report.json
74c2c26d48c73a06351231757e4027653946ec4938c3c8648e3d31e7a1cbfb8c  ./p18-imp-ea4bc955/replay-seed-0.jsonl
1372825e284ed17fc3ba682ad196f67aecafbdc4965b290f566f9155119bea88  ./p18-imp-ea4bc955/replay-seed-1.jsonl
463c6628fc072923b38fae32e7317d9daeab5a0c880fe349e88a93e3f5e52fe8  ./p18-imp-ea4bc955/replay-seed-10.jsonl
dbd52ef1d27df4ddb49ce4e5809dd4c8aeded4d3a22a9533b01d3652ae36ccc4  ./p18-imp-ea4bc955/replay-seed-11.jsonl
ad21829dff774b0391a0089361a255fdb3188f4cb9eda9aa83aa2ca3097342c3  ./p18-imp-ea4bc955/replay-seed-12.jsonl
21670a857ec078f990a709b4eb2d11563cc32ecee6bd10667bd2ace1e7356b4d  ./p18-imp-ea4bc955/replay-seed-13.jsonl
c656d43a68e5c7137c639665763ba843679ac9494a0b8be6360aaac76d4add2d  ./p18-imp-ea4bc955/replay-seed-14.jsonl
43330d1e1f6ad5e3c682eecb0ee6699d0692be807c3dc63d1243bb13f376eed8  ./p18-imp-ea4bc955/replay-seed-15.jsonl
d0bea171980a56e856ab36e81de27aa8a58fcbfb1385114d424a6b2dd6d99428  ./p18-imp-ea4bc955/replay-seed-16.jsonl
19c5304975f39143e332a54c037d2723428c7d7443e952e43ba7ba470f177f81  ./p18-imp-ea4bc955/replay-seed-17.jsonl
786cdc43748814d2889540d93a17845dfa49f1f7d8b07e27ae8f3ec33447006c  ./p18-imp-ea4bc955/replay-seed-18.jsonl
5a51e56f3774fb9974380da6fce5a3b3d5eccec076ce4324450827d71b3bcc3c  ./p18-imp-ea4bc955/replay-seed-19.jsonl
a231cb6df258eb15e9f1e50b6a933432bbafbb676632fbc07870483e7c9fb1df  ./p18-imp-ea4bc955/replay-seed-2.jsonl
57794fe9a2dad608f3dbaaa17c8d97f1382f2225ddb22767c1d32caff189ece0  ./p18-imp-ea4bc955/replay-seed-20.jsonl
59fbd36337d2394829d7ccf2c0ebc1831b5ee623e8745fa82497204fb656e3e8  ./p18-imp-ea4bc955/replay-seed-21.jsonl
6575fd32d183f63c0ff3957b638b38829809ae481d896600ffceb1a4423eeb98  ./p18-imp-ea4bc955/replay-seed-22.jsonl
85a30ca6d065d703209318bad84b7965827bede360ff27c0afb312825483ca8b  ./p18-imp-ea4bc955/replay-seed-23.jsonl
f8deb8d2d0becea3a2c093257001ba13d6cc296bd861b1febad851676ca7fe21  ./p18-imp-ea4bc955/replay-seed-24.jsonl
e80802429bf6b5f6368cc5bac23fc605e2f35f40bda2628b968206685c1d99e6  ./p18-imp-ea4bc955/replay-seed-25.jsonl
24b0cc348085f5cc892ad1dffb60b1e78784741907a60def2763d1530ea648ab  ./p18-imp-ea4bc955/replay-seed-26.jsonl
c3d5814c7c602bf8914138da02a1dcaaa21c7ed2adce2dd5c8775dc13673c77e  ./p18-imp-ea4bc955/replay-seed-27.jsonl
f821a7140b99df5dc11fa625f2bdac72be4fe781b4fbe2c7680d573e3c6fddb2  ./p18-imp-ea4bc955/replay-seed-28.jsonl
0e05b59716fd45712319cfbe3a11d217b8ee7762981f94cd6602af70052e2967  ./p18-imp-ea4bc955/replay-seed-29.jsonl
ef1b76a0b272508dab784440bec09253abac76af03c8cc16d9e1409ff6e6bbc0  ./p18-imp-ea4bc955/replay-seed-3.jsonl
64595ed9d2f294a54f44bb4cc65a7299e3f9c75a2a132c6b10a5a80a321a3ac9  ./p18-imp-ea4bc955/replay-seed-30.jsonl
222bdc4d2dba87f007f07e86fce07bc78a33802f48902c3f75adceb80e592462  ./p18-imp-ea4bc955/replay-seed-31.jsonl
d8ed609c204c0dd9b5bde7d49a862c9133877f7147f922622f8971cfcf82e23c  ./p18-imp-ea4bc955/replay-seed-32.jsonl
6caaa2c2014a739244050d57a219db48a35a23c7812b8630b815eb15929d640e  ./p18-imp-ea4bc955/replay-seed-33.jsonl
73e31e7d443fc86ad4294b2d4f8d703e77309ea8e6725b11d9e7343dc429d56e  ./p18-imp-ea4bc955/replay-seed-34.jsonl
43017fec35a51b0c40b63654bf29448c97e2f6469f508f400be2d75f3dcc0312  ./p18-imp-ea4bc955/replay-seed-35.jsonl
519b297dd78ffbb26e3d7600d3e34b52e61e1236784db9be4412003221e6881b  ./p18-imp-ea4bc955/replay-seed-36.jsonl
61f510a4f97a6f9d7fe2d50f48fffdb3d127b0098ad65e6d331e0dfc5a42ef3b  ./p18-imp-ea4bc955/replay-seed-37.jsonl
b317005056593933425e38c5fa8f50bb8508a7b664c66653f8c0d27ea696005a  ./p18-imp-ea4bc955/replay-seed-38.jsonl
47a2906b86aa49f0866c7881b0eea4d21e4145ea37c9d172011642530303ce1f  ./p18-imp-ea4bc955/replay-seed-39.jsonl
59d0af32ea213c19a5eb0ee568bcf302c88976508a2b30b2bd183f803a9e170b  ./p18-imp-ea4bc955/replay-seed-4.jsonl
bdf10955556107acccb4c3d0ca764a2b0b763249c8c7becd7af7e3034b289dad  ./p18-imp-ea4bc955/replay-seed-40.jsonl
822400acece16fe8e7896191f1474dd00443316ae3c8c383b9d322f6c21493a0  ./p18-imp-ea4bc955/replay-seed-41.jsonl
710318087cd9ffad6adc9ca4f19e732d7095c6e62567b83f41a53535946411f6  ./p18-imp-ea4bc955/replay-seed-42.jsonl
0744962983715a16cec76c5bd77811a68e1bdf85df36b8fc1bc1204bd82e7437  ./p18-imp-ea4bc955/replay-seed-43.jsonl
5bd578d9d5655577855d6ee22f5534f5b3b0c386a8bab81073958117ef6a635f  ./p18-imp-ea4bc955/replay-seed-44.jsonl
65306f458e318c36381ee58e53dd16825a773a1a78c8f8844bf9d4cb5db4f1be  ./p18-imp-ea4bc955/replay-seed-45.jsonl
8470e15338ead52bc3e6baf404b9893ab6bc48472b223a71457343c4b0928f50  ./p18-imp-ea4bc955/replay-seed-46.jsonl
7086d82b8d7f835a1154518091c9c43a34feb44084e8424ea909107d3a43cfa2  ./p18-imp-ea4bc955/replay-seed-47.jsonl
e80db1decffa8e7cd71a559d566399b288f0161e98bd278de29bf02893f464e9  ./p18-imp-ea4bc955/replay-seed-48.jsonl
31dc65234d4dc22c34b701bf763d9956ae9162a8f3b2c3cc0f39cc1c8abb80ce  ./p18-imp-ea4bc955/replay-seed-49.jsonl
5a67303f84d7704513d12968c6ccba0713cf1c4f1ef67c765b8cf1ca0febb474  ./p18-imp-ea4bc955/replay-seed-5.jsonl
8caaaaef1b51c903f4670d935e140d7da1e3eeede126f8ba9d970aea86d54f19  ./p18-imp-ea4bc955/replay-seed-6.jsonl
f89fb7981fbb48cf9679654a1e6987db5270ab70c75b8122f7c6db1a83dc09f6  ./p18-imp-ea4bc955/replay-seed-7.jsonl
2eca7160a0ec5d133be8c44d38411717c2838b9ebca08bc0043666124f606598  ./p18-imp-ea4bc955/replay-seed-8.jsonl
359575cc651acdacb0ee016d192ed4d9ead1ebd639dbdb2cd9e9641817289923  ./p18-imp-ea4bc955/replay-seed-9.jsonl
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./p18-imp-ea4bc955/roster.json
1f982c9befbcc92ed78417adeaaec120a78d009aa56c39fb8f04140037c23838  ./p18-imp-ea4bc955/tournament-eval-report.json
45da6914ad6652055983303d1ef9f9b27082f7d8e119aa0cd136c310dde8f84c  ./retry-stubborn.sh
b84aae6129c5ccd33a854ce70e252cbaf26f685eddbaf5f1c44e43cad3614205  ./score-arm.py
d79097b73c67a2731ff84f8e415c094c08b20e4b7a9cfccce85d0df43af0cee1  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-0.audit.jsonl
c738c466965c3e9899e723a97c8d9c4155ae87ae462029ac8329f986f4ff086b  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-1.audit.jsonl
4ff858eed213461864407b7382b0d2c5817a51666da2fa437d9ad897e67cd069  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-10.audit.jsonl
c359bc57c1491f7009315a1f7ac4f3a74058255ddb9268eaa00a84beb8ec5529  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-11.audit.jsonl
7b820354087e6b7cbdf18f47e9370bb9118f69f25ae75f0632d2d99bcab0fa14  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-12.audit.jsonl
7045327ffb54249720a55a9bf48e87b0914515e05224c50558c3a724c5617e20  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-13.audit.jsonl
3364e70d95678b5fb59789b5ceac9c33c51e3d0750e1447ae4c6d6e983450127  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-14.audit.jsonl
2cc408426acbc90cdac13c2378d8f509420d0e7876963a48025f9e69ea5070eb  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-15.audit.jsonl
73682a90cb331710a7f66521ec44ee5768e6d05fecad1730c09d9fa16d7d4cae  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-16.audit.jsonl
c5ff2123130a505f71e442ab21265ab84a35aad152b81750b672589da2ec6833  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-17.audit.jsonl
cef243808f33bb6fbc65f2c51342507b0fb2341e67f82eddb4247f28edbdbeff  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-18.audit.jsonl
7e2a30b7920a7b3d8b472d5882c929f52ea6a52d34a4132c5bf08be95c56ff07  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-19.audit.jsonl
276f23a16b4a101e739d501a048fbd76c3d166a91b9ec644f590030a8cc9e59f  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-2.audit.jsonl
787ea741323d47ef8e4961e61b9dd667ad519802e16bb76c2a14bd5d1790d200  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-20.audit.jsonl
2220cd2d7db3dd0b2a70f9592b363ee0e2bc227e04a8d7e0f07d83a75ff99888  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-21.audit.jsonl
990d2e22b38c8b31aa5b548ccec1e4614ec8a0ee303e05a19dc86ad63f49a771  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-22.audit.jsonl
1f195271d4a83da97eb4ef18d2bd37b377e6287c03749d81f19020b43a9fb9ae  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-23.audit.jsonl
99ae6c2f94699af704d221a71d5f04f79453b73b36aba24cb8d86e162a766bb2  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-24.audit.jsonl
149c3d3e5b18fafdee20ddfda3fceab5c05f2fdccc31af465f603d5b4293d8b8  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-25.audit.jsonl
b34cc88a8e3a0c5ca176e299be92262906f85075ed071afb5a1cacabe1cabadd  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-26.audit.jsonl
2163600587132cd31fedc54360f6c846edd4d37453a8d27ddbda9f6ccf2237e9  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-27.audit.jsonl
49dca26639a627fb3d90b8d1a38d448f8ca73327846c6d683297e669df38b001  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-28.audit.jsonl
083685bf94c81bc48a06b2f0f2f17d9a5c4c0fd51955839e54c482b110cc3b9c  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-29.audit.jsonl
7c3997a5fda232cb0b1f8e0457f4be464be4e20318371c390fce1ec58791cc18  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-3.audit.jsonl
581eee3e8dd907f919120d68a297a2ca27c767320ff3a54988a3d9e56dd5156b  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-30.audit.jsonl
48904d545eb0e511e920dec4322a7df0d2a4b258486bcec824c3924389d115c4  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-31.audit.jsonl
687733fc47bfa52dc8d829c3366dc0939a4b516ea0c7b0df5f2a2e0c9f927558  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-32.audit.jsonl
4e9b75c660897d9f684984e9efb5b369e44235eb4c77b71b1a0b9b12ca398c4b  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-33.audit.jsonl
fdaee2d19e3f1355072f1fed4f9ecaf2550eb82c4b142346d3e6860b8c9b6fd4  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-34.audit.jsonl
0e81111cb6776e309a6fa2e15709a219c3b818acfec971ea258fb0a75a560a1f  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-35.audit.jsonl
2f9488aebd0f3ec9cdf4517aedd643200da182a90f7d343fb7ee30316e3cbb7a  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-36.audit.jsonl
b824082a3eeef979f7cd7f74d45e6fe400d9091161baf82da7eebd63ea611bc1  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-37.audit.jsonl
836c9505f4485a3b3d98fc3f82f301b372da5088e4d4d911132a3384343c8478  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-38.audit.jsonl
b5806e0e243ffdf7e39ad0d001096a91903a0e0ac888ea0cd9291cd00b82b3a8  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-39.audit.jsonl
5a13f8d5822f84e6922796761b53c43e69be6f52967d63c6133416df3b03a0c8  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-4.audit.jsonl
98fe1101ecd50a0bf6dde72fadb47acb3c0c012017efbd4beb9f708553123170  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-40.audit.jsonl
b2c268c128f6a4605b60d3c032bac8277bd336fe2025d6c3d9939be46b6bf9dc  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-41.audit.jsonl
ee314c77aa806b36480020ec487135f87182614a261915e638fef978ed6b7d08  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-42.audit.jsonl
5d1097f13745a3137ba1fd8dc9610e2558c98faaf1aed2490177be29780aee76  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-43.audit.jsonl
e955973027d7c698998e53cf3c3c46287fd0451c097c36ac852a8d3efd465c12  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-44.audit.jsonl
4798e3b1189748623e9049a515c41e0f340b9e9a78067ca573398470eb46458d  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-45.audit.jsonl
eff2698b468374302f074e62b341ff42e306810adbc958c06fb0e67a58cc1530  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-46.audit.jsonl
60a952d554feccc219fdf79813f739c91027b46d5792692bdb8662978aef2bce  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-47.audit.jsonl
eab40bd0a52137ff0c2fb342c7aae9a11352fa379338eca3c3581fbe0e0fcc47  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-48.audit.jsonl
17ee0a81dbbf01074cff67feb0de4393e0fbd839b768f0793b8bf9c39f8ef23c  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-49.audit.jsonl
f794327f56c62b30c9999e8373f8a45b89271203b91213f392af63fa5b48515c  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-5.audit.jsonl
b37933effed95cf6474dad056ac2e1b1e6052f9f41b03f5417d41b03792b4ec9  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-6.audit.jsonl
24fa302d0f3495aa175a1f45697b6179989af822fd23c104e54b0c237591052b  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-7.audit.jsonl
87c07bc354c77b49169ec406789204a7f0776e6e8ef7e298a0ab1a14ce3cffdb  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-8.audit.jsonl
fc55df00a5f84668d2f9bd366ff1cd0d1de7fd01aaa335c3a453e1150d2c9729  ./scoring/p18-crew-c1-gen0/audit-sidecars/replay-seed-9.audit.jsonl
3912aca8bcb4109ad0346bff3bdb7e4ddce4ea0463be068f060c7de8fc5de1d3  ./scoring/p18-crew-c1-gen0/core.json
0408a2437a028a05e160c4f6fae626e871489fd7cf82c3b5a49ab4fca06514f9  ./scoring/p18-crew-c1-gen0/duration.json
09b75cc2e5914767ddf9889bafd95a5e38f7e5532ad1037d268a75e4271b4e78  ./scoring/p18-crew-c1-gen0/funnel.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-crew-c1-gen0/instruments-view/roster.json
387e9109dd236c22d5080868d6fa13ccd5e81ed34ffb89bd0e1b4aee501e3e13  ./scoring/p18-crew-c1-gen0/instruments.json
41e584f2de2f76ff57c0b7295ac3542910a5cd8976d1ff35a50d1e1730736f5a  ./scoring/p18-crew-c1-gen0/row.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-crew-c1-gen0/split-h1/roster.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-crew-c1-gen0/split-h2/roster.json
5c628cd6bbe14be3104269a92e24640644ef4ea0a8ad62dcd6d4ec5eeec601a5  ./scoring/p18-crew-c1-gen0/split-half.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-crew-c1-gen0/split-test_mod5_4/roster.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-crew-c1-gen0/split-train_mod5_012/roster.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-crew-c1-gen0/split-val_mod5_3/roster.json
b6e44b119630ce77626755acb52f07d3e265304b2b5dbc83c7b88574e6ee7f4e  ./scoring/p18-crew-c1-gen0/stamp-proof.json
4aebb5eeb103174ecafc4e8c8823ae78fe2eb18c441a5ade6ef3017982113b1c  ./scoring/p18-crew-c1-gen0/summary.json
35538034a35c2ae21f391865bfd9216ccff64b55927f1a2a679b96e3fe1e7668  ./scoring/p18-crew-c1-gen0/validity.json
71a344dea1398c2f29404d2303d3c89a617a8454ab2d452125171e0bc09ab0fc  ./scoring/p18-crew-c1-gen0/watchability-h1.json
3215d540891a12d6ebb0633da881c6217fb67a28e91fe02c4165eddfb0efebfd  ./scoring/p18-crew-c1-gen0/watchability-h2.json
5667610e1d25a4ffdc56f5802ca907d92b14754da8c8861415b1182e15179248  ./scoring/p18-crew-c1-gen0/watchability.json
a48119ad62d58bec31352b337d792d2363e50155f960114438072a238d17cd01  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-0.audit.jsonl
c738c466965c3e9899e723a97c8d9c4155ae87ae462029ac8329f986f4ff086b  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-1.audit.jsonl
b6b9a4ba80bab4af3a85e5037c8792ccac48fba6cf3203f22c0f272624b1a66e  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-10.audit.jsonl
e30ca14b804ba23bbef7507ed0ad8a4d8ac43503405b40d25825634a3f9b6ae1  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-11.audit.jsonl
5583f8ec5c5693c860a82a9846f3449362ceb40906d039ada40a6f2af7045241  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-12.audit.jsonl
63dfd510d88d62ece28268d636ce421b33dd00f476f1ecb23a557515b5e8a9f4  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-13.audit.jsonl
3364e70d95678b5fb59789b5ceac9c33c51e3d0750e1447ae4c6d6e983450127  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-14.audit.jsonl
2cc408426acbc90cdac13c2378d8f509420d0e7876963a48025f9e69ea5070eb  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-15.audit.jsonl
73682a90cb331710a7f66521ec44ee5768e6d05fecad1730c09d9fa16d7d4cae  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-16.audit.jsonl
c68871e752f95a2bac0c102a70c3f913bf811e25401eaf9f52a33fdd5ff4c7fd  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-17.audit.jsonl
2b4b99ba701863b2e7dc9cfb02c2830136399a74c02546fecf076e0c307b1fc8  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-18.audit.jsonl
dc56e13633d65e2facf47ddd8c7f7bb1b245cf6f5ad5f37b5919b04fe35afb78  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-19.audit.jsonl
d3b602dc9eef0f8e0c26cb4f424c219d149e160c686e704919188fbc1833c4b5  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-2.audit.jsonl
36aca387373658a405da5d50da59ca35353e47b0251f561d7e7c9aa741cab004  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-20.audit.jsonl
98ab15283c1ee3fe7581267af567345f92fa95151a6a4ecbe60cfd0324724a2a  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-21.audit.jsonl
23b8ba363dc6e7d745b48983cb568846e08990a7c8a0aa71269895a1a70a08ef  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-22.audit.jsonl
7f5806251a6eb07680498a046d4723f6dce192b627affddb84edc3132c4d9683  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-23.audit.jsonl
640b01c5e8ce3f65531069f80414fa5a9d90cd06297bc7ece7cf3a04b0daff32  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-24.audit.jsonl
4d2dc724293aea121999a1049c95ffd6e3e1ed34d0614661e79a46a5655b5ee5  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-25.audit.jsonl
6266f2b8ef1eccc82667caba10e7470c91a99f7918d9cb9c9980fcc317730a52  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-26.audit.jsonl
adfc21946399931955ac2b2cebb0cdc565c6c8402b4e21127283f9300ed336d2  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-27.audit.jsonl
c9554d3039065f694934234920b4fa6dda2d395d10171d7a227c7dd3cb6203e4  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-28.audit.jsonl
a1113a521d5f1d54c248273c93fdd02d4806196d1840d1113fbd8facc7407e85  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-29.audit.jsonl
0d3c223f89efaa5a128d3cfc4e8bb24b2ba0d68f84c2d675c41493d29f689ef5  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-3.audit.jsonl
015964f5e92604e8ee57d6f9874605abefee15567e644eda41a352266f520284  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-30.audit.jsonl
951a9aae6e3eccbd988a79f3cddd17a655786361ca2071a13b55b61b819006ab  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-31.audit.jsonl
ee4ff54fe3f262e169598c02ebc2edac69e3b48aed9785dad40be839b8554983  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-32.audit.jsonl
b5e057649f98c405278039d11c50238cab5ae5b56a6ad2f35bac1c93d686ef15  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-33.audit.jsonl
2254726df5e560e04fbfff9ed6b6721f4a202b4563b3cafbe350787f3406428d  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-34.audit.jsonl
8ef40a3e567bf2c702942efd5c383339bf0da120c8300a5ddd997ea1f5f316b7  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-35.audit.jsonl
62b81d12747846dea9281a70569ab6f6c0b2c68322d2396bc373b9f886a76ae8  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-36.audit.jsonl
fd830cdbd78ab5124f5ef1383c329ea842ab79922a436c099deda3a7d0ba2ede  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-37.audit.jsonl
3e72933925967b72af0397a675dabcb839d4e4047f42452067ac7823c17411b1  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-38.audit.jsonl
0a61a9e162aea4f74a2afcc1a365f258a2520329a3967a5f7b1cd52008c985a5  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-39.audit.jsonl
6d218b826233eb5e28f7d1aefc4ba97484ad1df28354c1931a6205f71a6cc712  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-4.audit.jsonl
98fe1101ecd50a0bf6dde72fadb47acb3c0c012017efbd4beb9f708553123170  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-40.audit.jsonl
b35c9a13166222bba0f0eccc4af11fd55850685aa170eff8c23a1fab562ba59a  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-41.audit.jsonl
6c94931328ed77499a1a12662db9fac78a119e4d7551ada6648a7393844f38e0  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-42.audit.jsonl
2318b69f1e2524208d69cd5eee364c160be1d270f1bc1b8512b320d733e0c358  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-43.audit.jsonl
7834e2b132c6911a5a825ba64a26431e041ba804ffaf1ba2efc716d8ae758923  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-44.audit.jsonl
4239fad93bf26654eabe5b425e64f1363796d8f06ff02e7b3ba895382590f2c3  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-45.audit.jsonl
bffc4a656865932add7b55e1389b4f461540814243fe8327e79de728a74eb62b  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-46.audit.jsonl
3c6bf7318d5457ec264190f766ef8609cda080965964d4957b2e110f4d43b83e  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-47.audit.jsonl
32f704f48e233bd6d18188efd8cf8af31c1b0461501c52ce14db551fcafd5fef  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-48.audit.jsonl
3876e8dd75ab732aa8a8824d3815f1c970d750a712ecade7f4bad462b8229eb7  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-49.audit.jsonl
96ced758aa78d74b53bfa748d4fae734e1fdeb09eed129d61010d96ac7b172a9  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-5.audit.jsonl
deaa922006551a1e604fe9f4dbf874db27d100a87137d8e1661293382411e8c5  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-6.audit.jsonl
610ff274c30676fe7eb17bfd9a3399132ac676185271a1b175e9e82bd908b214  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-7.audit.jsonl
6b840715d5e8b5918d90a66edf3bd9eed40f4c868413a297994d1f5562f2e219  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-8.audit.jsonl
e2af8201b19a53cf1f95121c6b6bbe71da62972ccd21e4b9aaa99f861287a577  ./scoring/p18-crew-c1-gen9/audit-sidecars/replay-seed-9.audit.jsonl
c6d18aa7d4c11273593cb2d8d607a8161ac035500c6689a0d4a5c365aeb43636  ./scoring/p18-crew-c1-gen9/core.json
0846d7a602d8f827f97dbd38fdec7ffd348feb3190bd15de3e64137c8c763a27  ./scoring/p18-crew-c1-gen9/duration.json
a6b68a7121c8ad05a01e1dc4027750fd07fec7a47558400ce7e96594fac74304  ./scoring/p18-crew-c1-gen9/funnel.json
eb970aab184fd8589ccb03f2e3ad530c936f692c1136dc72b8aac1dc30079bda  ./scoring/p18-crew-c1-gen9/instruments.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-crew-c1-gen9/rider-intersection-view/roster.json
7042f8a11d515220096b297db915dc3cf32efcb3ec7e9e66a888924691f3bace  ./scoring/p18-crew-c1-gen9/row.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-crew-c1-gen9/split-h1/roster.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-crew-c1-gen9/split-h2/roster.json
e17a99177513740f640d68a55b7130079935e305f390a0681ac7ecc795a4a174  ./scoring/p18-crew-c1-gen9/split-half.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-crew-c1-gen9/split-test_mod5_4/roster.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-crew-c1-gen9/split-train_mod5_012/roster.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-crew-c1-gen9/split-val_mod5_3/roster.json
b4a1374f872bb1b317a3a3b0d5a4330df45375b578b01a966e7885db89658f0d  ./scoring/p18-crew-c1-gen9/stamp-proof.json
a87edbf95c234c8565c921ae7a32610b329236fff0f328caecc94e2554e5fe07  ./scoring/p18-crew-c1-gen9/summary.json
c1c9c13b6983ed318a215daa0b399eeb8690b54259a1f92eb3aab8c6b9254637  ./scoring/p18-crew-c1-gen9/validity.json
c41cdc9b97564b9d70dd78ce2a7958e918ca27adb1ea50980db9d117a4024bff  ./scoring/p18-crew-c1-gen9/watchability-h1.json
545dea9b305ab60dd82019c94e52c4bc903a8b852f6e9e439f482f5c915e640a  ./scoring/p18-crew-c1-gen9/watchability-h2.json
ff80c2428ce11f49a1951eee91417cf9d275612dab5c3e50f5ee2b136ad6ca97  ./scoring/p18-crew-c1-gen9/watchability.json
ddfb601db74fea77b3307b843fa0c596ff384df387045b0f4ab1d003302ebfed  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-0.audit.jsonl
b1d7eead58b28089e0d66f8a3f151e77279c2d44b2e3c1644daa52ed4de21ab9  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-1.audit.jsonl
09bf224bc76c4452f195e776c4c278c84f33f06916001b85670a5940af96981a  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-10.audit.jsonl
d6e8dfc8acf17b41829f13ac05741252bc8d4e2429ef17e1f28f2a4da28ade05  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-11.audit.jsonl
7234b35b73ef6a1a559270184b2394d1989618ee08b815876a5cf279e3463ff9  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-12.audit.jsonl
97f36851171c6206109cdf8285274746189656ba70730c24d53a934b6a890dc2  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-13.audit.jsonl
ea0628129efae60a1edc263cc7db9c220a5ec9d0c27c1a0afec6a744ac67343e  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-14.audit.jsonl
c59df6b944c3bc86eea54847e97194b7570f627e3f5a0b7762fdd0a8fd116992  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-15.audit.jsonl
ae3f234719b874764e95eb38f10bc759fd21236b7aca1d92ac4616cb3e0fcbea  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-16.audit.jsonl
3abbc3b2e1a72eecb074e93ea23d48ae9d977800e3c968551679935740f674fe  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-17.audit.jsonl
b01f1c6005f6bed73914c0f190dab866e6b9cf5d7742d460ee49997a95b841e5  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-18.audit.jsonl
9ccda10f71b6b1e4c26bc4fe0884076310e505f26634228a9f97e7e2d70d9073  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-19.audit.jsonl
15464da74a51ec966cf839dfcd430b174f7be0130fa43c5d00b440c0511eed69  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-2.audit.jsonl
e056d9e45868ae9c0e060e0c7bb50a947617e8ecfce63acbbca93ef567c676b1  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-20.audit.jsonl
c447275898a4f8e335e6adcee36459bf7133c175c9a8ed3b71405b1534c8db51  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-21.audit.jsonl
fe415adc9473a28c6830e09833391e20f71eaa68ffe86d290933c25b13be0037  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-22.audit.jsonl
03ad8f8910641185036db1fa830df098fc32c896d9820d3f1c20a2d8d89e97b7  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-23.audit.jsonl
132bee4d33e5fc20b656d44a9faad6d6cd41594a26c6a4b08647054a2f52ac55  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-24.audit.jsonl
11ab98b76962da0d36edd12a5700f3ee11c82502c017f9bfe6810e2e3cfcf605  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-25.audit.jsonl
6281b7a7394d14778a83b3a50b95d49ffb4e2489fadd1374fbf4eb9147e2c5d8  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-26.audit.jsonl
3d0d76f9d4eca3f06005847bc691897addcb58379c88c50510f3d8a00f2ef4c8  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-27.audit.jsonl
5497e8843ced9fb0458d87dd74ce1707fbce34264b2414b9abb24f5ec48a6c44  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-28.audit.jsonl
9d000b73aa39096b7c23c39a6b789e74f1d25841c388886056f78c393f625697  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-29.audit.jsonl
f9246beab01f5853a1c86772b14d7036bc672ba71185f4e3ef862889272e3aba  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-3.audit.jsonl
375f2e48462b5291f954ca5434fdb6a6206728d1d054b8c09f45a0bfe2f86e49  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-30.audit.jsonl
7f0ab07d58f74d76f1bebf3f7a0d35f0fbacf94d9fb4d0ac43bcd2c3ea2fa691  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-31.audit.jsonl
9cb92190d212b9809019b1688bf45f7880a6c570e165bd182c3ac52968bab214  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-32.audit.jsonl
1cf3a87f3f3a3d7ae98cc48189779da6721dda286bb08e51ee342cb394343bb0  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-33.audit.jsonl
3a8ed226641735ab0b699659f740c1d3b5299c64993c84475a2da53010e80c6b  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-34.audit.jsonl
cd4805c563d1727d0eb2af0a63ebcbf9aafcb3392a7352666db6c54fd0e8e864  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-35.audit.jsonl
5ef47dca2c2e21414f7ed8886b117c104991d4e70fc8c4ab2e546eb7367297d6  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-36.audit.jsonl
c4c73dd05a79d01041900a4f274f412050563f490f41a080f4e7f1742e1e9a0c  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-37.audit.jsonl
f604a5612529d319a39f6318cbdac87e769b875fd92d193a0c1a7738e1dc6f64  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-38.audit.jsonl
9987b4f42cbb46f75382cfbdf058c96b084d67d7a296df4f36a8ffc643cf7f8b  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-39.audit.jsonl
6e1b00bfc5cf720f24380e03a72a36d9a2577bca84ede8deac04791dce82c3d7  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-4.audit.jsonl
23693f03f7e3682cdee3c94c52dee10583a4ffb3d6cc4d90b8f9dbd07cb70831  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-40.audit.jsonl
fd3a1274677dbb8e85149b0794abf708b7ef81fb326df4f330420e9b8827b99c  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-41.audit.jsonl
a650de726a6f79dd8d798d5f23c5a73ddb26ffd60159a047d3ff829b377daaec  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-42.audit.jsonl
f7af7a1baf6da5d8977c25be57bbe91bc9df46778cd0d53b9035be54a6275f9d  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-43.audit.jsonl
e33d326521930fa4233f56e72802848137d970aa8dd2e8be6409c6e3a61c88c8  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-44.audit.jsonl
9f8db673bbdccc2c1ff8ee3a86d9dee160e04d75efc35d2fa0059aecad66ab23  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-45.audit.jsonl
e917fd66f56204b3ea23dc6a7af6437ce63b236dfc23a6e474ace50c1bb7b20a  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-46.audit.jsonl
cd692206161e5c0d3dc7f2ad5c1c566019ab624794ce869e77abf86d9383cc43  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-47.audit.jsonl
2bc8e19d85196a62723cfa7558cc79cd9c0b03ddfb5b7cb2b889c0665630b22c  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-48.audit.jsonl
3a38ca6b4754a426d50919050dd63c6a03d41ae96d3e94dfc1fc5e7310024576  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-49.audit.jsonl
2b3f6ac0465539c3b7a4625a762e0828ddcfac80e90d8ddfb6b9307fb525b0a9  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-5.audit.jsonl
dbae994a83b71a8672f9ca0441204104ebc96da18eaf8a9617a09dcf1232665c  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-6.audit.jsonl
799b5f51aa37bb25724689dc320a7ed53e6fda59b1be9bb1861c890270a2b6e5  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-7.audit.jsonl
2df168f1082b0aaa09085de703f9da4001c16f0242298bf31613f8580ba02dee  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-8.audit.jsonl
1d9d4fbb693e625016dfcadd0b4488c3c3689ec62cb2c6ef04898f0f145c56d4  ./scoring/p18-crew-c2-gen0/audit-sidecars/replay-seed-9.audit.jsonl
fd71b994b2ed0906958225562aed0a758778607d66dd06c1f7c8024cb96e9800  ./scoring/p18-crew-c2-gen0/core.json
c919011d2dc3c8c1a55fefcf61fe61dd4775aeb401b54f22b64acc4f3a578ac6  ./scoring/p18-crew-c2-gen0/duration.json
cd99c2d0552ac3c421ff46a2a2036c9ec110809ad89088bad03c07dcdf14b461  ./scoring/p18-crew-c2-gen0/funnel.json
464bd6d65511df5472b82506bb2f01a94164155be3beddf252eecb82356f8439  ./scoring/p18-crew-c2-gen0/instruments.json
630eff0219f40db7e17b07cddf6719a5eb4d793893af21d0f9d582ee213dd7ae  ./scoring/p18-crew-c2-gen0/row.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-crew-c2-gen0/split-h1/roster.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-crew-c2-gen0/split-h2/roster.json
6f74eeb39901eb4b903b30a01177a579b728e89605bb848c2660252a69c23369  ./scoring/p18-crew-c2-gen0/split-half.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-crew-c2-gen0/split-test_mod5_4/roster.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-crew-c2-gen0/split-train_mod5_012/roster.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-crew-c2-gen0/split-val_mod5_3/roster.json
617b602c6ecc0498e00566e298a81ae70c0276b3af7e394d8ee722399f6223e7  ./scoring/p18-crew-c2-gen0/stamp-proof.json
9123124601a5bccd0840fd54cde282d719539b3c49b0309d19551e9bb40b363d  ./scoring/p18-crew-c2-gen0/summary.json
e498ae8544cfa226f1535b9de3d9a36269e237a5686983982de4c48db37e7248  ./scoring/p18-crew-c2-gen0/validity.json
ecc63cfbf9ea9b89b1fd8b8fd527d381a5576ef45c4cc440ac14722b71ea1e11  ./scoring/p18-crew-c2-gen0/watchability-h1.json
133b52ff9cdb86ab6a027badfd17d9b9f83fd68f953566f708e7620c4958cb6b  ./scoring/p18-crew-c2-gen0/watchability-h2.json
3b0190f1ed3bb9b913cc9436370ec46b589d1385bfcccc92e97ee159bc88df64  ./scoring/p18-crew-c2-gen0/watchability.json
2d85f039ac18a2c465edb2e9bbf333780e944430724f4f78d387aca33cab9106  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-0.audit.jsonl
b24e8ee7c1b421803fa9344af6ee7955d720c9a69bfb72828eead1329299eef8  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-1.audit.jsonl
9da4ed74671ccb12fa5ddfb876b53e91637e2ac75d90303d5e71939f5b89aa64  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-10.audit.jsonl
053da8122d266cfc4788ca847ca4266358c424b8433b0680aa88e2b0e3d4a24d  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-11.audit.jsonl
670b9e899a0e5c272091967e7f857aad60067d67c8f5fcee6cc8724001bdf4cd  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-12.audit.jsonl
bb8a4bb09551857b5714a0a9c3e6cbb62a044ad392f8cd10215e30f0d3b24bd6  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-13.audit.jsonl
2c4e245fb54208478b8011edc080722102c8e4781a7587cf05d6f4169b926189  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-14.audit.jsonl
482ff8c3afa7680d63d8b30d3ad99fafcf8a9d3bb939b30fbe7f7c81090ff101  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-15.audit.jsonl
fcd6179470ab5395bf04ba07c819d1fa6963527a8876a3545ff2acb8afeb3fc1  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-16.audit.jsonl
6d46e1d289b5bffd6f8c583608af39e25e1d09cce0891a900a0d426f632d5a4a  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-17.audit.jsonl
cd42a278a60e51b993ac76e8b10774e447502aad19fb70ed85ac6eef2417cfb7  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-18.audit.jsonl
aef60edd587e2bd19a609d992e1b6ff9bac52558c77f60a882bbce7996fdb395  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-19.audit.jsonl
efce7cf77e9ee1796ce982fc57f4a9eae6c0723271ce4f3e3817a2dd4449c3c9  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-2.audit.jsonl
cbbe946a2ea4e87832c206e17ce138eee18a6f1bd1085f82eda02880b99d48ca  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-20.audit.jsonl
156080e2fdd820f08777cc4eab99632f62ea51cee6edb0d1096447aeb0d19e48  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-21.audit.jsonl
c0fde0020d5229fcf4c8548be6f17f8e5363436bf2f7fb9a1503ec781f5e4160  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-22.audit.jsonl
5602483f0a31c719330e4951d4084a337f012cad230d6d266e77fd85c869625e  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-23.audit.jsonl
55a0c5b38eab03dd6dfd5fb91ad1d52452dd1121b37593ed8ecaabea8421e9fc  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-24.audit.jsonl
9906b76560e053f312ecb1b0be9aca05985a9ab82ebf59c9c934914809e27fea  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-25.audit.jsonl
481bd80e6b0d258746ec0448501e834cfbb11d5692199ed653b78d0c407b4e87  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-26.audit.jsonl
bc43d206b4a33623037c9a5537ff929035c8a65f70ae296843798d0e701bd6f2  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-27.audit.jsonl
4d23cd6a5fec5a691c1230e89779026b6f676fedb485dcae2e61426d59507ffa  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-28.audit.jsonl
9d000b73aa39096b7c23c39a6b789e74f1d25841c388886056f78c393f625697  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-29.audit.jsonl
bcb994352d32b3a940db263696cfc3de7475d23228b0164076ab98a142c9745f  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-3.audit.jsonl
0e312dda7bddcc4d33d9e152601081b07a95468157867f1576ba8fd78087b801  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-30.audit.jsonl
1ffa93351e2b0777e83f9ab9c530e87a7d97575c6a8e0c4697275876701e9050  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-31.audit.jsonl
9cb92190d212b9809019b1688bf45f7880a6c570e165bd182c3ac52968bab214  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-32.audit.jsonl
8559bc2810c71a0ef277dd909e2c4acb99066e174d985c2e1e1e6cdcd372f857  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-33.audit.jsonl
d0c4fddb230502959f3c2d6981c842c8f39ecf70d9acaaefe485471a01e66d02  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-34.audit.jsonl
cd4805c563d1727d0eb2af0a63ebcbf9aafcb3392a7352666db6c54fd0e8e864  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-35.audit.jsonl
981f95ef52239d5fb2cf9ad0edecede73ab5ed02f4e160ae127686c0ce2ff229  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-36.audit.jsonl
58970cc0888e2ad0d6ed34e017c70b9ce8bdbbf811b805845b4a9f406ff4dfee  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-37.audit.jsonl
1c009a10468d74bab2a8319224923c395cdc973adb9c22321fc167f2cb702a10  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-38.audit.jsonl
c78f676ba07231df0366ad96ecb6d221500c61b9952efe69ab95abce737a4fcb  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-39.audit.jsonl
6f832d763922d1d94189f7d47a7f5674ab9e012cb18aad294d55c515631ef366  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-4.audit.jsonl
6bff76cca5c18141f891fb5449a025ab902e565234d609888a0482b32304023f  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-40.audit.jsonl
704f04ca7538e5e50e196279f93e27d5bdb8f309d92f104c8ad246d904c8454f  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-41.audit.jsonl
4cfe442cde484f73e52e9a78cfe4465711fd389314529bbd51c971a6ca855ac9  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-42.audit.jsonl
f54781d5a08d63a8d6433179a7c63b34ca0c9f8a57c260376b6623fc1e5f4d7e  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-43.audit.jsonl
a638d69c95a90be24de2ec36ca077a88b97785715089bbf703c74f5b45712764  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-44.audit.jsonl
36ea0b7e37f4182d0771f5db1094efcac191ed030e693978f64c95da2f09d15b  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-45.audit.jsonl
f2f0a5e50b413bbeeb22a3c9fb50a9fff26aa90deee16d130b2aa8c39bbf8da3  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-46.audit.jsonl
4ad22ded84633e92e0af7ffafebdbd5692e2d555f5b48789f715b42c844c67a5  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-47.audit.jsonl
e9c2f7e269057c1d72073e697bad6ad34a92fb95d557389888ca8545e24d168f  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-48.audit.jsonl
4bd3926d4b40608adda3c7e305109c314eeba7fd80ff9cf4eeb3f5fb5f69a4f7  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-49.audit.jsonl
7c9335c18610c3f88f5eb90e862d58d5b08e48a40967584fceaa60d0a00a2aef  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-5.audit.jsonl
fe4c80fca1a9f90b9e993dda65a7bc47246b1e0f0e5a37853539c574544e49a7  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-6.audit.jsonl
b54ae5a70f1927114396a55082dc166d4789bd8258bef686e7ef39e6adf59fb6  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-7.audit.jsonl
496036a8e92a5f96d31f507f5072af7b96452e075ad4dc69988aaecbaad7d4b0  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-8.audit.jsonl
124db50a7f63389147be0e52bab563ad3a6b04777ce151880b5dbfe4b79ae31d  ./scoring/p18-crew-c2-gen9/audit-sidecars/replay-seed-9.audit.jsonl
7a43d0987472af059da046deb06def0177c7ce6b105c72ff5a0e62d1a92138ad  ./scoring/p18-crew-c2-gen9/core.json
0e507bd4b2bc16e3259bdc895998014ab3d82e88cda2ca7d89b86eabb07bd1ce  ./scoring/p18-crew-c2-gen9/duration.json
5b5000f49bbe785ef40d5f74d3e12d3c3414dff7d407a4bdf5e42601be9e249e  ./scoring/p18-crew-c2-gen9/funnel.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-crew-c2-gen9/instruments-view/roster.json
1d449e3d0898473f8938985eabe624467ae69c220d88c00af520d970d6a045ac  ./scoring/p18-crew-c2-gen9/instruments.json
ba4d4f35f4a00e8716bed2d9e6d236a4396a1afbf7138a4006aec8f2acac7fec  ./scoring/p18-crew-c2-gen9/row.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-crew-c2-gen9/split-h1/roster.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-crew-c2-gen9/split-h2/roster.json
0afd5c506f8c248dda0027f35de67f6ea236a82693a00eb33c0d3c05efa49d6c  ./scoring/p18-crew-c2-gen9/split-half.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-crew-c2-gen9/split-test_mod5_4/roster.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-crew-c2-gen9/split-train_mod5_012/roster.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-crew-c2-gen9/split-val_mod5_3/roster.json
c23e47aab5ae84a6a458bc6157c93aac7a3f419aaee321e5c40f1ca4b121d34d  ./scoring/p18-crew-c2-gen9/stamp-proof.json
37f9ba1723cdda8f4ba2b494c96aec47004064695636e787779191057985b4f2  ./scoring/p18-crew-c2-gen9/summary.json
4cb618a692210fd92dc6094d1c264b72e381f042341f0f0124c3f598fcc583ba  ./scoring/p18-crew-c2-gen9/validity.json
ac275969b43364aff7991c6e6b750e42d30bbbf704eb6b8dccd771b490ddc16e  ./scoring/p18-crew-c2-gen9/watchability-h1.json
1f4ff2ae0ea81c4c26c8c38e4654fb6c8d4bddcca12720f2ee1efe41f2f7085c  ./scoring/p18-crew-c2-gen9/watchability-h2.json
fffecdd1bf9a2cc3343e44fcd7d29fd7801283d6fdf76f10fe635d96270bff95  ./scoring/p18-crew-c2-gen9/watchability.json
35d7513e21dff63a704166cbf5726863e03ec63dd1dc76da8c561a63b38c2a0d  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-0.audit.jsonl
111570005c5296f4afa1cce674abaa64d8b9c6cd40352a6bf3f6d1b09b30f4c7  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-1.audit.jsonl
59de073a17770bd0de465fcb7fd3a1d4f7e00b95feeb9ee1899bf17356d5e106  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-10.audit.jsonl
4569802d99138267aac51d2ce626d17a6d31f9bae4310111ab40eb39573c1ead  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-11.audit.jsonl
47fbbe88c63946f9ec508bef5fb2ad24f20bdf906b726ef357c0b1760ce1421d  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-12.audit.jsonl
2aab5e0e697ce65a59a281e31eb6aeb28e2e9cd40d2a720445b15bd782d6b4b1  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-13.audit.jsonl
e92421d689306e5ae9d3800d179dabfb8589012189a0faee29bb0d770bc50d52  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-14.audit.jsonl
422cecdc71246b92be77437d9779d30c0dd5071e5f0d59f8b5da339501efbd3c  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-15.audit.jsonl
5e94551182648da11fd5d6d5f8eb48568981cb15108fc929b664883368cc5a4d  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-16.audit.jsonl
c5cea379f9a1cfc8cdaca71685173ae8265eff56bf56add9c72f1dc104f4bd20  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-17.audit.jsonl
3c7393813151bca7d8ff82f3a6cee53d109a12b1458e294a8d15f81095d92d71  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-18.audit.jsonl
d9f3cb8429ec2d777321af99437c4a38f73894eaf5b676c04807af6627f30de2  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-19.audit.jsonl
7e8699023bb8a2d5a315631b4d8fcf6b6753cb1eb540068a5b228011adc02b43  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-2.audit.jsonl
c0d08828e7a1a057f522be38623149f7bc19147e5f79233c1f33b0a4d9e0d534  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-20.audit.jsonl
5e67b06ebe03339cda106bc91e1b056315ae1c5d2f82ea18035d2a389b3e908b  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-21.audit.jsonl
b6c91257c6d8f755e6b78d3ddc09eb162f6c1bb06c80faeafcb0f3e22beee017  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-22.audit.jsonl
fc7baf6cb19fc0db3f7d928e45439918c0f347b36ebcb54fa8ebc18ade67ebaa  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-23.audit.jsonl
e0f8d5208216ef603855c2bdc56cd9c4447f8fa2c1d98705069e3f04374919c7  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-24.audit.jsonl
db4cde2d0cae60dd65b598b055c0b865b9ce8f94087ebe7790018259fac6280b  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-25.audit.jsonl
5dd8c5bec8d5d15efa9165422356f0edbeb70fdb048c51f97d23826cbe3f25c6  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-26.audit.jsonl
c690a16953e6405a896148a8d128e549a556b1f42e1ae942b1d9517938babe59  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-27.audit.jsonl
0eba4139d0ec8098846671d7f37a098ec6ab2fa65ea7024f4978cc34a65b3566  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-28.audit.jsonl
f4887e26665fce44bef668539bcb9e2311f733c46d93738d09b21cc61bdcdf02  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-29.audit.jsonl
afde563f52f2301f320f7b5d129f0f8e3671ecbd2b878c74d4b8a385e14d9be7  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-3.audit.jsonl
35a284c6a8a92c2c05a6e79b2cc6475ebecec4c27e08d6226b121dfa41ae8bc6  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-30.audit.jsonl
8f2f4c61a7c82833e90cca3284f41a3afc578b70db3ce22dc4d1bc9915ff0a56  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-31.audit.jsonl
a6f5f9f013c10704e2702cef58d6c4a1a1c3f1c357fc41a1d09f4560ec0b5fd4  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-32.audit.jsonl
26db869011398d646f52351be4a9243caaefb24768d296eee02d5a06f026366a  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-33.audit.jsonl
e7c0cd68dac96076f40c14e769863bfe3fe985a4ae5323601bc48e422055b215  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-34.audit.jsonl
ee1e1ea351cf394fc0cea2993772e4eac588fd195e53e72dd4f3183e991d9b8a  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-35.audit.jsonl
ecba3e9607891bd414e45c80695c01300cc28622f6d094f68f923792435f0ed2  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-36.audit.jsonl
9934f1c2db70215e62e14a28062a58b029425623d06ad8824df3248ee553c554  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-37.audit.jsonl
d5d98cc5024f1eada4430c8a2fbfd785e882397fd8a7b0e2da838a49b0fd9d19  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-38.audit.jsonl
7fb6647832cd8de9df034e5fab3a155ad714860c6085cf8cde899e109fa929ba  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-39.audit.jsonl
822e85bd6ab4a65ef2d8e541c8841bbb924861023f9ecb82421eb24e62540427  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-4.audit.jsonl
03c20bbff28ce1d70adabfac7ad2b78b45c20e8bdd5a4abe630faa0bd769f75e  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-40.audit.jsonl
63e6d00a89bacbafa26b3c9b4716abd71616d58c17b2d53af5c0c9c793bed988  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-41.audit.jsonl
164820de960ec08ae77b7662355d6d8409510c24a32dcdc4df2c6945599e3faf  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-42.audit.jsonl
6acda900e0bae597f751e939bc1cd0b57a4932b07a509ca53189c2d495e38fc7  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-43.audit.jsonl
65fbe1882b78272f802bea341172e6d399e8244832cc8cc013387e95f437a381  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-44.audit.jsonl
5024d35cfcade0083d5750b4c41c91633638671cb86f8a6ce06c6ab7aa308752  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-45.audit.jsonl
05141b4800611a9385b23185e9288717972a176b37c9f270677220b8474315c4  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-46.audit.jsonl
a722f2cc2527616f5d21b18c03b61fc371a4596cd6cf19cf532d578a4840ea3a  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-47.audit.jsonl
cad18da10f256c04326c2496ea1fe3dee7011836ddcdb42f16a274566981a67a  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-48.audit.jsonl
6303e21bf8b78106a2aaa0b57a0094545ca3ec5951ca4eb232b3ecc57c477d77  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-49.audit.jsonl
5ddb8c3e2912e72dc4643a9e8a8ed5e952beb4d3352124aecb321925f46fa68c  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-5.audit.jsonl
8b636a065b1cb9ebc3e25495a54db70525736dd2bfa159b3f0cdd6a3a59e65e6  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-6.audit.jsonl
e2b2590a85d9f872b8008edfb5cdff5c5b09f358dd23d2870a6357310767e7ff  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-7.audit.jsonl
f5d3cd7960d744bedcb5366ce6cdd1ec521c513741a33c69b42f9c5595cc07f1  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-8.audit.jsonl
2a3d67cf301a0884075a661c785cc7d4986c95ca80d73b3cb55d4d22b578d8cc  ./scoring/p18-fsm-comparator/audit-sidecars/replay-seed-9.audit.jsonl
08596c636e9dd7a0e2cafecd380e8f4fb05705a2e105f43eb12597398124dd6e  ./scoring/p18-fsm-comparator/core.json
bc9f9b5021bef101ab53aaa07781e6a7211eb25cceeadca8b40e0ecfa4c9b3d3  ./scoring/p18-fsm-comparator/duration.json
66438d780163cd3349fa82eb128a91b2e5ea0ef593c6fb455bf4ec299119cb98  ./scoring/p18-fsm-comparator/funnel.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-fsm-comparator/instruments-49-view/roster.json
f574cfd4e77fcd73b2ae914db9819a720ee573a471ed384ed39e12c056255995  ./scoring/p18-fsm-comparator/instruments-49.json
9dfbd57c4db6932562061de41cd17cb504815733a744ddcfc5766b71930fecd6  ./scoring/p18-fsm-comparator/instruments.json
2193119c57641799b4931e806128a53c2baaf8d41d05e74cc94e02110672bab1  ./scoring/p18-fsm-comparator/row.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-fsm-comparator/split-h1/roster.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-fsm-comparator/split-h2/roster.json
419a317fed402ae2cee4265e813ed65035b8008f6057ca1cdf45f3d921f39664  ./scoring/p18-fsm-comparator/split-half.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-fsm-comparator/split-test_mod5_4/roster.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-fsm-comparator/split-train_mod5_012/roster.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-fsm-comparator/split-val_mod5_3/roster.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-fsm-comparator/split49-test_mod5_4/roster.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-fsm-comparator/split49-train_mod5_012/roster.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-fsm-comparator/split49-val_mod5_3/roster.json
0207f6e448c2402175e75d5de921fce14b42049418fd2fd7e8d67bbc5bef517e  ./scoring/p18-fsm-comparator/stamp-proof.json
a86a67a6f529717c31bb3ea1a40b1f9dcf50bb8363cc4295d5167ede36af7e19  ./scoring/p18-fsm-comparator/summary.json
918f587f731ccbd9b683839650e09b105e2b6786b7068f2e4e5642d9d4e0399e  ./scoring/p18-fsm-comparator/validity.json
66e535c5cda63b912b4b6c99a7c5314f131c54f08a94cb7a78292b814f9f62e3  ./scoring/p18-fsm-comparator/watchability-h1.json
0fbdfac5a80b18c815c79bb466980e4310e62b728561abc8bba7fa12139e7c2c  ./scoring/p18-fsm-comparator/watchability-h2.json
ecbbf513c4632a9775e9b50607c4ebb9a72da10f302df78cbacea5122aad397d  ./scoring/p18-fsm-comparator/watchability.json
a3d34da25124f607e7363871a3155a2cf0652d5dd2fac841cb1a5d866e4649eb  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-0.audit.jsonl
0263f331c1820a8ffecd023bc9fe8ae967c2f84718ae09dc8bad2758919f646d  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-1.audit.jsonl
da3c545143d4f5556123cd008b2e93fb570c8577392ec5bb88f56a322199acc8  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-10.audit.jsonl
0e7d1528f24c81c3753cbf1ad97089cbaad1369b5703b10b215c6deedfebc854  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-11.audit.jsonl
9c31fb0bff5764c2cbe96d0ab05bc87dc08999b3193863562d64bbf1990c71b3  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-12.audit.jsonl
e0f4c852c362a58b715ef0fa70c55e571cf9029c680527582263a85c2bda152a  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-13.audit.jsonl
c8b0d02dfbd5c1969d2a82d8ba3247455e0216f86ee3ebc3b2f15a5447ebee0f  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-14.audit.jsonl
9a5ba41f4e07ee7965e5383ec312e3c635a06b313f6b83f05225d328b5ffa051  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-15.audit.jsonl
452f9c6e75c2d364cbcec139a3d508da0dfee9f52c173cb0ec05d3f62c912fec  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-16.audit.jsonl
1fe127c16044f1d5bddcf86a68d12c682db130c023938727aa613b5f375378d0  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-17.audit.jsonl
6a3cd6db72a7a738663d5bee9a2d07ef4c563b052cbad1b4a2e595b61718677c  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-18.audit.jsonl
9cd531046e49d04e9be520d194b2db48a43f163e343d592b57ab609763f520de  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-19.audit.jsonl
3b641f1eecd20527d845b32094de00f8396f4f8f6e2b93518a7f520e331cc586  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-2.audit.jsonl
0c58d6dfc4d080dbdefef02501d8866c21d93b5d10058dc244f9ba473e54de12  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-20.audit.jsonl
a7540a9638f99a2fd824136a5ed779756f4e1a4a7a825eb6b8d0b54303e4bb09  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-21.audit.jsonl
d87428535e17eeef18f6f29b28a6de34bd530dcb5bc5ca787262834568900d7c  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-22.audit.jsonl
a9add7a99c9245a6029fba14389d3b7fbdd47b2d04c8535cee685c0d7a640369  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-23.audit.jsonl
62d1b0f7859f440e8aeea18b784e7b386abb6df18b44f8808f1bde9c62ca6570  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-24.audit.jsonl
faca6c6932500919ba8f8f70ebd87704c9c9ae9911fa66012b434f24fdc7fe75  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-25.audit.jsonl
35217f918c54c158a04b61e0ac1acfc502de501aeb6c9516ca5ce010e7b42bec  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-26.audit.jsonl
4bdfa85d1779f54ebab345d0e69f2db7fcb5d9a7e6dc85f06a74816fc23396c4  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-27.audit.jsonl
656589f2a4c8f4166ac610c4c93d99e2033528c1c4761ff537b12ba8f75187ff  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-28.audit.jsonl
8af74d9c1cb8450b33a5fb8af65218f478bd756b1e8dcb8548da34be0ee43c10  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-29.audit.jsonl
57dfc888205a84d7215f29a55bb6066909e54129dd30e008ba7ad419ea850b76  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-3.audit.jsonl
83a882d87886ed7431987124621fb49025dc053f0660c252ced678c245388139  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-30.audit.jsonl
399e83236471990eae84365dc377b3efb80f4ec2bb93de691718f86297cc23bc  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-31.audit.jsonl
86a1f34e79746626877782320808a48e5ea05ddf4a7af342f4a4f792e61fcc14  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-32.audit.jsonl
f0028adab46a7db0f324695caebe4b132dde8636e723b4ca25659cf91695a86c  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-33.audit.jsonl
ac1ca846972b14f35d6664ad5b0c5a14a00ed904b20d17bff64570343c765f50  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-34.audit.jsonl
49d6a95412d4e9019cb072534c9de4a94b26fa87ad9efb5d96cf4392368ce61d  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-35.audit.jsonl
30fd9e12a0860b5c6d8bff6e1484254d12701e4b5402ec1bab5f1f6689a29e49  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-36.audit.jsonl
2cbb532af997cb3e33ed1c20bc3b4ab79562e436e5f6e58b0be9f6d0aa9664c1  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-37.audit.jsonl
5f12e36d0199e335d9b9c615bc98289903db05a787f6169f396fd49f1aec3e6e  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-38.audit.jsonl
f2bbfd9c6a6f2d8449dc5c613befad753215f5c1dacf25bda4b7528b36848f6d  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-39.audit.jsonl
754ef666804ed3587bee747f723645ca95576439b3886d7a5465c1f642c7f23d  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-4.audit.jsonl
ffb685efb0a4296e6a34e29e9f5b3a0507f25a218920d16824448f063953274a  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-40.audit.jsonl
53bd23e93234d34d302a0dfe41121f8bfeddf06ea73b7530ca5e0fa9ca277011  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-41.audit.jsonl
a0ba6d9285fee1de26e360df6d4a2a7da809c112143601004fec21afc9d67c14  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-42.audit.jsonl
0fe768e5437f759351b9d996eea31784f63e717f29db4411f77b4b94ddcf8d63  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-43.audit.jsonl
d8b1b954f7f52f158c6202cd6df1423500116cdd6edec3e7e5c1ffbc0d56749e  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-44.audit.jsonl
2c667ff40b019c93b7e618721815c0643bea17500ca562a25b822a16ce19e83b  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-45.audit.jsonl
c5ac6c20bc67448a10c76132f0aff891761560a6093a66a0fdee5dd9c2f6429c  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-46.audit.jsonl
a0dea8dea1adb3a4d55417ff2cd6d0043d12ffc3f17b23bee56a6d7446e9a88b  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-47.audit.jsonl
1c4f6923c77c47d53a1932a8d73fa7ab15be38cc11733baeecd7e75d4dff20e2  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-48.audit.jsonl
24e57748d1253af91d6ad08a85d20cdbe22f8fd665c255784fe22e1690ad93e4  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-49.audit.jsonl
384194df7ce18f8745159a5b556eb26d2de46e9698eb6206153505f1749be2cd  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-5.audit.jsonl
da9dde36b0a2e0606d29dccbd1a04df1909547833012c6580ebc0b681627059b  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-6.audit.jsonl
a2e5c5238b5acf8f0206b8c9cdd2c5b7f99018975772100dcc5edb47b67736cf  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-7.audit.jsonl
d80e14db9cec398205f5df62752e195296537c6bf4a5a2c59e7544066f3fa933  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-8.audit.jsonl
18f050b517f27df8afae543374fd67fe2a45df586f093228567a6c1e2b0e08de  ./scoring/p18-imp-6d327dcb/audit-sidecars/replay-seed-9.audit.jsonl
791c5e322a5df86e8b583084c21615191d0a39a316dcd7636a98ad977f3fd835  ./scoring/p18-imp-6d327dcb/core.json
755734946027d15f596e35c501e59cb54a08b4674eb4aa26a3928c8e37fd3cc7  ./scoring/p18-imp-6d327dcb/duration.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-imp-6d327dcb/f13-intersection-view/roster.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-imp-6d327dcb/f13-split-h1/roster.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-imp-6d327dcb/f13-split-h2/roster.json
e3a13720965fde7d9cce699bf8a36600a0594e4d94bd4154a201e1e59a926c21  ./scoring/p18-imp-6d327dcb/funnel.json
abf89c38cf0bf8e3adbd17ede3f035f114ddb9d61583c614401f0591bdeffd7b  ./scoring/p18-imp-6d327dcb/instruments.json
347656f7edf28beda6333aea42209671fabceb6a4e5b47b74576f76395168fbb  ./scoring/p18-imp-6d327dcb/row.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-imp-6d327dcb/split-h1/roster.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-imp-6d327dcb/split-h2/roster.json
7137ef95e8b14c4c4acee35cb83c161273a5a9ec75bd19249e46c105dc53863a  ./scoring/p18-imp-6d327dcb/split-half.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-imp-6d327dcb/split-test_mod5_4/roster.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-imp-6d327dcb/split-train_mod5_012/roster.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-imp-6d327dcb/split-val_mod5_3/roster.json
3ac1a33eceff06e88f41fd5293a335755ee19bcbaf4ea0f008247026efe0dc40  ./scoring/p18-imp-6d327dcb/stamp-proof.json
031710b6c1505dd04a0e742b82eae6043575745f392e4bd8635512decb3f4a43  ./scoring/p18-imp-6d327dcb/summary.json
118eb3d0384db2620f5063a2490cf3ef024a91cbfe4b1f5f8f687e6b63c02315  ./scoring/p18-imp-6d327dcb/validity.json
60b48e514d1b373e87459bbac9418b9482722d39b193dd8ae0bcb41989e58e2c  ./scoring/p18-imp-6d327dcb/watchability-f13-intersection.json
8b17446eca5b1d0fecb3e072082125b536e669ea6530538ca415060001320b9d  ./scoring/p18-imp-6d327dcb/watchability-h1.json
c280088e810cf3085fb042d02b638731566509123fec48c67ab34774dcc47051  ./scoring/p18-imp-6d327dcb/watchability-h2.json
c8753e386e98d54a7b0d71199ec786f6e3904e405116589d81eaf7d8d447934c  ./scoring/p18-imp-6d327dcb/watchability.json
496ef05159ce421e571cca8c648091a73cd8b1b260514be96f4dafe6d43c7dbe  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-0.audit.jsonl
0e39fd79aeb6408be13227db98032aa30b6df525df46813abd50ef315e8af870  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-1.audit.jsonl
27208ef7985bfd5c17cf8f696a41e8fad865859d717bd30bfa8e11026e4a351b  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-10.audit.jsonl
6f69efb29daf2898ac0ae5131c60a11a5687df6afa4f71c77083a2e25f492cf4  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-11.audit.jsonl
8e6f1ede9e13e9ead580716384cda3e72621f41eecc6ad43f1e1f3296a579b86  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-12.audit.jsonl
b67c72f4c6dc9aa52b29bd7f050948d270daf8acd30ec801d3b1b45a1ee20231  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-13.audit.jsonl
0ee5d01cafb065fb884e7cdc0f73bdaf0b8895cdf068252753b038716937faaa  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-14.audit.jsonl
771cad241426da7372ffb829f36bd6b5e1bcad0d2d7b41747359ed1edf8e0eff  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-15.audit.jsonl
337f348f0847c725e98fdc70fdf8140e2df0bed0cb34e39793b2ea50d46cd808  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-16.audit.jsonl
17add5da06d4e49306c88c78de39565825cf7c57ddd312128daed83cb75c8019  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-17.audit.jsonl
f386184515811d0478f5032ad4a650179f1f3cf65caadf8cebeb8e46ec4a872b  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-18.audit.jsonl
cc81d1bf335f8c30892024acc0f4d7ad6e7399acd32b6e47d08e9590b082d36c  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-19.audit.jsonl
9b315041fb612ad785a3cb67eb9b690299879e82a06b9d75c2b54b6d8e1598f2  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-2.audit.jsonl
0c58d6dfc4d080dbdefef02501d8866c21d93b5d10058dc244f9ba473e54de12  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-20.audit.jsonl
99b0b22e8366ad5534b8fc991d9ba63c64ee0e9ec9fe45e9ba111ee15d2304c3  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-21.audit.jsonl
6949d1be7e31c8393881d1442d7b262ea473b3194ccb56680159a761da51ed38  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-22.audit.jsonl
2336a9351aaef3d5fcf0a82d5ec5f9345b832ef49faa0ed237e88866838997f3  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-23.audit.jsonl
b880f84d3a5106226cb7fe8b09fac7c967f1167666e1531b59a7cc9b5f2e8916  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-24.audit.jsonl
9f12da2bfe71a2f903483607c6b29662cb0773cce9e40e8cd6b4eded3b50de55  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-25.audit.jsonl
cfd88fb92597b9a1d5416f2d540d5de1df7cf25b9430b2f89b143eea7ffbd864  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-26.audit.jsonl
e1ad99e1431d5d75d08672292b7e58f616ac7c49f354592e23f104871ad9d3a3  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-27.audit.jsonl
2434a12749d5e52751dac74ede1e2f61790030a99b15b9df58104555527da26a  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-28.audit.jsonl
1041c15e7b2f2c8c9c8009870cc3c668cde1ffa32bdea4bdd6ce3590da7b7311  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-29.audit.jsonl
958420e76ca6aaa12757a48e6d276b34945e61332153f1803dd37841604806a9  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-3.audit.jsonl
d434edd7b2ee2f82e75dd4153931addebaa52893401f65f8f530233c8a7943c9  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-30.audit.jsonl
2aca177ba8312d2811c43516f2419f75d369ab46ffd72b29ae5dd73cdfe75304  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-31.audit.jsonl
5d2d9b9949f3a20fc656fee8d32d3a6d65307e91bff9e426960eb347e1cce31f  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-32.audit.jsonl
8c45d8afe9164bf84781376e567b31b17e15d40f2a2f7d539287ddc9d68267b7  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-33.audit.jsonl
9b793404105515fa20626abc8196b0212b68a378d51bc1a1d9d2e2bd3fc87bed  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-34.audit.jsonl
5bd200f955d46ddc20930a968dddc02c05754ccd0cf0cf165d6bf30eaf8d45b7  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-35.audit.jsonl
797347e057e91bd6b67d8caed3f2a30291d091cfc1d2b5976124296e367b9f16  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-36.audit.jsonl
4e61975beff56a6d082cb811dea87c7c034fe7cb1aae71d29142a8dc7895713a  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-37.audit.jsonl
b48e02eec5acab5e75c03ff1d39527b2cfa43e188ee0f727598c1e59c35c1788  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-38.audit.jsonl
39aa9be75114fb2549d2ab1331a37b33522b83a15a176cda5cb05f6e8034a5ce  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-39.audit.jsonl
b4c8189f90bff1c3b8205512500f4c0fd869790e83ed43ba30633c565bbcb10b  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-4.audit.jsonl
93176af2ccb536df38b41934ac68886367fe1106cbb57814ba59152686e465ef  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-40.audit.jsonl
e6e88df6df6fad2ffa320fa135573dd9921c28706a669bd6664fc88e5db3a914  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-41.audit.jsonl
38115c21d0143f8d7fcaebe521014d4b0b305a1fecc5a3166ca4d0e19700940e  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-42.audit.jsonl
b2caa24af78dd8dcf55d3c4d435a4375b62cc74ba7a34678fa0ca03892cf0f72  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-43.audit.jsonl
c5b6445ad76b2c937e24df15c178d215416cc749d100b2203fdaa9ac5ab2d261  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-44.audit.jsonl
38514fceba4d7a1b9cd0f4b2e5a61ba6dc6f6db548322fceb49ad7a62c1c1c2e  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-45.audit.jsonl
83e38692dae4c9f595b595574e45889ab43b886faaa38ed0625a608bf42402a9  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-46.audit.jsonl
8fef6471b978e427a3899ac5614e272151c969ebe8db2249e8fc73b1a71ec2b5  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-47.audit.jsonl
6585384621f5ad4f3fcb6897d80b1cf83964d4be8289378a92642f4699d98628  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-48.audit.jsonl
24e57748d1253af91d6ad08a85d20cdbe22f8fd665c255784fe22e1690ad93e4  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-49.audit.jsonl
c152defb74d1bcf9332171fecbe60cea051d8cdd57f94984e979269fa6c095bc  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-5.audit.jsonl
d5887999835be4a7e26c56f889bad0751e789405475a0f8f81015c778cef8182  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-6.audit.jsonl
1198fad9d8184c6a8e738c36fbadc8009c09adcf9637f43d504ebbf0d55a8a0f  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-7.audit.jsonl
f6851501b9f1141fc6d43dac99789d1ff38e7de019f6bddf2014824a66925e19  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-8.audit.jsonl
d5096556b57421a14699d4f6b115f6a865e974196b788419f9bdaaac9d7e4d2c  ./scoring/p18-imp-7f73929d/audit-sidecars/replay-seed-9.audit.jsonl
2db0d6f4bb7e3c7f1a14f9a6208ee0c34c1a95474da8194bc276a86267171983  ./scoring/p18-imp-7f73929d/core.json
678cba2832fa8559a1c1f6e1efd28c2c0b45c8c05cc8c2f665af02d7932a1787  ./scoring/p18-imp-7f73929d/duration.json
940d772848908eca9d8bd1c78f61e328bcdcf939c419f988147b8aa55cc097e8  ./scoring/p18-imp-7f73929d/funnel.json
f7d77a4a84660e39af9a7f99fcf12bf8a4034aa0d412fc57947cd0809cc4ebc8  ./scoring/p18-imp-7f73929d/instruments.json
91ff5e76d6706985a4794c405b8d640123209a79aae87bf3266b2ed530e4f205  ./scoring/p18-imp-7f73929d/row.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-imp-7f73929d/split-h1/roster.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-imp-7f73929d/split-h2/roster.json
138741a499b301fd5d349d8114bb3f72789b2f3060e9ca27fd4daf192246d395  ./scoring/p18-imp-7f73929d/split-half.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-imp-7f73929d/split-test_mod5_4/roster.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-imp-7f73929d/split-train_mod5_012/roster.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-imp-7f73929d/split-val_mod5_3/roster.json
866f76fc02c1466c710e899153abb360d37d284cd309155e3e6d1e3230dd2605  ./scoring/p18-imp-7f73929d/stamp-proof.json
88c30cd45671036438772e67e82f70d7de5dca87bd293d656a247e97f75f3b59  ./scoring/p18-imp-7f73929d/summary.json
f5770a8aec1c8ef872782b63b2f306e1b7b42cfcda77a9b97620d5a7cbbda501  ./scoring/p18-imp-7f73929d/validity.json
25318795886242adfed19170d58ed756bd2711249ac629e41447993c1202b579  ./scoring/p18-imp-7f73929d/watchability-h1.json
c83c9abcf41dc3a2a33d2bc93025d5d8900ab73980da783d5303cad1a27bd49e  ./scoring/p18-imp-7f73929d/watchability-h2.json
c9a473c1efe2e8f853641e64bdf06b9cea5abc7187aba32d2f596ad8461649c3  ./scoring/p18-imp-7f73929d/watchability.json
e76c0e4e9bfefa780f364f3c98718422c31772b97ddc5dde564193b93ec5f4a2  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-0.audit.jsonl
5a05b65bd5f697bb941a2cb9d1a4b1e6e77037b6a9be8a7a1111e0bf4f161f94  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-1.audit.jsonl
df03b96b68c94601551e7f15a8b634cedd7a3b9e081e00a82dd1a01a03178f20  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-10.audit.jsonl
0bb7439212a1411ad53020c201f70ed804cfcf5cf1c28d8663585fc70a02250e  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-11.audit.jsonl
474fd5fc879685a5a7788b4b8cac2031cb9fc9806e27bb2830207542f2612055  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-12.audit.jsonl
b87872764afdd35f50ac9fec392d9b9a4c754ef81d00637b5c610ae15f4622af  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-13.audit.jsonl
dad60bc2cbc550291a22007cd596900777955bfd07755cb5f730075609fb4a8c  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-14.audit.jsonl
f263941199a35a06d3974d6e4a7ab36fbf2c1b53a5a0263b37b4af58989ffceb  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-15.audit.jsonl
73682a90cb331710a7f66521ec44ee5768e6d05fecad1730c09d9fa16d7d4cae  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-16.audit.jsonl
faecfb4bf7f4c390ec2058635a440b6939c351b824c42fdd98b5fe485cdd85c5  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-17.audit.jsonl
581b7018662a1de8a4bc8f5e1b5072b307a41d886d638fce73294cf31e644371  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-18.audit.jsonl
c6db2f489091a1e4efc3d58f91e96b0f35f9448fbb4749ef61899eebb046841e  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-19.audit.jsonl
2f7bf935bb57f6f9445b06995ae4fe6be54d9e800564fa91e138fb77a9fd7a54  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-2.audit.jsonl
4c110f1449260ec58ffb5aa28f5fcd1cb499b8578cdfdaa0e4aef693844ba779  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-20.audit.jsonl
95cd4ebdae99ab546ab9e41a8fb3aef9bc36bb5e099a747f79a8bf9b77c2ccf1  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-21.audit.jsonl
4b3e1e4ff8e995a0c96ef951980380d15430a76061db2309e7744f4e59b89362  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-22.audit.jsonl
1f195271d4a83da97eb4ef18d2bd37b377e6287c03749d81f19020b43a9fb9ae  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-23.audit.jsonl
e33a78b9ec9609cf1b93f9973a186d8c0192684bd627455cb562198f984f1692  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-24.audit.jsonl
78302ce1fa5e134602aa826eb06fb4f3ce52b780100f939772e344e429e30843  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-25.audit.jsonl
a6b0afde73d4154aced4a0d1c6b7a690b862ead8de4473aa90f75707019a06c3  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-26.audit.jsonl
6704381f1e6b73631ccb043cd16bf8617e036f17bb87742badb2f3d6a8b69894  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-27.audit.jsonl
460823baf70d73c3d6bcb79328f71fd759024ce01e6432e83768c23c83777389  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-28.audit.jsonl
37f522a418c4b34f1051666117f3dccc91e126179c9f7e109a4c49b79e73290d  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-29.audit.jsonl
0be288bbfeaeea142656bb3f1f13bd157ee65fbfd571f42150ec159e28b5ea9d  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-3.audit.jsonl
4462ca7475940ad3c21ace3609057a600316f1b058bc7677b9dc7868e124004c  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-30.audit.jsonl
f43791286c7830b55887dd10640c857344c0999db559a2343957f4f94a8cf762  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-31.audit.jsonl
ee4ff54fe3f262e169598c02ebc2edac69e3b48aed9785dad40be839b8554983  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-32.audit.jsonl
7620c8ca5b9ae62397d027093cdd569b27455cfb457cba7f1b1628528bf30b5d  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-33.audit.jsonl
fd7029b9b1c36d0708b3aa406673e1919097be8561ec1eb731e57bc58e1fb725  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-34.audit.jsonl
7b4d758339c1d2ebaf11c4005050cd2ba6de1495396f87fc62139778d30fa022  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-35.audit.jsonl
25aeb538a99edbc2fa44c7fdb0efae0fc5c8b35d3fea25e1973257def256a6ee  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-36.audit.jsonl
cdcff06df026ddfd76ffcf84fb284e19a292dc7b17dc912cd624b348740bdd72  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-37.audit.jsonl
66c52ebf190f762930860f31c2b78162ef76c0c576c37b5ec525b7cf129cec6c  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-38.audit.jsonl
9798e2e37ea5a1b4c2dc8d4f38e53f1d8c490511bc55173165249679138c2a9f  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-39.audit.jsonl
6d218b826233eb5e28f7d1aefc4ba97484ad1df28354c1931a6205f71a6cc712  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-4.audit.jsonl
ea36334306fbb5ea06770d0f40d2c163fdf7bfd26ee81cbb24b4dc6df37c0597  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-40.audit.jsonl
b35c9a13166222bba0f0eccc4af11fd55850685aa170eff8c23a1fab562ba59a  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-41.audit.jsonl
cfd17e01ec84202c467b5cbe422668c531c44202b0b1db02f2ca6f7e3c71a3ec  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-42.audit.jsonl
ee01cc7f5d1e125c8e3a8d477b474f5f4e6a8bdafc690fc06ab3bb337db04dc3  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-43.audit.jsonl
e955973027d7c698998e53cf3c3c46287fd0451c097c36ac852a8d3efd465c12  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-44.audit.jsonl
2c97bf1171afb80f4ea0bfc26b09b6a995f12da0b87db6817705bf10160774d4  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-45.audit.jsonl
47ffd4478f440a956b1d5edb97cce2d05b9f7efbe600cf7e702d6f1a31e9afd5  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-46.audit.jsonl
6ce641a50c619a0c6124e33f9654b37d446499bb23c440bbc26f49333ff0bcdb  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-47.audit.jsonl
32f704f48e233bd6d18188efd8cf8af31c1b0461501c52ce14db551fcafd5fef  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-48.audit.jsonl
fb33e5e825138a8c99b9d8aa6a1db9af84b15a3845fafb39d651155ac2bf6f52  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-49.audit.jsonl
faf501279a123b35617ac54efbd4db3110d1bf6dafb7ea7528db971a2a49cf4c  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-5.audit.jsonl
deaa922006551a1e604fe9f4dbf874db27d100a87137d8e1661293382411e8c5  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-6.audit.jsonl
a5a7c1ff9218314c038b5bfb652f6d668a4339d7b0a110709de6ddd28b2e7184  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-7.audit.jsonl
e1a31c22c877a161d7ea8137d9a142225dd7698d7f6178a7882e58e7a21af8dc  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-8.audit.jsonl
2e3b50a512a8cd2215dc90b2ee7faa2ed632d6df795b9c1a439fb2d572b8ca28  ./scoring/p18-imp-bfd145cb/audit-sidecars/replay-seed-9.audit.jsonl
272730f81abf18e31fc143a63e08b7ef2132e98567534162ef62529fa5c60e6e  ./scoring/p18-imp-bfd145cb/core.json
b373aab97adcfaf86999a0c15e1efe05bfd24e6feca07c1aeda20731d4e5b8a5  ./scoring/p18-imp-bfd145cb/duration.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-imp-bfd145cb/f13-intersection-view/roster.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-imp-bfd145cb/f13-split-h1/roster.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-imp-bfd145cb/f13-split-h2/roster.json
c71dbf0b64a7c657e9f07b939bce3536714eeb35137532305770da28cd12635b  ./scoring/p18-imp-bfd145cb/funnel.json
62386a61d521586b4c70aac9be420871abc4974feabac72d967c2f78dc66d9a9  ./scoring/p18-imp-bfd145cb/instruments.json
a8ab6644c6ab356dd4a85eff2ce1169560ce3422f5a6397474b986802c2cad48  ./scoring/p18-imp-bfd145cb/row.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-imp-bfd145cb/split-h1/roster.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-imp-bfd145cb/split-h2/roster.json
322127e6edbf03fdd0c8476bc4b3c35802b575272e39117b4219aaa8ec42cd81  ./scoring/p18-imp-bfd145cb/split-half.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-imp-bfd145cb/split-test_mod5_4/roster.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-imp-bfd145cb/split-train_mod5_012/roster.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-imp-bfd145cb/split-val_mod5_3/roster.json
648c6930e5f523f4385461ac0940582ef553945416c130ab5a9f986347290542  ./scoring/p18-imp-bfd145cb/stamp-proof.json
9bca9fa986d1e958b87c7d1f7938c65fa302f4396e2426c9e6456adb402aed70  ./scoring/p18-imp-bfd145cb/summary.json
b9e8ea658a22f6088034b1799887bd5855c300fdc8da1cf5f7b0e377e309cf1e  ./scoring/p18-imp-bfd145cb/validity.json
bd1068f0674573d2cf2068091b134872d1b0f9c6632df05aa6f23a268a7d7b5c  ./scoring/p18-imp-bfd145cb/watchability-f13-intersection.json
78bd77343d47680982b16b94802ce8e7dd021e2754202bdc6bebbac4bdfea6a1  ./scoring/p18-imp-bfd145cb/watchability-h1.json
57f00b85436d59986a85a0853c65e0150588becdab437bc1135463770b6576d0  ./scoring/p18-imp-bfd145cb/watchability-h2.json
0eca0b0390d6fe753b5a63f6f4e39e432e6cf6b24bcece6efc79b29c9f140571  ./scoring/p18-imp-bfd145cb/watchability.json
d79097b73c67a2731ff84f8e415c094c08b20e4b7a9cfccce85d0df43af0cee1  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-0.audit.jsonl
c738c466965c3e9899e723a97c8d9c4155ae87ae462029ac8329f986f4ff086b  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-1.audit.jsonl
76153c8304705e107d46b47e002565f5a43f3269d86ce71988f6acbd2338d4a6  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-10.audit.jsonl
e30ca14b804ba23bbef7507ed0ad8a4d8ac43503405b40d25825634a3f9b6ae1  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-11.audit.jsonl
474fd5fc879685a5a7788b4b8cac2031cb9fc9806e27bb2830207542f2612055  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-12.audit.jsonl
63dfd510d88d62ece28268d636ce421b33dd00f476f1ecb23a557515b5e8a9f4  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-13.audit.jsonl
dad60bc2cbc550291a22007cd596900777955bfd07755cb5f730075609fb4a8c  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-14.audit.jsonl
26e09d2ec574a10b9030d4de95f2ab5f3345119f5efa9b85c483612f7359d00c  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-15.audit.jsonl
1f4f48b3f8c3aa80c6d51b960b5311e80a9dac58b725656edac5e153308e6a48  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-16.audit.jsonl
e5712da3c4bfb10dfef70800cbfebc87454851afff0846973ef922d6ba3b25c4  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-17.audit.jsonl
fde2d912980273b6fc0e1d7169318643df761c51f51513b0c753b8f288589be7  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-18.audit.jsonl
4cee2220f3cc1dd7f90985a231a682c464eb8b480014b76f3e6faaf03b5bb81d  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-19.audit.jsonl
1826999b5e06cd5517c2a3131a58d845cc750918988ea670db2e8d15ee0724b8  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-2.audit.jsonl
4c110f1449260ec58ffb5aa28f5fcd1cb499b8578cdfdaa0e4aef693844ba779  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-20.audit.jsonl
95cd4ebdae99ab546ab9e41a8fb3aef9bc36bb5e099a747f79a8bf9b77c2ccf1  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-21.audit.jsonl
c17ec60f12fdee8bd4abfacd8f8cdc2bb945211e119fd337b9dd05969385768c  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-22.audit.jsonl
97ef0104fdde8d089f7e94aa905a0e4ae9fe664d63b5e0585d0b58ff1f972cd2  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-23.audit.jsonl
4b88a43add1412f1cec0b65b41442a0b67550255b05193c90ae18f4889015bb1  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-24.audit.jsonl
6cd15a4c8446832469e97dff692ce255bc6693499f351bfad3c745d42b014edf  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-25.audit.jsonl
6266f2b8ef1eccc82667caba10e7470c91a99f7918d9cb9c9980fcc317730a52  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-26.audit.jsonl
adfc21946399931955ac2b2cebb0cdc565c6c8402b4e21127283f9300ed336d2  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-27.audit.jsonl
cd599320e6b71bcd60d66e5c4c0f7d2deb5c037029cf5194ee2db68eb8282547  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-28.audit.jsonl
836e6aa247f3fb47c9bf0047613141188b513b8c9ea4035703b43917cc4e4d9b  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-29.audit.jsonl
7c3997a5fda232cb0b1f8e0457f4be464be4e20318371c390fce1ec58791cc18  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-3.audit.jsonl
74d918201ea0ceedcfd6265c09eb1dcbab0c2a394c11878f4dffb4c10f1fc613  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-30.audit.jsonl
e7e0bed1d6cb635632339bae1cdf530fd8efba4419d7be86bd7d7b24754db07a  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-31.audit.jsonl
547f0702cb05f5a98ca80bd1c94c8cf8c8c12ca4662876d696fadcd6c1a2c441  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-32.audit.jsonl
593a7285e1853af267a4afe6ee9e1e9b0939c09092c8ea9ed68a329b14de7a7c  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-33.audit.jsonl
c8bb8c9e12a3ca85b47dac8a687e926e37526024d3fce70d1f90c9ec1f86c25b  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-34.audit.jsonl
8d39c94d223bdac6f124e063ac5779b8028da443a6a0fdc5604ca871a98a8a1f  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-35.audit.jsonl
f211a387cdd448fe179b320861ce43e786f75403d0c4c2f319bd62c1679c8c8f  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-36.audit.jsonl
8e27afcc66ffca2443b4867182beb5c8300540a98711b8555d65bd3cf4025f59  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-37.audit.jsonl
6c5d94d3d00443ee01a899d9adcb9a0474d7f7b3ad119ed947204006414f0396  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-38.audit.jsonl
c303411f212c17f8ee78ae817570c64ffac8e156f1545b5425828df3ae43634d  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-39.audit.jsonl
8c0b757df1c2745ce1a587242cca22b799438061cbfd37553d29131712ac1ad0  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-4.audit.jsonl
98fe1101ecd50a0bf6dde72fadb47acb3c0c012017efbd4beb9f708553123170  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-40.audit.jsonl
b35c9a13166222bba0f0eccc4af11fd55850685aa170eff8c23a1fab562ba59a  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-41.audit.jsonl
c9f129e5f6f9ad4768cf62687fcf83fa407c16150a110f5382632f55d40b587c  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-42.audit.jsonl
ee01cc7f5d1e125c8e3a8d477b474f5f4e6a8bdafc690fc06ab3bb337db04dc3  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-43.audit.jsonl
e955973027d7c698998e53cf3c3c46287fd0451c097c36ac852a8d3efd465c12  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-44.audit.jsonl
4798e3b1189748623e9049a515c41e0f340b9e9a78067ca573398470eb46458d  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-45.audit.jsonl
a2358135d85a2d79c3dacc357d194a33cec7820fdb2c366b804ddf8f4f19c8a1  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-46.audit.jsonl
be0feb77eea727515e33473a746f5fea3dfc11a48afd1f47de4d8d4800f48638  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-47.audit.jsonl
32f704f48e233bd6d18188efd8cf8af31c1b0461501c52ce14db551fcafd5fef  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-48.audit.jsonl
fb33e5e825138a8c99b9d8aa6a1db9af84b15a3845fafb39d651155ac2bf6f52  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-49.audit.jsonl
731c477d0046ce6e543d6c4821ed2155ab2ddbc3c4ca94b33afbd147d53c530d  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-5.audit.jsonl
59371c2c827f7e7a05cfd276f160ed0b431edae41fc28902279c13e36275f541  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-6.audit.jsonl
893669956cefcbd012291d799ab4fa1235aff886f11db80b288e8681ee8cd8c1  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-7.audit.jsonl
e9b11cb9f707ad0ad04913b8ff6685cf90514b420be90d227d0cdf313885b11c  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-8.audit.jsonl
08e8467270897b6aea199916ec86871736ca5619f967dee8d249bd665e32f780  ./scoring/p18-imp-ea4bc955/audit-sidecars/replay-seed-9.audit.jsonl
eaac787bf1740346baee43225269a4722afdf04b0dc6ee82df0ac770fb599b51  ./scoring/p18-imp-ea4bc955/core.json
48d46a7fc4b0e68a7a637d400d7c4c20b41060abba6df47d76c26f40f57b21dc  ./scoring/p18-imp-ea4bc955/duration.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-imp-ea4bc955/f13-intersection-view/roster.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-imp-ea4bc955/f13-split-h1/roster.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-imp-ea4bc955/f13-split-h2/roster.json
43d3b86925042e666fb4605f2b8d5a0a5529d2b739f019b29ae0acb297b951cf  ./scoring/p18-imp-ea4bc955/funnel.json
ef4b4c4c4600c8acf7a4cebbef9c433d8d25d27257a30aa7981808008558ddd3  ./scoring/p18-imp-ea4bc955/instruments.json
431ffaed4c4f608cb9084e4d401428463c81a23d90e680b899ff836e21fe645c  ./scoring/p18-imp-ea4bc955/row.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-imp-ea4bc955/split-h1/roster.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-imp-ea4bc955/split-h2/roster.json
62167db35de2ff1974bce3a11b3cdc25bac7c5f45d10139382b1ad677404a424  ./scoring/p18-imp-ea4bc955/split-half.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-imp-ea4bc955/split-test_mod5_4/roster.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-imp-ea4bc955/split-train_mod5_012/roster.json
01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340  ./scoring/p18-imp-ea4bc955/split-val_mod5_3/roster.json
883d53a35ed14a980ae0aa7a991aedd11d0b8f0d88b0c5b6106765155f5e8f84  ./scoring/p18-imp-ea4bc955/stamp-proof.json
53c7727a85d66e1096215f5d5d726faf6d27529e9dccbcb95548e0dbb1f3e474  ./scoring/p18-imp-ea4bc955/summary.json
56354f1905b0a719469f739b011b44889ebd1923eb4ea8eb1aaa7f90fe95458a  ./scoring/p18-imp-ea4bc955/validity.json
15cb7fdf1f19e255cdf09a9668481ef015dc6a4a9d501364bf4e62977a38257e  ./scoring/p18-imp-ea4bc955/watchability-f13-intersection.json
78013735a5a4a8b24db79c0420ebce96545ad8272396114d42da2936280cd693  ./scoring/p18-imp-ea4bc955/watchability-h1.json
9643c86a52a5f537662f8a6b87e45a7f05feb36d647fdd1150cb222b256452b3  ./scoring/p18-imp-ea4bc955/watchability-h2.json
bdb699d4e22eb2bdca31aca4a8e09925805f7da1c13494ecba81c28bcc792001  ./scoring/p18-imp-ea4bc955/watchability.json
e77d08d11b3dd406a5ce3ef95faf02b056567ae009f3ff2f99d86a12e3a968c7  ./stdout-p18-crew-c1-gen0-seed-0.log
e77d08d11b3dd406a5ce3ef95faf02b056567ae009f3ff2f99d86a12e3a968c7  ./stdout-p18-crew-c1-gen0-seed-1.log
dabf7b854788973cf895381c7d43758bc8a42a5d6bf6e110378e9244474c1658  ./stdout-p18-crew-c1-gen0-seed-10.log
5d7a3976ecf721bcdfebcceba1a06bc46c0d1445fac4fb2b34efbe8f78cbddc4  ./stdout-p18-crew-c1-gen0-seed-11.log
e14f138149448e5e5dc2bf407e48431e4d0d420b4e27ee395b612c0c0710a42c  ./stdout-p18-crew-c1-gen0-seed-12.log
e14f138149448e5e5dc2bf407e48431e4d0d420b4e27ee395b612c0c0710a42c  ./stdout-p18-crew-c1-gen0-seed-13.log
e77d08d11b3dd406a5ce3ef95faf02b056567ae009f3ff2f99d86a12e3a968c7  ./stdout-p18-crew-c1-gen0-seed-14.log
5d7a3976ecf721bcdfebcceba1a06bc46c0d1445fac4fb2b34efbe8f78cbddc4  ./stdout-p18-crew-c1-gen0-seed-15.log
e77d08d11b3dd406a5ce3ef95faf02b056567ae009f3ff2f99d86a12e3a968c7  ./stdout-p18-crew-c1-gen0-seed-16.log
e14f138149448e5e5dc2bf407e48431e4d0d420b4e27ee395b612c0c0710a42c  ./stdout-p18-crew-c1-gen0-seed-17.log
5f74f9c151d472229c25b438d66afea19195f43f895fa212442873cadd6ae152  ./stdout-p18-crew-c1-gen0-seed-18.log
e77d08d11b3dd406a5ce3ef95faf02b056567ae009f3ff2f99d86a12e3a968c7  ./stdout-p18-crew-c1-gen0-seed-19.log
5d7a3976ecf721bcdfebcceba1a06bc46c0d1445fac4fb2b34efbe8f78cbddc4  ./stdout-p18-crew-c1-gen0-seed-2.log
10a90dc252d0beda3b60b9e7ac4ba574fa9ab62f639bd2e29932eacd52529454  ./stdout-p18-crew-c1-gen0-seed-20.log
dabf7b854788973cf895381c7d43758bc8a42a5d6bf6e110378e9244474c1658  ./stdout-p18-crew-c1-gen0-seed-21.log
dd489ed716f35c064cd760639ad85176ed37b9918c22567cd612dc378861ae9f  ./stdout-p18-crew-c1-gen0-seed-22.log
e77d08d11b3dd406a5ce3ef95faf02b056567ae009f3ff2f99d86a12e3a968c7  ./stdout-p18-crew-c1-gen0-seed-23.log
8af889c74253eced101dfcda82a94f3a4e011d65e75e36e3a90f6e74178044de  ./stdout-p18-crew-c1-gen0-seed-24.log
8af889c74253eced101dfcda82a94f3a4e011d65e75e36e3a90f6e74178044de  ./stdout-p18-crew-c1-gen0-seed-25.log
dabf7b854788973cf895381c7d43758bc8a42a5d6bf6e110378e9244474c1658  ./stdout-p18-crew-c1-gen0-seed-26.log
e77d08d11b3dd406a5ce3ef95faf02b056567ae009f3ff2f99d86a12e3a968c7  ./stdout-p18-crew-c1-gen0-seed-27.log
5d7a3976ecf721bcdfebcceba1a06bc46c0d1445fac4fb2b34efbe8f78cbddc4  ./stdout-p18-crew-c1-gen0-seed-28.log
e14f138149448e5e5dc2bf407e48431e4d0d420b4e27ee395b612c0c0710a42c  ./stdout-p18-crew-c1-gen0-seed-29.log
54a863c36e10bee12e3db01b4495bd1657bcb8962f87848192d2d2455135a586  ./stdout-p18-crew-c1-gen0-seed-3.log
dabf7b854788973cf895381c7d43758bc8a42a5d6bf6e110378e9244474c1658  ./stdout-p18-crew-c1-gen0-seed-30.log
8af889c74253eced101dfcda82a94f3a4e011d65e75e36e3a90f6e74178044de  ./stdout-p18-crew-c1-gen0-seed-31.log
dd489ed716f35c064cd760639ad85176ed37b9918c22567cd612dc378861ae9f  ./stdout-p18-crew-c1-gen0-seed-32.log
8af889c74253eced101dfcda82a94f3a4e011d65e75e36e3a90f6e74178044de  ./stdout-p18-crew-c1-gen0-seed-33.log
dabf7b854788973cf895381c7d43758bc8a42a5d6bf6e110378e9244474c1658  ./stdout-p18-crew-c1-gen0-seed-34.log
e14f138149448e5e5dc2bf407e48431e4d0d420b4e27ee395b612c0c0710a42c  ./stdout-p18-crew-c1-gen0-seed-35.log
e14f138149448e5e5dc2bf407e48431e4d0d420b4e27ee395b612c0c0710a42c  ./stdout-p18-crew-c1-gen0-seed-36.log
dd489ed716f35c064cd760639ad85176ed37b9918c22567cd612dc378861ae9f  ./stdout-p18-crew-c1-gen0-seed-37.log
e77d08d11b3dd406a5ce3ef95faf02b056567ae009f3ff2f99d86a12e3a968c7  ./stdout-p18-crew-c1-gen0-seed-38.log
e14f138149448e5e5dc2bf407e48431e4d0d420b4e27ee395b612c0c0710a42c  ./stdout-p18-crew-c1-gen0-seed-39.log
01b5ff803ce66fadf277f5d79642261a7f780a156c0d210ceeb768fd913990cb  ./stdout-p18-crew-c1-gen0-seed-4.log
8bd22fe87fe7ea84592f8d5130e94c43e771ac320664175f99526417ba8e3fcf  ./stdout-p18-crew-c1-gen0-seed-40.log
8af889c74253eced101dfcda82a94f3a4e011d65e75e36e3a90f6e74178044de  ./stdout-p18-crew-c1-gen0-seed-41.log
e14f138149448e5e5dc2bf407e48431e4d0d420b4e27ee395b612c0c0710a42c  ./stdout-p18-crew-c1-gen0-seed-42.log
54a863c36e10bee12e3db01b4495bd1657bcb8962f87848192d2d2455135a586  ./stdout-p18-crew-c1-gen0-seed-43.log
dabf7b854788973cf895381c7d43758bc8a42a5d6bf6e110378e9244474c1658  ./stdout-p18-crew-c1-gen0-seed-44.log
5d7a3976ecf721bcdfebcceba1a06bc46c0d1445fac4fb2b34efbe8f78cbddc4  ./stdout-p18-crew-c1-gen0-seed-45.log
54a863c36e10bee12e3db01b4495bd1657bcb8962f87848192d2d2455135a586  ./stdout-p18-crew-c1-gen0-seed-46.log
dabf7b854788973cf895381c7d43758bc8a42a5d6bf6e110378e9244474c1658  ./stdout-p18-crew-c1-gen0-seed-47.log
8af889c74253eced101dfcda82a94f3a4e011d65e75e36e3a90f6e74178044de  ./stdout-p18-crew-c1-gen0-seed-48.log
5d7a3976ecf721bcdfebcceba1a06bc46c0d1445fac4fb2b34efbe8f78cbddc4  ./stdout-p18-crew-c1-gen0-seed-49.log
e14f138149448e5e5dc2bf407e48431e4d0d420b4e27ee395b612c0c0710a42c  ./stdout-p18-crew-c1-gen0-seed-5.log
e77d08d11b3dd406a5ce3ef95faf02b056567ae009f3ff2f99d86a12e3a968c7  ./stdout-p18-crew-c1-gen0-seed-6.log
e77d08d11b3dd406a5ce3ef95faf02b056567ae009f3ff2f99d86a12e3a968c7  ./stdout-p18-crew-c1-gen0-seed-7.log
54a863c36e10bee12e3db01b4495bd1657bcb8962f87848192d2d2455135a586  ./stdout-p18-crew-c1-gen0-seed-8.log
e77d08d11b3dd406a5ce3ef95faf02b056567ae009f3ff2f99d86a12e3a968c7  ./stdout-p18-crew-c1-gen0-seed-9.log
7110fdd1ab75204fd9880880134702f36df8be4dbb48e9611fa9afd255580b9b  ./stdout-p18-crew-c1-gen9-seed-0.log
6a3a9bca9af1c28b9b158145a6156843806d5a6e306abfb0c352872729ba3601  ./stdout-p18-crew-c1-gen9-seed-1.log
930564ce7185bf11ab27ba8ca2591286cf0958d13a7875c3a88427d96ae33ea4  ./stdout-p18-crew-c1-gen9-seed-10.log
6a3a9bca9af1c28b9b158145a6156843806d5a6e306abfb0c352872729ba3601  ./stdout-p18-crew-c1-gen9-seed-11.log
6827369bd102b34ab031eb9ea98541b04b88835cc33959cc7098cc77cafeaae9  ./stdout-p18-crew-c1-gen9-seed-12.log
c9036bc81f74e7a48405965abe53cc36cb68a39bdc23f90d8e87b35b54b7b93c  ./stdout-p18-crew-c1-gen9-seed-13.log
6a3a9bca9af1c28b9b158145a6156843806d5a6e306abfb0c352872729ba3601  ./stdout-p18-crew-c1-gen9-seed-14.log
7110fdd1ab75204fd9880880134702f36df8be4dbb48e9611fa9afd255580b9b  ./stdout-p18-crew-c1-gen9-seed-15.log
6a3a9bca9af1c28b9b158145a6156843806d5a6e306abfb0c352872729ba3601  ./stdout-p18-crew-c1-gen9-seed-16.log
930564ce7185bf11ab27ba8ca2591286cf0958d13a7875c3a88427d96ae33ea4  ./stdout-p18-crew-c1-gen9-seed-17.log
7110fdd1ab75204fd9880880134702f36df8be4dbb48e9611fa9afd255580b9b  ./stdout-p18-crew-c1-gen9-seed-18.log
5107f7ec0edab8d55b738544160ca44a8f8e56755a32bfa863b1fa0ef0eeb4c8  ./stdout-p18-crew-c1-gen9-seed-19.log
6a3a9bca9af1c28b9b158145a6156843806d5a6e306abfb0c352872729ba3601  ./stdout-p18-crew-c1-gen9-seed-2.log
930564ce7185bf11ab27ba8ca2591286cf0958d13a7875c3a88427d96ae33ea4  ./stdout-p18-crew-c1-gen9-seed-20.log
930564ce7185bf11ab27ba8ca2591286cf0958d13a7875c3a88427d96ae33ea4  ./stdout-p18-crew-c1-gen9-seed-21.log
020799e3036229c586bc3efacb8b689022f19a57fc167c5d526ae7277bf6d49a  ./stdout-p18-crew-c1-gen9-seed-22.log
6a3a9bca9af1c28b9b158145a6156843806d5a6e306abfb0c352872729ba3601  ./stdout-p18-crew-c1-gen9-seed-23.log
7110fdd1ab75204fd9880880134702f36df8be4dbb48e9611fa9afd255580b9b  ./stdout-p18-crew-c1-gen9-seed-24.log
15302970edb931030ed9ae5b537a308b05f3216ebacd1139c0c0bbab80a918f1  ./stdout-p18-crew-c1-gen9-seed-25.log
6827369bd102b34ab031eb9ea98541b04b88835cc33959cc7098cc77cafeaae9  ./stdout-p18-crew-c1-gen9-seed-26.log
6a3a9bca9af1c28b9b158145a6156843806d5a6e306abfb0c352872729ba3601  ./stdout-p18-crew-c1-gen9-seed-27.log
7110fdd1ab75204fd9880880134702f36df8be4dbb48e9611fa9afd255580b9b  ./stdout-p18-crew-c1-gen9-seed-28.log
5107f7ec0edab8d55b738544160ca44a8f8e56755a32bfa863b1fa0ef0eeb4c8  ./stdout-p18-crew-c1-gen9-seed-29.log
6a3a9bca9af1c28b9b158145a6156843806d5a6e306abfb0c352872729ba3601  ./stdout-p18-crew-c1-gen9-seed-3.log
6827369bd102b34ab031eb9ea98541b04b88835cc33959cc7098cc77cafeaae9  ./stdout-p18-crew-c1-gen9-seed-30.log
5107f7ec0edab8d55b738544160ca44a8f8e56755a32bfa863b1fa0ef0eeb4c8  ./stdout-p18-crew-c1-gen9-seed-31.log
de0677755bd2b5d26601a9ea4224e6e6b30513514099cd135bcaa08d844cedff  ./stdout-p18-crew-c1-gen9-seed-32.log
930564ce7185bf11ab27ba8ca2591286cf0958d13a7875c3a88427d96ae33ea4  ./stdout-p18-crew-c1-gen9-seed-33.log
6827369bd102b34ab031eb9ea98541b04b88835cc33959cc7098cc77cafeaae9  ./stdout-p18-crew-c1-gen9-seed-34.log
5107f7ec0edab8d55b738544160ca44a8f8e56755a32bfa863b1fa0ef0eeb4c8  ./stdout-p18-crew-c1-gen9-seed-35.log
c9036bc81f74e7a48405965abe53cc36cb68a39bdc23f90d8e87b35b54b7b93c  ./stdout-p18-crew-c1-gen9-seed-36.log
020799e3036229c586bc3efacb8b689022f19a57fc167c5d526ae7277bf6d49a  ./stdout-p18-crew-c1-gen9-seed-37.log
15302970edb931030ed9ae5b537a308b05f3216ebacd1139c0c0bbab80a918f1  ./stdout-p18-crew-c1-gen9-seed-38.log
15302970edb931030ed9ae5b537a308b05f3216ebacd1139c0c0bbab80a918f1  ./stdout-p18-crew-c1-gen9-seed-39.log
c9036bc81f74e7a48405965abe53cc36cb68a39bdc23f90d8e87b35b54b7b93c  ./stdout-p18-crew-c1-gen9-seed-4.log
15302970edb931030ed9ae5b537a308b05f3216ebacd1139c0c0bbab80a918f1  ./stdout-p18-crew-c1-gen9-seed-40.log
930564ce7185bf11ab27ba8ca2591286cf0958d13a7875c3a88427d96ae33ea4  ./stdout-p18-crew-c1-gen9-seed-41.log
6827369bd102b34ab031eb9ea98541b04b88835cc33959cc7098cc77cafeaae9  ./stdout-p18-crew-c1-gen9-seed-42.log
6a3a9bca9af1c28b9b158145a6156843806d5a6e306abfb0c352872729ba3601  ./stdout-p18-crew-c1-gen9-seed-43.log
5107f7ec0edab8d55b738544160ca44a8f8e56755a32bfa863b1fa0ef0eeb4c8  ./stdout-p18-crew-c1-gen9-seed-44.log
5107f7ec0edab8d55b738544160ca44a8f8e56755a32bfa863b1fa0ef0eeb4c8  ./stdout-p18-crew-c1-gen9-seed-45.log
15302970edb931030ed9ae5b537a308b05f3216ebacd1139c0c0bbab80a918f1  ./stdout-p18-crew-c1-gen9-seed-46.log
930564ce7185bf11ab27ba8ca2591286cf0958d13a7875c3a88427d96ae33ea4  ./stdout-p18-crew-c1-gen9-seed-47.log
6827369bd102b34ab031eb9ea98541b04b88835cc33959cc7098cc77cafeaae9  ./stdout-p18-crew-c1-gen9-seed-48.log
7110fdd1ab75204fd9880880134702f36df8be4dbb48e9611fa9afd255580b9b  ./stdout-p18-crew-c1-gen9-seed-49.log
6827369bd102b34ab031eb9ea98541b04b88835cc33959cc7098cc77cafeaae9  ./stdout-p18-crew-c1-gen9-seed-5.log
c9036bc81f74e7a48405965abe53cc36cb68a39bdc23f90d8e87b35b54b7b93c  ./stdout-p18-crew-c1-gen9-seed-6.log
6a3a9bca9af1c28b9b158145a6156843806d5a6e306abfb0c352872729ba3601  ./stdout-p18-crew-c1-gen9-seed-7.log
7325fd50cf5030c1ad994f8b6e027b1493c9042640d0bed84a77d4b305a42e5f  ./stdout-p18-crew-c1-gen9-seed-8.log
6a3a9bca9af1c28b9b158145a6156843806d5a6e306abfb0c352872729ba3601  ./stdout-p18-crew-c1-gen9-seed-9.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-0.log
13afe46a06f356c77f8dad9618b21c773138aab407a994af9494e47367fc230f  ./stdout-p18-crew-c2-gen0-seed-1.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-10.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-11.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-12.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-13.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-14.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-15.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-16.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-17.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-18.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-19.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-2.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-20.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-21.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-22.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-23.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-24.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-25.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-26.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-27.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-28.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-29.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-3.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-30.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-31.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-32.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-33.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-34.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-35.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-36.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-37.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-38.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-39.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-4.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-40.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-41.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-42.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-43.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-44.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-45.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-46.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-47.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-48.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-49.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-5.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-6.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-7.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-8.log
e94875071b86ec8f11829899e445028c53147df60a257b86519c77c3bf9efbe9  ./stdout-p18-crew-c2-gen0-seed-9.log
9dc2d387665680bc2216ef5ba697e488b43d047485d2bfaeebd7858aba4f82d7  ./stdout-p18-crew-c2-gen9-seed-0.log
9dc2d387665680bc2216ef5ba697e488b43d047485d2bfaeebd7858aba4f82d7  ./stdout-p18-crew-c2-gen9-seed-1.log
5eeaeaf53a1a9d87c91ae77980daa626597636124eb4062199e1fcf66b4563b0  ./stdout-p18-crew-c2-gen9-seed-10.log
5eeaeaf53a1a9d87c91ae77980daa626597636124eb4062199e1fcf66b4563b0  ./stdout-p18-crew-c2-gen9-seed-11.log
5eeaeaf53a1a9d87c91ae77980daa626597636124eb4062199e1fcf66b4563b0  ./stdout-p18-crew-c2-gen9-seed-12.log
5eeaeaf53a1a9d87c91ae77980daa626597636124eb4062199e1fcf66b4563b0  ./stdout-p18-crew-c2-gen9-seed-13.log
9dc2d387665680bc2216ef5ba697e488b43d047485d2bfaeebd7858aba4f82d7  ./stdout-p18-crew-c2-gen9-seed-14.log
5eeaeaf53a1a9d87c91ae77980daa626597636124eb4062199e1fcf66b4563b0  ./stdout-p18-crew-c2-gen9-seed-15.log
5eeaeaf53a1a9d87c91ae77980daa626597636124eb4062199e1fcf66b4563b0  ./stdout-p18-crew-c2-gen9-seed-16.log
8cff0aba64a16e58fd625a07e87ccbbf063e1d3c284299ebb83ecabe36d0ad1c  ./stdout-p18-crew-c2-gen9-seed-17.log
2461e6223bc45cd6ee63606d1c9c5ca4889b3c242377ea4663a890a73516c84c  ./stdout-p18-crew-c2-gen9-seed-18.log
76575d208c563c0754be2a412ec6a6762686ee0a87254dc092f94ca0b5efe895  ./stdout-p18-crew-c2-gen9-seed-19.log
5eeaeaf53a1a9d87c91ae77980daa626597636124eb4062199e1fcf66b4563b0  ./stdout-p18-crew-c2-gen9-seed-2.log
76575d208c563c0754be2a412ec6a6762686ee0a87254dc092f94ca0b5efe895  ./stdout-p18-crew-c2-gen9-seed-20.log
5eeaeaf53a1a9d87c91ae77980daa626597636124eb4062199e1fcf66b4563b0  ./stdout-p18-crew-c2-gen9-seed-21.log
631ea0db0392a05cb08500f3241dc730117793f28cc9902a82897fa3dc5ed22e  ./stdout-p18-crew-c2-gen9-seed-22.log
9dc2d387665680bc2216ef5ba697e488b43d047485d2bfaeebd7858aba4f82d7  ./stdout-p18-crew-c2-gen9-seed-23.log
7332991efcc29c8882229a38f49413eb1fb2cb2cfffdd18805c726a7e7e17ae2  ./stdout-p18-crew-c2-gen9-seed-24.log
5eeaeaf53a1a9d87c91ae77980daa626597636124eb4062199e1fcf66b4563b0  ./stdout-p18-crew-c2-gen9-seed-25.log
667f17abcada1a3a94f76257d5c358438d6d6330eceaa313fea4b9b79fdfe9b6  ./stdout-p18-crew-c2-gen9-seed-26.log
667f17abcada1a3a94f76257d5c358438d6d6330eceaa313fea4b9b79fdfe9b6  ./stdout-p18-crew-c2-gen9-seed-27.log
8cff0aba64a16e58fd625a07e87ccbbf063e1d3c284299ebb83ecabe36d0ad1c  ./stdout-p18-crew-c2-gen9-seed-28.log
9dc2d387665680bc2216ef5ba697e488b43d047485d2bfaeebd7858aba4f82d7  ./stdout-p18-crew-c2-gen9-seed-29.log
5eeaeaf53a1a9d87c91ae77980daa626597636124eb4062199e1fcf66b4563b0  ./stdout-p18-crew-c2-gen9-seed-3.log
5eeaeaf53a1a9d87c91ae77980daa626597636124eb4062199e1fcf66b4563b0  ./stdout-p18-crew-c2-gen9-seed-30.log
9dc2d387665680bc2216ef5ba697e488b43d047485d2bfaeebd7858aba4f82d7  ./stdout-p18-crew-c2-gen9-seed-31.log
9dc2d387665680bc2216ef5ba697e488b43d047485d2bfaeebd7858aba4f82d7  ./stdout-p18-crew-c2-gen9-seed-32.log
9dc2d387665680bc2216ef5ba697e488b43d047485d2bfaeebd7858aba4f82d7  ./stdout-p18-crew-c2-gen9-seed-33.log
9dc2d387665680bc2216ef5ba697e488b43d047485d2bfaeebd7858aba4f82d7  ./stdout-p18-crew-c2-gen9-seed-34.log
9dc2d387665680bc2216ef5ba697e488b43d047485d2bfaeebd7858aba4f82d7  ./stdout-p18-crew-c2-gen9-seed-35.log
5eeaeaf53a1a9d87c91ae77980daa626597636124eb4062199e1fcf66b4563b0  ./stdout-p18-crew-c2-gen9-seed-36.log
9dc2d387665680bc2216ef5ba697e488b43d047485d2bfaeebd7858aba4f82d7  ./stdout-p18-crew-c2-gen9-seed-37.log
9dc2d387665680bc2216ef5ba697e488b43d047485d2bfaeebd7858aba4f82d7  ./stdout-p18-crew-c2-gen9-seed-38.log
9dc2d387665680bc2216ef5ba697e488b43d047485d2bfaeebd7858aba4f82d7  ./stdout-p18-crew-c2-gen9-seed-39.log
5eeaeaf53a1a9d87c91ae77980daa626597636124eb4062199e1fcf66b4563b0  ./stdout-p18-crew-c2-gen9-seed-4.log
631ea0db0392a05cb08500f3241dc730117793f28cc9902a82897fa3dc5ed22e  ./stdout-p18-crew-c2-gen9-seed-40.log
5eeaeaf53a1a9d87c91ae77980daa626597636124eb4062199e1fcf66b4563b0  ./stdout-p18-crew-c2-gen9-seed-41.log
9dc2d387665680bc2216ef5ba697e488b43d047485d2bfaeebd7858aba4f82d7  ./stdout-p18-crew-c2-gen9-seed-42.log
7332991efcc29c8882229a38f49413eb1fb2cb2cfffdd18805c726a7e7e17ae2  ./stdout-p18-crew-c2-gen9-seed-43.log
9dc2d387665680bc2216ef5ba697e488b43d047485d2bfaeebd7858aba4f82d7  ./stdout-p18-crew-c2-gen9-seed-44.log
8cff0aba64a16e58fd625a07e87ccbbf063e1d3c284299ebb83ecabe36d0ad1c  ./stdout-p18-crew-c2-gen9-seed-45.log
5eeaeaf53a1a9d87c91ae77980daa626597636124eb4062199e1fcf66b4563b0  ./stdout-p18-crew-c2-gen9-seed-46.log
9dc2d387665680bc2216ef5ba697e488b43d047485d2bfaeebd7858aba4f82d7  ./stdout-p18-crew-c2-gen9-seed-47.log
5eeaeaf53a1a9d87c91ae77980daa626597636124eb4062199e1fcf66b4563b0  ./stdout-p18-crew-c2-gen9-seed-48.log
8cff0aba64a16e58fd625a07e87ccbbf063e1d3c284299ebb83ecabe36d0ad1c  ./stdout-p18-crew-c2-gen9-seed-49.log
5eeaeaf53a1a9d87c91ae77980daa626597636124eb4062199e1fcf66b4563b0  ./stdout-p18-crew-c2-gen9-seed-5.log
631ea0db0392a05cb08500f3241dc730117793f28cc9902a82897fa3dc5ed22e  ./stdout-p18-crew-c2-gen9-seed-6.log
667f17abcada1a3a94f76257d5c358438d6d6330eceaa313fea4b9b79fdfe9b6  ./stdout-p18-crew-c2-gen9-seed-7.log
9dc2d387665680bc2216ef5ba697e488b43d047485d2bfaeebd7858aba4f82d7  ./stdout-p18-crew-c2-gen9-seed-8.log
9dc2d387665680bc2216ef5ba697e488b43d047485d2bfaeebd7858aba4f82d7  ./stdout-p18-crew-c2-gen9-seed-9.log
37b24c617fc47b2ce8e3222dd90fb8a93a06fea40de974992b8498d20b146301  ./stdout-p18-fsm-comparator-seed-0.log
7c5915c70c49df10a78114b3a7f4b2cb0e9fd674edd86c183a780de08a6c3ac0  ./stdout-p18-fsm-comparator-seed-1.log
77a38d17ebf1a84d596f0031ce72d0e1fe2ae4c306702343fffecad84e075c6c  ./stdout-p18-fsm-comparator-seed-10.log
7c5915c70c49df10a78114b3a7f4b2cb0e9fd674edd86c183a780de08a6c3ac0  ./stdout-p18-fsm-comparator-seed-11.log
5bb74fa5373f15696b65a21cc0371c5665fa93e41f8fedaa3fee575e3409ae86  ./stdout-p18-fsm-comparator-seed-12.log
c41a54f6be28653325a0ec194d856d45ce6a1c065d049bb326a90829850a2fda  ./stdout-p18-fsm-comparator-seed-13.log
c41a54f6be28653325a0ec194d856d45ce6a1c065d049bb326a90829850a2fda  ./stdout-p18-fsm-comparator-seed-14.log
a28bd6b7d61d4a8810f6d3aed6ed21937ed1e30d003130ddd2d99e11c9b814eb  ./stdout-p18-fsm-comparator-seed-15.log
37b24c617fc47b2ce8e3222dd90fb8a93a06fea40de974992b8498d20b146301  ./stdout-p18-fsm-comparator-seed-16.log
a28bd6b7d61d4a8810f6d3aed6ed21937ed1e30d003130ddd2d99e11c9b814eb  ./stdout-p18-fsm-comparator-seed-17.log
73f6f77eb7c4913bcf7ead3cb39801572eadb7aef038d81ca0a6d626e28d8282  ./stdout-p18-fsm-comparator-seed-18.log
37b24c617fc47b2ce8e3222dd90fb8a93a06fea40de974992b8498d20b146301  ./stdout-p18-fsm-comparator-seed-19.log
22d4b7539e90a5b45c7296b4d95466222df8e122c756ebe67e2d8330d4538da2  ./stdout-p18-fsm-comparator-seed-2.log
a0cb36cc462aaaf6b504fd3be32ddb0c255c62e45d165bd914942eb3c85cc3ef  ./stdout-p18-fsm-comparator-seed-20.log
36ba48400eb2b0f79d5c156ad9e6b6eb1585090775767c4fcea2d7478e14de17  ./stdout-p18-fsm-comparator-seed-21.log
a0cb36cc462aaaf6b504fd3be32ddb0c255c62e45d165bd914942eb3c85cc3ef  ./stdout-p18-fsm-comparator-seed-22.log
37b24c617fc47b2ce8e3222dd90fb8a93a06fea40de974992b8498d20b146301  ./stdout-p18-fsm-comparator-seed-23.log
a28bd6b7d61d4a8810f6d3aed6ed21937ed1e30d003130ddd2d99e11c9b814eb  ./stdout-p18-fsm-comparator-seed-24.log
5bb74fa5373f15696b65a21cc0371c5665fa93e41f8fedaa3fee575e3409ae86  ./stdout-p18-fsm-comparator-seed-25.log
a0cb36cc462aaaf6b504fd3be32ddb0c255c62e45d165bd914942eb3c85cc3ef  ./stdout-p18-fsm-comparator-seed-26.log
5bb74fa5373f15696b65a21cc0371c5665fa93e41f8fedaa3fee575e3409ae86  ./stdout-p18-fsm-comparator-seed-27.log
a28bd6b7d61d4a8810f6d3aed6ed21937ed1e30d003130ddd2d99e11c9b814eb  ./stdout-p18-fsm-comparator-seed-28.log
7c5915c70c49df10a78114b3a7f4b2cb0e9fd674edd86c183a780de08a6c3ac0  ./stdout-p18-fsm-comparator-seed-29.log
a28bd6b7d61d4a8810f6d3aed6ed21937ed1e30d003130ddd2d99e11c9b814eb  ./stdout-p18-fsm-comparator-seed-3.log
a28bd6b7d61d4a8810f6d3aed6ed21937ed1e30d003130ddd2d99e11c9b814eb  ./stdout-p18-fsm-comparator-seed-30.log
da85876a7c9893726a21c0c9866f2f486ce8a4f874af8084d9a79c9c0dc977c3  ./stdout-p18-fsm-comparator-seed-31.log
a0cb36cc462aaaf6b504fd3be32ddb0c255c62e45d165bd914942eb3c85cc3ef  ./stdout-p18-fsm-comparator-seed-32.log
7c5915c70c49df10a78114b3a7f4b2cb0e9fd674edd86c183a780de08a6c3ac0  ./stdout-p18-fsm-comparator-seed-33.log
a0cb36cc462aaaf6b504fd3be32ddb0c255c62e45d165bd914942eb3c85cc3ef  ./stdout-p18-fsm-comparator-seed-34.log
77a38d17ebf1a84d596f0031ce72d0e1fe2ae4c306702343fffecad84e075c6c  ./stdout-p18-fsm-comparator-seed-35.log
7c5915c70c49df10a78114b3a7f4b2cb0e9fd674edd86c183a780de08a6c3ac0  ./stdout-p18-fsm-comparator-seed-36.log
5bb74fa5373f15696b65a21cc0371c5665fa93e41f8fedaa3fee575e3409ae86  ./stdout-p18-fsm-comparator-seed-37.log
c41a54f6be28653325a0ec194d856d45ce6a1c065d049bb326a90829850a2fda  ./stdout-p18-fsm-comparator-seed-38.log
a43c69c0e4ddee2f05a0c0cc337b8111450f880765880f84f8a4a1307c84e9a6  ./stdout-p18-fsm-comparator-seed-39.log
c41a54f6be28653325a0ec194d856d45ce6a1c065d049bb326a90829850a2fda  ./stdout-p18-fsm-comparator-seed-4.log
e85d403f4f1dc0a1fdfd3cba29506f6901d8ec2e6755d060f851e7b4271874a5  ./stdout-p18-fsm-comparator-seed-40.log
7c5915c70c49df10a78114b3a7f4b2cb0e9fd674edd86c183a780de08a6c3ac0  ./stdout-p18-fsm-comparator-seed-41.log
7c5915c70c49df10a78114b3a7f4b2cb0e9fd674edd86c183a780de08a6c3ac0  ./stdout-p18-fsm-comparator-seed-42.log
7c5915c70c49df10a78114b3a7f4b2cb0e9fd674edd86c183a780de08a6c3ac0  ./stdout-p18-fsm-comparator-seed-43.log
5bb74fa5373f15696b65a21cc0371c5665fa93e41f8fedaa3fee575e3409ae86  ./stdout-p18-fsm-comparator-seed-44.log
a28bd6b7d61d4a8810f6d3aed6ed21937ed1e30d003130ddd2d99e11c9b814eb  ./stdout-p18-fsm-comparator-seed-45.log
36ba48400eb2b0f79d5c156ad9e6b6eb1585090775767c4fcea2d7478e14de17  ./stdout-p18-fsm-comparator-seed-46.log
77a38d17ebf1a84d596f0031ce72d0e1fe2ae4c306702343fffecad84e075c6c  ./stdout-p18-fsm-comparator-seed-47.log
c41a54f6be28653325a0ec194d856d45ce6a1c065d049bb326a90829850a2fda  ./stdout-p18-fsm-comparator-seed-48.log
a28bd6b7d61d4a8810f6d3aed6ed21937ed1e30d003130ddd2d99e11c9b814eb  ./stdout-p18-fsm-comparator-seed-49.log
7c5915c70c49df10a78114b3a7f4b2cb0e9fd674edd86c183a780de08a6c3ac0  ./stdout-p18-fsm-comparator-seed-5.log
a43c69c0e4ddee2f05a0c0cc337b8111450f880765880f84f8a4a1307c84e9a6  ./stdout-p18-fsm-comparator-seed-6.log
5bb74fa5373f15696b65a21cc0371c5665fa93e41f8fedaa3fee575e3409ae86  ./stdout-p18-fsm-comparator-seed-7.log
5bb74fa5373f15696b65a21cc0371c5665fa93e41f8fedaa3fee575e3409ae86  ./stdout-p18-fsm-comparator-seed-8.log
7c5915c70c49df10a78114b3a7f4b2cb0e9fd674edd86c183a780de08a6c3ac0  ./stdout-p18-fsm-comparator-seed-9.log
fff8c3cd1cd9dce1d17db239dd8eff7ccbe425d64fcb7403988d82222807820e  ./stdout-p18-imp-6d327dcb-seed-0.log
e4303c4b8b6139eec1da1ae8c8bd78255af1aa0cf60efbc89b8c8a444c02ad80  ./stdout-p18-imp-6d327dcb-seed-1.log
eda5acc35d858dc7ef5dde784f24fa65f9b7c3d13d249d3f19c47d486db13fb9  ./stdout-p18-imp-6d327dcb-seed-10.log
fff8c3cd1cd9dce1d17db239dd8eff7ccbe425d64fcb7403988d82222807820e  ./stdout-p18-imp-6d327dcb-seed-11.log
2ca413b95aa463c4e0742a3c882035484e68ffa18516e42406d3a5cdbd510375  ./stdout-p18-imp-6d327dcb-seed-12.log
d1443f2825aa1ce6e0838f2f90f63001870767c4703df26ecdbe5ec954ead2ce  ./stdout-p18-imp-6d327dcb-seed-13.log
ad8c8de4b2c48560a616d6b737bed25b3b1b2cfc64466653ba5b5902d914d59d  ./stdout-p18-imp-6d327dcb-seed-14.log
e4303c4b8b6139eec1da1ae8c8bd78255af1aa0cf60efbc89b8c8a444c02ad80  ./stdout-p18-imp-6d327dcb-seed-15.log
2ca413b95aa463c4e0742a3c882035484e68ffa18516e42406d3a5cdbd510375  ./stdout-p18-imp-6d327dcb-seed-16.log
eda5acc35d858dc7ef5dde784f24fa65f9b7c3d13d249d3f19c47d486db13fb9  ./stdout-p18-imp-6d327dcb-seed-17.log
fff8c3cd1cd9dce1d17db239dd8eff7ccbe425d64fcb7403988d82222807820e  ./stdout-p18-imp-6d327dcb-seed-18.log
d1443f2825aa1ce6e0838f2f90f63001870767c4703df26ecdbe5ec954ead2ce  ./stdout-p18-imp-6d327dcb-seed-19.log
fff8c3cd1cd9dce1d17db239dd8eff7ccbe425d64fcb7403988d82222807820e  ./stdout-p18-imp-6d327dcb-seed-2.log
82ea2dec7877a26bee2906d9ccd696002e9060b2475c4ffb218765b7f8360f54  ./stdout-p18-imp-6d327dcb-seed-20.log
fff8c3cd1cd9dce1d17db239dd8eff7ccbe425d64fcb7403988d82222807820e  ./stdout-p18-imp-6d327dcb-seed-21.log
82ea2dec7877a26bee2906d9ccd696002e9060b2475c4ffb218765b7f8360f54  ./stdout-p18-imp-6d327dcb-seed-22.log
d1443f2825aa1ce6e0838f2f90f63001870767c4703df26ecdbe5ec954ead2ce  ./stdout-p18-imp-6d327dcb-seed-23.log
eda5acc35d858dc7ef5dde784f24fa65f9b7c3d13d249d3f19c47d486db13fb9  ./stdout-p18-imp-6d327dcb-seed-24.log
fff8c3cd1cd9dce1d17db239dd8eff7ccbe425d64fcb7403988d82222807820e  ./stdout-p18-imp-6d327dcb-seed-25.log
b9e480d1c5a0dc58ae10c7bb0887837b7fec1ab87bc944647fae9ea00c25b139  ./stdout-p18-imp-6d327dcb-seed-26.log
40ed6913d64897f46b4b6aa20b926e49cc82c6981dccdab3f412b70f324cccbd  ./stdout-p18-imp-6d327dcb-seed-27.log
ad8c8de4b2c48560a616d6b737bed25b3b1b2cfc64466653ba5b5902d914d59d  ./stdout-p18-imp-6d327dcb-seed-28.log
eb58bb7e5a893effd99f40374b23d2745660ce4ef61e5dc95f761e701758db83  ./stdout-p18-imp-6d327dcb-seed-29.log
eb58bb7e5a893effd99f40374b23d2745660ce4ef61e5dc95f761e701758db83  ./stdout-p18-imp-6d327dcb-seed-3.log
ad8c8de4b2c48560a616d6b737bed25b3b1b2cfc64466653ba5b5902d914d59d  ./stdout-p18-imp-6d327dcb-seed-30.log
eb58bb7e5a893effd99f40374b23d2745660ce4ef61e5dc95f761e701758db83  ./stdout-p18-imp-6d327dcb-seed-31.log
d1443f2825aa1ce6e0838f2f90f63001870767c4703df26ecdbe5ec954ead2ce  ./stdout-p18-imp-6d327dcb-seed-32.log
eda5acc35d858dc7ef5dde784f24fa65f9b7c3d13d249d3f19c47d486db13fb9  ./stdout-p18-imp-6d327dcb-seed-33.log
2327d4733e53de64215ba457f0c75073d8ad82e60542c54d8ddc6f99a40cc025  ./stdout-p18-imp-6d327dcb-seed-34.log
fff8c3cd1cd9dce1d17db239dd8eff7ccbe425d64fcb7403988d82222807820e  ./stdout-p18-imp-6d327dcb-seed-35.log
eda5acc35d858dc7ef5dde784f24fa65f9b7c3d13d249d3f19c47d486db13fb9  ./stdout-p18-imp-6d327dcb-seed-36.log
eb58bb7e5a893effd99f40374b23d2745660ce4ef61e5dc95f761e701758db83  ./stdout-p18-imp-6d327dcb-seed-37.log
82ea2dec7877a26bee2906d9ccd696002e9060b2475c4ffb218765b7f8360f54  ./stdout-p18-imp-6d327dcb-seed-38.log
40ed6913d64897f46b4b6aa20b926e49cc82c6981dccdab3f412b70f324cccbd  ./stdout-p18-imp-6d327dcb-seed-39.log
40ed6913d64897f46b4b6aa20b926e49cc82c6981dccdab3f412b70f324cccbd  ./stdout-p18-imp-6d327dcb-seed-4.log
fff8c3cd1cd9dce1d17db239dd8eff7ccbe425d64fcb7403988d82222807820e  ./stdout-p18-imp-6d327dcb-seed-40.log
eb58bb7e5a893effd99f40374b23d2745660ce4ef61e5dc95f761e701758db83  ./stdout-p18-imp-6d327dcb-seed-41.log
eb58bb7e5a893effd99f40374b23d2745660ce4ef61e5dc95f761e701758db83  ./stdout-p18-imp-6d327dcb-seed-42.log
82ea2dec7877a26bee2906d9ccd696002e9060b2475c4ffb218765b7f8360f54  ./stdout-p18-imp-6d327dcb-seed-43.log
d1443f2825aa1ce6e0838f2f90f63001870767c4703df26ecdbe5ec954ead2ce  ./stdout-p18-imp-6d327dcb-seed-44.log
c760e35d72c010433ae021f0a429df5c86803809abd735a949c223f7c2a4df70  ./stdout-p18-imp-6d327dcb-seed-45.log
fff8c3cd1cd9dce1d17db239dd8eff7ccbe425d64fcb7403988d82222807820e  ./stdout-p18-imp-6d327dcb-seed-46.log
c760e35d72c010433ae021f0a429df5c86803809abd735a949c223f7c2a4df70  ./stdout-p18-imp-6d327dcb-seed-47.log
fff8c3cd1cd9dce1d17db239dd8eff7ccbe425d64fcb7403988d82222807820e  ./stdout-p18-imp-6d327dcb-seed-48.log
c760e35d72c010433ae021f0a429df5c86803809abd735a949c223f7c2a4df70  ./stdout-p18-imp-6d327dcb-seed-49.log
fff8c3cd1cd9dce1d17db239dd8eff7ccbe425d64fcb7403988d82222807820e  ./stdout-p18-imp-6d327dcb-seed-5.log
eda5acc35d858dc7ef5dde784f24fa65f9b7c3d13d249d3f19c47d486db13fb9  ./stdout-p18-imp-6d327dcb-seed-6.log
d1443f2825aa1ce6e0838f2f90f63001870767c4703df26ecdbe5ec954ead2ce  ./stdout-p18-imp-6d327dcb-seed-7.log
2ca413b95aa463c4e0742a3c882035484e68ffa18516e42406d3a5cdbd510375  ./stdout-p18-imp-6d327dcb-seed-8.log
d1443f2825aa1ce6e0838f2f90f63001870767c4703df26ecdbe5ec954ead2ce  ./stdout-p18-imp-6d327dcb-seed-9.log
0de2ecf6fd5ffbf34be04df05a54dceddf58a754b6eceeac5efcfcc3c85794d7  ./stdout-p18-imp-7f73929d-seed-0.log
b423b9b4e6614056d11136d24d6fce2d12caf634c2f3bdb2f0362ebf5f774e2d  ./stdout-p18-imp-7f73929d-seed-1.log
3f58d2cba8fb20bf9d8d929880fb0f5aaf017ad6a7a1f7a845730192fa5226af  ./stdout-p18-imp-7f73929d-seed-10.log
b6ec2d15fbd721b9d2b06bbb3298aa38be1a08400e9f159e092d98350b8ee9d2  ./stdout-p18-imp-7f73929d-seed-11.log
3d9562ae35c4a18cd39ed53b161d224cb23c10ac428b783e1359e3646e84430f  ./stdout-p18-imp-7f73929d-seed-12.log
7459c6a647e63f3b93fa55c473440bf42b7ce4669137574f01b89924f5838b71  ./stdout-p18-imp-7f73929d-seed-13.log
b7b7dff8cc797da9d928d5b963f4e8970729b9ae025c42069daf8dbfc0de5b25  ./stdout-p18-imp-7f73929d-seed-14.log
b7b7dff8cc797da9d928d5b963f4e8970729b9ae025c42069daf8dbfc0de5b25  ./stdout-p18-imp-7f73929d-seed-15.log
7459c6a647e63f3b93fa55c473440bf42b7ce4669137574f01b89924f5838b71  ./stdout-p18-imp-7f73929d-seed-16.log
e7ee950f88e58472b3febfcaacd2310491fec45f2d5e898996c84797614ce623  ./stdout-p18-imp-7f73929d-seed-17.log
e7ee950f88e58472b3febfcaacd2310491fec45f2d5e898996c84797614ce623  ./stdout-p18-imp-7f73929d-seed-18.log
df3d3a7fbf0e766ee32e0aa7bd541ef616cfab6dc0f68a79e560470a870efd71  ./stdout-p18-imp-7f73929d-seed-19.log
09981f91b5a799250e290022ee6a3483b7096ed2e8173830499d31a72a688302  ./stdout-p18-imp-7f73929d-seed-2.log
df3d3a7fbf0e766ee32e0aa7bd541ef616cfab6dc0f68a79e560470a870efd71  ./stdout-p18-imp-7f73929d-seed-20.log
e7ee950f88e58472b3febfcaacd2310491fec45f2d5e898996c84797614ce623  ./stdout-p18-imp-7f73929d-seed-21.log
8dad2629dbd94425389ba8dbcb6b54232b671293229ae5a1edd9f7b00b7d3d0c  ./stdout-p18-imp-7f73929d-seed-22.log
b6ec2d15fbd721b9d2b06bbb3298aa38be1a08400e9f159e092d98350b8ee9d2  ./stdout-p18-imp-7f73929d-seed-23.log
09981f91b5a799250e290022ee6a3483b7096ed2e8173830499d31a72a688302  ./stdout-p18-imp-7f73929d-seed-24.log
09981f91b5a799250e290022ee6a3483b7096ed2e8173830499d31a72a688302  ./stdout-p18-imp-7f73929d-seed-25.log
e7ee950f88e58472b3febfcaacd2310491fec45f2d5e898996c84797614ce623  ./stdout-p18-imp-7f73929d-seed-26.log
e7ee950f88e58472b3febfcaacd2310491fec45f2d5e898996c84797614ce623  ./stdout-p18-imp-7f73929d-seed-27.log
09981f91b5a799250e290022ee6a3483b7096ed2e8173830499d31a72a688302  ./stdout-p18-imp-7f73929d-seed-28.log
df3d3a7fbf0e766ee32e0aa7bd541ef616cfab6dc0f68a79e560470a870efd71  ./stdout-p18-imp-7f73929d-seed-29.log
8dad2629dbd94425389ba8dbcb6b54232b671293229ae5a1edd9f7b00b7d3d0c  ./stdout-p18-imp-7f73929d-seed-3.log
09981f91b5a799250e290022ee6a3483b7096ed2e8173830499d31a72a688302  ./stdout-p18-imp-7f73929d-seed-30.log
e7ee950f88e58472b3febfcaacd2310491fec45f2d5e898996c84797614ce623  ./stdout-p18-imp-7f73929d-seed-31.log
09981f91b5a799250e290022ee6a3483b7096ed2e8173830499d31a72a688302  ./stdout-p18-imp-7f73929d-seed-32.log
3f58d2cba8fb20bf9d8d929880fb0f5aaf017ad6a7a1f7a845730192fa5226af  ./stdout-p18-imp-7f73929d-seed-33.log
8dad2629dbd94425389ba8dbcb6b54232b671293229ae5a1edd9f7b00b7d3d0c  ./stdout-p18-imp-7f73929d-seed-34.log
8dad2629dbd94425389ba8dbcb6b54232b671293229ae5a1edd9f7b00b7d3d0c  ./stdout-p18-imp-7f73929d-seed-35.log
e7ee950f88e58472b3febfcaacd2310491fec45f2d5e898996c84797614ce623  ./stdout-p18-imp-7f73929d-seed-36.log
09981f91b5a799250e290022ee6a3483b7096ed2e8173830499d31a72a688302  ./stdout-p18-imp-7f73929d-seed-37.log
3f58d2cba8fb20bf9d8d929880fb0f5aaf017ad6a7a1f7a845730192fa5226af  ./stdout-p18-imp-7f73929d-seed-38.log
3f58d2cba8fb20bf9d8d929880fb0f5aaf017ad6a7a1f7a845730192fa5226af  ./stdout-p18-imp-7f73929d-seed-39.log
3f58d2cba8fb20bf9d8d929880fb0f5aaf017ad6a7a1f7a845730192fa5226af  ./stdout-p18-imp-7f73929d-seed-4.log
09981f91b5a799250e290022ee6a3483b7096ed2e8173830499d31a72a688302  ./stdout-p18-imp-7f73929d-seed-40.log
09981f91b5a799250e290022ee6a3483b7096ed2e8173830499d31a72a688302  ./stdout-p18-imp-7f73929d-seed-41.log
e7ee950f88e58472b3febfcaacd2310491fec45f2d5e898996c84797614ce623  ./stdout-p18-imp-7f73929d-seed-42.log
df3d3a7fbf0e766ee32e0aa7bd541ef616cfab6dc0f68a79e560470a870efd71  ./stdout-p18-imp-7f73929d-seed-43.log
3f58d2cba8fb20bf9d8d929880fb0f5aaf017ad6a7a1f7a845730192fa5226af  ./stdout-p18-imp-7f73929d-seed-44.log
09981f91b5a799250e290022ee6a3483b7096ed2e8173830499d31a72a688302  ./stdout-p18-imp-7f73929d-seed-45.log
8dad2629dbd94425389ba8dbcb6b54232b671293229ae5a1edd9f7b00b7d3d0c  ./stdout-p18-imp-7f73929d-seed-46.log
7459c6a647e63f3b93fa55c473440bf42b7ce4669137574f01b89924f5838b71  ./stdout-p18-imp-7f73929d-seed-47.log
b423b9b4e6614056d11136d24d6fce2d12caf634c2f3bdb2f0362ebf5f774e2d  ./stdout-p18-imp-7f73929d-seed-48.log
b423b9b4e6614056d11136d24d6fce2d12caf634c2f3bdb2f0362ebf5f774e2d  ./stdout-p18-imp-7f73929d-seed-49.log
0de2ecf6fd5ffbf34be04df05a54dceddf58a754b6eceeac5efcfcc3c85794d7  ./stdout-p18-imp-7f73929d-seed-5.log
7459c6a647e63f3b93fa55c473440bf42b7ce4669137574f01b89924f5838b71  ./stdout-p18-imp-7f73929d-seed-6.log
8dad2629dbd94425389ba8dbcb6b54232b671293229ae5a1edd9f7b00b7d3d0c  ./stdout-p18-imp-7f73929d-seed-7.log
e7ee950f88e58472b3febfcaacd2310491fec45f2d5e898996c84797614ce623  ./stdout-p18-imp-7f73929d-seed-8.log
09981f91b5a799250e290022ee6a3483b7096ed2e8173830499d31a72a688302  ./stdout-p18-imp-7f73929d-seed-9.log
5431ac4eafe45ab5906cfc091c6fe5675f1cf3c53c6d74a13488f92ba2b0501b  ./stdout-p18-imp-bfd145cb-seed-0.log
7992f193e94255591b45df4115f6e726522a421ad8bbffdea5ba1c7f814e20eb  ./stdout-p18-imp-bfd145cb-seed-1.log
7992f193e94255591b45df4115f6e726522a421ad8bbffdea5ba1c7f814e20eb  ./stdout-p18-imp-bfd145cb-seed-10.log
e32e919f74fcd69154081d48020b85ed54611869f59690612b0f9810af47606c  ./stdout-p18-imp-bfd145cb-seed-11.log
874f838cc0da0495327a25a83a70a3748d572f56da62890e8e8d3b71e84018ec  ./stdout-p18-imp-bfd145cb-seed-12.log
7992f193e94255591b45df4115f6e726522a421ad8bbffdea5ba1c7f814e20eb  ./stdout-p18-imp-bfd145cb-seed-13.log
e32e919f74fcd69154081d48020b85ed54611869f59690612b0f9810af47606c  ./stdout-p18-imp-bfd145cb-seed-14.log
c71f2b4978895283de81ee7068cea60a37a23409fbbb0e75bda7dd60ac93f007  ./stdout-p18-imp-bfd145cb-seed-15.log
c71f2b4978895283de81ee7068cea60a37a23409fbbb0e75bda7dd60ac93f007  ./stdout-p18-imp-bfd145cb-seed-16.log
e7ebf9b83e07da0b20603d22044c97c6eecffcabeed88d1b4d1b9f5504a702b6  ./stdout-p18-imp-bfd145cb-seed-17.log
6c9ee838f6c386fe6684e5b0d3811c441665c72d435bc955b74039996dde5004  ./stdout-p18-imp-bfd145cb-seed-18.log
c71f2b4978895283de81ee7068cea60a37a23409fbbb0e75bda7dd60ac93f007  ./stdout-p18-imp-bfd145cb-seed-19.log
93c70ef12acfbf90d47caeade547e5dc666dd14c5e9cf49a771a9bb0d6e3fef9  ./stdout-p18-imp-bfd145cb-seed-2.log
874f838cc0da0495327a25a83a70a3748d572f56da62890e8e8d3b71e84018ec  ./stdout-p18-imp-bfd145cb-seed-20.log
7992f193e94255591b45df4115f6e726522a421ad8bbffdea5ba1c7f814e20eb  ./stdout-p18-imp-bfd145cb-seed-21.log
395e78fa57abc69c8b11b0139585e1aca2636267502c58bb7b121ce4164dd9e7  ./stdout-p18-imp-bfd145cb-seed-22.log
c71f2b4978895283de81ee7068cea60a37a23409fbbb0e75bda7dd60ac93f007  ./stdout-p18-imp-bfd145cb-seed-23.log
7992f193e94255591b45df4115f6e726522a421ad8bbffdea5ba1c7f814e20eb  ./stdout-p18-imp-bfd145cb-seed-24.log
e7ebf9b83e07da0b20603d22044c97c6eecffcabeed88d1b4d1b9f5504a702b6  ./stdout-p18-imp-bfd145cb-seed-25.log
874f838cc0da0495327a25a83a70a3748d572f56da62890e8e8d3b71e84018ec  ./stdout-p18-imp-bfd145cb-seed-26.log
c71f2b4978895283de81ee7068cea60a37a23409fbbb0e75bda7dd60ac93f007  ./stdout-p18-imp-bfd145cb-seed-27.log
874f838cc0da0495327a25a83a70a3748d572f56da62890e8e8d3b71e84018ec  ./stdout-p18-imp-bfd145cb-seed-28.log
93c70ef12acfbf90d47caeade547e5dc666dd14c5e9cf49a771a9bb0d6e3fef9  ./stdout-p18-imp-bfd145cb-seed-29.log
874f838cc0da0495327a25a83a70a3748d572f56da62890e8e8d3b71e84018ec  ./stdout-p18-imp-bfd145cb-seed-3.log
93c70ef12acfbf90d47caeade547e5dc666dd14c5e9cf49a771a9bb0d6e3fef9  ./stdout-p18-imp-bfd145cb-seed-30.log
c71f2b4978895283de81ee7068cea60a37a23409fbbb0e75bda7dd60ac93f007  ./stdout-p18-imp-bfd145cb-seed-31.log
d493c66cfc8f76c79908dd336210c5a29e3f379cd78b5e848ede69a49b36125f  ./stdout-p18-imp-bfd145cb-seed-32.log
5431ac4eafe45ab5906cfc091c6fe5675f1cf3c53c6d74a13488f92ba2b0501b  ./stdout-p18-imp-bfd145cb-seed-33.log
dd688f6750d7151b7e9437d88731ce43f315c5c4c916b03ffa6f8b5ec3f6fb90  ./stdout-p18-imp-bfd145cb-seed-34.log
395e78fa57abc69c8b11b0139585e1aca2636267502c58bb7b121ce4164dd9e7  ./stdout-p18-imp-bfd145cb-seed-35.log
e7ebf9b83e07da0b20603d22044c97c6eecffcabeed88d1b4d1b9f5504a702b6  ./stdout-p18-imp-bfd145cb-seed-36.log
7992f193e94255591b45df4115f6e726522a421ad8bbffdea5ba1c7f814e20eb  ./stdout-p18-imp-bfd145cb-seed-37.log
e32e919f74fcd69154081d48020b85ed54611869f59690612b0f9810af47606c  ./stdout-p18-imp-bfd145cb-seed-38.log
7992f193e94255591b45df4115f6e726522a421ad8bbffdea5ba1c7f814e20eb  ./stdout-p18-imp-bfd145cb-seed-39.log
7992f193e94255591b45df4115f6e726522a421ad8bbffdea5ba1c7f814e20eb  ./stdout-p18-imp-bfd145cb-seed-4.log
e32e919f74fcd69154081d48020b85ed54611869f59690612b0f9810af47606c  ./stdout-p18-imp-bfd145cb-seed-40.log
e7ebf9b83e07da0b20603d22044c97c6eecffcabeed88d1b4d1b9f5504a702b6  ./stdout-p18-imp-bfd145cb-seed-41.log
e7ebf9b83e07da0b20603d22044c97c6eecffcabeed88d1b4d1b9f5504a702b6  ./stdout-p18-imp-bfd145cb-seed-42.log
93c70ef12acfbf90d47caeade547e5dc666dd14c5e9cf49a771a9bb0d6e3fef9  ./stdout-p18-imp-bfd145cb-seed-43.log
7992f193e94255591b45df4115f6e726522a421ad8bbffdea5ba1c7f814e20eb  ./stdout-p18-imp-bfd145cb-seed-44.log
c71f2b4978895283de81ee7068cea60a37a23409fbbb0e75bda7dd60ac93f007  ./stdout-p18-imp-bfd145cb-seed-45.log
dd688f6750d7151b7e9437d88731ce43f315c5c4c916b03ffa6f8b5ec3f6fb90  ./stdout-p18-imp-bfd145cb-seed-46.log
e7ebf9b83e07da0b20603d22044c97c6eecffcabeed88d1b4d1b9f5504a702b6  ./stdout-p18-imp-bfd145cb-seed-47.log
874f838cc0da0495327a25a83a70a3748d572f56da62890e8e8d3b71e84018ec  ./stdout-p18-imp-bfd145cb-seed-48.log
e32e919f74fcd69154081d48020b85ed54611869f59690612b0f9810af47606c  ./stdout-p18-imp-bfd145cb-seed-49.log
dd688f6750d7151b7e9437d88731ce43f315c5c4c916b03ffa6f8b5ec3f6fb90  ./stdout-p18-imp-bfd145cb-seed-5.log
7992f193e94255591b45df4115f6e726522a421ad8bbffdea5ba1c7f814e20eb  ./stdout-p18-imp-bfd145cb-seed-6.log
25ce6986fdc5355d4ee01d5e0a43d90d2a9e6dcc566ccaa8d0a99cb29745de97  ./stdout-p18-imp-bfd145cb-seed-7.log
dd688f6750d7151b7e9437d88731ce43f315c5c4c916b03ffa6f8b5ec3f6fb90  ./stdout-p18-imp-bfd145cb-seed-8.log
c71f2b4978895283de81ee7068cea60a37a23409fbbb0e75bda7dd60ac93f007  ./stdout-p18-imp-bfd145cb-seed-9.log
d4e7769bff7b82c21da22a91aea96806f638ef543682871c9769cdf099df2044  ./stdout-p18-imp-ea4bc955-seed-0.log
d4e7769bff7b82c21da22a91aea96806f638ef543682871c9769cdf099df2044  ./stdout-p18-imp-ea4bc955-seed-1.log
7ac92fa34195f5a7d7c7886fe6fea130f6a14ee9730733dab64fd8043113d423  ./stdout-p18-imp-ea4bc955-seed-10.log
d4e7769bff7b82c21da22a91aea96806f638ef543682871c9769cdf099df2044  ./stdout-p18-imp-ea4bc955-seed-11.log
478479a66f05ce3ddaa0045ada7730d2f877f2d6ea2a4bf9b0ef3087c0bb61c9  ./stdout-p18-imp-ea4bc955-seed-12.log
5f714bf293875379e4cec907c19871428b2b5b37d59c4d44e70f52ac9cca281e  ./stdout-p18-imp-ea4bc955-seed-13.log
673f8079cbee5589779f7f4f0453e1de3f31fb491f7a7632383f08d272660d58  ./stdout-p18-imp-ea4bc955-seed-14.log
869f9438d18f5ba257270d9245d273233564ab10c7640cf15bb6819677ce0917  ./stdout-p18-imp-ea4bc955-seed-15.log
d4e7769bff7b82c21da22a91aea96806f638ef543682871c9769cdf099df2044  ./stdout-p18-imp-ea4bc955-seed-16.log
12d2062e0a9f905c1fefbe9180cb2480e97e3b190c8fd027f6d8b76e7a0b1941  ./stdout-p18-imp-ea4bc955-seed-17.log
6037c0412fcdabfced6356dbd0477b620b2c275bc80655f2ed5c32d12b114eed  ./stdout-p18-imp-ea4bc955-seed-18.log
869f9438d18f5ba257270d9245d273233564ab10c7640cf15bb6819677ce0917  ./stdout-p18-imp-ea4bc955-seed-19.log
478479a66f05ce3ddaa0045ada7730d2f877f2d6ea2a4bf9b0ef3087c0bb61c9  ./stdout-p18-imp-ea4bc955-seed-2.log
478479a66f05ce3ddaa0045ada7730d2f877f2d6ea2a4bf9b0ef3087c0bb61c9  ./stdout-p18-imp-ea4bc955-seed-20.log
5f714bf293875379e4cec907c19871428b2b5b37d59c4d44e70f52ac9cca281e  ./stdout-p18-imp-ea4bc955-seed-21.log
a450d02b6e4c9a644a129a37aa89ed2be8ba2e27b2fb06f61bba1b4c31b0fe6b  ./stdout-p18-imp-ea4bc955-seed-22.log
5f714bf293875379e4cec907c19871428b2b5b37d59c4d44e70f52ac9cca281e  ./stdout-p18-imp-ea4bc955-seed-23.log
5f714bf293875379e4cec907c19871428b2b5b37d59c4d44e70f52ac9cca281e  ./stdout-p18-imp-ea4bc955-seed-24.log
d4e7769bff7b82c21da22a91aea96806f638ef543682871c9769cdf099df2044  ./stdout-p18-imp-ea4bc955-seed-25.log
478479a66f05ce3ddaa0045ada7730d2f877f2d6ea2a4bf9b0ef3087c0bb61c9  ./stdout-p18-imp-ea4bc955-seed-26.log
d4e7769bff7b82c21da22a91aea96806f638ef543682871c9769cdf099df2044  ./stdout-p18-imp-ea4bc955-seed-27.log
673f8079cbee5589779f7f4f0453e1de3f31fb491f7a7632383f08d272660d58  ./stdout-p18-imp-ea4bc955-seed-28.log
478479a66f05ce3ddaa0045ada7730d2f877f2d6ea2a4bf9b0ef3087c0bb61c9  ./stdout-p18-imp-ea4bc955-seed-29.log
869f9438d18f5ba257270d9245d273233564ab10c7640cf15bb6819677ce0917  ./stdout-p18-imp-ea4bc955-seed-3.log
5f714bf293875379e4cec907c19871428b2b5b37d59c4d44e70f52ac9cca281e  ./stdout-p18-imp-ea4bc955-seed-30.log
869f9438d18f5ba257270d9245d273233564ab10c7640cf15bb6819677ce0917  ./stdout-p18-imp-ea4bc955-seed-31.log
12d2062e0a9f905c1fefbe9180cb2480e97e3b190c8fd027f6d8b76e7a0b1941  ./stdout-p18-imp-ea4bc955-seed-32.log
478479a66f05ce3ddaa0045ada7730d2f877f2d6ea2a4bf9b0ef3087c0bb61c9  ./stdout-p18-imp-ea4bc955-seed-33.log
478479a66f05ce3ddaa0045ada7730d2f877f2d6ea2a4bf9b0ef3087c0bb61c9  ./stdout-p18-imp-ea4bc955-seed-34.log
478479a66f05ce3ddaa0045ada7730d2f877f2d6ea2a4bf9b0ef3087c0bb61c9  ./stdout-p18-imp-ea4bc955-seed-35.log
74e761ab515ccb82dab4762f335b6a532d111f15f440cae4478157a29d73bc07  ./stdout-p18-imp-ea4bc955-seed-36.log
673f8079cbee5589779f7f4f0453e1de3f31fb491f7a7632383f08d272660d58  ./stdout-p18-imp-ea4bc955-seed-37.log
7ac92fa34195f5a7d7c7886fe6fea130f6a14ee9730733dab64fd8043113d423  ./stdout-p18-imp-ea4bc955-seed-38.log
673f8079cbee5589779f7f4f0453e1de3f31fb491f7a7632383f08d272660d58  ./stdout-p18-imp-ea4bc955-seed-39.log
673f8079cbee5589779f7f4f0453e1de3f31fb491f7a7632383f08d272660d58  ./stdout-p18-imp-ea4bc955-seed-4.log
96dfc8d9d1d187b06ec1cd7abdfe0e5d3acdba035a237d35cccbc3efe1c85c7a  ./stdout-p18-imp-ea4bc955-seed-40.log
7ac92fa34195f5a7d7c7886fe6fea130f6a14ee9730733dab64fd8043113d423  ./stdout-p18-imp-ea4bc955-seed-41.log
7ac92fa34195f5a7d7c7886fe6fea130f6a14ee9730733dab64fd8043113d423  ./stdout-p18-imp-ea4bc955-seed-42.log
869f9438d18f5ba257270d9245d273233564ab10c7640cf15bb6819677ce0917  ./stdout-p18-imp-ea4bc955-seed-43.log
5f714bf293875379e4cec907c19871428b2b5b37d59c4d44e70f52ac9cca281e  ./stdout-p18-imp-ea4bc955-seed-44.log
673f8079cbee5589779f7f4f0453e1de3f31fb491f7a7632383f08d272660d58  ./stdout-p18-imp-ea4bc955-seed-45.log
478479a66f05ce3ddaa0045ada7730d2f877f2d6ea2a4bf9b0ef3087c0bb61c9  ./stdout-p18-imp-ea4bc955-seed-46.log
5f714bf293875379e4cec907c19871428b2b5b37d59c4d44e70f52ac9cca281e  ./stdout-p18-imp-ea4bc955-seed-47.log
478479a66f05ce3ddaa0045ada7730d2f877f2d6ea2a4bf9b0ef3087c0bb61c9  ./stdout-p18-imp-ea4bc955-seed-48.log
673f8079cbee5589779f7f4f0453e1de3f31fb491f7a7632383f08d272660d58  ./stdout-p18-imp-ea4bc955-seed-49.log
7ac92fa34195f5a7d7c7886fe6fea130f6a14ee9730733dab64fd8043113d423  ./stdout-p18-imp-ea4bc955-seed-5.log
5f714bf293875379e4cec907c19871428b2b5b37d59c4d44e70f52ac9cca281e  ./stdout-p18-imp-ea4bc955-seed-6.log
d4e7769bff7b82c21da22a91aea96806f638ef543682871c9769cdf099df2044  ./stdout-p18-imp-ea4bc955-seed-7.log
d4e7769bff7b82c21da22a91aea96806f638ef543682871c9769cdf099df2044  ./stdout-p18-imp-ea4bc955-seed-8.log
869f9438d18f5ba257270d9245d273233564ab10c7640cf15bb6819677ce0917  ./stdout-p18-imp-ea4bc955-seed-9.log
d2c4a102083edc6d616dbfcda02268fdab92b933dbf2d203826ec2451ee1f6ec  ./sync-jsonl.py
```
