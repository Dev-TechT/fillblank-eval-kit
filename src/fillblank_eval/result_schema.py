from __future__ import annotations

from typing import Any

REQUIRED_RESULT_ROW_FIELDS = {
    "case_id",
    "tier",
    "language",
    "translation_group",
    "construct",
    "phenomenon",
    "control_type",
    "score",
    "labels",
    "rationale",
    "provider",
    "model",
    "prompt",
    "output_text",
}

REQUIRED_SUMMARY_FIELDS = {
    "ok",
    "errors",
    "provider",
    "model",
    "dataset_paths",
    "parallel_groups",
    "summary",
    "progress_events",
    "breakdowns",
    "case_results",
    "public_claim_ready",
    "caveat",
    "interpretation",
}


def validate_result_row(row: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in sorted(REQUIRED_RESULT_ROW_FIELDS):
        if field not in row:
            errors.append(f"missing required field: {field}")
    if "case_id" in row and not isinstance(row["case_id"], str):
        errors.append("case_id must be a string")
    if "translation_group" in row and row["translation_group"] is not None and not isinstance(row["translation_group"], str):
        errors.append("translation_group must be a string or null")
    if "score" in row and row["score"] is not None and row["score"] not in {0, 1, 2, 3}:
        errors.append("score must be one of 0, 1, 2, 3 or null for failed rows")
    if "labels" in row and not isinstance(row["labels"], dict):
        errors.append("labels must be an object")
    if "output_text" in row and not isinstance(row["output_text"], str):
        errors.append("output_text must be a string")
    return errors


def validate_run_summary(summary: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in sorted(REQUIRED_SUMMARY_FIELDS):
        if field not in summary:
            errors.append(f"missing required field: {field}")
    if summary.get("public_claim_ready") is not False:
        errors.append("public_claim_ready must be false for this public kit")
    aggregate = summary.get("summary")
    if isinstance(aggregate, dict):
        for field in ["case_count", "completed_count", "error_count", "mean_score"]:
            if field not in aggregate:
                errors.append(f"summary missing required field: {field}")
    elif "summary" in summary:
        errors.append("summary must be an object")
    breakdowns = summary.get("breakdowns")
    if isinstance(breakdowns, dict):
        for field in ["by_language", "by_construct", "by_control_type"]:
            if field not in breakdowns:
                errors.append(f"breakdowns missing required field: {field}")
    elif "breakdowns" in summary:
        errors.append("breakdowns must be an object")
    if "parallel_groups" in summary and not isinstance(summary["parallel_groups"], list):
        errors.append("parallel_groups must be a list")
    return errors
