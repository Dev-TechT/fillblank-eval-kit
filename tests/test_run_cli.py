import json
from pathlib import Path

from fillblank_eval import run_cli


def test_dry_run_uses_mock_model_even_when_real_model_env_is_set(tmp_path, monkeypatch):
    monkeypatch.setenv("FILLBLANK_PROVIDER", "openai-compatible")
    monkeypatch.setenv("FILLBLANK_MODEL", "real-model-from-env")
    out_dir = tmp_path / "dry-run"

    exit_code = run_cli.main(["--dry-run", "--limit", "1", "--out-dir", str(out_dir)])

    assert exit_code == 0
    summary = json.loads((out_dir / "summary.json").read_text(encoding="utf-8"))
    assert summary["provider"] == "mock"
    assert summary["model"] == "mock-model"


def test_private_client_scope_rejects_public_repo_output_path():
    out_dir = Path.cwd() / "runs" / "cli-client-x"

    exit_code = run_cli.main(["--dry-run", "--limit", "1", "--run-scope", "private-client", "--out-dir", str(out_dir)])

    assert exit_code == 1
    assert not (out_dir / "summary.json").exists()
