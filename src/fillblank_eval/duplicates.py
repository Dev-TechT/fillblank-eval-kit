from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from .validator import PUBLIC_CAVEAT, _load_jsonl, validate_dataset

_WORD_RE = re.compile(r"[\w{}]+", re.UNICODE)


@dataclass(frozen=True)
class DuplicateFinding:
    kind: str
    severity: str
    case_ids: tuple[str, str]
    message: str
    similarity: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "severity": self.severity,
            "case_ids": list(self.case_ids),
            "message": self.message,
            "similarity": self.similarity,
        }


@dataclass(frozen=True)
class DuplicateCheckResult:
    ok: bool
    findings: list[DuplicateFinding]
    case_count: int
    error_count: int
    warning_count: int

    def to_dict(self, *, include_warnings: bool = True) -> dict[str, Any]:
        findings = self.findings if include_warnings else [finding for finding in self.findings if finding.severity == "error"]
        return {
            "ok": self.ok,
            "case_count": self.case_count,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "findings": [finding.to_dict() for finding in findings],
            "caveat": PUBLIC_CAVEAT,
        }


def normalize_prompt(prompt: str) -> str:
    """Normalize prompt text for deterministic duplicate detection."""
    tokens = _WORD_RE.findall(prompt.casefold())
    return " ".join(tokens)


def token_set(prompt: str) -> set[str]:
    return set(normalize_prompt(prompt).split())


def jaccard_similarity(left: str, right: str) -> float:
    left_tokens = token_set(left)
    right_tokens = token_set(right)
    if not left_tokens and not right_tokens:
        return 1.0
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)


def _pairs(rows: list[dict[str, Any]]) -> Iterable[tuple[dict[str, Any], dict[str, Any]]]:
    for index, left in enumerate(rows):
        for right in rows[index + 1 :]:
            yield left, right


def _case_id(row: dict[str, Any]) -> str:
    value = row.get("id")
    return value if isinstance(value, str) else "<missing-id>"


def check_duplicates(paths: list[str | Path], *, near_threshold: float = 0.82, public_mode: bool = True) -> DuplicateCheckResult:
    """Check one or more JSONL case files for duplicate and near-duplicate rows.

    Blocking errors:
    - duplicate IDs;
    - exact normalized prompt duplicates in the same language.

    Non-blocking warnings:
    - near-duplicate prompts with same language and construct.
    """
    if not 0.0 < near_threshold <= 1.0:
        raise ValueError("near_threshold must be in the interval (0.0, 1.0]")

    rows: list[dict[str, Any]] = []
    findings: list[DuplicateFinding] = []

    for path in paths:
        rows_for_path, parse_errors = _load_jsonl(Path(path))
        if parse_errors:
            for error in parse_errors:
                findings.append(DuplicateFinding(
                    kind="invalid_dataset",
                    severity="error",
                    case_ids=(str(path), str(path)),
                    message=error,
                ))
            continue
        rows.extend(rows_for_path)

        validation = validate_dataset(path, public_mode=public_mode)
        if not validation.ok:
            duplicate_id_errors = [error for error in validation.errors if "duplicate id" in error]
            other_errors = [error for error in validation.errors if "duplicate id" not in error]
            for error in duplicate_id_errors:
                findings.append(DuplicateFinding(
                    kind="duplicate_id",
                    severity="error",
                    case_ids=(str(path), str(path)),
                    message=error,
                ))
            for error in other_errors:
                findings.append(DuplicateFinding(
                    kind="invalid_dataset",
                    severity="error",
                    case_ids=(str(path), str(path)),
                    message=error,
                ))
            if other_errors:
                continue

    ids: dict[str, list[dict[str, Any]]] = defaultdict(list)
    prompts: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)

    for row in rows:
        ids[_case_id(row)].append(row)
        prompt = row.get("prompt_template")
        language = row.get("language")
        if isinstance(prompt, str) and isinstance(language, str):
            prompts[(language, normalize_prompt(prompt))].append(row)

    for case_id, matches in ids.items():
        if len(matches) > 1:
            first, second = matches[0], matches[1]
            findings.append(DuplicateFinding(
                kind="duplicate_id",
                severity="error",
                case_ids=(_case_id(first), _case_id(second)),
                message=f"Duplicate case id {case_id!r}",
            ))

    for (language, normalized), matches in prompts.items():
        if len(matches) > 1:
            first, second = matches[0], matches[1]
            findings.append(DuplicateFinding(
                kind="exact_prompt_duplicate",
                severity="error",
                case_ids=(_case_id(first), _case_id(second)),
                message=f"Exact normalized prompt duplicate in language {language!r}: {normalized!r}",
                similarity=1.0,
            ))

    for left, right in _pairs(rows):
        if left.get("language") != right.get("language"):
            continue
        if left.get("construct") != right.get("construct"):
            continue
        left_prompt = left.get("prompt_template")
        right_prompt = right.get("prompt_template")
        if not isinstance(left_prompt, str) or not isinstance(right_prompt, str):
            continue
        if normalize_prompt(left_prompt) == normalize_prompt(right_prompt):
            continue
        similarity = jaccard_similarity(left_prompt, right_prompt)
        if similarity >= near_threshold:
            findings.append(DuplicateFinding(
                kind="near_prompt_duplicate",
                severity="warning",
                case_ids=(_case_id(left), _case_id(right)),
                message=(
                    f"Near-duplicate prompt candidate in language {left.get('language')!r}, "
                    f"construct {left.get('construct')!r}: similarity={similarity:.3f}"
                ),
                similarity=round(similarity, 3),
            ))

    error_count = sum(1 for finding in findings if finding.severity == "error")
    warning_count = sum(1 for finding in findings if finding.severity == "warning")
    return DuplicateCheckResult(
        ok=error_count == 0,
        findings=findings,
        case_count=len(rows),
        error_count=error_count,
        warning_count=warning_count,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check fillblank JSONL case files for duplicates and near-duplicates.")
    parser.add_argument("paths", nargs="+", help="JSONL files to check")
    parser.add_argument("--near-threshold", type=float, default=0.82, help="Jaccard warning threshold for near-duplicates")
    parser.add_argument("--allow-private", action="store_true", help="Allow private tiers while checking private/off-repo data")
    parser.add_argument("--show-warnings", action="store_true", help="Include near-duplicate warning details in JSON output")
    args = parser.parse_args(argv)
    result = check_duplicates(args.paths, near_threshold=args.near_threshold, public_mode=not args.allow_private)
    print(json.dumps(result.to_dict(include_warnings=args.show_warnings), ensure_ascii=False, indent=2))
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
