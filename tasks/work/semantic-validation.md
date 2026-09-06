# Verify event entitlement and engine outcomes independently

**Status:** active

## Outcome

The remaining code-first gate findings B-3/B-4/B-27/B-29/B-30 have independent
semantic controls and current coverage measurements. A passing recording scan
cannot derive its entire witness permission from the witness list being tested.

## Evidence

The current factory leak scan trusts kill/vent witness lists, checks task-field
shape without the existing ownership-to-world comparison, and requires only a
visible body for coverage. The corpus is not exercised by that factory sweep.
Engine property tests cover totality while meeting-win invariants are covered
only by examples. These are gate gaps, not evidence that every production event
is wrong. The historical default opening-ID exposure remains separately declared.

## Acceptance

- [x] Reconstruct event-local player positions, life and vent occupancy from
  pre-tick state and ordered events, independently check kill/vent witness sets,
  and wire the check into factory reconstruction. Planted widened and omitted
  witnesses fail; arrivals/departures and later deaths remain valid.
- [x] Run the actual task-ownership comparison on factory packets; a foreign
  valid map-task ID fails beyond the schema/shape checks.
- [x] Add engine property assertions for life/role/body consistency and terminal
  outcomes, including a planted meeting-at-parity result. Preserve the engine's
  intentional early-meeting action interruption and passive task API.
- [x] Supply a reproducible current-corpus packet scan with input identities and
  actual per-channel counts. Check strict replay validity separately and prove
  the scanner rejects planted contamination. Describe it as observation-service
  coverage, not proof about the training feature reducer or model prompts.
- [ ] Independently review, run focused and complete checks and canonical samples;
  record every retained limitation and assign findings in the current ledger.

## Constraints

Follow docs/architecture.md; scanners are privileged and agents remain engine-free.
No engine behavior, current prompt/detector bytes, weights, historical records,
provider calls or adoption change. Do not claim a broader privacy proof than
the checked channel and clock. Reconstruction must respect event order.

## Expected scope

Root owns eval/leak_scan.py, a new corpus scan script and tests, engine property
tests and relevant gate tests. New semantic helpers may live beside the scanner.
Provenance owner coordinates later verify_ml_evidence.py wiring; tactical owner
owns engine implementation, and its default behavior must remain unchanged.

## Record impact

None to gameplay or historical bytes. Read-only verification and explicit
invalid-evidence refusal; any implementation-experiment input remains versioned
and is scanned only by readers supporting its declared profile.

## Validation

Run real factory/current-corpus streams and temporary planted defects; report
source fingerprints and separate packet channel counts. Exercise properties and
legacy controls, strict typing/lint, `bash scripts/check.sh` and all samples.

## Results in progress

Factory reconstruction now independently folds ordered movement/kill/vent
changes from the pre-tick state, checks both vent endpoints and the exact
witness union, and requires the final player positions/life/vent occupancy to
agree. It does not import the engine witness helper. Actual source-side witness
omission changes no engine hash but fails this check; widened/omitted kill
witnesses, reordered movement and a later-killed observer have adverse and valid
controls. Factory packets also run the real owned-task-to-world comparison.

Engine property runs now assert immutable roles, no resurrection, bodies only
for dead players and terminal outcome/event consistency. Planted resurrection
and meeting-at-parity states fail; actual meeting interruption remains valid.

The standalone command is:

```sh
uv run python scripts/scan_recording_packets.py replays/ml_corpus/4p1i
uv run python scripts/scan_recording_packets.py replays/ml_corpus/9p2i
```

Both strict scans passed against unchanged input sets. These counts are
snapshot rows/appearances, not distinct events or temporal delivery batches:

| Set | Games | Packets | Kill views | Vent views | Body views | Movement rows | Alarms |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 4p1i | 50 | 1,880 | 0 | 31 | 156 | 649 | 0 |
| 9p2i | 150 | 24,291 | 50 | 370 | 2,597 | 12,660 | 348 |

The four-player zeros are unexercised channels, not evidence of error-free
handling. The default pytest suite runs both real sets; the independent
scripted/property cases supply additional channels and plants. Five corpus
checks passed, including actual witness-producer contamination, a valid roster
whose bytes change during scanning, and missing explicit roster refusal.

Source fingerprints: 4p1i sha256:bb890a313ecaf8ec0f050a5aac14618b320d685ea93b911e71f81cdf6ba3003c;
9p2i sha256:0f5d8a9de28e7a85480aa683d210f077a9995e68b7bc43f06e21916ee60bc86a.
Canonical map SHA-256: 070346ceabc353d84101038ed8d281c02c74cc7879423d925f13895a75af6b3e.
Logs: /tmp/ailibi-corpus-packet-4p.json, /tmp/ailibi-corpus-packet-9p.json,
/tmp/ailibi-corpus-scan-tests.log. All 43 existing leak/property integrations
passed; the later combined targeted selection is recorded in the protocol card.
These are observation-service checks, not certification of the training feature
reducer, every model prompt, or default opening body-ID privacy.
Independent review and the new full-project gate are still pending.
