# Owner decisions deferred at the merge (2026-09-07)

The merge of `codex/cleanup` into `main` (`8161689a`, PR #435) left two items
open on purpose. This memo assesses each and leaves a ruling line. It authorizes
nothing by itself: item A's recommended action is prepared as a draft pull
request, and item B's recommended limits become an authorization only if the
owner merges the pull request that carries them. Line references are at
`8161689a`.
Both ready patches are branches with draft pull requests, which the delivery
text at `AGENTS.md:11-14` does not yet allow; the owner's 2026-09-07 instruction
supersedes it, and item A's patch is what resolves the contradiction.

Each section gives the state at `main`, what goes wrong if the item is left, the
options, the recommendation and its reason, the cost of acting, and a ruling
line. A blank ruling means undecided, not accepted.

## A. The branch-policy documents

**Ready patch:** branch `work/branch-policy-flip`, draft PR #436 — merge to
accept, close to decline. Documentation plus one deleted line of
`.github/workflows/ci.yml`; no source, test, recording or report byte moves.

### State at main

Ten surfaces still instruct a worker to deliver on `codex/cleanup` and to keep
`main` unchanged:

| Location | What it still says |
| --- | --- |
| `AGENTS.md:11-19` | Work directly on `codex/cleanup`, push to `origin/codex/cleanup`, do not create implementation branches or require a per-task PR, keep `main` unchanged |
| `.github/workflows/ci.yml:8` | `codex/cleanup` is a push trigger |
| `tasks/README.md:3-7, :16-26, :37-38` | Implementation continues on the branch; a four-row ownership table for the finished correction batch; the inherited PRs "have not been merged" |
| `docs/workflow.md:11-27, :98, :146-158` | `codex/cleanup` is the working branch; a per-task PR is optional; the pilot paragraph reads as standing policy |
| `tasks/cleanup-roadmap.md:3-5, :25` | Implement on the branch; "not merged into main" |
| `tasks/post-review-plan.md:4` | "Implementation stays on `codex/cleanup`; main merge ... remain separate decisions" |
| `tasks/review-ledger.md:5-6, :172-173, :219` | "All rows remain unmerged into main"; main is `cfde4c89` |
| `README.md:53` | "Active cleanup remains on its review branch until final owner review" |
| `docs/cleanup-dispositions.md:3, :148-149` | "the cleanup branch" as a live place |
| `docs/lessons.md:18` | The workflow "now uses ... focused commits on one working branch" |

The ledger recorded the deferral itself at `tasks/review-ledger.md:247-252`,
naming these surfaces and "the merge's own coordination record" as the vehicle.
The seven queued post-merge cards carry no branch instruction of their own, so
`AGENTS.md:11` is the only delivery instruction a dispatched worker finds.

### What goes wrong if left

A worker dispatched against any of the seven post-merge cards reads AGENTS.md,
commits to `codex/cleanup`, pushes, and produces work that is neither on `main`
nor in a pull request. The ledger calls every row unmerged while every row is
merged, so the delivery-state vocabulary at `docs/workflow.md:53-62` — where
"Merged" means the merge exists — stops describing reality. Nothing fails
loudly: no gate reads AGENTS.md, the workflow, the task index, the ledger, the
roadmap or the dispositions, so the error surfaces as a wasted branch rather
than a red check.

### Options

1. Flip the documents and the CI trigger together (the ready patch).
2. Flip the documents, keep the `codex/cleanup` push trigger. Harmless, and
   leaves CI running on a branch nobody should push to.
3. Leave everything and correct the policy per dispatch. Every dispatch then has
   to contradict the standing rules in writing.

### Recommendation and why

Option 1, with this policy written into `AGENTS.md` and `docs/workflow.md`:
implementation for a card goes on a short-lived branch named `work/<card-slug>`
and reaches `main` through one pull request per card; planning and contract
documents may land on `main` directly as `docs:` or `coordination:` commits; a
merge commit or fast-forward, never a squash that orphans a SHA another document
cites.

The pull-request half restores the review-evidence route the cleanup suspended,
and `.github/pull_request_template.md`, `docs/agent-procedures.md:36-77` and
`CONTRIBUTING.md:9-17` already describe it. The direct-to-main half matches what
this repository actually does with planning documents. The no-squash rule is the
choice #435 made in its own commit message, so that cited branch SHAs stay
reachable.

The patch also states one fact no delivery document states today: a push to
`main` publishes. `.github/workflows/pages.yml` rebuilds the demo bundle from
the committed recordings and the featured list on every push to `main`, so a
change to the viewer, the featured games or the public-results payload is a
publication decision; `docs/deployment.md` is the authority.

Removing the `codex/cleanup` push trigger has exactly one effect: pushes to that
retained branch stop running CI. `pull_request` carries no branch filter, so
pull requests from any branch still run the whole workflow; there is no branch
protection to update, and `pages.yml` and `campaign-tier.yml` are untouched.

### Cost

One documentation commit across ten files plus one deleted YAML line. No
behavior change and no test change. `README.md` and `docs/lessons.md` are the
only gated pages: the patch leaves README at 1,436 of its 1,600-word ceiling and
lessons at 1,444 inside its 800–1,500 band. Verification is `bash
scripts/check.sh` plus `scripts/check_doc_facts.py`, and CI on the pull request
is the same gate again. Reverting is one revert commit.

### Ruling: merged #436 as proposed (owner, 2026-09-07; merge commit `081aee15`)

## B. Authorization for the fresh-model deduction evaluation

**Ready patch:** branch `work/fresh-eval-authorization`, draft PR #437 — a card,
`tasks/work/fresh-deduction-authorization.md`, holding the limits below as
PROPOSED, plus the two decision rows of `tasks/post-merge-plan.md` routed at it.
Merging is the authorization act; closing declines. Nothing is authorized while
it is open, and even merged it authorizes limits rather than a run: the run also
needs outcome 5's instrument and its frozen manifest.

### B.0 Current state

`audits/deduction-candidate/execution-manifest.md` does not exist. The
preregistration reaches stage 2 — "Before any fresh provider run, the execution
manifest must bind:" ([`preregistration.md:105`](../audits/deduction-candidate/preregistration.md))
— lists what a manifest must carry at `:107-118`, and stops: `:120-121` states
that "No live call, including a pilot or retry on flat-rate service, is
authorized by this draft." Of the fields at `:113-115`, six are the owner's
alone — exact provider, exact model, requested token caps, elapsed-time limit,
cost limit, and the owner's explicit authorization for those limits — plus a
cost statement that flat-rate access does not excuse, and plus the death-tick
body-handle choice carried at [`post-merge-plan.md:83`](post-merge-plan.md).

The machine-readable side already has the hole cut to shape:
`audits/investigation-candidate/candidate-handoff.json:20-31` carries
`required_before_live_execution` with ten null fields, six of which are the
owner's (`provider`, `model`, `token_budget`, `wall_time_budget_seconds`,
`cost_budget_usd`, `owner_authorization`) and four of which the worker fills
(`sampling`, `held_out_inputs`, `grading_rubric`, `numeric_decision_bars`).

The card that will build the manifest, [`work/fresh-deduction-instrument.md`](work/fresh-deduction-instrument.md),
is `ready` and not started. Its `:71-75` requires the manifest to land with the
owner fields present and EMPTY; its `:82-85` authorizes no live call, pilot,
smoke run or retry; its `:96-101` names two preconditions —
[the renderer repair](work/evidence-renderer-salience.md) and
[the provenance gaps](work/recorded-provenance-gaps.md) — both `ready` and both
not started. `post-merge-plan.md:50-53` puts this outcome in parallel with
outcomes 3 and 4 but forbids exercising its arms until 2 and 3 land.

**Nothing is blocked on this decision today.** What is blocked is the *shape* of
the decision: when the manifest does land, its owner fields will be empty and
whoever fills them will be reconstructing this analysis from scratch, weeks
later, under pressure to start a run.

### B.1 Decision-input sheet — the eight owner fields

Every "value the tree already suggests" below is a recommendation, not a
commitment. The Ruling block at B.12 is where they bind.

| # | Owner field | Value the tree already suggests | Evidence anchor |
|---|---|---|---|
| 1 | **provider** | `featherless` | `llm/provider.py:74` — flat-rate hosted subscription, $25/mo Premium, owner decision 2026-06-25. `llm/featherless_client.py:243-244` exposes `0.0` pre-flight rates, so `BudgetedLLMClient`'s USD dimension self-disables. |
| 2 | **exact model** | `Qwen/Qwen3.6-27B` (un-suffixed repo form; `-Instruct` is HTTP 404 on the plan) | `llm/featherless_client.py:147` `DEFAULT_FEATHERLESS_MODEL`; `audits/audit-phase-16-model-lock.md:35-80` LOCKED DECISION. Unlisted ids fail loud at `llm/featherless_client.py:620`. |
| 3 | **per-call token cap** | turn `2048` / vote `1024`, unchanged | `meetings/manager.py:210-213` shipped defaults. The committed lab rows for this exact model-and-prompt-set pair ran at `max_tokens=4096` and never exceeded **195** output tokens (`experiments/lab/results-featherless-sweep-qwen3-6-27b-ab.jsonl`, n=104, median 138), so 2048 is ~10x the observed need and a truncation would be a real signal. |
| 4 | **total token budget** | **2,400,000 input / 200,000 output** run-level, and **45,000 input / 4,000 output** per unit | `GameBudget` has two token dimensions, not one (`llm/budget.py:110-112`), so the card's single "about 2.5 M" must be split. Arithmetic in B.2. |
| 5 | **wall-clock deadline** | **4 h of model work + a 2 h stall margin = 6 h elapsed** | Work window from B.3's latency correction: 600 calls x 12 s sequential = 2.0 h, x 23.1 s = 3.9 h. Stall margin from the single recorded 3h21m HTTP-529 loss at `../audits/audit-phase-21-adopting-record.md:373-380`. |
| 6 | **dollar limit** | **$0.00 marginal** | Flat-rate. Recorded as a bound, not as an enforcement mechanism — see the cost statement. |
| 7 | **cost statement** | the paragraph at B.10 | `preregistration.md:115` "Flat-rate access still needs bounded token/time use and a cost statement"; card `:75`. |
| 8 | **death-tick body handle** | **leave the default path as-is, state it, and assert the masking mechanically** | Both arms run temporal v2 and therefore already take the masked branch. Full argument at B.7. |

Two further fields are not the owner's to invent but **bind the token budget**,
so they are recorded in the same block and a change to either invalidates the
budget:

| Field | Recommended | Why it is here |
|---|---|---|
| **roster shape / living voter count** | 4p1i, **3 living voters** at meeting open | This is the largest single cost driver in the design and it is currently unbound. 3 voters = 600 calls / 1.72 M tokens; 5 voters = 1,000 calls / 4.68 M; 7 voters = 1,400 calls / 6.55 M. Going 3 -> 5 multiplies the run **2.7x**. |
| **execution mode** | **sequential** | `RunDeadline` (`orchestrator/run_limits.py:18`) is a single cooperative clock, and a `HeadlessGame`-driven instrument is sequential unless it adds a pool. The 2-worker parallelism used by the recorders lives in the shell (`scripts/refresh_samples.sh:426-440`) and is a *plan ceiling*, not a tuning knob: the Featherless plan permits 4 units and a 32B-class request costs 2, so 2 workers saturate it and 3 would exceed it. |

Locked upstream and re-stated so the authorization is not silently portable, not
re-decided here: prompt set `qwen3_6_27b` (`agents/strategic/prompts/loader.py:185`,
rendered by every arm of the committed deduction matrix); `enable_thinking=false`
pinned on every call; `response_format_mode = json_object`; thinking policy
`fail_loud` — all four from `../audits/audit-phase-16-model-lock.md:35-80`.

### B.2 The three options

All three run the same comparison: 50 held-out proof-free scripted prefixes x 2
arms = 100 paired units, `repaired_clock` (temporal 2 + evidence 2) versus
`combined_accounts` (plus public accounts and attributed testimony), scored with
the exact paired McNemar at `scripts/paired_stats.py:95`. They differ only in
shape, size and provider.

**Option A — Featherless / `Qwen/Qwen3.6-27B`, 4p1i shape, 3 living voters. RECOMMENDED.**

- 100 units x 6 calls (3 turns + 3 ballots) = **600 calls**.
- Input, per arm, at the corrected 1.28x calibration over the committed `len//4`
  figures: `repaired_clock` 2,841 -> 3,636 per call x 300 = **1,090,800**;
  `combined_accounts` 1,907 -> 2,441 per call x 300 = **732,300**; total
  **1,823,100**.
- Output: 600 x 220 (the conservative 9p2i measured figure; 4p1i measures 188) =
  **132,000**.
- **Measured projection ~1.96 M tokens** (~1.72 M on the flat 4p1i average of
  2,680 in / 188 out per call — both denominators are stated deliberately; see B.3).
- **Authorized budget 2,400,000 input / 200,000 output** = 2.6 M ceiling, a 1.32x
  margin on input and 1.5x on output. Per-unit budget 45,000 / 4,000, roughly 2x
  the larger arm's 21,822 / 1,320.
- **$0.00 marginal.** Wall 2.0-3.9 h of model work; **4 h authorized work window,
  6 h elapsed with the stall margin.**

**Option B — same, 9p2i shape, 5 living voters.**

- 100 units x 10 calls = **1,000 calls**, **4.68 M tokens measured**, budget
  **5,600,000 in / 400,000 out**, **$0.00**, wall 3.3-6.4 h -> **8 h authorized
  work window, 10-11 h elapsed with the stall margin**.
- Buys a larger table with more crossfire and a roster closer to the corpus the
  calibration comes from. Costs 2.7x the tokens and roughly double the wall, for
  the same 100 paired units and therefore the *same statistical power*. The
  extra spend buys realism, not resolution.

**Option C — metered Anthropic cross-check on a subsample.**

- A 10-20% slice of option A's calls re-run on a metered model to check that the
  result is not a single-model artifact. At `llm/provider.py:58-61` rates
  (sonnet-4-6 $3/$15 per MTok; haiku-4-5 $1/$5): full 600 calls = **$6.52
  sonnet / $2.17 haiku**; a 120-call (20%) slice = **$1.30 / $0.43**; a 60-call
  (10%) haiku slice = **$0.22**. Range **$0.22-$6.52**.
- **Caveat that bounds what C can mean:** the `qwen3_6_27b` prompt family was
  authored *for* this model, from a from-scratch ladder, and locked on that
  basis (`../audits/audit-phase-16-model-lock.md:35-80`). A different model
  reading Qwen-tuned prompts measures the prompt-model pair, not the model. A
  low score on C is not evidence the design fails elsewhere; a high score is
  weak evidence it generalises. C answers "did we accidentally measure one
  model's quirk", and nothing stronger.
- Not recommended as part of this authorization. If the owner wants it, it is a
  **separate** authorization with its own dollar limit, because it is the only
  one of the three where a bug costs money.

### B.3 Two corrections the owner must carry into the manifest

**(1) Output calibration is 1.51x, not 3.7x.** The card's Evidence line
(`work/fresh-deduction-instrument.md:42-43`) says "real input runs about 1.27x
and real output about 3.7x" the committed `len//4` heuristics. Input is right
(measured 1.28x, n=1,974). **Output is not.** Real output is **1.51x** the
`len//4` heuristic. The 3.7x figure compares real output per call against the
*scripted capture's* per-call output — a different denominator — and the honest
figure on that denominator is **3.05x**. A manifest that budgets output at 3.7x
the heuristic over-provisions by ~2.5x and, worse, teaches the next reader that
the calibration is unreliable. **The manifest must name its denominator on every
ratio it quotes.** Both denominators are legitimate; conflating them is not.

**(2) Latency IS recorded — the review's "no latency" residual is wrong.**
`experiments/lab/probe_backends.py:258-272` stamps `latency_s` on every probe
call, and `experiments/lab/results-featherless-sweep-qwen3-6-27b-ab.jsonl`
carries **104 committed rows for exactly this model and prompt set**
(`Qwen/Qwen3.6-27B` x `qwen3_6_27b`, non-thinking, `parsed_ok` 104/104):
**median 23.1 s/call**, mean 22.6, p25 10.8, p75 28.5, max 87.3; by call kind,
opening 14.9, reply 23.8, vote 23.2. Independently, the 2026-09-03 four-leg
recording gives a sequential figure: `samples/9p2i` recorded 1,740 calls in
3h03m29s at 2 workers = 6.3 s/call wall = **~12.7 s/call sequential**;
`samples/4p1i` 234 calls in 20m21s = **~10.4 s sequential**.

The two figures bracket rather than contradict: the lab rows ran at
`max_tokens=4096` on lab corpora, the recordings ran production caps on real
meetings. **Budget the wall on the 12-23 s/call band, not on a guess.** That
band is what makes option A's 4 h defensible and option B's 8 h necessary.

### B.4 Stalls, caps and what actually stops a run

**Recommended enforcement: a per-unit `GameBudget` with a run-level parent, plus
one `RunDeadline` measured against elapsed wall.**

- `GameBudget(parent=...)` exists at `llm/budget.py:111`; every charge reaches
  both budgets even after either cap is exceeded, and `preflight` (`:145`)
  rejects a doomed call without mutating totals.
- `build_default_meeting_runner(llm_client=, budget=, deadline=, env=)`
  (`orchestrator/game.py:1258-1267`) is the seam; passing a budget wraps the
  recording client in `BudgetedLLMClient` at `orchestrator/game.py:1151`, which
  is fail-loud *before* the call.
- The copy-ready precedent is `experiments/tactical_gameplay.py:585-620`: build
  the budget and the deadline, hand both to the runner and the game, then
  reconcile the recorded spend against the budget snapshot afterwards and raise
  on any mismatch. Reuse it.
- **`GameBudget` and `BudgetedLLMClient` have no default production call site.**
  The instrument must construct them; nothing enforces a budget by default.

**Why per-unit-with-a-parent rather than run-level caps on the CLI.** The
tournament CLI's cumulative caps (`--max-total-cost-usd`,
`--max-total-input-tokens`, `--max-total-output-tokens`,
`scripts/run_tournament.py:388-410`) are **mutually exclusive** with
`--attest-unknown-usage` (`:1223`: "a cumulative cap cannot be enforced over
unmeasured usage"). That exclusion has a sharp edge here. Featherless runs
stall: `../audits/audit-phase-21-adopting-record.md:373-380` records a **3h21m
loss** to a provider-side HTTP 529 kill on one leg. If a stall lands **before
the first row is written**, a run started under `--max-total-*` has no forward
path: it cannot resume under the caps without measured totals, and it cannot
attest unknown usage without dropping the caps. The escape and the cap cannot
both be held.

Two ways out, both acceptable:

- **Recommended.** The instrument constructs its own `GameBudget` and
  `RunDeadline` directly and never goes through the tournament CLI, so the
  exclusion never binds. Cost: the CLI's resume-awareness
  (`scripts/run_tournament.py:1383-1405` seeds the budget from
  `progress.totals()` and shortens the deadline by `progress.elapsed_seconds`)
  is lost and must be replaced by the instrument's own per-unit checkpoint, so
  a resumed run re-authorizes from what it already spent rather than from zero.
- **Alternative.** Run through the CLI with `--max-wall-seconds` only, leaving
  `--max-total-*` unset so `--attest-unknown-usage` stays reachable, and enforce
  the token ceiling through the per-unit `GameBudget` instead. Keeps resume;
  gives up the cumulative token cap at the CLI layer.

**Stop semantics are already written and must not be re-invented.**
`preregistration.md:233-234`: reaching an authorized time, token or cost limit
"stops new calls, retains partial evidence and unresolved accounting, and does
not trigger unbudgeted retries or silent expansion." Concretely: a per-unit
overrun aborts **that unit** and marks it deliberately partial; a parent overrun
stops the **run**. Neither is a retry. The operating rule for genuine transport
blips is the recorders' (`scripts/refresh_samples.sh:449-462`,
`AILIBI_SEED_MAX_ATTEMPTS=4` on Featherless, 1 elsewhere; a recorded
parse/schema failure is not a crash and does not spend the budget) — but a
retry budget is **not** authorized by this memo and belongs in the manifest.

**The dollar cap does not stop anything on this provider.**
`llm/featherless_client.py:243-244` reports `0.0` pre-flight rates, so
`BudgetedLLMClient` (`llm/budgeted_client.py:118-126`) disables the USD
dimension entirely and every recorded `cost_usd` is 0.0 by construction. On
Featherless the **token budget and the wall deadline are the only limits with
teeth**. Recording `$0.00` is honest bookkeeping, not a safety mechanism, and
the manifest must say so in those words.

### B.5 The arm-asymmetric budget — one cap, sized on the larger arm

The two arms are not the same size, and prompt size is **not** monotone in
features. On the committed scripted matrix, per call:
`repaired_clock` **2,841 input** — the largest arm, 1.316x the legacy reference
— against `combined_accounts` **1,907**. The candidate arm is the *cheaper* one.

The methodological consequence matters more than the money: **do not set
per-arm caps.** In a paired design, a cap that truncates one arm more often than
the other is a confound that looks exactly like an effect. Set **one** per-unit
cap sized on the larger arm (`repaired_clock`), apply it identically to both,
and **record per-arm usage separately** so the asymmetry stays visible in the
results. A truncation in either arm is a stop, not a datum.

### B.6 The held-out preparer is a separate person, and this is an owner action

`preregistration.md:143-149`: "A separate reviewer should prepare and freeze new
held-out legal schedules and information patterns before the candidate is
evaluated on them." The card restates it twice — acceptance `:52-56` ("prepared
by someone other than the runner … The seven committed development cases are
excluded by hash") and constraints `:87-88` ("Inspecting a held-out input
converts it to development data; the generator and the runner are different
roles for that reason").

**No held-out prefixes exist today.** Before the manifest can be frozen the
owner names two roles: a **preparer** who generates, freezes and hashes 50
proof-free scripted prefixes excluding the seven development cases by hash, and
a **runner** who never opens the prefix files. The split convention already in
the tree is disjoint seed bands
(`experiments/tactical_gameplay.py:719-728`, `split: "development" | "held_out"`).

This is not a spending field, but it is an owner action with the same deadline:
an authorization whose held-out set was prepared by the runner authorizes a run
that cannot make a generalization claim.

### B.7 The death-tick body handle — what "mask equally in both arms" means

**The code.** `engine/rules.py:87` mints `body_id = f"body-{target.id}-{state.tick}"`;
the suffix **is** the exact kill tick, verified 41/41 with zero mismatches in
the follow-up review's OFF corpus. `orchestrator/game.py:3352-3358` chooses:

    described_body = (
        (public_body_id(victim_id) if victim_id is not None else None)
        if temporal_observations
        else body_id
    )

and `:3359-3363` renders it into the meeting trigger line every participant
reads: `"{actor} reported body {described_body} at tick {trigger_tick}"`.
`observation/body_ids.py:6-11` returns `body-{victim}` — "a stable handle
without encoding a death tick or kill attribution". The packet side is already
repaired unconditionally: `observation/service.py:425-433` uses `public_body_id`
unless `legacy_body_ids` (default `False`), and `:236` refuses v2 together with
legacy handles.

**So what does the choice actually reduce to?** Both arms of this evaluation run
temporal v2. Both therefore take the masked branch at `game.py:3355`, and both
render `body-p-N` with no tick suffix. The review's own per-arm census confirms
it: `a_off {'body-p-N-N': 40}`; `e_temporal_v1 {'body-p-N': 40}`;
`b_temporal_evidence {'body-p-N': 39}`; `c_accounts {'body-p-N': 39}`.
**The masking is already equal, and it is a property of the arm definitions, not
a new decision.** "Mask equally in both arms" is satisfied by construction.

**Recommendation: leave the default path as-is, state it in the manifest, and
add one mechanical assertion.** The assertion is the one the finding itself
prescribes: **no rendered prompt in either arm, and no frozen prefix, matches
`body-p-\d+-\d+`.** A claim about a leak that is checked by a regex over the
actual served bytes is worth more than a sentence.

**One trap the card does not name.** If the held-out prefix *generator* runs on
the default (temporal-off) path, a scripted earlier trigger line can carry
`body-p-N-T` identically into **both** arms. That is not asymmetry — it is a
constant, so it does not bias the paired contrast — but it inflates both arms'
absolute deduction score by handing the model a free time of death, which is
precisely the quantity this evaluation exists to measure. **The manifest must
bind the prefix generator to the same temporal version as the arms, and the
regex assertion must run over the frozen prefixes as well as the live prompts.**

**Rejected alternative, and why.** The finding's own "smallest fix" — route the
handle through `public_body_id` unconditionally at `game.py:3355` and in the
report-action payload projection, outside the temporal gate. It is the right
repair and it should happen eventually. It is rejected *here* because it moves
default-path recorded bytes, it is owned by no card in this queue, it would need
the adopting-record path, and it is not needed for this evaluation, whose arms
are already masked. It stays filed as an accepted limitation, documented at
`../docs/observation-contract.md:36-39` and disclosed on the front door at
`../README.md:45-47`.

### B.8 What goes wrong if this is left

- The manifest lands with empty fields and no analysis behind them. Whoever
  fills them re-derives the calibration, the latency band, the arm asymmetry and
  the stall behaviour from scratch — most likely at the moment they want to
  start a run, which is the worst moment to be doing arithmetic.
- The **3.7x** output figure in a `ready` card is copied into the manifest
  unchallenged and the budget is over-provisioned ~2.5x on the output dimension.
- The roster stays unbound and the run silently becomes option B's cost with
  option A's authorization — a 2.7x overrun that no cap catches, because the
  cap was sized for a different roster.
- The wall deadline is guessed. Guessed low, one recorded-scale stall consumes
  the whole allowance and the run stops partial with nothing to show. Guessed
  high, the deadline stops being a runaway guard.
- The death-tick question stays open and gets answered implicitly by whichever
  config the prefix generator happened to use.

None of this is urgent. All of it is cheap now and expensive later.

### B.9 Recommendation

**Option A, on the values in B.1, enforced as B.4 describes, with the death-tick
handle left as-is and asserted.** Land the unsigned `B-AUTH` block below so the
owner's act is filling blanks rather than reconstructing a design. The block
binds nothing until the manifest lands with cards (a) and (b) discharged.

The evidence for preferring A over B: identical statistical power (100 paired
units either way), 2.7x the tokens and ~2x the wall for B, and the 4p1i shape is
the one the follow-up review actually dry-ran end to end through the fake
provider. The evidence for preferring A over C: the prompt family was authored
for this model and locked on that basis, so a metered cross-check measures the
prompt-model pair; and A is the only option where a bug cannot cost money.

### B.10 Cost

**Effort.** The memo and the `B-AUTH` block: prose only, no code, no tests, no
`audits/` bytes, no `docs/artifacts.md` refresh. Roughly one sitting to write,
one to review.

**Spend authorized by this memo: none. $0.00, unconditionally.** See B.11.

**Cost statement (flat-rate service) — the template the manifest carries:**

> This evaluation runs on the Featherless AI Premium plan, a flat-rate hosted
> subscription at $25/month authorized by the owner on 2026-06-25
> (`llm/provider.py:74`). Its marginal cost is **$0.00**: no per-token charge is
> incurred, and the provider-keyed zero rate makes every recorded `cost_usd` on
> this run exactly 0.0 by construction rather than by measurement. The resources
> this run actually consumes are subscription capacity and elapsed wall time:
> ____ projected model calls and about ____ tokens over a ____-hour elapsed
> window, against a plan whose concurrency ceiling is four units and whose
> 32B-class request costs two — i.e. two workers saturate it, and this run uses
> ____. The dollar cap recorded in this manifest is $0.00 and is **not** an
> enforcement mechanism on this provider: `BudgetedLLMClient`'s USD pre-flight
> dimension self-disables at a zero rate
> (`llm/featherless_client.py:243-244`, `llm/budgeted_client.py:118-126`), so the
> token budget and the wall deadline are the only limits that can stop this run.
> The same run on a metered provider would cost ____ at the rates in
> `llm/provider.py:58-61` and would require its own separate authorization;
> nothing in this statement carries over to one.

### B.11 What signing this does NOT do

Stated plainly, because a signed block that reads like a green light is worse
than no block at all:

1. **It authorizes no spending today.** Nothing can be spent until
   [the renderer repair](work/evidence-renderer-salience.md) and
   [the provenance gaps](work/recorded-provenance-gaps.md) have both landed
   (`work/fresh-deduction-instrument.md:96-101`) **and**
   `audits/deduction-candidate/execution-manifest.md` exists with these values
   copied verbatim (`:71-75`).
2. **It authorizes no pilot, no smoke run, no retry — including on flat-rate
   service.** `work/fresh-deduction-instrument.md:82-85` and
   `../audits/deduction-candidate/preregistration.md:120-121` both say this in
   those words. A free call is still a call.
3. **This memo is not the manifest.** The manifest is card (d)'s deliverable and
   binds ~35 fields; this memo assesses eight of them.
4. **Ratification is the merge of the execution card's PR, not of this one.**
   Merging the `B-AUTH` section lands the *shape* of the authorization. An
   all-`____` block authorizes nothing and says so on its first line.
5. **It authorizes no adoption.** A result from this evaluation is not an
   adopting record. `post-merge-plan.md:81` keeps the evidence-v2 adopting
   record outstanding and separate, and `:82` keeps adoption of public accounts
   and attributed testimony outstanding and separate.
6. **It does not settle the held-out preparer.** B.6 is an owner action with the
   same deadline and it is not one of the eight fields.

### B.12 Ruling: merged #437 as proposed (owner, 2026-09-07; merge commit `0f49d8e6`) — the limits in `work/fresh-deduction-authorization.md` are authorized; no run, pilot or retry is, until cards (a) and (b), the manifest and the frozen held-out set land; the preparer and runner roles were ruled later the same day (B.13)

If the card is amended, record the changed fields here so the memo and the card agree:

- **Option:** ____  (A / B / C / other)
- **provider:** ____
- **exact model:** ____
- **per-call token cap:** turn ____ / vote ____
- **total token budget:** ____ input / ____ output (run) · ____ / ____ (per unit)
- **wall-clock deadline:** ____ h work · ____ h elapsed
- **dollar limit:** ____
- **cost statement:** approved as drafted at B.10 / amended: ____
- **death-tick body handle:** leave as-is and state it / mask equally in both arms — ____
- **roster shape and living voter count:** ____
- **execution mode:** sequential / 2 workers — ____
- **held-out preparer:** a fresh preparer session on `work/held-out-prefix-freeze.md` · **runner:** a separate session on `work/fresh-deduction-instrument.md`, started after the freeze (B.13)
- **Ruling:** ____
- **Date:** ____

### B.13 Ruling on the two roles (owner, 2026-09-07): mechanical generation, two sessions

Four options were put to the owner for B.6: (1) the owner prepares by hand and
a session runs, which converts the owner's inspection into development data;
(2) one agent session prepares and a second runs; (3) one session does both
with an inspection ban, which no record can prove; (4) a deterministic
generator draws from a band preregistered before it is written, so no person
or session chooses or reads a prefix. The owner chose 4 for generation and 2
for the roles. The preparer is a fresh session dispatched on
[the freeze card](work/held-out-prefix-freeze.md) alone: it builds the
generator, draws the first fifty proof-free prefixes from seeds 3000 to 3999
ascending, commits the band and the per-prefix hashes but no prefix bytes, and
opens the pull request whose owner merge is the freeze. The runner is a
separate session started after that merge and dispatched on the instrument
card; it regenerates the set from the committed generator, refuses to proceed
on any hash mismatch, and opens no prefix before the run. Neither the owner
nor the coordinator reads a prefix. If a held-out result later informs a fix,
the manifest marks the set development and a new band is frozen under a new
card. The blanks in the authorization card and in the B.12 field list carry
this ruling.

## Not assessed here

PRs #432-#434 (closed on the owner's instruction on 2026-09-07 after each
head — `26386914`, `55ed6d9a`, `62ba0162` — was confirmed reachable from `main`
through #435; they remain review records); deleting `origin/codex/cleanup`; the first review's seven
workflow recommendations; CONC-6 and the probe-descriptor lifetime in
`orchestrator/recording.py` (`post-merge-plan.md:84`); and the adopting record
for evidence reasoning v2 (`post-merge-plan.md:81`). Each remains outstanding
and none is ruled on by this memo.
