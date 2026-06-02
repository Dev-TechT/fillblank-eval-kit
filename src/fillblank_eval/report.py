from __future__ import annotations

import html
from typing import Any

from .interpretation import build_interpretation
from .scorer import score_outputs
from .validator import PUBLIC_CAVEAT


SUMMARY_KEYS = [
    "case_count",
    "completed_count",
    "error_count",
    "mean_score",
    "unsupported_assumption",
    "harmful_generalization",
    "essentialism",
    "uncertainty_preserved",
    "over_refusal",
]


def _markdown_table(title: str, rows: dict[str, dict[str, Any]]) -> list[str]:
    lines = [f"## {title}", "", "| group | cases | mean score | unsupported | harmful | uncertainty | over-refusal |", "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for group, values in rows.items():
        lines.append(
            "| {group} | {cases} | {mean} | {unsupported} | {harmful} | {uncertainty} | {over_refusal} |".format(
                group=group,
                cases=values.get("case_count", 0),
                mean=values.get("mean_score", 0),
                unsupported=values.get("unsupported_assumption", 0),
                harmful=values.get("harmful_generalization", 0),
                uncertainty=values.get("uncertainty_preserved", 0),
                over_refusal=values.get("over_refusal", 0),
            )
        )
    return lines


def build_markdown_report(result: dict) -> str:
    interpretation = result.get("interpretation") or build_interpretation(result)
    lines = [
        "# Fillblank eval report",
        "",
        f"Provider: `{result.get('provider', 'unknown')}`",
        f"Model: `{result.get('model', 'unknown')}`",
        f"Caveat: {result.get('caveat') or PUBLIC_CAVEAT}",
        f"Public claim ready: `{str(result.get('public_claim_ready', False)).lower()}`",
        "",
        "## Summary",
    ]
    summary = result.get("summary") or {}
    for key in SUMMARY_KEYS:
        lines.append(f"- {key.replace('_', ' ')}: {summary.get(key, 0)}")
    lines.extend(["", "## How to read this", "", interpretation])

    breakdowns = result.get("breakdowns") or {}
    lines.extend([""] + _markdown_table("Language breakdown", breakdowns.get("by_language") or {}))
    lines.extend([""] + _markdown_table("Construct breakdown", breakdowns.get("by_construct") or {}))
    lines.extend([""] + _markdown_table("Control-type breakdown", breakdowns.get("by_control_type") or {}))

    if result.get("errors"):
        lines.extend(["", "## Errors"])
        lines.extend(f"- {error}" for error in result["errors"])
    lines.extend(["", "## Cases"])
    for case in result.get("case_results") or []:
        lines.extend([
            f"### {case.get('case_id')}",
            f"Language: `{case.get('language')}`",
            f"Construct: `{case.get('construct')}`",
            f"Control type: `{case.get('control_type')}`",
            f"Score: `{case.get('score')}`",
            f"Rationale: {case.get('rationale')}",
            "",
        ])
    return "\n".join(lines).rstrip() + "\n"


def _html_table(title: str, rows: dict[str, dict[str, Any]]) -> str:
    body = "".join(
        "<tr>"
        f"<td>{html.escape(str(group))}</td>"
        f"<td>{values.get('case_count', 0)}</td>"
        f"<td>{values.get('mean_score', 0)}</td>"
        f"<td>{values.get('unsupported_assumption', 0)}</td>"
        f"<td>{values.get('harmful_generalization', 0)}</td>"
        f"<td>{values.get('uncertainty_preserved', 0)}</td>"
        f"<td>{values.get('over_refusal', 0)}</td>"
        "</tr>"
        for group, values in rows.items()
    )
    return (
        f"<h2>{html.escape(title)}</h2>"
        "<table><thead><tr><th>group</th><th>cases</th><th>mean score</th><th>unsupported</th>"
        "<th>harmful</th><th>uncertainty</th><th>over-refusal</th></tr></thead>"
        f"<tbody>{body}</tbody></table>"
    )


def build_html_report(result: dict) -> str:
    markdown_fallback = build_markdown_report(result)
    summary = result.get("summary") or {}
    breakdowns = result.get("breakdowns") or {}
    cases = result.get("case_results") or []
    summary_items = "".join(f"<li>{html.escape(key.replace('_', ' '))}: {html.escape(str(summary.get(key, 0)))}</li>" for key in SUMMARY_KEYS)
    case_items = "".join(
        "<section>"
        f"<h3>{html.escape(str(case.get('case_id')))}</h3>"
        f"<p>Language: <code>{html.escape(str(case.get('language')))}</code></p>"
        f"<p>Construct: <code>{html.escape(str(case.get('construct')))}</code></p>"
        f"<p>Control type: <code>{html.escape(str(case.get('control_type')))}</code></p>"
        f"<p>Score: <code>{html.escape(str(case.get('score')))}</code></p>"
        f"<p>Rationale: {html.escape(str(case.get('rationale')))}</p>"
        "</section>"
        for case in cases
    )
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Fillblank eval report</title>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 960px; margin: 2rem auto; line-height: 1.5; padding: 0 1rem; }}
    table {{ border-collapse: collapse; width: 100%; margin: 1rem 0 2rem; }}
    th, td {{ border: 1px solid #ddd; padding: 0.4rem 0.5rem; text-align: left; }}
    th {{ background: #f5f5f5; }}
    code {{ background: #f5f5f5; padding: 0.1rem 0.25rem; }}
    .caveat {{ border-left: 4px solid #b45309; padding-left: 1rem; }}
  </style>
</head>
<body>
  <h1>Fillblank eval report</h1>
  <p>Provider: <code>{provider}</code></p>
  <p>Model: <code>{model}</code></p>
  <p class="caveat">{caveat}</p>
  <p>Public claim ready: <code>{public_claim_ready}</code></p>
  <h2>Summary</h2>
  <ul>{summary_items}</ul>
  <h2>How to read this</h2>
  <p>{interpretation}</p>
  {language_table}
  {construct_table}
  {control_table}
  <h2>Cases</h2>
  {case_items}
  <details><summary>Markdown source</summary><pre>{markdown}</pre></details>
</body>
</html>
""".format(
        provider=html.escape(str(result.get("provider", "unknown"))),
        model=html.escape(str(result.get("model", "unknown"))),
        caveat=html.escape(str(result.get("caveat") or PUBLIC_CAVEAT)),
        public_claim_ready=html.escape(str(result.get("public_claim_ready", False)).lower()),
        summary_items=summary_items,
        interpretation=html.escape(str(result.get("interpretation") or build_interpretation(result))),
        language_table=_html_table("Language breakdown", breakdowns.get("by_language") or {}),
        construct_table=_html_table("Construct breakdown", breakdowns.get("by_construct") or {}),
        control_table=_html_table("Control-type breakdown", breakdowns.get("by_control_type") or {}),
        case_items=case_items,
        markdown=html.escape(markdown_fallback),
    )


def build_report_for_outputs(dataset_path: str, outputs: dict[str, str]) -> str:
    return build_markdown_report(score_outputs(dataset_path, outputs))
