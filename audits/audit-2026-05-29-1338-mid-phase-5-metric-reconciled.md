# Mid-Phase-5 Metric Audit — Reconciled

Reconciles the two newest unreconciled metric audits:

- `audits/audit-2026-05-29-1334-mid-phase-5-metric-claude.md` (Auditor: **claude**)
- `audits/audit-2026-05-29-1334-mid-phase-5-metric-codex.md` (Auditor: **codex**)

Adjudicated read-only at current `HEAD`; no source, test, fixture, or
config file was modified. Every finding below was re-verified against
the code and, for the one metric-behavioral claim, against a
fixture built fresh for this reconciliation.

## 1. Verdict

**Mid-phase metric audit passes — proceed to fan out 5.7 + 5.8.**

Both source audits independently reached this verdict and zero blocking
findings. Re-verification at `HEAD` confirms it: the only substantive
finding (claude's E-1, a cost-dashboard docstring overstatement)
reproduces exactly but does not corrupt any computed number, so no
repair task gates fan-out. No repair tasks required.

## 2. Environment

- **HEAD:** `91e0595` (Merge PR #80 — Task 5.6 metric integration +
  per-seed meeting-abort recovery merged).
- **`bash scripts/check.sh`:** exit 0 — `All checks passed!`; pytest
  `964 passed, 12 skipped`; frontend `tsc --noEmit && vite build` OK.
  Matches both source audits' reported counts.
- **`git log --oneline -6`:**

```
91e0595 Merge pull request #80 from dkdan10/claude/zen-archimedes-ME5g0
e8d1f18 task 5.6: recover partial game on per-seed meeting abort
c9e2e56 task 5.6: tournament metric integration
5a48c61 expand task 5.6
2d2b1ad Merge pull request #77 from dkdan10/phase-5-cost-dashboard
3a0aab2 Merge pull request #79 from dkdan10/phase-5-alibi-fabrication-rate-metric
```

All verification ran on the fake provider / direct-model fixtures.
Zero API spend.

---

## 3. Class A — Metric vs. docstring correctness

**No findings.** Both auditors built independent known-answer fixtures
(neither reusing shipped test fixtures) across all four public metrics
and every probe returned the value known by inspection. The two probe
sets cross-corroborate rather than overlap, which strengthens the clean
result:

- **vote_correctness** — the circularity guard holds: an impostor
  ejection with no contradiction and no co-located kill-witness scores
  `evidence_backed=0` (claude A1, codex no-evidence probe). Bucket
  invariant enforced; `rate=None` (not `0.0`) on zero impostor
  ejections; `EJECTED` with `ejected_player_id=None` is skipped, not
  crashed.
- **accusation_calibration** — claim and ballot curves never pooled;
  `confidence==1.0` lands in the closed top bin; `"SKIP"` excluded
  before role lookup; a missing target raises (fail-loud); ECE uses
  empirical mean confidence and is `None` over zero samples.
- **alibi_fabrication** — join rule is subject-membership; denominator
  keyed by AUTHOR role, not subject. **Both auditors built the
  cross-author fixture** (claude AF5, codex cross-author case) and both
  reproduced the module's documented, conservative
  (survival-undercounting) false positive as accepted behavior, not a
  defect.
- **cost_dashboard** — no double-count of failed-call cost
  (`total_cost_usd` is authoritative); per-version totals overlap and
  do not partition; `mean_cost_per_game` guarded to `0.0` on zero games.

No Class A gap: the cross-author alibi case the audit prompt singles
out as the easy-to-miss probe was covered by both auditors.

## 4. Class B — Loader fidelity & roles ground truth

**No findings.** Both auditors ran a fake-provider tournament and
inspected the produced `TournamentReport` directly (claude: 6 seeds 3–8;
codex: 3 seeds 3–5). Concordant results:

- `roles` non-empty and complete; key set equals
  `seed_initial_state(...).players`; exactly `num_impostors` entries are
  `"IMPOSTOR"`; `_seeded_roles` abort-fallback matches the live
  assignment for the same seed+config. Roles come from
  `final_state.players`, never the replay JSONL.
- Per-game `cost.total_cost_usd == compute_cost_usd(replay-seed-N.jsonl)`
  and `sum(by_model.values()) == total_cost_usd`. No double-count.
- `MeetingReplayEntry` → `MeetingReport` maps 1:1 on the meeting fields;
  `run_balance_eval` reduces to a `BalanceReport` whose buckets match
  the report winners and sum to `games`.

## 5. Class C — Partial-replay robustness

**No findings.** Both auditors drove degenerate replays through the
loader. Concordant: no `game_over` row → `winner/final_tick=None`, no
raise; failed-call-only replay (5.6 abort path) counts cost exactly once
(dashboard total equals `compute_cost_usd`, not doubled); doubled/
corrupted file raises `CorruptedFileError` (fail-loud); empty `roles`
for a finished game fails loud; missing replay file (zero-tick) treated
as empty log; `EJECTED` with `ejected_player_id=None` skipped; empty
`prompt_versions` handled. Meeting-abort recovery yields a partial
report with non-empty roles and cost counted once.

## 6. Class D — Schema integrity

**No findings.** Both auditors validated the emitted
`tournament-eval-report.json`: validates against `TournamentEvalReport`;
`model_validate_json(model_dump_json(x)) == x` is identity (embedded
`TournamentReport` re-validates); `format_version == 1` and a bumped
version is rejected; an extra field is rejected (`extra="forbid"`);
`build_tournament_eval_report` packs the four metric blocks without
recomputation (each equals an independent `compute_*`).

## 7. Class E — Prompt-version provenance

**One informational finding (R-1), non-blocking.** Provenance itself is
clean per both auditors: `GameReport.prompt_versions` reflects the live
templates; `per_prompt_version` keys by the real `(template_name,
version)` pairs; a no-meeting game has empty `prompt_versions` and does
not corrupt the roll-up.

### R-1 (Informational) — cost_dashboard's "single-run collapse" docstring overstates an equality the empty-`prompt_versions` case breaks

**Disposition: Unique-but-verified (claude only). Verified: yes.**

`eval/cost_dashboard.py:34-43` (the "Single-run collapse" decision)
asserts that within one run *"every `(template, version)` key appears in
every game and each per-version total equals the tournament total."*
That equality holds only when **every game ran a meeting**. A game with
spend but empty `prompt_versions` — the canonical case being the **5.6
meeting-abort recovery path**, where a meeting crashes before completing
(no `MeetingReplayEntry`, hence no `prompt_versions`) but a
`FailedCallReplayEntry` carries real spend — contributes to the
tournament total but to **no** per-version key. The same module's
"Empty inputs" decision (`eval/cost_dashboard.py:44-49`) and the loop at
`eval/cost_dashboard.py:152` describe exactly this case, so the docstring
is internally inconsistent with itself.

Reconciliation fixture (built fresh, not borrowed from either auditor):
a 2-game `TournamentReport` — game A (template `meeting/v1`, cost 1.0) +
game B (empty `prompt_versions`, cost 0.5):

```
tournament total_cost_usd = 1.5
  per-version meeting/v1: total=1.0  games=1
docstring 'each per-version total == tournament total' holds: False
every version key appears in every game: False
```

**Why informational, not blocking:** the per-version `total_cost_usd`
value is *correct* — it is exactly the sum of game cost over games that
ran the template — so no downstream metric receives a wrong number, and
Task 5.8's cross-run delta (matching keys across two dashboards) is
unaffected. Only the docstring's stated equality is idealized. codex
observed the same mechanism (a no-meeting game has `prompt_versions={}`
and contributes no per-version row, total cost well-defined) but framed
it as correct behavior and did not flag the docstring tension; codex did
not reject the finding, so the union rule applies. Worth recording
because the 5.8 close-gate narrative ("a prompt change shows a cost
delta") leans on per-version ≈ tournament cost; a one-line docstring
qualification would make the roll-up self-describing. No code change to
the metric.

---

## 8. Repair task proposals

None. No blocking findings → no repair task gates 5.7/5.8 fan-out.

Optional (documentation-only, foldable into 5.7's dashboard contract):
qualify the `eval/cost_dashboard.py` "single-run collapse" docstring so
its equality reads *"each per-version total equals the tournament total
when every game ran a meeting; a game with spend but empty
`prompt_versions` (e.g. a crashed meeting recovered by the 5.6 abort
path) contributes to the total but to no version key."* Not a gate.

## 9. §3 Reconciliation

### §3.1 Comparison table

| ID | Class | Title | claude says | codex says | Verified | Final severity | Disposition |
|----|-------|-------|-------------|------------|----------|----------------|-------------|
| R-1 | E | cost_dashboard "single-run collapse" docstring overstates per-version=tournament equality | Informational — empty-`prompt_versions` game breaks the stated invariant | — (observed the mechanism as correct behavior; no finding raised) | yes (fresh fixture: 1.5 total vs 1.0 per-version) | Informational | Unique-but-verified |

All four metrics in Class A, and Classes B/C/D, produced **no findings**
in both audits; per the "findings without a row do not exist" rule and
"informational notes count as rows," only R-1 is a row. The
no-findings classes are recorded as prose concordance in §3–§6 above.

### §3.2 Disagreements and resolutions

**R-1 (Unique-but-verified).** This is the only row whose disposition is
not `Confirmed`, and the only point of divergence between the two
audits. claude graded it Informational; codex raised no Class E finding.
There was no *severity* disagreement to resolve — codex did not grade
R-1 lower, it simply did not surface the docstring tension while
observing the same underlying behavior (empty-`prompt_versions` game →
no per-version row, cost still counted). Under the union rule (§3 of the
reconciliation contract), a finding one auditor cited and the other
neither cited nor rejected is included if it re-verifies at HEAD. It
does: my independently-built fixture reproduced tournament total `1.5`
against a sole per-version total of `1.0`, falsifying both halves of the
docstring's claim. The severity stays Informational — not by splitting
the difference, but because re-verification confirms the computed
per-version values are individually correct and no consumer receives a
wrong number; the defect is confined to docstring prose. No higher
grading is warranted because the audit prompt's bar for Class A/E
blocking is a metric that returns a wrong value or a contract the code
violates, and here the code matches its own "Empty inputs" decision —
it is the "Single-run collapse" sentence that is unqualified.

### §3.3 Verdict reconciliation

Both source audits returned the identical verbatim verdict ("passes —
proceed to fan out 5.7 + 5.8"), so the agreement is adopted directly;
the conservative tie-breaker is not engaged. Re-verification supports
it: the sole finding is documentation-only and confined to a docstring,
the check suite is green, and the one metric-behavioral claim that could
have gated fan-out (R-1's equality) was confirmed to leave every
computed number correct. No gap was left unaudited — in particular the
cross-author alibi fixture the audit prompt flags as the easy miss was
built by both auditors. Verdict: **passes**.

## 10. Required closing fields

- **Report path:** `audits/audit-2026-05-29-1338-mid-phase-5-metric-reconciled.md`
- **Verdict:** Mid-phase metric audit passes — proceed to fan out 5.7 + 5.8.
- **Findings count by class:**
  - Class A (metric vs. docstring): 0
  - Class B (loader fidelity & roles): 0
  - Class C (partial-replay robustness): 0
  - Class D (schema integrity): 0
  - Class E (prompt-version provenance): 1 (Informational)
- **Total findings:** 1 (0 Blocking, 0 High, 0 Medium, 0 Low, 0 Concern, 1 Informational)
- **Disposition counts:** Confirmed 0 / Unique-but-verified 1 / Promoted 0 / Demoted 0 / Dropped 0 / New 0
