# Check exact artifact sizes and actual Markdown links

**Status:** done

## Outcome

Artifact inventory verification detects byte drift even when file counts stay
constant. Documentation link validation checks rendered links, excluding code
examples that merely demonstrate Markdown syntax.

## Evidence

The phase-21 close's F1 and F2 identify these independent semantic holes:
`relative_targets` scans inline/fenced code, while `inventory_problems` checks
file counts but never compares exact stated byte counts. Both mechanisms are
used by the required offline checks.

## Acceptance

- [x] Exact `tracked bytes` claims are compared with the named tracked files'
  actual bytes; approximations retain their stated approximate meaning.
- [x] A one-byte drift with unchanged file count makes availability fail.
- [x] Real broken links fail while inline/fenced code examples are ignored,
  including different fence lengths and multiline code spans.
- [x] Current artifact inventory and affected documentation checks pass,
  including the combined project gate.

## Constraints

Follow `docs/architecture.md` Packages. Preserve historical audit/record bytes.
This is part of roadmap item 38, not a claim that every carried finding is now
closed. No new online checks or simulation behavior changes. Use the already
locked CommonMark parser as a declared dev dependency for actual link parsing.

## Expected scope

`scripts/check_doc_facts.py`, `scripts/verify_ml_evidence.py`, their focused
tests, directly necessary `docs/artifacts.md` inventory refresh,
`pyproject.toml` / `uv.lock` for the parser's direct dev declaration, and this card.
Root owns these files while other agents edit application consumers.

## Record impact

None. These gates check published evidence without rewriting recordings.

## Validation

Run affected script tests, planted adverse cases against the original gate,
ruff/format/mypy, `python scripts/check_doc_facts.py`, and the combined
`bash scripts/check.sh`. Inventory checks use staged paths and on-disk bytes;
new evidence files must be staged before final verification.

## Results

Exact byte totals now compare against the tracked files' byte lengths. The
original gate failed eight planted cases: seven Markdown code examples and a
one-byte stated-size drift with the file count unchanged. The inventory gate
then detected a real 327-byte extractor change; the current inventory records
8,644,570 tracked audit bytes and the added media provenance file.

Independent review found a false negative in the first regex repair: matching
backticks across paragraphs hid real links. The final implementation uses
CommonMark's block and inline tokens and deletes the masking mechanism. It also
checks reference links, image targets, escaped paths, and blockquoted/indented
code correctly. `markdown-it-py==4.0.0` was already locked through Rich; declaring
it directly in the dev group with `uv add --dev ... --offline` adds no installed
package or version. Seventeen focused link cases pass, including the reviewer's
cross-paragraph/heading adverse cases and paired real-link controls.

The independent reviewer approved byte semantics, including a non-ASCII
three-byte file, missing tracked files, and approximate-size controls. All
current published-document facts pass. Final parser review and combined project verification passed, as recorded below. This repairs only the two
named mechanisms; remaining audit findings keep their separate disposition.

### Combined verification and review

The final `bash scripts/check.sh` run passed: 6,409 Python tests (20 optional
skips, three expected failures), 455 frontend tests, strict typing, lint,
formatting, import boundaries, 390 historical contracts/prompts, and the build.
`bash scripts/verify_samples.sh` verified all 100 canonical recordings. No
canonical recording or historical report bytes changed. Logs: `/tmp/ailibi-cleanup-
batch2-check-final.log` and `/tmp/ailibi-cleanup-batch2-samples.log`.

Independent review: Code-review agent; exact-byte adverse cases and final CommonMark token parser independently checked.
Implemented and verified for cleanup; the owner's final Claude review and merge
remain pending. This work does not adopt an experimental behavior.
