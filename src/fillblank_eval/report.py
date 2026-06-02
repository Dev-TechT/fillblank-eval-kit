from __future__ import annotations

from .scorer import score_outputs
from .validator import PUBLIC_CAVEAT


def build_markdown_report(result: dict) -> str:
    lines = [
        "# Fillblank eval report",
        "",
        f"Caveat: {PUBLIC_CAVEAT}",
        f"Public claim ready: `{str(result.get('public_claim_ready', False)).lower()}`",
        "",
        "## Summary",
    ]
    summary = result.get("summary") or {}
    for key in ["case_count", "mean_score", "unsupported_assumption", "harmful_generalization", "essentialism", "uncertainty_preserved", "over_refusal"]:
        lines.append(f"- {key.replace('_', ' ')}: {summary.get(key, 0)}")
    if result.get("errors"):
        lines.extend(["", "## Errors"])
        lines.extend(f"- {error}" for error in result["errors"])
    lines.extend(["", "## Cases"])
    for case in result.get("case_results") or []:
        lines.extend([
            f"### {case.get('case_id')}",
            f"Language: `{case.get('language')}`",
            f"Construct: `{case.get('construct')}`",
            f"Score: `{case.get('score')}`",
            f"Rationale: {case.get('rationale')}",
            "",
        ])
    return "\n".join(lines).rstrip() + "\n"


def build_report_for_outputs(dataset_path: str, outputs: dict[str, str]) -> str:
    return build_markdown_report(score_outputs(dataset_path, outputs))
