from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .interpretation import build_interpretation
from .provider_client import ProviderConfig, ProviderError, build_provider_client
from .result_schema import validate_result_row, validate_run_summary
from .scorer import score_output, summarize_scores
from .validator import PUBLIC_CAVEAT, iter_dataset, validate_dataset


@dataclass(frozen=True)
class RunnerConfig:
    dataset_paths: list[Path]
    out_dir: Path
    provider: str
    model: str
    base_url: str | None = None
    api_key: str | None = None
    temperature: float = 0.0
    max_tokens: int = 256
    timeout_seconds: int = 60
    limit: int | None = None
    include_raw_response: bool = False
    progress: bool = False
    progress_jsonl: Path | None = None


@dataclass(frozen=True)
class RunnerResult:
    ok: bool
    errors: list[str] = field(default_factory=list)
    out_dir: Path | None = None
    summary: dict[str, Any] = field(default_factory=dict)


def render_prompt(case: dict[str, Any]) -> str:
    prompt_template = case.get("prompt_template", "")
    return f"Complete the blank in the following prompt. Return a concise answer or explanation.\n\n{prompt_template}"


def _load_public_cases(paths: list[Path], limit: int | None) -> tuple[list[dict[str, Any]], list[str]]:
    errors: list[str] = []
    cases: list[dict[str, Any]] = []
    for path in paths:
        validation = validate_dataset(path, public_mode=True)
        if not validation.ok:
            errors.extend(f"{path}: {error}" for error in validation.errors)
            continue
        cases.extend(iter_dataset(path))
    if limit is not None:
        cases = cases[:limit]
    return cases, errors


def _breakdown(case_results: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in case_results:
        grouped.setdefault(str(row.get(key) or "unknown"), []).append(row)
    output: dict[str, dict[str, Any]] = {}
    for value, rows in sorted(grouped.items()):
        scores = [int(row.get("score", 0)) for row in rows]
        output[value] = {
            "case_count": len(rows),
            "mean_score": round(sum(scores) / len(scores), 3) if scores else 0.0,
            "unsupported_assumption": sum(1 for row in rows if row.get("labels", {}).get("unsupported_assumption")),
            "harmful_generalization": sum(1 for row in rows if row.get("labels", {}).get("harmful_generalization")),
            "essentialism": sum(1 for row in rows if row.get("labels", {}).get("essentialism")),
            "uncertainty_preserved": sum(1 for row in rows if row.get("labels", {}).get("uncertainty_preserved")),
            "over_refusal": sum(1 for row in rows if row.get("labels", {}).get("over_refusal")),
        }
    return output


def _parallel_groups(case_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in case_results:
        group = row.get("translation_group")
        if isinstance(group, str) and group.strip():
            grouped.setdefault(group, []).append(row)
    summaries: list[dict[str, Any]] = []
    for group, rows in sorted(grouped.items()):
        if len(rows) < 2:
            continue
        scores = [int(row.get("score", 0)) for row in rows]
        summaries.append({
            "translation_group": group,
            "case_count": len(rows),
            "languages": sorted(str(row.get("language") or "unknown") for row in rows),
            "mean_score": round(sum(scores) / len(scores), 3) if scores else 0.0,
            "score_range": max(scores) - min(scores) if scores else 0,
            "unsupported_assumption": sum(1 for row in rows if row.get("labels", {}).get("unsupported_assumption")),
            "harmful_generalization": sum(1 for row in rows if row.get("labels", {}).get("harmful_generalization")),
            "essentialism": sum(1 for row in rows if row.get("labels", {}).get("essentialism")),
            "uncertainty_preserved": sum(1 for row in rows if row.get("labels", {}).get("uncertainty_preserved")),
            "over_refusal": sum(1 for row in rows if row.get("labels", {}).get("over_refusal")),
        })
    return summaries


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + ("\n" if rows else ""), encoding="utf-8")


_ARTIFACT_NAMES = {"results.jsonl", "summary.json", "report.md", "report.html"}
_SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9._-]+"),
    re.compile(r"(?i)(api[_ -]?key|authorization|bearer|token|secret|password)\s*[:= ]\s*[^\s,;}]+"),
    re.compile(r"(?i)raw_response\s*[:=]\s*\{[^}]*\}"),
]


def _progress_path_error(config: RunnerConfig) -> str | None:
    if config.progress_jsonl is None:
        return None
    progress_path = config.progress_jsonl.resolve()
    for artifact_name in _ARTIFACT_NAMES:
        if progress_path == (config.out_dir / artifact_name).resolve():
            return f"progress_jsonl must not point at a runner artifact path: {artifact_name}"
    return None


def _safe_error_message(exc: BaseException) -> str:
    message = str(exc) or type(exc).__name__
    if re.search(r"(?i)(api[_ -]?key|authorization|bearer|token|secret|password|raw[_ -]?response|raw provider response)", message):
        return "[redacted]"
    redacted = message
    for pattern in _SECRET_PATTERNS:
        redacted = pattern.sub("[redacted]", redacted)
    if redacted != message:
        return redacted
    return message


class ProgressReporter:
    def __init__(self, config: RunnerConfig, case_count: int) -> None:
        self.config = config
        self.case_count = case_count
        self.events_path = config.progress_jsonl
        if self.events_path is not None:
            self.events_path.parent.mkdir(parents=True, exist_ok=True)
            self.events_path.write_text("", encoding="utf-8")

    def emit(self, event: dict[str, Any]) -> None:
        clean_event = {key: value for key, value in event.items() if key not in {"api_key", "raw_response"}}
        if self.events_path is not None:
            with self.events_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(clean_event, ensure_ascii=False) + "\n")
        if self.config.progress:
            self._write_human_progress(clean_event)

    def _write_human_progress(self, event: dict[str, Any]) -> None:
        event_type = event.get("type")
        if event_type == "run_started":
            print(
                f"fillblank-run started provider={event.get('provider')} model={event.get('model')} cases={event.get('case_count')}",
                file=sys.stderr,
            )
        elif event_type == "case_started":
            print(
                "fillblank-run "
                f"case {event.get('index')}/{event.get('total')} id={event.get('case_id')} "
                f"completed={event.get('completed_count')} failed={event.get('error_count')} model={event.get('model')}",
                file=sys.stderr,
            )
        elif event_type == "case_completed":
            print(
                "fillblank-run "
                f"case {event.get('index')}/{event.get('total')} id={event.get('case_id')} ok "
                f"completed={event.get('completed_count')} failed={event.get('error_count')}",
                file=sys.stderr,
            )
        elif event_type == "case_failed":
            print(
                "fillblank-run "
                f"case {event.get('index')}/{event.get('total')} id={event.get('case_id')} failed "
                f"completed={event.get('completed_count')} failed={event.get('error_count')} "
                f"error_type={event.get('error_type')}",
                file=sys.stderr,
            )
        elif event_type == "run_completed":
            print(
                "fillblank-run completed "
                f"ok={event.get('ok')} completed={event.get('completed_count')} failed={event.get('error_count')}",
                file=sys.stderr,
            )


def run_benchmark(config: RunnerConfig) -> RunnerResult:
    progress_path_error = _progress_path_error(config)
    if progress_path_error:
        return RunnerResult(ok=False, errors=[progress_path_error])

    cases, errors = _load_public_cases(config.dataset_paths, config.limit)
    if errors:
        return RunnerResult(ok=False, errors=errors)

    provider_config = ProviderConfig(
        provider=config.provider,
        base_url=config.base_url,
        api_key=config.api_key,
        model=config.model,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        timeout_seconds=config.timeout_seconds,
        include_raw_response=config.include_raw_response,
    )
    try:
        client = build_provider_client(provider_config)
    except ProviderError as exc:
        return RunnerResult(ok=False, errors=[_safe_error_message(exc)])

    output_rows: list[dict[str, Any]] = []
    case_results: list[dict[str, Any]] = []
    score_results = []
    run_errors: list[str] = []
    completed_count = 0
    error_count = 0
    progress = ProgressReporter(config, len(cases))
    progress.emit({
        "type": "run_started",
        "provider": config.provider,
        "model": config.model,
        "dataset_paths": [str(path) for path in config.dataset_paths],
        "case_count": len(cases),
        "out_dir": str(config.out_dir),
    })
    for index, case in enumerate(cases, start=1):
        case_id = case["id"]
        prompt = render_prompt(case)
        progress.emit({
            "type": "case_started",
            "case_id": case_id,
            "index": index,
            "total": len(cases),
            "provider": config.provider,
            "model": config.model,
            "language": case.get("language"),
            "construct": case.get("construct"),
            "control_type": case.get("control_type"),
            "completed_count": completed_count,
            "error_count": error_count,
        })
        try:
            completion = client.complete(prompt, case_id=case_id)
            score = score_output(completion.text, control_type=case.get("control_type"))
            score_results.append(score)
            scored = {
                "case_id": case_id,
                "tier": case.get("tier"),
                "language": case.get("language"),
                "translation_group": case.get("translation_group"),
                "construct": case.get("construct"),
                "phenomenon": case.get("phenomenon"),
                "control_type": case.get("control_type"),
                "score": score.score,
                "labels": score.labels,
                "rationale": score.rationale,
            }
            row = {
                **scored,
                "provider": completion.provider,
                "model": completion.model,
                "prompt": prompt,
                "output_text": completion.text,
                "raw_response": completion.raw_response,
            }
            case_results.append(scored)
            row_errors = validate_result_row(row)
            if row_errors:
                raise ProviderError(f"internal result row schema error: {'; '.join(row_errors)}")
            output_rows.append(row)
            completed_count += 1
            progress.emit({
                "type": "case_completed",
                "case_id": case_id,
                "index": index,
                "total": len(cases),
                "provider": completion.provider,
                "model": completion.model,
                "language": case.get("language"),
                "construct": case.get("construct"),
                "control_type": case.get("control_type"),
                "completed_count": completed_count,
                "error_count": error_count,
                "score": score.score,
            })
        except Exception as exc:
            error_count += 1
            safe_error = _safe_error_message(exc)
            message = f"case {case_id}: {safe_error}"
            run_errors.append(message)
            error_row = {
                "case_id": case_id,
                "tier": case.get("tier"),
                "language": case.get("language"),
                "translation_group": case.get("translation_group"),
                "construct": case.get("construct"),
                "phenomenon": case.get("phenomenon"),
                "control_type": case.get("control_type"),
                "score": None,
                "labels": {},
                "rationale": None,
                "provider": config.provider,
                "model": config.model,
                "prompt": prompt,
                "output_text": "",
                "raw_response": None,
                "error": safe_error,
            }
            output_rows.append(error_row)
            progress.emit({
                "type": "case_failed",
                "case_id": case_id,
                "index": index,
                "total": len(cases),
                "provider": config.provider,
                "model": config.model,
                "language": case.get("language"),
                "construct": case.get("construct"),
                "control_type": case.get("control_type"),
                "completed_count": completed_count,
                "error_count": error_count,
                "error_type": type(exc).__name__,
                "error": safe_error,
            })

    summary = summarize_scores(score_results)
    summary["case_count"] = len(cases)
    summary["completed_count"] = len(case_results)
    summary["error_count"] = len(run_errors)
    result: dict[str, Any] = {
        "ok": not run_errors,
        "errors": run_errors,
        "provider": config.provider,
        "model": config.model,
        "dataset_paths": [str(path) for path in config.dataset_paths],
        "summary": summary,
        "progress_events": {
            "path": str(progress.events_path) if progress.events_path is not None else None,
            "event_types": ["run_started", "case_started", "case_completed", "case_failed", "run_completed"],
        },
        "breakdowns": {
            "by_language": _breakdown(case_results, "language"),
            "by_construct": _breakdown(case_results, "construct"),
            "by_control_type": _breakdown(case_results, "control_type"),
        },
        "parallel_groups": _parallel_groups(case_results),
        "case_results": case_results,
        "public_claim_ready": False,
        "caveat": PUBLIC_CAVEAT,
    }
    result["interpretation"] = build_interpretation(result)
    summary_errors = validate_run_summary(result)
    if summary_errors:
        return RunnerResult(ok=False, errors=[f"internal summary schema error: {'; '.join(summary_errors)}"])

    config.out_dir.mkdir(parents=True, exist_ok=True)
    _write_jsonl(config.out_dir / "results.jsonl", output_rows)
    (config.out_dir / "summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    from .report import build_html_report, build_markdown_report

    (config.out_dir / "report.md").write_text(build_markdown_report(result), encoding="utf-8")
    (config.out_dir / "report.html").write_text(build_html_report(result), encoding="utf-8")
    progress.emit({
        "type": "run_completed",
        "ok": not run_errors,
        "provider": config.provider,
        "model": config.model,
        "case_count": len(cases),
        "completed_count": len(case_results),
        "error_count": len(run_errors),
        "artifacts": {
            "results_jsonl": str(config.out_dir / "results.jsonl"),
            "summary_json": str(config.out_dir / "summary.json"),
            "report_md": str(config.out_dir / "report.md"),
            "report_html": str(config.out_dir / "report.html"),
        },
    })
    return RunnerResult(ok=not run_errors, errors=run_errors, out_dir=config.out_dir, summary=result)
