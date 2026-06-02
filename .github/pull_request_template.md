## Summary

## Type of change

- [ ] Documentation
- [ ] Validator/scorer code
- [ ] Public sample/dev data
- [ ] Adapter/reporting/tooling
- [ ] GitHub/contributor workflow
- [ ] Other

## Benchmark/data checklist

- [ ] No private/client data, private holdout rows, prompts, answer keys, raw provider outputs, model logs, credentials, or private reviewer notes are included.
- [ ] Any new case has exactly one `{blank}` marker.
- [ ] Any new case names one primary construct.
- [ ] Any new case includes provenance/license/review notes.
- [ ] No unsupported model claims are added; public claims remain narrow, with no model-safety, alignment, unbiasedness, fairness, compliance, or production-readiness proof claims.
- [ ] No public leaderboard or ranking claim is added.
- [ ] No real provider/client output artifacts are committed.
- [ ] Private/client/holdout work remains off-repo and approval-gated.

## Verification

Paste commands and results. Use the commands relevant to your change; keep skipped checks explicit.

```bash
uv run --with pytest python -m pytest -q
uv run python -m fillblank_eval.validator examples/public_sample.jsonl examples/public_dev.jsonl examples/public_top10_sample.jsonl
uv run python -m fillblank_eval.duplicates examples/public_sample.jsonl examples/public_dev.jsonl examples/public_top10_sample.jsonl
uv run python -m fillblank_eval.leak_scan .
```

## Notes for reviewers

- If this changes public data, check duplicate/near-duplicate findings and language/review status.
- If this changes reports/adapters, check failed-row visibility and claim-boundary caveats.
- If this changes provider behavior, confirm private/client outputs cannot land in public repo artifacts.
