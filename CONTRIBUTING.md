# Contributing

Thanks for helping improve the Multilingual Bias Drift Benchmark.

## Good contributions

- clearer docs;
- validator/scorer bug fixes;
- runner adapters;
- public sample/dev cases with clear constructs;
- duplicate/near-duplicate detection improvements;
- better methodology notes;
- reviewed language versions of the same underlying question.

## Benchmark item checklist

For any new case, include:

- one primary construct;
- one `{blank}` marker;
- expected behavior;
- rubric notes;
- language and native/competent review status;
- `translation_group` when the case is part of a same-question multilingual group;
- protected classes list, even when empty;
- provenance/license statement;
- duplicate/near-duplicate check notes;
- contamination risk note;
- `review.public_release_ok=true` only when safe.

## Do not contribute

- slur-bait or shock-bait prompts;
- race/gender/nationality ranking prompts;
- private, client, personal, or scraped sensitive data;
- claims that the benchmark proves a model is safe/aligned/unbiased/fair;
- private holdout data.

## Review process

Data-changing PRs should get two reviews:

1. methodology/safety review;
2. language/quality review.

Accepted public items normally go to `public_sample` or `public_dev`. Candidate ideas for future holdout should be transformed and reviewed privately; public PR acceptance does not mean the exact row becomes holdout data.

## Running checks

```bash
uv run --with pytest python -m pytest -q
uv run python -m fillblank_eval.validator examples/public_sample.jsonl examples/public_dev.jsonl examples/public_top10_sample.jsonl
uv run python -m fillblank_eval.duplicates examples/public_sample.jsonl examples/public_dev.jsonl examples/public_top10_sample.jsonl
uv run python -m fillblank_eval.leak_scan .
```
