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
- private holdout rows, raw model/provider logs, credentials, or private reviewer notes;
- claims that the benchmark proves a model is safe/aligned/unbiased/fair;
- model leaderboard, winner, compliance, or production-readiness claims;
- private holdout data.

## Contribution and task templates

Use the focused GitHub templates so issues stay small and public-safe:

- Public case proposals: `.github/ISSUE_TEMPLATE/case-proposal.yml`
- Agent-friendly adapter/reporting/tooling tasks: `.github/ISSUE_TEMPLATE/agent-task.yml`
- Validator/adapter bug reports: `.github/ISSUE_TEMPLATE/bug.yml`
- Pull request checklist: `.github/pull_request_template.md`

For coding-agent tasks, include a narrow goal, explicit scope/non-goals, acceptance criteria, verification commands, and the privacy/claim boundary. Do not post private/client data or unsupported model claims in issue bodies, PR bodies, logs, screenshots, or artifacts.

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
