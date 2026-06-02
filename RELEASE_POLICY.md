# Release Policy

## Before any public release

Run:

```bash
uv run --with pytest python -m pytest -q
uv run python -m fillblank_eval.validator examples/public_sample.jsonl examples/public_dev.jsonl examples/public_top10_sample.jsonl
uv run python -m fillblank_eval.duplicates examples/public_sample.jsonl examples/public_dev.jsonl examples/public_top10_sample.jsonl
uv run python -m fillblank_eval.leak_scan .
```

Also verify:

- no private holdout rows in repo history or build artifacts;
- no private model outputs/logs in CI artifacts;
- README and docs keep narrow claims;
- data/scorer/runner versions are recorded;
- known limitations are included.

## Versioning

Use semantic-ish versions:

- patch: docs/tests/tooling fixes that do not change benchmark behavior;
- minor: new public examples, new runner adapters, rubric clarifications;
- major: scoring, schema, or construct changes that affect comparability.

## Leaderboards

Do not launch a public leaderboard from the current public examples alone.

A responsible leaderboard needs:

- enough cases per construct/language;
- stable private holdout;
- no per-sample feedback leakage;
- submission limits;
- clear data/scorer versioning;
- methodology review.

## Hugging Face publication

If publishing to Hugging Face:

- publish public sample/dev only;
- dataset card must say this is not a hidden benchmark;
- avoid uploading private split names/files;
- remember that gated datasets are controlled sharing, not a true hidden holdout.
