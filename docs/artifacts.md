# Artifact classes — what lives in git, and what lives on a pinned sha

This document is the retention rule for every byte this repository **produces**.
It is vendor-neutral on purpose: the classes describe *what an artifact is for*,
not which host holds it, so the rule survives a move off GitHub.

**Where the boundary is**, because "every byte" needs one to be checkable:
this covers *produced* artifacts — recordings, weights, measurements, manifests,
renders, harness outputs. It does not cover **source** (code, prompt templates,
the tests themselves, hand-authored assets such as `frontend/src/assets/`),
**configuration** (`pyproject.toml`, `frontend/package.json`, lockfiles,
`tsconfig.json`, `.env.example`) or **prose** (`docs/`, `tasks/`,
`agent_prompts/`, `audits/`, per-package `README.md`), none of which is produced
by running anything. The registry below is complete against that boundary — a
family missing from it is a defect in this document, not an unclassified byte.

Anchors: `audits/audit-phase-19-triage.md` §7 item 23 \[C; VERIFIED §8 row 11\]
(*"define vendor-neutral artifact classes and manifests **before** moving
bytes"*); Phase-19 **locked decision 5** (`tasks/phase-19.md` — artifact
retention: prune coevo only); `audits/audit-phase-18-close.md` §6.3 C4 (the
coevo namespace rules).

**The one-line summary.** Small canonical bytes and every manifest stay in git;
large immutable evidence lives on ONE orphan commit fetched **by sha**;
regenerable views are never committed at all. A test-pinned byte is never
class (c), whatever it weighs.

## The four classes

### (a) Small canonical fixtures — **in git**

The bytes a reader or a test must have on a bare checkout, with no network and
no extra command. They are small, they are read constantly, and a checkout
without them is broken rather than merely incomplete.

*Rule:* committed, tracked, diffable. Anything a test opens is class (a) by
definition — the test is the authority, not the file's size.

### (b) Manifests, hashes and summaries — **in git**

The records *about* bytes: per-file sha-256 manifests, provenance logs, the
flattened measurement rows a report's cells are read from, the audits. They are
tiny relative to what they describe and they are what makes class (c)
verifiable, so as a rule they do not move with the bytes they cover (the one
deliberate exception is named under "What does not move" below).

*Rule:* committed, and each fact has exactly ONE owning file. A second copy of a
digest table is a drift class, not a backup — where a manifest delegates, it
says which file owns the rows and how to transform them.

### (c) Large immutable evidence — **on the evidence commit, fetched by sha**

The event-level bytes behind a closed campaign: raw per-seed recordings, audit
sidecars, unpinned genome directories. Large, never edited again, and read only
when someone audits a specific claim. They are reachable, hashed and immutable —
they are simply not in your working tree until you ask for them.

*Rule:* one **orphan** commit per evidence set, its tip sha **pinned in an
in-tree class-(b) manifest**, fetched by that sha and never by branch name.
A branch name is a moving pointer; the sha is not, and that is the entire
immutability guarantee. Restored bytes are **untracked by design** and must
never be committed back into the tree — `scripts/fetch_evidence.sh` enforces
that rather than merely asking, by writing a `.gitignore` at each destination
root so `git add -A` cannot stage them (tracked files are unaffected by an
ignore rule, so the retained in-tree bytes still show up in `git status`). Those
files go down **before the first byte is extracted**, not after the last one, so
a restore that dies half-way — a full disk, a killed process — still leaves
nothing stageable behind. `--clean` removes the restored bytes and those files
together.

### (d) Disposable regenerated views — **not committed**

Anything a command reproduces from class (a)/(b)/(c) bytes: local replay runs,
tournament report directories, the observation firewall's packet audit logs,
`frontend/dist/`, the static demo bundle, coverage output.

*Rule:* not committed, and the command that regenerates it is documented rather
than its output preserved.

## The registry

| artifact | class | where | size |
|---|---|---|---|
| `replays/samples/` — the baseline-6 adopting record (100 replays + per-set `MANIFEST.md`) | (a) + (b) | in git | 61 MB / 107 files |
| `replays/ml_corpus/` — the committed ML corpus | (a) | in git | 161 MB / 209 files |
| `agents/tactical/learned/{weights,crew_weights}.json` + `.sha256` — the **shipped inference weights** the live tactical factories load | (a) + (b) | in git | 4 files |
| `tests/fixtures/` — golden fixtures (rendered memory views and their inputs) | (a) | in git | 2.1 MB / 19 files |
| `data/personas.json` — the canonical persona set | (a) | in git | 12 KB |
| `training/artifacts/impostor/`, `crew/`, `anchor_study/` — the **canonical learned genomes** (`weights.json` + `config.json` + `stamp.json` + `weights.json.sha256`) | (a) + (b) | in git | 1.5 MB / 105 files |
| `training/artifacts/surrogate/`, `conviction/`, `composed/` — the ballot surrogate, the conviction model and the composed-runner verdict, with their sidecars | (a) + (b) | in git | 52 KB / 10 files |
| `training/artifacts/coevo/` — the 90 retained bytes (rankings, `measurement-stability.json`, the 8 pinned genome dirs, `provenance/`, `PATHS.md`) | (a) + (b) | in git | 495 KiB / 90 files |
| `training/artifacts/coevo/EVIDENCE-MANIFEST.md` — the pin + the digests + the consumer enumeration | (b) | in git | 283 KiB |
| `training/reports/` — the reports and their flattened `results-*.jsonl` rows | (b) | in git | 2.5 MB / 21 files |
| `training/reports/_finalist_eval_raw/MANIFEST.md` — the slate's per-file digests (Task 19.21) | (b) | in git | 1,569 digests |
| `audits/` — the audit record | (b) | in git | 6.8 MB / 149 files |
| `docs/media/` — the README capture + screenshot | (a) | in git | 1.7 MB / 3 files |
| `design/phase-12/` — the design-artifact record (map reference renders + briefs) | (b) | in git | 1.9 MB / 18 files |
| `experiments/lab/`, `experiments/model_probe/` — recorded read-only harness outputs and their syntheses (`experiments/` outputs are artifacts, not behavior — `docs/architecture.md`) | (b) | in git | 7.3 MB / 164 files |
| **`coevo/` on `evidence/phase-18-coevo`** — every unpinned Phase-18 co-evolution byte | **(c)** | pinned sha | **101.097 MiB / 1,383 files** |
| **`finalist-eval-raw/` on `evidence/phase-18-coevo`** — the Phase-18 finalist raw slate (Task 19.21's outcome, below) | **(c)** | pinned sha | **298.157 MiB / 1,569 files** |
| local `replays/*.jsonl`, tournament report dirs, the firewall's `**/*.audit.jsonl` packet logs, `frontend/dist/`, the demo bundle | (d) | regenerated (`.gitignore`d) | — |

**Why the other `training/artifacts/` families are class (a) and coevo mostly is
not.** The six sibling families above are the *live* learned artifacts — the
weights the inference path loads and the sidecars 19.23 verifies offline — and
the test suite opens them directly, which is what class (a) means. `coevo/` is
the *record of a closed campaign*: 90 of its files are opened by a test and stay,
and the 1,383 nobody opens are class (c). Same directory tree, two different
classes, decided the same way in both cases — by what the consumers read.

### The class-(c) rows in detail

Both live on **one** orphan commit —
`evidence/phase-18-coevo` @ `476a1f85492439277350af9708f1d120eb1c0a71` — and
that sha is pinned in `training/artifacts/coevo/EVIDENCE-MANIFEST.md` §1.
Restore either or both with:

```bash
bash scripts/fetch_evidence.sh            # fetch by the pinned sha, restore, verify
bash scripts/fetch_evidence.sh --verify   # verify what is already restored
bash scripts/fetch_evidence.sh --clean    # remove the restored bytes again
```

**`coevo/` — the Phase-18 co-evolution prune (Task 19.22).** The 1,383 files
under `training/artifacts/coevo/` that no test opens: the `realpath*` per-seed
recordings and their roster descriptors, the 245 unpinned genome directories,
the per-tranche `recordings-manifest*.sha256`, the campaign plans/rows and
hall-of-fame files. What stayed, and which test pins each retained path, is
enumerated in the manifest's §3. A weight and its sidecar always travel
together (§5), so verification-after-fetch has something to check against.

**`finalist-eval-raw/` — the Phase-18 finalist raw slate (Task 19.21's
outcome).** 19.21 asked whether the 449-game slate behind the Phase-18 adoption
decision still existed. **Ruling 2026-08-15: RECOVERED** — 1,569 files /
298.157 MiB, content-addressed into
`training/reports/_finalist_eval_raw/MANIFEST.md` and staged on a temporary
`evidence/raw-slate-staging` ref. Task 19.22 re-verified all 1,569 files against
that manifest (1,569/1,569 OK, 0 failures) and folded them into the evidence
commit, which **supersedes and retires that ref** — its actual deletion is the
one step that task could not execute (GitHub refused the delete-push with 403),
and `EVIDENCE-MANIFEST.md` §4 carries the one-command owner step and the current
status. Nothing was re-recorded; the slate's ~57
busy-hour price is named and declined by the Phase-19 charter. Preserving the
bytes makes the lineage *auditable* — these are real-provider draws, so it does
not make the run re-runnable.

## What does not move, and why

- **Anything a test opens.** The consumer enumeration comes first and the
  consumers win. `training/artifacts/coevo/EVIDENCE-MANIFEST.md` §3 records it
  path by path, taken empirically (an audit hook over a full `pytest` run), not
  from prose.
- **`replays/`** — samples and `ml_corpus` both stay whole in git
  (locked decision 5). They are the reproducibility surface the front door
  promises on a bare clone.
- **`measurement-stability.json` and `provenance/`** — the campaign's own
  measurement and its provenance records are class (b) and stay in-tree even
  though the bytes they describe left.
- **Manifests never travel with what they hash**, with one deliberate exception:
  the per-tranche `recordings-manifest*.sha256` files moved *with* their
  recordings, because they verify in place after a restore exactly as
  `training/artifacts/coevo/PATHS.md` documents, and the in-tree manifest hashes
  them too.

## The namespace rule (from `audits/audit-phase-18-close.md` §6.3 C4)

`scripts/generate_campaign_tables.py::DEFAULT_RANKING_ROOTS` folds whole trees,
and `measurement-stability.json` is byte-pinned over a default-roots
recomputation — so a new ranking landing *under* a default root silently changes
the pinned reproduction. **A future campaign takes a SIBLING root, never a subdir
of a default root.** The prune obeys this: it removed only files and left the
four default roots (`realpath`, `realpath-backfill`, `realpath-runnerups`,
`realpath-runnerups-gen3`) exactly as `DEFAULT_RANKING_ROOTS` names them, with
every `ranking*.jsonl` they hold still in-tree.

## The fast clone

```bash
git clone --filter=blob:none https://github.com/dkdan10/AiLibi.git
```

A blobless partial clone fetches the commit graph up front and file contents on
demand, so a fresh checkout downloads roughly the 256 MiB the working tree
actually needs rather than every version of every blob the history holds.

**The honest caveat: a full-history clone stays heavy.** Phase 19 rewrote no
history (locked decision 5), so every byte the prune removed is still reachable
from an older commit and a plain `git clone` still pays for all of it. The prune
shrinks the *working tree*, not the repository. Making a full clone smaller
needs a deliberate history rewrite — a `filter-repo` pass and a force-push that
invalidates every existing clone and every commit sha in every audit — which is
a decision with its own cost, not a cleanup. It is not scheduled.
