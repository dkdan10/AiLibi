# A 300-game recording that is not one of the canonical replay sets

**These games read only with three levers switched on** — `AILIBI_REPORTER_REASONING`,
`AILIBI_CORROBORATION_DISCIPLINE` and `AILIBI_TESTIMONY_SHAPES`, all `1`, with
`AILIBI_IMPOSTOR_ROLL_CALL` unset. Every game stamps those three keys, and they are still optional
switches that resolve off in a plain shell, so `api/replay_loader.py::_assert_substrate_matches`
compares the recorded value against the live one and refuses the game. A plain-shell read failing
here is the mechanism working, not a corrupt recording. The slate is declared, machine-readably, in
`EVIDENCE-MANIFEST.md` beside this file.

That is the whole reason these bytes are not under `replays/samples/` or `replays/ml_corpus/`:
putting them there would break the plain-shell sample verifier, the served frontend and the release
gate, on games that are perfectly valid under their own settings.

## What was recorded, and what it decided

300 games across the four set shapes, recorded live at that slate. The bars they were measured
against were fixed in writing before the games existed, and **three of the four were met while the
fourth was missed** — so the levers were not adopted, the canonical sets were left alone, and the
recording is kept as evidence rather than promoted. A recording that missed one of its own
pre-registered bars is evidence either way, which is why it is here at all.

The full reading, cell by cell, is `audits/audit-phase-21-adopting-record.md`. These are the bytes
it reads.

## Where the games are

This directory holds the pin and the digests only. The games themselves — 316 files,
260,116,543 bytes — live on one parentless commit and are fetched by its sha:

```bash
bash scripts/fetch_evidence.sh            # fetch by sha, restore, verify
bash scripts/fetch_evidence.sh --verify   # offline: re-hash what is restored
bash scripts/fetch_evidence.sh --clean    # remove restored files that still match
```

Restored files land beside this one, untracked and ignored by design, and are never committed back.
`EVIDENCE-MANIFEST.md` owns the pinned sha, the per-file `sha256` digests and the declared slate.

## How the landing may still change

Whether a recording like this is carried in the tree or on a pinned commit is an owner decision that
was open when it was taken; the pinned commit is the provisional answer. If the other is chosen, the
games move into this directory and the registry row moves with them — nothing in the reading depends
on which.
