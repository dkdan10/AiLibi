# How a change gets in

Choose the next change from evidence, verify it, and let the result choose what
follows. [AGENTS.md](../AGENTS.md) carries the standing rules and
[architecture.md](architecture.md) the system boundaries. The
[task index](../process/tasks/README.md) names current work and the next
candidates; only work ready to start receives a detailed card. Phase contracts
and past audits under `process/` are historical records and are never
rewritten.

## One card per change

A new task lives at `process/tasks/work/<slug>.md`. That file is the canonical
contract: dispatch it by path instead of copying it into a prompt or an issue,
and link longer evidence or design discussion rather than repeating it.

A card has one `#` title, a `**Status:**` of `ready`, `active` or `done`, and
these sections:

| Section | Content |
| --- | --- |
| Outcome | The observable problem to resolve and the resulting behavior. |
| Evidence | A reproducible case and relevant source or decision links. |
| Acceptance | Checkboxes describing success and a meaningful adverse case. |
| Constraints | Non-goals, protected decisions, prerequisites and any authorized run budget. |
| Expected scope | Likely files and the boundaries of permitted follow-through. |
| Record impact | Effects on future behavior, recorded bytes, compatibility and evaluation. |
| Validation | Commands that establish acceptance, including the full project check. |

A completed card adds `## Results` with the verification evidence and material
limitations. Implementation detail belongs in the code, and durable decisions in
the architecture or a decision record. `scripts/validate_task_docs.py`, part of
the gate, checks each card's structure and the index's card counts.

Track delivery states separately, in Results and the
[review ledger](../process/tasks/review-ledger.md):

| State | Evidence required |
| --- | --- |
| Implemented | A focused commit containing the change and its card. |
| Verified | Acceptance checks and the combined project gate passed on the implementation. |
| Independently reviewed | Another agent attempted adverse cases and resolved any blocking findings. |
| Owner reviewed | The owner's final Claude review and any resulting fixes are recorded. |
| Merged | The actual merge into main exists; pushing cleanup does not qualify. |
| Adopted | A behavior experiment's decision and adopting record exist; implementation or a green test alone does not qualify. |

A card's `Status` is its work state, not a claim that all six delivery states
occurred. A repair with no experimental behavior records adoption as "not
applicable".

## Discover, implement, verify

1. **Ready:** the outcome is understood, prerequisites are available, and the
   owner has authorized the scope. Reproduce the failure, inspect current
   consumers, and choose an implementation before editing. Update the card if
   discovery changes the expected files; ask for an unresolved protected
   decision before dependent work.
2. **Active:** implement one coherent change with relevant tests and the
   directly necessary follow-through [AGENTS.md](../AGENTS.md) permits,
   recorded in Results. Anything beyond it needs authorization.
3. **Done:** acceptance is demonstrated, the required checks pass, and Results
   records the evidence. Done means locally verified and ready for review, not
   merged, deployed or adopted.

Do not tick an acceptance item merely because its implementation exists. A new
invariant gate needs a planted or perturbed failure proving it detects the
claimed defect. Reopen a done card if verification or review reveals unfinished
work.

## Environment and history

Run `bash scripts/setup_env.sh` in a fresh checkout. It installs the Python
environment with the `dev` dependency group, which holds the gate's tools, and
the frontend packages; a plain `uv sync --no-dev` deliberately leaves the tools
out. Make an intentional dependency change with `uv add` or `uv lock` and commit
the project metadata with the lockfile.

Checks never reach the network: tests use the deterministic fake provider, and
real-provider tests are opt-in behind the environment gates in
[llm/README.md](../llm/README.md).

Before a claim derived from history, check
`git rev-parse --is-shallow-repository`. A shallow clone needs
`git fetch --unshallow` or an equivalent full fetch; never read a truncated log
as the complete project history.

## The local gate

`bash scripts/check.sh` is the required gate and the one-command local truth:
ruff and its formatter, import-linter, the task-card and link checks, strict
mypy, pytest across one worker per core, and the frontend's lint, typecheck,
unit-test and build legs. Targeted `uv run ...` commands are fine while
iterating; a change is not done until the whole script is green.

CI adds one check the script leaves out, because it needs a browser and both dev
servers: a Playwright journey over the real app and API (the `frontend-e2e` job
in `.github/workflows/ci.yml`). To run it locally:

```bash
cd frontend
npx playwright install chromium   # once per Playwright version
npm run e2e
```

Neither the script nor CI's per-change jobs run the campaign tier, the frozen
ML-campaign families selected with `uv run pytest -m campaign`.
`.github/workflows/campaign-tier.yml` runs it weekly on `main` and on every pull
request that changes `tests/training/**`. A change to a campaign-tier file
records the campaign count in its pull request and Results: from that
workflow's run at the exact head, cited by run id, or from
`uv run pytest -m campaign` when no run exists.

## Branch and delivery

Implementation for a card happens on a short-lived branch named
`work/<card-slug>` and reaches `main` through one pull request per card. CI runs
on every pull request and every push to `main`. Delete the branch after the
merge; its commits stay reachable from `main`.

Planning and contract documents (plans, indexes, ledgers, checkpoints and
records) change no behavior and may land on `main` directly as `docs:` or
`coordination:` commits, carrying the pull request's evidence in the card's
Results instead.

Include the card path in the commit body, so a reviewer can find the contract
from the commit and the implementation with `git log -- <card-path>`. Preserve
published history: merge or fast-forward, never a squash that orphans a commit
another document cites, and never amend a published commit.

A merge into `main` also publishes. `.github/workflows/pages.yml` rebuilds the
demo bundle on every push to `main`, so a change to the viewer, the featured
games or the public-results payload is a publication decision as well as a
merge ([deployment.md](deployment.md)). Task completion never authorizes a
deployment or an experimental adoption.

## GitHub operations

Dispatch environments provision different GitHub integrations, so detect what
is available. If the `gh` CLI is present and authenticated
(`which gh && gh auth status`), use it; otherwise use the environment's GitHub
integration, such as the `mcp__github__*` tools. Try both before declaring
GitHub work impossible.

Every pull request, card-driven or not, fills each section of
[the template](../.github/pull_request_template.md):

- **Summary:** what changed and why, the card path, and each material decision
  made without the owner.
- **Acceptance:** the card's checklist, each item ticked against its evidence;
  without a card, the scope actually executed.
- **Verification:** the commands run and their results, including the full gate.
- **Record impact:** effects on recordings, compatibility and evaluation, or
  "None".
- **Limitations:** what remains unproven, and any blocking question for the
  owner.

Pass the populated body explicitly, with `gh pr create --body-file <file>` or
the body parameter of the integration's create call. An explicit body replaces
the repository template, so it must carry every section itself; `--fill`,
`--body ""` and an omitted body ship an empty description and are not
permitted.

## Coordinate and review

Keep the active queue to the available workers and the next few candidates in
the task index, scheduled by hand; write the next card once its dependencies and
evidence are clear, and declare semantic prerequisites in Constraints. Assign
one writer per file at a time, with isolated worktrees where independent
investigation or review helps. Investigation, test design and review can run
alongside implementation.

A reviewer attempts the adverse case and inspects the failure paths rather than
repeating the implementer's summary. Keep engine truth, agent-visible
information and model inference distinct, and human decisions about game rules
and experimental adoption explicit.

## Records and experiments

Every card declares record impact, including a repair that changes future
failure handling without changing committed recordings, and uses the existing
replay stamps, manifests and experiment switches.

For a behavior experiment, specify the hypothesis, inputs, comparison,
measurement and decision rule before the evaluation that decides adoption;
development cases can inform that rule but are not independent confirmation.
Inspect existing candidates and prior findings before creating another variant,
freeze development and held-out inputs before evaluating one, and record
negative results and stop rules as carefully as apparent improvements. A later
experiment never changes an earlier verdict.

For gameplay experiments and release reviews, one reviewer writes a
gameplay-first assessment from viewed or reconstructed games before reading the
implementation, and another writes the code-first assessment independently.
Preserve both before their synthesis, and label mechanism checks,
recorded-model analysis and fresh-model evaluation separately. Fake-provider
games establish mechanics, not reasoning quality.

A live-provider run needs an authorized provider and explicit token, wall-time
and cost limits, with a cost statement even for flat-rate service. Each
experiment needs a decision point and a retirement condition: adoption deletes
the switch, as the next section describes, and rejection deletes the candidate
unless an authorized comparison still needs it. Keep the recorded evidence and
its provenance.

## Retiring substrate levers

When a substrate lever graduates (its `AILIBI_*` gate retired and its behavior
unconditional, normally at an adopting baseline record), **delete the
mechanism, keep the stamp key and one history line.**

What goes: the `*_enabled()` resolver, the `ENV_*` constant and its `__all__`
entry, the `env` parameter wherever no live resolver is reachable from that call
chain, every `if <lever>_enabled():` guard (replaced by its always-taken side),
and the tests that pin the parameter rather than the behavior.

What stays: the lever's snake_case key in
`orchestrator/replay.py::_RETIRED_ALWAYS_ON_LEVERS`, so a recording keeps
describing the substrate that produced it and the loader can still refuse a
legacy stamp that recorded it OFF, plus at most one trailing provenance line
naming the adopting record.

Then sweep the prose. Grep the lever's name repo-wide and rewrite every
docstring, comment and doc line that still describes it as live or default-OFF,
and move it into the graduated note in `.env.example`, which
`scripts/check_doc_facts.py` holds to the registry. `_RETIRED_ALWAYS_ON_LEVERS`
and `_TOGGLEABLE_LEVER_RESOLVERS` in `orchestrator/replay.py` are the source of
truth for which levers still switch, and `tests/meetings/test_lever_registry.py`
fails on any `*_enabled` function under `agents/`, `meetings/` or
`orchestrator/` that neither reads its `env` argument nor returns anything but a
bare `True`.
