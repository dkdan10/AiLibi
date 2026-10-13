# Phase-15 close — every gate on the shipped branch-A end-state is green; the fresh champion recording passes the HARD validity gate and FAILS the hardened referee's backing floor — the close's one pass-bar — pausing per contract for the owner call; the owner ruled the miss benign (a baseline-relative floor met by a gameplay-shifting champion, with the floors' starvation failure mode absent) and CLOSED the phase over the recorded FAIL. The banner is flipped; the floor-recalibration question is handed to Phase 16/17.

**Date:** 2026-07-10 (recording + measurement) / 2026-07-11 (owner ruling + close)
**Task:** 15.23 — phase close: gates on the shipped end-state, the close audit, the banner flip
(operator-run, $0).
**The one fresh measurement:** the champion close recording — seeds 0–49, 9p2i
(`tasks_per_crewmate=2`), `Qwen/Qwen3-32B` (Featherless, `qwen3_32b` prompt set: turn/opening v5,
`vote_ballot` v6 — the baseline-3 substrate), recorded through the committed 15.21 CLI
(`scripts/run_tournament.py --agent-factory learned-champion`; no Python driver), committed as
`training/reports/results-champion-close.jsonl`. The raw recordings are uncommitted working artifacts
per the pause's provenance separation (audits/audit-phase-15-pause.md §3.1); they never joined
`replays/samples/` or `replays/ml_corpus/`.
**Recording identity (the anti-laundering record):** recorded 2026-07-10 — start 19:58:45Z, complete
23:07:01Z, wall ≈ 3 h 08 m per the operator recording log (the committed row pins the date + sha; the
clock times are operator-log provenance, like the pause's) — on checkout `5cf4e35` (the post-squash
main sha of PR #249) — the sha is
back-filled into the committed measurement row as `recording.recording_git_sha`, the back-fill arm of
the owner-ratified Q5 provenance-durability convention (2026-07-09; the annotated-tag arm is the
equivalent for a recording commit that is not already a main sha — this one is). Every number quoted
for the champion below comes from `results-champion-close.jsonl`, none from the pause's cached
finalist rows.
**Method:** measurement-only. `eval/`, `agents/`, `training/`, `engine/`, `orchestrator/` are
read-only for this task; every number below is regenerated from the committed CLIs
(`scripts/validity_gate.py`, `scripts/measure_baseline.py [--watchability|--funnel] --json`,
`bash scripts/verify_samples.sh`) on this checkout or quoted from a committed artifact, and each
table names its source. Zero hand-computed figures — deltas are shown as side-by-side cells.
**Label key:** **[RAN]** reproduced by a command on this checkout · **[VERIFIED]** read directly in a
committed source/artifact.

---

## 0. Verdict in one line

The shipped branch-A end-state is mechanically sound — full repo gate green, all four committed
replay sets validity-PASS, hardened-referee-PASS, and byte-identical bare, provenance proven
end-to-end from bytes — and the fresh champion recording through the committed CLI is validity-PASS
with the stamp proof holding on all 50 games; but the hardened 15.19 referee **FAILS** it on the
subject-aware `testimony_backed_conversion` floor (measured **0.5743** vs floor **0.6636**, one gauge
of three, the other two passed with wide margin), and per the contract that outcome **paused the
close for an owner call rather than shipping**. This is the pass-bar inversion the contract
pre-registered, not a defect in the close: the referee-before-selection ordering exists precisely to
catch a champion that was selected under the softer instrument. The owner call came back
(2026-07-11, §10): the recorded FAIL stands as the instrument's verdict, and the phase **CLOSES over
it** — the floor is the FSM baseline's own measured value met by a champion that legitimately
reshapes gameplay, the starvation failure mode the supply floors exist for is absent, and the
conversion-floor recalibration is contracted forward rather than adjudicated by a close edit. The
STATUS banner is flipped to CLOSED with the verdict quoted, so the close cannot be read as a
champion referee-endorsement.

---

## 1. Mechanical health — gates re-run on HEAD, all green

Everything below is **[RAN]** on this task's tree (recording checkout `5cf4e35` + this task's
document/measurement commits; no code changed).

| Gate | Result |
|---|---|
| `bash scripts/check.sh` | green end-to-end |
| `ruff check .` / `ruff format --check .` | All checks passed |
| `uv run lint-imports` | 4 contracts kept, 0 broken |
| `mypy .` | Success: no issues found in 273 source files (`strict = true`) |
| `pytest` | 3188 passed, 20 skipped, 3 xfailed |
| `validate_task_docs.py` / `generate_prompts.py --check` | 227 tasks, 227 prompts, all in sync |
| `validity_gate.py replays/samples/9p2i --json --expected-model Qwen/Qwen3-32B --require-zero-cost` | **PASS** — 10/10 checks, 50 games |
| `validity_gate.py replays/samples/4p1i …` | **PASS** — 10/10 checks, 50 games |
| `validity_gate.py replays/ml_corpus/9p2i …` | **PASS** — 10/10 checks, 150 games |
| `validity_gate.py replays/ml_corpus/4p1i …` | **PASS** — 10/10 checks, 50 games |

The HARDENED referee on the four committed sets (`measure_baseline.py --watchability --json`,
floors = the 15.19 subject-aware re-pin, `baseline-3`) — the committed baseline still passes its own
hardened instrument, with the three 9p2i floors sitting at exact measured==floor equality on the
same bytes they were re-pinned from:

| Set | Referee | mean / median | Gauges |
|---|---|---|---|
| samples 9p2i | **PASS** | 35.19 / 46.55 | witnessed 0.0325=floor · flags 1.8633=floor · backing conversion 0.6636=floor (all hard) |
| samples 4p1i | **PASS** | 8.40 / 2.90 | witnessed 0.0182=floor (advisory, numerator 1) · flags 1.0769=floor · conversion 0.6061=floor |
| corpus 9p2i | **PASS** | 43.84 / 48.60 | witnessed 0.0340 · flags 2.1545 · conversion 0.7100 — all above floor |
| corpus 4p1i | **PASS** | 10.39 / 16.60 | witnessed 0.0000 vs 0.0182 fails but ADVISORY (the 15.19 rare-event rule — the pause-audit §1 one-event degeneracy, now closed) · flags 1.5000 · conversion 0.7222 |

Byte-identical reconstruction holds BARE (no `AILIBI_*` export) on every committed replay:
`bash scripts/verify_samples.sh` (no-arg walk: samples 9p2i + 4p1i, 50+50 games) and the explicit
corpus invocations (`scripts/verify_samples.sh replays/ml_corpus/9p2i` — 150 games — and
`… replays/ml_corpus/4p1i` — 50 games) all reconstruct clean, MANIFEST completeness enforced by the
verifier on all four sets. `replays/samples/` and `replays/ml_corpus/` are byte-untouched by this
task — branch A ships no baseline 4. **[RAN]**

---

## 2. The champion close recording — the §3.1 recipe through the 15.21 CLI

**[RAN]** — the pause's finalist recipe (audits/audit-phase-15-pause.md §3.1) re-run through the
committed CLI surface that 15.21 built to close its one gap:

- **Per seed 0–49:** `uv run python scripts/run_tournament.py --start-seed <seed> --num-games 1
  --output-dir <stage> --num-players 9 --num-impostors 2 --tasks-per-crewmate 2
  --agent-factory learned-champion --force`, environment `AILIBI_LLM_PROVIDER=featherless`,
  `AILIBI_PROMPT_SET=qwen3_32b`, `AILIBI_LLM_MEETING_MODEL=Qwen/Qwen3-32B`,
  `AILIBI_LLM_TRIGGER_MODEL=Qwen/Qwen3-32B`; $0 flat-rate. No `--tactical-policy-stamp` is passed —
  the champion stamp is auto-wired by the factory selection and the 15.21 mis-stamp guard makes a
  contradiction impossible.
- **Worker/retry shape:** 2 parallel seed workers (the 15.7/15.12 concurrency: a 32B request is 2 of
  the 4 plan units), per-seed crash-retry ≤ 4 with backoff. Observed: 3 seeds (22, 38, 41) hit one
  transient transport failure each and cleared on attempt 2; no other retries.
- **Per-seed provenance guard,** mirroring `scripts/record_ml_corpus.sh::check_replay_provenance`
  with the champion expectation: the read-back stamp must equal the champion's five fields
  field-for-field, every recorded model row must be `Qwen/Qwen3-32B`, recorded cost must be exactly
  $0. Observed: **0 violations in 50 seeds** — no wall-clock-miss `(deadline_default)` phantom rows
  this run (the pause observed 2/50 on its utility-es recording).
- **Set hygiene:** `roster.json` (`{"num_players": 9, "num_impostors": 2, "tasks_per_crewmate": 2}`)
  written into the set dir BEFORE recording via `scripts/_manifest_writer.py roster`; each seed is
  staged and only the replay JSONL moves into the set, so the `*.audit.jsonl` sidecars and per-run
  reports never touch the scorers' seed glob.
- **The stamp proof (the machine-checkable part):** the five-field `tactical_policy` stamp was read
  back from the bytes of EVERY recording via `orchestrator.replay.read_tactical_policy_stamp` (never
  echoed from the launch config), asserted uniform across all 50 games, and asserted equal to the
  committed sidecar digest. All three hold: `stamp_verified_games: 50`,
  `stamp_equals_committed_sha256: true`, stamp `weights_sha256 =
  6d327dcbde940a5ee1bb4f9e22ff91fbbc4d74c0ddb33797043fdff69fef71d0` — equal to
  `agents/tactical/learned/weights.json.sha256` (the sidecar the factory loads and verifies at CLI
  startup), which is byte-identical in digest to the training-side original
  `training/artifacts/impostor/utility-es/weights.json.sha256` (asserted at scoring time). The
  learned factory, not the FSM default wearing a champion label, produced the recorded bytes.
- **One label note:** the read-back stamp's `method` is `utility-scorer-es` — the 15.20/15.21
  productized method string — where the pause's Python-driver rows carried the hand-stamped
  `neuroevolution`. The stamp is reported as read from bytes per the recipe; the load-bearing
  equality is the sha, which holds. Recorded as a decision, not a defect.

Scoring ran the four committed CLIs unchanged on the set
(`validity_gate.py <dir> --json --expected-model Qwen/Qwen3-32B --require-zero-cost`;
`measure_baseline.py <dir> --json`, `… --watchability --json --baseline-id baseline-3`,
`… --funnel --json`) and the row in `results-champion-close.jsonl` carries all four outputs verbatim
plus the read-back stamp and the committed sha it was verified against — the same row shape as
`results-finalist-eval.jsonl`.

---

## 3. The one pass-bar: validity gate PASS, hardened referee FAIL → the close pauses

Source: `training/reports/results-champion-close.jsonl` **[RAN]**.

**HARD validity gate: PASS — 10/10 checks over 50 games**, including
`byte_identical_reconstruction` (all 50 champion recordings reconstruct byte-identically through the
engine) and `cost_and_provenance_exact` under `--expected-model Qwen/Qwen3-32B --require-zero-cost`.

**Hardened referee: FAIL — one gauge of three:**

| Gauge (all hard at 9p2i) | measured | floor (15.19 re-pin) | verdict |
|---|---|---|---|
| `witnessed_event_rate` | **0.2195** | 0.0325 | PASS |
| `flags_per_meeting` | **3.0432** | 1.8633 | PASS |
| `testimony_backed_conversion` | **0.5743** | 0.6636 | **FAIL** |

`integrity_ok: true`; geomean mean/median **38.58 / 45.7** — the mean sits ABOVE the hardened
baseline's own 35.19 (§1), so the miss is not score starvation; it is the single conversion floor.
The champion's games supply evidence far above the baseline floor on both supply gauges, but the
crew convert subject-aware-backed accusations at a lower rate than the re-pinned baseline bar.

**Why this outcome was pre-registered, in the contract's own words:** "the hardened referee landing
in 15.19 means the close referee is STRICTER than the one the finalists were measured under; a
champion that passed at the pause may fail at close, and that outcome pauses for an owner call — it
is the exact scenario the referee-before-selection ordering exists to catch, not a defect in the
close." The pause's own reading of the same gauge (pre-hardening, subject-agnostic, its own fresh
bytes): measured 0.5922 vs the old floor 0.6068 — already a marginal FAIL, deliberately left
un-adjudicated because "the hardened re-score is 15.23's pass-bar" (audit-phase-15-pause.md §3.2).
The 15.19 re-pin moved the floor 0.6068 → 0.6636 on the same committed baseline bytes (numerator 71
held while the subject-aware definition tightened the backed-supply denominator 117 → 107, per the
15.19 contract), and the fresh champion recording measures 0.5743 under the subject-aware
definition. Two things moved between the pause cell and the close cell — the bytes (a fresh
recording) and the definition (subject-aware) — and they cannot be decomposed without the pause's
discarded raw recordings; the composite is reported as the finding.

**Consequence (the contract's own rule):** the champion recording does NOT pass the close's one
pass-bar as written, so the close paused for the owner call rather than shipping — consistent with
decision 2's own rationale for branch A: "a default flip today would ship a referee-failing
measurement"; the opt-in factory shipped precisely so this verdict could be rendered by the hardened
instrument before any irreversible move. The owner call was made 2026-07-11 and is recorded as the
locked decision in §10: the phase closes over the recorded FAIL, the measurement stands unedited,
and the recalibration question moves forward as a contract input, not a close edit.

---

## 4. R-gate vs baseline 3 — FINDINGS, not gates

Champion cells from `results-champion-close.jsonl` (`core`); baseline-3 cells **[RAN]** from
`measure_baseline.py --json` on `replays/samples/9p2i` at this checkout; pause-finalist cells
**[VERIFIED]** from `training/reports/results-finalist-eval.jsonl` (same seeds, pre-hardening,
driver-recorded — quoted for replication context only).

| Metric | baseline 3 (FSM) | pause finalist (utility-es) | **champion close** |
|---|---|---|---|
| impostor win rate | 0.30 (15/50 imp wins) | 0.38 | **0.40** (20/50) |
| reason histogram | eject 34 / parity 15 / tasks 1 | eject 30 / parity 19 / tasks 1 | eject 29 / parity 20 / tasks 1 |
| R1 eject-decided wins | 34 | 30 | 29 |
| ejection accuracy | 0.6972 (76/33 of 109) | 0.6126 (68/43 of 111) | **0.6195** (70/43 of 113) |
| genuine-class conversion | 0.769 (10/13) | 0.75 (9/12) | **0.833** (20/24) |
| resolved meetings / rate | 139 / 1.0 | 138 / 1.0 | 139 / 1.0 |
| accusation-claim ECE (n) | 0.2749 (372) | 0.4039 (414) | 0.3746 (448) |
| vote-ballot ECE (n) | 0.1776 (753) | 0.2589 (788) | 0.2429 (786) |
| tick-budget games | 0 | 0 | 0 |

Findings: the close replicates the pause's finalist read within seed noise on every shared cell (win
0.38 → 0.40, accuracy 0.6126 → 0.6195, 43 crew ejections in both recordings) — fresh bytes, fresh
timestamps, no cached numbers (§0 metadata names the recording). Against the FSM baseline the
champion holds the modest impostor edge the pause selected it for (win 0.40 vs 0.30) inside games
with unchanged meeting supply (139 meetings both), at the cost of more crew mis-ejections (43 vs 33)
— accuracy 0.6195 vs 0.6972 — and higher accusation/ballot mis-calibration (ECE 0.3746/0.2429 vs
0.2749/0.1776). Genuine-class conversion is UP (0.833 vs 0.769) with nearly double the supplied
opportunities (24 vs 13). Per the charter these are measurements on a valid recording, reported as
findings; the tournament-balance split is measured, never gated to a band (DESIGN.md §3.5).

---

## 5. Funnel vs baseline 3 — FINDINGS

Champion cells from `results-champion-close.jsonl` (`funnel`); baseline-3 cells **[RAN]** from
`measure_baseline.py replays/samples/9p2i --funnel --json` at this checkout.

| Funnel cell (9p2i, 50 games) | baseline 3 | **champion close** |
|---|---|---|
| report meetings / report ejections | 124 / 95 | 133 / 108 |
| kills witnessed | 5 | **32** |
| witnessed vents (meetings) | 73 | **40** |
| vent mentioned / structured vent observed | 53 / 55 | 32 / 30 |
| killer accused | 75 | 77 |
| hard clue held | 98 | 84 |
| killer in candidate set | 109 | 126 |
| candidate-set median | 3.0 | 3.0 |
| votes outside small (≤3) candidate set | 30 (of 64) | **16** (of 61) |
| reporter ejected (all innocent, both) | 4 | 7 |
| killer self-reported | 0 | 0 |

Findings: the champion's play *reshapes* the evidence funnel rather than starving it. Its kills are
witnessed 32 times vs the FSM's 5 (the dominant mover behind the witnessed-event-rate gauge, 0.2195
vs floor 0.0325), while its vent exposure drops sharply (73 → 40 witnessed-vent meetings) — utility-es was selected
partly for low vent exposure, and the funnel confirms the mechanism on the real path. Crew voting
discipline improves in-window (votes outside a ≤3 candidate set 30 → 16), the wave-0 exculpation
channel holds (innocent-reporter ejections 7 vs 4, against 22 pre-Wave-0), and the v5 vent
elicitation rate stays in band on the champion set (32 mentioned of 40 witnessed-vent meetings,
alongside the baseline's 53/73 and the corpus's 188/255). The evidence-supply story and the
backing-conversion miss (§3) are two views of the same substrate: MORE raw evidence per meeting, a
LOWER rate of converting the backed accusations it licenses.

---

## 6. Canaries — judged on corpus denominators (Q3), 50-seed figures alongside

Owner-ratified rule (2026-07-09 Q3, restated by the pause §6): canaries are judged on the largest
same-substrate validity-gated set — the corpus — with the samples figure alongside for continuity.
Corpus/samples cells **[RAN]** from `measure_baseline.py … --json` at this checkout; champion cells
from `results-champion-close.jsonl`.

| Canary (9p2i) | corpus (judged) | samples (continuity) | **champion close** | read |
|---|---|---|---|---|
| genuine-class conversion | 0.654 (34/52) | 0.769 (10/13) | **0.833** (20/24) | above both anchors — the over-damping canary is quiet |
| ejection accuracy | 0.7019 (252/107 of 359) | 0.6972 (76/33 of 109) | **0.6195** (70/43 of 113) | DOWN in champion games — the crew mis-eject cost of the champion's pressure; a finding for the owner call, not a gate |
| R1 eject-decided win share | 109/150 | 34/50 | 29/50 | eject-decided wins remain the dominant decisive mode |
| impostor win rate | 0.233 | 0.30 | **0.40** | the champion's selection edge, present on the real path; the floor question belongs to the referee (which fails it on conversion, §3) |

---

## 7. Provenance verified end-to-end

- **Stamps:** all four committed sets remain FSM-default-stamped and byte-verify bare (§1); the
  champion recording is champion-stamped on all 50 games, read back from bytes, uniform, sha-equal
  to the committed sidecar (§2). **[RAN]**
- **MANIFESTs:** `_verify_samples.py` enforces MANIFEST completeness (exact on-disk seed set) on all
  four committed sets — green bare (§1). The close recording is a working artifact and carries no
  MANIFEST by design; its provenance lives in the committed measurement row (stamp + models + $0 +
  recording sha). **[RAN]**
- **Sidecar shas:** `agents/tactical/learned/weights.json.sha256` ==
  `training/artifacts/impostor/utility-es/weights.json.sha256` ==
  the read-back stamp's `weights_sha256` == `committed_weights_sha256` in the measurement row
  (`6d327dcb…71d0`). The factory verifies the digest at load (fail-loud on drift); the Q4 bit-exact
  training-vs-shipped forward-pass gate is pinned in the 15.20 test suite, green in §1's pytest.
  **[RAN/VERIFIED]**
- **Q5 convention:** back-fill arm — `recording.recording_git_sha = 5cf4e35` in the committed row;
  the sha is main-reachable (the PR #249 squash commit), so no annotated tag is required. **[VERIFIED]**

---

## 8. The permanent close record — decisions 3, 4, 7 re-stated

Re-stated from the pause's locked-decision blocks (audits/audit-phase-15-pause.md §7), unchanged by
the close's findings, standing as the phase's permanent record:

- **Decision 3 — torch:** experiment-tier forever this phase; promotion DECLINED; the Wave-2 torch
  track RETIRED. Torch never entered `pyproject.toml`/`uv.lock` (re-confirmed by §1's firewall test
  and lockfile state); the probe stays in-tree (`experiments/lab/torch_probe/`, mypy-excluded,
  opt-in via `uv run --with torch`) as the re-runnable instrument iff impostor reward design ever
  re-opens; distill-to-pure-Python is proven mechanically (0.9709 agreement ≥ 0.90) and was
  capability-empty this wave (student fitness −2.58) — even a future torch win ships without the
  dependency.
- **Decision 4 — co-evolution:** NO-GO for Wave 2, deferred to Phase 17 with an explicit entry
  condition: a re-grounded, re-verdicted surrogate (the 15.13 NO-GO is not re-litigated between
  baselines) plus the full stabilizer stack; never the naive two-population form against a meeting
  layer that cannot convict.
- **Decision 7 — surrogate re-grounding cadence:** standing policy — mandatory re-ground after any
  mover change, any meeting-layer/prompt change, or the sha-keyed cumulative 50,000-meeting
  staleness cap (`training/artifacts/surrogate/max-uses.json`); plus a re-fit and re-verdict against
  the same population-relative GO bar at every new recorded baseline; diagnostic-only until a
  verdict GOes. First scheduled re-grounding: Phase 17.

---

## 9. The end-of-phase merge criteria, walked

The pause-locked criteria (tasks/phase-15.md, "Merge criteria (end-of-phase — locked at the PAUSE,
2026-07-10…)"), item by item:

1. **Champion ships as the pure-Python opt-in factory — MET.** `agents/tactical/learned/` beside the
   untouched FSM default; the Q4 bit-exact gate is test-pinned and green (§1, §7).
2. **Committed replays byte-untouched and byte-verified bare at close — MET** (§1).
3. **Hardened referee lands BEFORE the close re-score; close recording passes validity gate + the
   hardened referee — HALF-MET AS WRITTEN, closed over by the owner ruling.** The ordering held
   (15.19 merged before this close; the dependency edge did its job); the recording passes the
   validity gate; the hardened referee FAILS it on the backing-conversion floor (§3), the outcome
   paused per contract, and the owner ruling (§10) closed the phase over the recorded FAIL. The
   R-gate, funnel, and canaries are reported as findings on corpus denominators with samples
   alongside (§4–§6).
4. **Stamped recordings, machine-checked sha equality from bytes, Q5 convention — MET** (§2, §7).
5. **Torch out of the lockfile; production `agents/` numpy/torch-free — MET** (§1 firewall test, §8).
6. **This audit records all of the above and the banner is flipped to CLOSED — MET**, with the
   referee verdict quoted in the banner per the ruling (§10) so the CLOSED state is not readable as
   a champion referee-endorsement.

---

## 10. The owner call — made, and recorded as the locked close decision

The contract's rule: a hardened-referee failure at close "pauses for an owner call rather than
shipping." The close paused on the 2026-07-10 measurement; the owner ruled on 2026-07-11. The block
below follows the Task-14.6 locked-decision shape; sign-off is the owner's merge of this task's PR.

**LOCKED DECISION (owner, 2026-07-11) — the phase CLOSES over the recorded referee FAIL; the
0.5743-vs-0.6636 backing-conversion miss is judged benign, not blocking:**

- **The ruling and its rationale (the owner's, recorded verbatim in substance):** the measured
  0.5743 and the floor 0.6636 are relatively close; the floor is not a principled necessity but the
  FSM baseline's own measured conversion re-pinned (71/107 under the subject-aware definition) —
  a baseline-relative calibration pin, pinned on FSM-driven gameplay. The champion legitimately
  changes gameplay (this close's own findings: witnessed kills 5 → 32, vent exposure 73 → 40,
  in-window voting up, §5), so swings in crew-side conversion behavior are natural, and 0.5743
  should not be read as a failing number for the close.
- **What makes the ruling safe on this evidence:** the failure mode the supply floors exist to
  catch — perfect-stealth evidence starvation — is measurably absent: both supply gauges pass at
  wide margins (witnessed 0.2195 vs 0.0325; flags 3.0432 vs 1.8633), the geomean 38.58 sits above
  the hardened baseline's own 35.19, integrity is clean, and the validity gate is a full PASS. The
  miss is confined to one crew-side conversion-rate gauge measured against the FSM baseline's own
  value.
- **What the ruling does NOT do:** the committed measurement is untouched — `referee_passed: false`
  stands in `results-champion-close.jsonl` as the instrument's verdict, quoted in the CLOSED banner;
  no referee code or floor is edited inside this close (the contract forbids it: a defect the close
  finds becomes a Phase-16/17 contract, never a close edit); the default flip stays un-blessed
  (decision 2's re-evaluation condition is unchanged — a default flip still requires a
  referee-passing measurement under the then-current instrument).
- **The contracted consequence — floor recalibration is a Phase-16/17 scoping input (§11):** the
  hardened conversion floor is pinned to the FSM baseline population; this close is the first
  measurement of a non-FSM population against it, and it exposes a calibration question the 15.19
  contract could not have answered (champion-shifted crew behavior vs baseline-pinned bar). Whether
  the floor should be re-anchored population-relative (the project's Q1-precedent instinct),
  band-tolerant, or kept baseline-absolute is referee-calibration work for the phase that next
  touches the referee — with this close's committed row as its evidence.
- **Recorded honestly, per this project's convention:** the gauge also correlates with a real
  finding — crew convert backed accusations less and mis-eject more in champion games (accuracy
  0.6972 → 0.6195, §4) — so the ruling trades a calibrated-instrument FAIL for a documented,
  committed finding; it does not declare the signal noise. The pause deliberately made this gauge
  the shipping pass-bar, and the deliberate record of overriding it is this block.

---

## 11. Phase-16 hand-off inputs (restated for the `tasks/phase-16.md` author)

- **v5 vent-elicitation uptake — real, partial, stable at scale:** corpus 188/255 vent-witnessed
  meetings mentioned (structured observations 201/255), samples 53/73, champion set 32/40 (§5). The
  residual unspoken tail is elicitation scope.
- **The v5 impostor self-accusation artifact** (3/851 9p2i ballots, pause §5.2) — dialogue-quality,
  firewall-clean, unaddressed by design under record-only discipline.
- **The residual zero-flag conviction channel** (the Phase-14 close's §4 finding: crew convictions
  on carried suspicion/voice outside any flag channel, which came to dominate mis-ejects) plus the
  citation gate, with the 15.19 subject-aware backing definition as the citation gate's natural
  referee counterpart.
- **The funnel deltas:** Wave 0's structural wins hold on HEAD (structured vents 55, innocent-reporter
  ejections 4 on the committed baseline; §1/§5), and the champion close adds the reshaped-funnel
  finding (§5): witnessed kills 5 → 32, vent exposure 73 → 40, in-window voting 30 → 16 outside-votes.
- **NEW from this close — the conversion seam is the champion's binding constraint:** the hardened
  referee's one failing gauge (0.5743 vs 0.6636, §3) is a crew-side conviction-conversion rate on
  subject-aware-backed accusations. Raising it is voice/judgment work (how testimony converts to
  votes), not tactical-policy work — exactly Phase 16's lane, and the natural companion to the
  zero-flag channel above.
- **NEW from the ruling (§10) — the conversion-floor recalibration question:** the hardened floor is
  pinned to the FSM baseline's own conversion (71/107); this close is the first non-FSM population
  measured against it and the owner ruled the baseline-pinned bar non-blocking for a
  gameplay-shifting champion. The phase that next touches the referee owns the calibration decision
  (population-relative re-anchor, tolerance band, or keep absolute), with
  `results-champion-close.jsonl` as the committed evidence.
- **Phase-17 inputs (unchanged from the pause, plus one):** decision 4's entry condition and
  decision 7's cadence (§8); the branch-B revisit with the Q3 corpus-companion corollary; the
  surrogate synthetic-provenance ask; and the 15.22 gate-valid crew ceiling now measured — learned
  crew fitness 10.335 vs the FSM's 11.469 with 0/30 wins vs 3/30 under a PASSING validity gate,
  task-pace 35.08 → 37.42 tasks/100 ticks (`training/reports/report-crew-owned-tasks.md`).

---

## 12. What I did not do / caveats

- **The banner flip shipped WITH the owner ruling, not before it.** The close first paused with the
  banner untouched (the 2026-07-10 state of this audit); the flip to CLOSED landed only after the
  2026-07-11 ruling (§10), and the banner quotes the referee verdict so CLOSED cannot be read as a
  referee-endorsement of the champion.
- **No re-record, no re-run-until-agree.** One 50-seed recording, per the recipe; its disagreements
  with the pause's numbers are reported as findings (§4) and sit within seed noise on every shared
  cell.
- **No byte-coupled test re-pins** — the deliberate asymmetry vs 14.12: branch A re-records nothing,
  so nothing needed re-pinning.
- **The pause-vs-close conversion delta is a composite** (fresh bytes AND the subject-aware
  definition moved together, §3); decomposing it would need the pause's discarded raw recordings or
  a re-score of these recordings under the retired definition — neither exists in committed form.
- **The stamp `method` label** differs from the pause rows (`utility-scorer-es` vs `neuroevolution`)
  — the productized constant read back from bytes, recorded in §2.
- **The referee numbers quoted for the champion are the HARDENED instrument's** — that is the point
  of this close; no selection or verdict above leans on the retired subject-agnostic gauge.
