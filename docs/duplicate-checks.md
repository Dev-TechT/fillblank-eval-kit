# Duplicate and near-duplicate checks

Use this gate when adding or reviewing public sample/dev rows or private quarantine candidates.

## Command

```bash
uv run python -m fillblank_eval.duplicates examples/public_sample.jsonl examples/public_dev.jsonl examples/public_top10_sample.jsonl
```

For private/off-repo candidate files:

```bash
uv run python -m fillblank_eval.duplicates --allow-private /path/to/quarantine_candidates.jsonl
```

## Behavior

Blocking errors:

- duplicate IDs;
- exact normalized prompt duplicates in the same language;
- invalid dataset rows.

Warnings:

- near-duplicate prompts in the same language and construct.

Run with `--show-warnings` to inspect warning details.

## Why this matters

Benchmarks become easier to game and less informative when many rows are tiny paraphrases of the same prompt. Duplicate checks do not replace human review, but they catch obvious mistakes before review time.
