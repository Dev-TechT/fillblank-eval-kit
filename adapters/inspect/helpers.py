from __future__ import annotations

from pathlib import Path
from typing import Any

from fillblank_eval.validator import iter_dataset, validate_dataset

REPO_ROOT = Path(__file__).resolve().parents[2]


def resolve_dataset_path(dataset_path: str | Path) -> Path:
    path = Path(dataset_path)
    if path.exists() or path.is_absolute():
        return path
    repo_relative = REPO_ROOT / path
    if repo_relative.exists():
        return repo_relative
    return path


def load_public_cases(dataset_path: str | Path) -> list[dict[str, Any]]:
    """Validate and load a public fillblank dataset for runner adapters."""
    path = resolve_dataset_path(dataset_path)
    validation = validate_dataset(path, public_mode=True)
    if not validation.ok:
        raise ValueError("Invalid public fillblank dataset: " + "; ".join(validation.errors))
    return list(iter_dataset(path))


def record_to_sample(record: dict[str, Any]) -> dict[str, Any]:
    """Convert one canonical JSONL row to an Inspect-style sample dict."""
    return {
        "input": record["prompt_template"],
        "target": record["expected_behavior"],
        "id": record["id"],
        "metadata": record,
    }
