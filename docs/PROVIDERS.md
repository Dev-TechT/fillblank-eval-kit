# Provider setup

`fillblank-run` runs the public fill-in-the-blank benchmark splits against either a credential-free mock provider or an OpenAI-compatible chat completions API.

The runner is provider-agnostic at the result/report layer, but the first real provider transport is OpenAI-compatible `/chat/completions`.

## Credential-free smoke run

Use this first after cloning:

```bash
uv run fillblank-run --dry-run --limit 5 --out-dir runs/mock-smoke
```

Expected artifacts:

- `runs/mock-smoke/results.jsonl` — one machine-readable row per case;
- `runs/mock-smoke/summary.json` — aggregate machine-readable summary;
- `runs/mock-smoke/report.md` — human-readable report;
- `runs/mock-smoke/report.html` — browser-readable report.

The mock provider does not call a network service and does not need credentials. Its scores are only a pipeline smoke test, not model evidence.

## Default public split

Without `--dataset`, the runner evaluates these public files:

- `examples/public_sample.jsonl`
- `examples/public_dev.jsonl`
- `examples/public_top10_sample.jsonl`

The top-10-language file is a small translation-assisted smoke sample. Its rows share a `translation_group`, so reports include a parallel-language summary for checking whether the same model behaves differently on the same underlying question across languages. Treat this as runner/scorer diagnostics, not native-reviewed language evidence.

## Private/off-repo validation

The validator schema also recognizes private/off-repo tier names (`private_holdout`, `quarantine_candidates`, `retired_holdout`) so maintainers can validate local private files with `--allow-private`. Those rows must not be added to public dataset files or public CI artifacts.

## OpenAI-compatible provider

Set environment variables, then run the public split:

```bash
export FILLBLANK_PROVIDER=openai-compatible
export FILLBLANK_BASE_URL=https://api.openai.com/v1
export FILLBLANK_API_KEY=sk-...
export FILLBLANK_MODEL=gpt-4o-mini

uv run fillblank-run --out-dir runs/openai-compatible-public
```

Equivalent generic OpenAI-style names are also read when the `FILLBLANK_*` variables are absent:

```bash
export OPENAI_BASE_URL=https://api.openai.com/v1
export OPENAI_API_KEY=sk-...
export OPENAI_MODEL=gpt-4o-mini
uv run fillblank-run --provider openai-compatible --out-dir runs/provider-public
```

Useful options:

```bash
uv run fillblank-run \
  --provider openai-compatible \
  --base-url "$FILLBLANK_BASE_URL" \
  --model "$FILLBLANK_MODEL" \
  --limit 10 \
  --timeout-seconds 90 \
  --out-dir runs/smoke-real-provider
```

## Secrets and raw responses

Do not commit `.env` files, API keys, raw provider logs, or private holdout outputs.

By default, `results.jsonl` stores the evaluated prompt text and model output text, but not raw provider JSON. The optional `--include-raw-response` flag is for local debugging only; avoid it when provider responses or metadata might contain sensitive data.

## Public/private split boundary

The public runner validates datasets in public mode before running. It rejects rows with private tiers such as `private_holdout`, `quarantine_candidates`, or `retired_holdout`.

Private holdout rows and quarantine candidates must stay off-repo and out of public CI artifacts. If you build a maintainer-only private workflow later, keep its data paths outside this repository and publish only aggregate, reviewed summaries.
