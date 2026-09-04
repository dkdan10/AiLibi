# Phase-21 Wave-2 lever-ON recording — the FINDING record

**These bytes reconstruct only under the declared Wave-2 slate**
(`AILIBI_REPORTER_REASONING=1`, `AILIBI_CORROBORATION_DISCIPLINE=1`, `AILIBI_TESTIMONY_SHAPES=1`,
with `AILIBI_IMPOSTOR_ROLL_CALL` unset), and the reason is mechanical rather than stylistic: every
game stamps those three keys `True`, the pre-registered rule read FINDING so the keys stay live
toggles that resolve `False` in a bare shell, and `api/replay_loader.py::_assert_substrate_matches`
compares the recorded `True` against a live `False` and refuses the game. A bare-shell read failing
here is the mechanism working.

This directory holds the recording's in-tree half only — the pin and the digests. The 300 recorded
games (260,113,361 bytes over 315 files) live on ONE parentless evidence commit,
`evidence/phase-21-wave2-finding` @ `29af85d5457caeba4f8ba8ba77610c6a0ab2213a`, and are fetched by
that sha. `EVIDENCE-MANIFEST.md` beside this file owns the pin, the per-file `sha256` digests and
the restore command; restored bytes are untracked by design and are never committed back.

**Task 21.24 recorded 300 games at the Wave-2 slate and the ratified rule read FINDING over them**
— bars 1, 2 and 3 MET, bar 4 MISSED at 0.5500 against a target of < 0.40. The levers stayed
toggles, the ladder tip stayed at baseline 8, and `replays/samples/` and `replays/ml_corpus/` kept
their baseline-8 bytes. The read, cell by cell, is `audits/audit-phase-21-adopting-record.md`; these
are the bytes it reads, and they are published rather than discarded because a recording that missed
one of its own pre-registered bars is evidence either way.

The landing mechanism is **PROVISIONAL**: the owner decision on how a FINDING record carries its
bytes (in-tree, or the pinned evidence commit used here) was open at dispatch, and this record
executed the orchestrator's recommendation. Nothing in the read depends on which is chosen.
