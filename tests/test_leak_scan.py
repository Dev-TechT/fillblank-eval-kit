from pathlib import Path

from fillblank_eval.leak_scan import scan_for_private_leaks


def test_leak_scan_flags_private_tiers_in_public_data_file(tmp_path):
    examples = tmp_path / "examples"
    examples.mkdir()
    (examples / "public_sample.jsonl").write_text(
        "\n".join([
            '{"id":"x","tier":"private_holdout"}',
            '{"id":"y","tier":"quarantine_candidates"}',
            '{"id":"z","tier":"retired_holdout"}',
        ]) + "\n",
        encoding="utf-8",
    )
    result = scan_for_private_leaks(tmp_path)
    assert not result.ok
    snippets = "\n".join(finding.snippet for finding in result.findings)
    assert "private_holdout" in snippets
    assert "quarantine_candidates" in snippets
    assert "retired_holdout" in snippets


def test_leak_scan_allows_policy_docs_without_private_rows():
    root = Path(__file__).resolve().parents[1]
    result = scan_for_private_leaks(root)
    assert result.ok, [f"{f.path}:{f.line}:{f.snippet}" for f in result.findings]
