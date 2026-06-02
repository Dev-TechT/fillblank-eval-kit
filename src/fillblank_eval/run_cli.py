from __future__ import annotations

import argparse
import os
from pathlib import Path

from .provider_client import ProviderError
from .runner import RunnerConfig, run_benchmark


DEFAULT_PUBLIC_DATASETS = [Path("examples/public_sample.jsonl"), Path("examples/public_dev.jsonl")]


def _env(name: str, default: str | None = None) -> str | None:
    value = os.environ.get(name)
    return value if value not in {None, ""} else default


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run public fillblank benchmark cases against a provider/model.")
    parser.add_argument("--dataset", action="append", type=Path, help="Public JSONL dataset path; can be repeated")
    parser.add_argument("--out-dir", type=Path, default=Path("runs/fillblank-public"), help="Directory for results.jsonl, summary.json, report.md, report.html")
    parser.add_argument("--provider", default=_env("FILLBLANK_PROVIDER", "mock"), help="Provider: mock or openai-compatible")
    parser.add_argument("--base-url", default=_env("FILLBLANK_BASE_URL") or _env("OPENAI_BASE_URL"), help="OpenAI-compatible base URL, e.g. https://api.openai.com/v1")
    parser.add_argument("--api-key", default=_env("FILLBLANK_API_KEY") or _env("OPENAI_API_KEY"), help="API key; prefer environment variables over shell history")
    parser.add_argument("--model", default=_env("FILLBLANK_MODEL") or _env("OPENAI_MODEL") or "mock-model", help="Model name")
    parser.add_argument("--temperature", type=float, default=float(_env("FILLBLANK_TEMPERATURE", "0") or 0))
    parser.add_argument("--max-tokens", type=int, default=int(_env("FILLBLANK_MAX_TOKENS", "256") or 256))
    parser.add_argument("--timeout-seconds", type=int, default=int(_env("FILLBLANK_TIMEOUT_SECONDS", "60") or 60))
    parser.add_argument("--limit", type=int, default=None, help="Optional first-N case limit for smoke tests")
    parser.add_argument("--include-raw-response", action="store_true", help="Include raw provider JSON in results.jsonl; avoid when responses may contain sensitive data")
    parser.add_argument("--dry-run", action="store_true", help="Force credential-free mock provider")
    args = parser.parse_args(argv)

    provider = "mock" if args.dry_run else args.provider
    model = "mock-model" if args.dry_run else args.model
    config = RunnerConfig(
        dataset_paths=args.dataset or DEFAULT_PUBLIC_DATASETS,
        out_dir=args.out_dir,
        provider=provider,
        base_url=args.base_url,
        api_key=args.api_key,
        model=model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        timeout_seconds=args.timeout_seconds,
        limit=args.limit,
        include_raw_response=args.include_raw_response,
    )
    try:
        result = run_benchmark(config)
    except ProviderError as exc:
        print(f"Provider error: {exc}")
        return 2
    if result.ok:
        print(f"OK: wrote {args.out_dir / 'results.jsonl'}")
        print(f"OK: wrote {args.out_dir / 'summary.json'}")
        print(f"OK: wrote {args.out_dir / 'report.md'}")
        print(f"OK: wrote {args.out_dir / 'report.html'}")
        return 0
    print("FAILED")
    for error in result.errors:
        print(f"- {error}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
