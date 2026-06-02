# Inspect AI adapter

The Inspect AI adapter is a runnable starter for the public development set.

Important boundaries:

- Use public sample/dev data only unless you are running a private local evaluation.
- Running `inspect eval` with a real provider sends prompts to that provider.
- Do not use this adapter to publish leaderboard/model-safety claims from the public data.

## Smoke checks without model calls

List the task:

```bash
uv run --with inspect-ai inspect list tasks adapters/inspect/fillblank_task.py
```

Expected task:

```text
adapters/inspect/fillblank_task.py@fillblank_public_dev
```

## Local mock run

This uses Inspect AI's mock model and does not call an external model provider:

```bash
uv run --with inspect-ai inspect eval adapters/inspect/fillblank_task.py \
  --model mockllm/model \
  --limit 1 \
  --log-dir /tmp/fillblank-inspect-smoke
```

Expected result: the task runs and writes an Inspect `.eval` log. The mock model score is not meaningful.

## Real model run

Only use public sample/dev data unless you have an approved private local provider path:

```bash
uv run --with inspect-ai inspect eval adapters/inspect/fillblank_task.py \
  --model openai/gpt-4o-mini \
  --limit 10
```

Replace the provider with your approved model/provider. Never paste private holdout rows into public logs or shared screenshots.

## Implementation notes

- `adapters/inspect/helpers.py` is dependency-light and covered by normal tests.
- `adapters/inspect/fillblank_task.py` imports Inspect AI and defines the runnable task.
- The canonical schema, validator, scorer, duplicate check, and leak scan live under `src/fillblank_eval/`.
