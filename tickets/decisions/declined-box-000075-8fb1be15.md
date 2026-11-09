---
id: declined-box-000075-8fb1be15
kind: declined
link: box-000075-8fb1be15
reopen_after_days: 30
---
The eval harness scores a review as catching a planted defect from its verdict alone. Any `snag` or `rma` on a planted fixture counts as a catch, even when the reviewer's findings name a different defect class or file. The suggestion is for GO grading to also require the reviewer's finding to match the planted defect's class or path, so the catch rate is not overstated.

The gap is real but deliberate. The `score` docstring in `eval/harness.py` says 'Verdict-level scoring: snag and rma both count as catching a planted defect'. No evidence shows that it has produced a wrong GO grade. The GO-grade run has already merged (`go-grade-run`, `phase6-exit`), and nothing in the message or the repository shows a fixture that was snagged for an unrelated reason and counted as a catch, or a reviewer that passed `MIN_CATCH_RATE` only because of such snags. Without that, this is a proposal to make the measurement stricter (speculative hardening of an evaluation metric), not a demonstrated harmful runtime behavior. Reopen if a GO-grade or baseline report shows at least one planted fixture counted as caught where the reviewer's findings do not name the planted defect's class or file, especially if removing those catches would drop `catch_rate` below `MIN_CATCH_RATE`.

- eval/harness.py:105-109: `score()` docstring says verdict-level scoring; `caught = [r for r in planted if r.verdict in ("snag", "rma")]` never compares findings with `expected.defect_class` or the diff path
- eval/harness.py:273 and chupa/artifacts.py:515: the GO verdict is gated on `catch_rate >= MIN_CATCH_RATE` and `clean_false_snag <= MAX_FALSE_SNAG_RATE`
- go-grade-machinery, go-grade-run and phase6-exit are merged; no report in the message or the decision registry shows a snag for the wrong reason being counted as a catch
- No open ticket or registry record covers matching findings to the planted defect

Message: box-000075-8fb1be15
