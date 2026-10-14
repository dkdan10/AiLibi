# Contributing

Read this before opening anything. The short version: **issues are welcome;
pull requests from outside the project are not merged.**

## Why outside pull requests are not merged

Every coding change here is written by an AI coding agent working against a
task contract the owner has authorized. CI is the gate, separate AI reviewers
check each change, and the owner decides what is accepted and published. The
contract, not this file and not a conversation on a pull request, is the
specification the agent sees.

So there is no review lane for unsolicited code. A drive-by pull request has no
contract behind it, no authorized scope and no reviewer budget. It will not be
merged, and saying so up front is fairer than leaving one open.

## What is welcome

**Issues.** Bug reports, reproductions, questions about the architecture, and
"this claim in the docs does not match the code" findings are all useful, the
last especially: a stale number or a docstring that contradicts the bytes is
exactly what the internal audits look for. A good issue says what you observed,
what you expected and how to reproduce it; for a specific claim, quote the file
and line.

**Forks.** The license is MIT (see [LICENSE](LICENSE)). Fork it, take it apart,
build something else with it. No permission needed.

**Security reports** go through [SECURITY.md](SECURITY.md), not the issue
tracker.

## Read these first

1. [README.md](README.md): what the project is, what the recordings show, and
   how to install and verify it offline.
2. [docs/architecture.md](docs/architecture.md): the current architecture and
   its enforced boundaries.
3. [docs/workflow.md](docs/workflow.md): how a change gets in, from task card to
   local gate to pull request.
4. [AGENTS.md](AGENTS.md): the standing rules every agent working here follows.
