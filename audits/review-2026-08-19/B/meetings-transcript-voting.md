# Code review — meetings/transcript.py, voting.py, render_contract.py, schemas.py (+ tests)

Track: CODE-UP, read-only. Reviewer label: `meetings-transcript-voting`.
Repo: /Users/danielkeinan/projects/AiLibi @ main (b809b19c). Python 3.11 via `uv run`.
Machine load during timings: `load averages: 6.14–6.56` (10-core, other reviewers concurrent).

Scratch/evidence scripts (all reproducible with `PYTHONPATH=. uv run python <script>` from repo root):
- `.../scratchpad/work/meetings-transcript-voting/probe_provenance.py` — fabrication / provenance probe (7 cases)
- `.../scratchpad/work/meetings-transcript-voting/probe_schema.py` — pydantic strictness probe
- `.../scratchpad/work/meetings-transcript-voting/probe_conflict.py` — alibi_conflict STRONG shapes
- `.../scratchpad/work/meetings-transcript-voting/census.py`, `census2.py` — recorded-flag census + detector timing + byte-identity over 204 committed meetings
- `.../scratchpad/work/meetings-transcript-voting/fuzz_detector.py` — hypothesis (3,000 examples) invariant probe

---

## 1. Executive read (10 lines)

1. The area is small in *logic* and huge in *prose*: `transcript.py` is 3,537 lines but only ~1,339 SLOC / 792 logical lines; 52% of the file is docstring/comment, with 131 "Task N.N" references, 60 "audit" references and 27 "seed-N" references narrating history rather than describing behaviour [VERIFIED, radon raw + grep].
2. The pure core — chain walk, `canonical_rooms`, `detect_contradictions` and its sub-detectors, `tally_ballots` — is genuinely deterministic, fast (0.12 ms/meeting mean, 0.27 ms max over the committed corpus) and re-derives every one of the 204 committed meetings' recorded flags byte-identically [VERIFIED]. A 3,000-example hypothesis probe found no exception, no non-determinism, no duplicate `contradiction_id`, no dangling event id, and the weak marker at most once per description [VERIFIED].
3. The task's central question — *does anything verify an observer COULD have seen what they claim?* — the answer is **no** for the incriminating channels: `alibi_vs_sighting` and `alibi_conflict` take any speaker's `saw_player`/proxy-alibi at face value. Grounding against the speaker's own typed records exists (`SightingRecord`, Task 16.7) but is wired ONLY to the exculpatory vouch channel and (per manager comment) not even fed live. The corpus shows the consequence: of 60 STRONG `alibi_vs_sighting` flags in the committed sample sets, **53 (88%) name a crewmate** — 17 minted by an impostor's sighting, 36 by crew-vs-crew recall mismatch — while the module's own docstring repeats "a STRONG flag naming a CREWMATE is a false positive" as the design crux [VERIFIED].
4. `alibi_vs_physical`'s "two independent voices" bar equals the impostor count in the canonical 7p2i/9p2i configs; two colluding impostors naming an innocent as `co_present` mint a STRONG flag against them (the adversarial guard only excludes accuser/accused pairs) [VERIFIED by probe]. In the corpus the co-presence path has never minted a STRONG flag; all 6 STRONG `alibi_vs_physical` are the vent-placement variant.
5. Weak/strong classification is carried **in-band in free text** (`"[weak signal: …]"` appended to `description`, read back by substring). The description embeds the RAW LLM room label, so a room string like `"CAFETERIA/[weak signal: x]"` canonicalises to `{CAFETERIA}` yet makes the resulting flag read as weak [VERIFIED]. Structural, low-likelihood with a 9B, but the design is what makes it possible.
6. Docs have drifted from code in several places: 13.14 removed the self-stated weak band but the module header, `is_weak_contradiction` docstring and the proxy-guard comment still describe it; `_iter_alibis` says whereabouts ids are `_turn_observation_id` (they are `_turn_whereabouts_id`), and the spectator TurnCard consequently never attaches a badge to a whereabouts observation (15% of committed event ids are whereabouts-anchored); `constants.py` names a non-existent `tally_votes` [VERIFIED].
7. Retired levers left as always-True resolvers with an ignored `env` parameter threaded through `detect_contradictions`, a dead `False` branch in `_detect_alibi_vs_sightings`, a test-only record-driven `absent_players(include_vent_sightings=…)` path with its own 46-line helper, and a `_NO_ROSTER` sentinel that re-implements `Optional` — accidental complexity that tests actively pin.
8. Duplication: three near-identical vent walks (`_detect_grounded_vent_flags`, `_detect_vent_placement_contradictions`, `_grounded_vent_subjects`), two identical record matchers differing only in a constant, and `normalize_ballot_target` duplicated byte-for-byte in `manager.py` with a 1,225-line parity suite proving the copies agree instead of deleting one.
9. Schemas are frozen + `extra="forbid"` but otherwise permissive (lax coercion `"5"`→5, negative ticks, empty ids/rooms, `reply` without `reply_to`, self-vote, empty `subjects`); the manager compensates with mark-and-null normalisation. Adequate, but the "structured output is validated" claim is thinner than it reads.
10. Tests are numerous (512 in the area, 2.8 s) and mostly behavioural, but a meaningful fraction pin implementation/prose (source-grep for variable names, docstring-quoted corpus totals, "resolver returns True and ignores env" ×6, per-set census cell counts).

Overall: correct and deterministic core, no P0. Two P1s (no provenance on incriminating testimony + the doc/behaviour inversion around STRONG-naming-crew; and the in-band classification channel), the rest P2 maintainability.

---

## 2. Findings (ranked)

### F1 [P1] [VERIFIED] No provenance check on incriminating testimony; 88% of STRONG `alibi_vs_sighting` flags on the committed corpus name a crewmate, contradicting the module's own stated crux
- **Where**: `meetings/transcript.py:2380-2495` (`_detect_alibi_vs_sightings`), `:2331-2378` (`_detect_alibi_conflicts`), `:3061-3094` (`_weak_signal_reasons`, `include_self_stated=False` on the sighting path since 13.14).
- **What**: A `saw_player` observation (or a proxy `AlibiClaim`) by ANY speaker contradicts a subject's self-alibi and mints a flag with no check that the speaker was co-located, alive, or holds a matching `SightingRecord`. Since 13.14 the self-stated band is STRONG unless narrow/endpoint. The grounding machinery that COULD check it (`_sighting_observation_matches_record`, `SightingRecord`, `grounded_vouch_subjects`) is only used to *exculpate*, and manager L1236-1246 says the live sighting-record mapping is not threaded yet.
- **Evidence**:
  - `probe_provenance.py` case 1: p-2 says "MEDBAY 10-20"; p-1 says "saw p-2 in REACTOR at 15" with no claim to have been anywhere → `alibi_vs_sighting subjects=('p-2',) weak=False`.
  - `probe_conflict.py`: p-2 says nothing; p-1 and p-3 disagree about where p-2 was → `alibi_conflict ('p-2',) STRONG` — the SUBJECT is flagged for two third parties' disagreement.
  - `census2.py` over 96 games with exact role truth (kill/vent actors == declared impostor count): STRONG `alibi_vs_sighting` = 60 → 53 name crew (17 sighting spoken by an impostor, 36 crew-vs-crew), 7 name impostors. Weak band: 16 crew / 3 impostor. `vent_sighting` (grounded): 107/107 impostor.
  - Module docstring L164-166, L237-241, L2600ff repeat "A STRONG flag naming a CREWMATE is a false positive" as the design invariant.
- **Why it matters**: The recorded flag set — the input to belief Rule 2, the ballot prompt, the spectator "evidence" taxonomy and the eval metrics — carries a STRONG class that is mostly wrong on the corpus, and the docs claim the opposite. Whether it drives wrong ejections is the belief-layer/gameplay track's call; code-up, it is a documented invariant that the measured behaviour violates, and the typed channel that would ground it exists but is inert.
- **Confidence**: high on the mechanics and the census; medium on "should" (13.14 is an owner decision).

### F2 [P1] [VERIFIED] Weak/strong classification is an in-band substring of LLM-influenced free text
- **Where**: `transcript.py:531` (`WEAK_CONTRADICTION_MARKER_PREFIX`), `:759-778` (`is_weak_contradiction` = `PREFIX in flag.description`), `:3186-3310` (describe helpers embed RAW `alibi.room` / `sighting.room`), `:3447-3467` (`_split_weak_marker` — first-occurrence `find`, `rstrip("]")`).
- **Evidence**: `probe_provenance.py` case 5: alibi room `"CAFETERIA/[weak signal: x]"` → `canonical_rooms` = `{CAFETERIA}` (spatial, flag mints) but the description carries the raw label and `is_weak_contradiction` returns **True** on what should be a STRONG flag. Consumers of this predicate: `agents/memory/beliefs.py`, `api/schemas.py` (`category`), `eval/*`, `training/surrogate/dataset.py`, frontend via API.
- **Why**: A voter (LLM) chooses its own room strings; the classification of a flag against its own alibi is derivable from that string. Also `audits/workflows/extract_gameplay_facts.py:306` tests `WEAK_REASON_SELF_STATED in desc` — a substring of `WEAK_REASON_SELF_PAIR` ("self-stated alibi pair"), so that census cell is polluted. Root cause: `ContradictionRef` has no `weak: bool` / `reasons: tuple[str,...]` field; the docstring (L770-776) argues the marker "survives any record/replay round-trip without a schema field" — true, but a schema field would too, and would be typed.
- **Confidence**: high (mechanism); low probability of adversarial trigger with the current 9B.

### F3 [P2] [VERIFIED] `alibi_vs_physical` STRONG bar (2 voices) equals the impostor count; two colluders mint STRONG against a crewmate
- **Where**: `transcript.py:2518-2695`, `PHYSICAL_CONTRADICTION_MIN_VOICES = 2` (L640).
- **Evidence**: `probe_provenance.py` case 2 → two `alibi_vs_physical subjects=('p-2',) weak=False`. Guards exclude only speakers in an accuser/accused pair with the subject; two impostors who never *accuse* p-2 in claims pass. Docstring L2600-2612 claims the two-source conjunction "separates a genuine fabricated alibi from a one-off recall slip".
- **Mitigation observed**: on the corpus the co-presence path has minted zero STRONG flags (all 6 STRONG `alibi_vs_physical` are the vent-placement variant — see F6). So low live impact today; the risk grows with a stronger model.

### F4 [P2] [VERIFIED] Docstrings drifted from behaviour (four concrete cases)
1. `transcript.py:42-51` (module header) and `:764-766` (`is_weak_contradiction`) still say a *self-stated* `alibi_vs_sighting` gets the weak marker; since 13.14 (`_detect_alibi_vs_sightings` passes `include_self_stated=False`) it does not — probe case 1 shows STRONG. `WEAK_REASON_SELF_STATED` is never written to any description any more (corpus grep: 0 occurrences of a bare "self-stated alibi]"), yet is exported in `__all__` and consumed by the audit workflow.
2. `transcript.py:3389-3391` — proxy-intra-turn guard passes a same-speaker self-contradiction through as "the weak band's own business"; probe case 4 (self-alibi MEDBAY 10-20 + own `saw_player(self)` WEST_HALL@15) → STRONG. Inconsistent with the self-PAIR alibi_conflict shape (WEAK) — same "subject's own recollection disagreeing with itself".
3. `transcript.py:2121-2124` — `_iter_alibis` says the synthesized whereabouts alibi's event id is "the OBSERVATION id (`_turn_observation_id`) … so a flag referencing it resolves through … the spectator surface exactly like any other observation". Code uses `_turn_whereabouts_id` (`turn:X:whereabouts:i`). The frontend `TurnCard.tsx:237-240` looks up observation badges by `turn:X:obs:i` only → whereabouts observations never get their contradiction badge; `MeetingView.tsx:315` was patched for the segment, `lib/contradictions.ts:12-18` was not. 61 of 404 event ids in `replays/samples` and 169 in `ml_corpus` are whereabouts-anchored.
4. `meetings/constants.py:32` references `meetings.voting.tally_votes`; the function is `tally_ballots`.

### F5 [P2] [VERIFIED] Retired levers, dead branches and test-only paths kept alive
- `whereabouts_interior_flags_enabled` / `vent_placement_contradictions_enabled` (`transcript.py:1362-1411`) — `del env; return True`; `detect_contradictions(env=…)` still accepts and threads `env`; `_detect_alibi_vs_sightings(whereabouts_interior_flags: bool = False)` keeps a "False branch … only for direct callers of this private helper" (L2385-2410). Six tests (`TestWhereaboutsInteriorFlagsResolver`, `TestVentPlacementContradictionsResolver`) assert the resolvers return True and ignore env.
- `absent_players(include_vent_sightings=, vent_witness_records=)` + `_grounded_vent_subjects` (L3014-3059): no non-test caller (`grep -rn include_vent_sightings` → tests only); production uses `grounded_vent_subjects_from_flags`. Docstring "guarantees" equality of two implementations instead of having one.
- `ENV_WHEREABOUTS_INTERIOR_FLAGS` / `ENV_VENT_PLACEMENT_CONTRADICTIONS` retained "for naming provenance".
- `_NO_ROSTER` sentinel + `_subject_in_roster` (L280-291, L2058-2068): `roster: frozenset | None` is converted to a sentinel frozenset to distinguish None from empty — `None` already distinguishes them; `roster is None or subject in roster` is the whole function.

### F6 [P2] [VERIFIED] Vent-placement variant reuses kind `alibi_vs_physical`, so role-proof flags are indistinguishable from inferential ones downstream
- `transcript.py:2918-3012` emits `kind="alibi_vs_physical"` for a grounded (engine-truth) vent record contradicting the subject's alibi. `api/schemas.py:700-730` classifies category by kind/self-link: `vent_sighting`/self-linked → `role_proof`, else weak/cross_statement — so these six flags render as `cross_statement`. Only the description text ("witnessed … vent in") tells them apart (corpus: 6/6 STRONG `alibi_vs_physical` are this variant). A distinct kind (or a `grounded: bool` field) is the fix; the frontend/API union already tolerates a new kind (they were extended for `vent_sighting`).

### F7 [P2] [VERIFIED] Duplication
- `_vent_observation_matches_record` (L2697) and `_sighting_observation_matches_record` (L2721) are identical bodies modulo the tolerance constant.
- `_detect_grounded_vent_flags` (L2857), `_detect_vent_placement_contradictions` (L2918), `_grounded_vent_subjects` (L3014) walk turns → speaker records → `SawVentObservation` → roster → match, three times.
- `meetings/voting.py::normalize_ballot_target` and `meetings/manager.py:2752 _normalize_ballot_target` are the same function; `_SKIP_TARGET`/`INVALID_VOTE_TARGET_MARKER` literals are duplicated; `voting.py:52-79` (a 30-line "manager-side implementation note") and `tests/meetings/test_vote_tally_parity.py` (1,225 lines) exist to prove the copies agree. `test_the_manager_no_longer_carries_a_private_tally_body` uses `inspect.getsource` and greps for `max_votes`/`leader_max_confidence` — a pure implementation pin.

### F8 [P2] [VERIFIED] Schema validation is lax; invariants live in the manager
`probe_schema.py`: accepted — `tick="5"`, `tick=5.0`, `tick=True`(→1), negative ticks/indices, `room=""`, `subject=""`, self-vote (`voter==target`), `target="skip"` (lowercase, then normalised as an *invalid* target by the manager), `ContradictionRef(subjects=())`, `MeetingTurn(turn_kind="reply", reply_to=None)`, opening with `reply_to`. Rejected — reversed alibi range, extra fields, confidence>1/NaN, missing `free_text`, `EJECTED` without id. `model_validate_json` is called non-strict everywhere (`llm/*.py`). Not a bug per se (manager guards + walk_chain fail loud), but `MeetingTurn` could carry the `reply`↔`reply_to` and `opening`↔index-0 invariants the way `MeetingResult` carries its outcome invariant, and ticks could be `ge=0`.

### F9 [P2] [VERIFIED] Turn-time vs vote-time `trigger_kind` inconsistency is deliberate but undocumented at the call site that omits it
`manager.py:1114-1118, 1146-1150, 1188-1192` call `detect_contradictions` without `trigger_kind`; `:1229-1234` passes it. For an emergency meeting whose opening carries a fabricated `found_body`, turn prompts and the vote prompt/recorded flags see different kill-scene gating (probe case 7: same count, different descriptions/banding paths; corroboration suppression can differ). The manager comment at L1249-1256 explains the sibling folds keep `None` for byte-identity of the recorded corpus. This is the byte-identity doctrine freezing a known inconsistency into the substrate.

### F10 [P2] [JUDGMENT] Documentation volume as a maintenance liability
`transcript.py`: 229-line module docstring; `detect_contradictions` docstring ≈120 lines for ≈70 lines of code; `_detect_alibi_vs_physical` docstring ≈70 lines; radon CC: `_detect_alibi_vs_physical` E(31), `independent_voices` D(21). Most prose is change-log ("Task 10.6 (audit gp-1 C-C-5/C-C-4)… seed 13 m2…"), which git history already holds; the behavioural contract is buried in it and — per F4 — is the part that has rotted.

### Also checked, no issue found [VERIFIED]
- Determinism/purity/sorting of `detect_contradictions`, `detect_corroborations`, `independent_voices`, `absent_players`: 3,000 hypothesis examples, no exception, no duplicate ids, event ids always resolve, results sorted, idempotent. (One nit: a proxy re-target names the *speaker*, which is not roster-checked — unreachable in production since speakers are living participants; 38/3000 fuzz cases.)
- Byte-identical re-derivation of recorded flags on all 204 committed meetings under either `trigger_kind=None` or `"emergency"`.
- `tally_ballots`: rules match the docstring; inclusive threshold; SKIP as first-class; NaN rejected at schema; order-independent. `walk_chain` fails loud on malformed chains.
- `CANONICAL_ROOMS` engine pin exists (`tests/meetings/test_transcript.py:715`).
- Detector cost is negligible (0.12 ms mean / 0.27 ms max per meeting; load avg ~6.5).

---

## 3. Architecture / design assessment

**Well designed**
- Pure-function detector over a frozen transcript, canonical ids (`contra:{kind}:{a}|{b}` with sorted pair), sorted output — replay determinism is real and cheap. Grounding chokepoints (`_vent_observation_matches_record`) are the right idea: typed private records vs public speech, no prose parsing.
- `canonical_rooms` as the single normalisation point with an allowlist (not a denylist) is a good, testable decision; the engine-map pin closes the drift hole.
- `render_contract.py` / `constants.py` as leaf modules that let `agents/` avoid importing the 4-KLoC manager is a sound layering move.
- Voting is tiny and correct; the delegation of `_tally` to `tally_ballots` was the right consolidation.

**Accidental complexity**
- Classification-in-description (F2) forces `_split_weak_marker`, `_retarget_proxy_intra_turn`, `_fold_proxy_intra_turn` to *parse and re-append* prose; a `reasons: tuple[str, ...]` field on `ContradictionRef` would delete ~80 lines and the injection surface.
- One kind for two different evidence classes (F6); three id segments (`claim`/`obs`/`whereabouts`) hand-mirrored in frontend + eval (F4.3).
- Retired levers kept as always-True resolvers with threaded `env` and dead branches; test-only alternate implementations "guaranteed equal" by prose (F5).
- `_NO_ROSTER` sentinel; `sort_turns_canonically`/`is_canonically_ordered` public API for a producer that does not exist.
- The proxy re-target machinery (10.6 + 10.10) is two overlapping post-hoc rewrite passes; the need for a "fold" step to stop them stacking is a symptom of patch-on-patch.

**What I would refactor (how)**
1. Add `weak_reasons: tuple[str, ...] = ()` (and derive `is_weak`) to `ContradictionRef`; keep description purely descriptive; make `is_weak_contradiction` read the field. Re-record is required anyway on any substrate change per project doctrine — bundle it.
2. Split `transcript.py` into `chain.py` (accusation_target/next_chain_step/walk_chain), `rooms.py` (canonical_rooms, relevance gate), `detector/*.py` (one module per kind + a `pipeline.py` that composes), `grounding.py` (record matchers, vouch/vent subject folds, ONE generic `_iter_grounded(transcript, records, obs_type, matcher)`), `voices.py`. Move change-log prose to `audits/` links; keep contracts.
3. Give the vent-placement variant its own kind (`vent_placement`) or a `grounded: bool`; API/eval classify by field, not by description.
4. Delete `env` params, retired resolvers, the `False` branch, `_grounded_vent_subjects` + `include_vent_sightings`, `_NO_ROSTER`; delete `manager._normalize_ballot_target` and import `voting.normalize_ballot_target`; shrink the parity suite to a handful of behavioural cases.
5. Provenance for incrimination: thread `sighting_records` into `detect_contradictions` and band an UNGROUNDED contradicting sighting WEAK (or require grounding for STRONG) — symmetric with the vouch channel. This is the one item that needs an owner decision (it reverses 13.14's economics), so I list it as a recommendation, not a defect fix.

---

## 4. Test assessment

- 512 tests across 11 files run in 2.8 s; ratio ≈ 11.8 K test lines to ≈1.65 K source SLOC. Coverage of the detector's rules is thorough and mostly behavioural (builders, explicit shapes, "corroborated alibi suppresses physical", "adversarial voice does not count", determinism, idempotence).
- Corpus byte-identity pins (`TestLiveDetectorCommittedBytesByteIdentity`, `TestCommittedBytes*Pins`, census cell tests) are a strong regression net for the replay invariant, but per-set cell counts (`test_samples_9p2i_cells`, `test_committed_corpus_counts_are_pinned`, `test_committed_corpus_totals_are_pinned` — "the whole-corpus totals the module docstring quotes") are data pins that must be re-edited on every re-record and test the docstring, not the code.
- Implementation-detail pins: `test_the_manager_no_longer_carries_a_private_tally_body` (source grep for local variable names), six "resolver returns True / ignores env" tests for retired levers, tests importing private helpers (`_dedupe_echo_alibis`, `_grounded_vent_subjects`, `_iter_alibis`, `_turn_whereabouts_id`) — these lock structure, so the cleanups in §3 will require test surgery.
- Missing: (a) any test that a *fabricated* incriminating sighting is down-weighted (there is none — because it isn't); (b) a property/fuzz test — the hypothesis probe above found the whole area invariant-clean in minutes and would be a cheap permanent guard; (c) a test that a whereabouts-anchored flag resolves on the spectator surface (the frontend gap in F4.3 would have been caught); (d) schema invariant tests for `reply`↔`reply_to`.

---

## 5. Recommendations (prioritised)

1. **[P1] Decide the provenance policy for incriminating sightings** (F1). Cheapest code path: pass the participants' `SightingRecord` mapping into `detect_contradictions` and add a `WEAK_REASON_UNGROUNDED_SIGHTING` when the contradicting `saw_player` has no matching record in the speaker's own channel. Measure on the corpus first (the census script here gives the baseline: 53/60 STRONG name crew). Until decided, fix the docstrings that claim STRONG-naming-crew is unreachable.
2. **[P1] Move weak classification out of the description** (F2): `ContradictionRef.weak_reasons` field; `is_weak_contradiction` reads it; describe helpers stop appending; retarget/fold stop parsing. Bundle with the next re-record.
3. **[P2] Give grounded vent-placement flags their own kind** (F6) so API/eval/frontend can classify them as role proof without text sniffing.
4. **[P2] Fix the whereabouts id gap end-to-end** (F4.3): `frontend/src/lib/contradictions.ts` needs a `turnWhereaboutsEventId` (or the detector should emit `:obs:` and stop special-casing); update the `_iter_alibis` docstring; add a cross-layer test that every committed flag's event ids resolve to a card.
5. **[P2] Delete retired-lever scaffolding and test-only paths** (F5): `env` params, always-True resolvers, `False` branch, `_grounded_vent_subjects`/`include_vent_sightings`, `_NO_ROSTER`; consolidate `normalize_ballot_target` into `voting.py` and cut the parity suite to behaviour.
6. **[P2] Split `transcript.py`** as in §3 and relocate change-log prose to `audits/` (keep contracts, drop "Task X (audit Y) seed Z" narration). Refresh the four drifted docstrings (F4) in the same pass.
7. **[P2] Add a hypothesis property test** (determinism, sorted unique ids, event ids resolve, marker/field consistency, subjects ⊆ roster) — the probe script is a ready starting point.
8. **[P2] Tighten schemas where cheap** (F8): `ge=0` on ticks/indices, non-empty ids/rooms, `reply`↔`reply_to` model validator on `MeetingTurn`.

---

Report path: /private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/reports/B/meetings-transcript-voting.md
