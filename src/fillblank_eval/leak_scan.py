from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

PRIVATE_MARKERS = (
    "\"tier\": \"private_holdout\"",
    "'tier': 'private_holdout'",
    "tier: private_holdout",
    "\"tier\":\"private_holdout\"",
    "\"tier\": \"quarantine_candidates\"",
    "'tier': 'quarantine_candidates'",
    "tier: quarantine_candidates",
    "\"tier\":\"quarantine_candidates\"",
    "\"tier\": \"retired_holdout\"",
    "'tier': 'retired_holdout'",
    "tier: retired_holdout",
    "\"tier\":\"retired_holdout\"",
    "private_answer",
    "official_runner_config",
)
SCAN_SUFFIXES = {".md", ".py", ".json", ".jsonl", ".yaml", ".yml", ".toml", ".txt"}
SKIP_DIRS = {".git", ".pytest_cache", "__pycache__", "dist", "build", ".ruff_cache", ".mypy_cache", ".venv"}
SKIP_FILES = {"tests/test_leak_scan.py", "src/fillblank_eval/leak_scan.py"}


@dataclass(frozen=True)
class LeakFinding:
    path: str
    line: int
    snippet: str


@dataclass(frozen=True)
class LeakScanResult:
    ok: bool
    findings: list[LeakFinding]


def _should_scan(path: Path) -> bool:
    return path.is_file() and path.suffix in SCAN_SUFFIXES


def _is_policy_context(path: Path) -> bool:
    name = path.name.lower()
    rel = str(path).lower()
    return name in {"benchmark_spec.md", "data_tiers.md", "release_policy.md", "readme.md", "contributing.md", "security.md", ".gitignore"} or rel.endswith("docs/private-holdout-ops.md")


def scan_for_private_leaks(root: str | Path) -> LeakScanResult:
    root_path = Path(root)
    findings: list[LeakFinding] = []
    for path in root_path.rglob("*"):
        rel = path.relative_to(root_path)
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if str(rel) in SKIP_FILES:
            continue
        if not _should_scan(path):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for line_no, line in enumerate(text.splitlines(), start=1):
            lowered = line.lower()
            for marker in PRIVATE_MARKERS:
                if marker.lower() in lowered:
                    if _is_policy_context(path):
                        continue
                    findings.append(LeakFinding(str(path.relative_to(root_path)), line_no, line.strip()[:240]))
    return LeakScanResult(ok=not findings, findings=findings)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scan public repo tree for private benchmark data leaks.")
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args(argv)
    result = scan_for_private_leaks(args.root)
    if result.ok:
        print("OK: no private benchmark data markers found outside policy docs")
        return 0
    for finding in result.findings:
        print(f"{finding.path}:{finding.line}: {finding.snippet}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
