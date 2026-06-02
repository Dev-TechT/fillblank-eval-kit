from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
ISSUE_TEMPLATE_DIR = ROOT / ".github" / "ISSUE_TEMPLATE"
CASE_FORM = ISSUE_TEMPLATE_DIR / "case-proposal.yml"
TASK_FORM = ISSUE_TEMPLATE_DIR / "agent-task.yml"
PR_TEMPLATE = ROOT / ".github" / "pull_request_template.md"
CONTRIBUTING = ROOT / "CONTRIBUTING.md"
README = ROOT / "README.md"


def _load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    assert isinstance(value, dict), path
    return value


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_github_issue_forms_parse_and_include_required_forms():
    forms = {path.name: _load_yaml(path) for path in ISSUE_TEMPLATE_DIR.glob("*.yml")}

    assert "case-proposal.yml" in forms
    assert "agent-task.yml" in forms
    assert forms["case-proposal.yml"]["name"] == "Public benchmark case proposal"
    assert forms["agent-task.yml"]["name"] == "Agent-friendly implementation task"


def test_case_proposal_form_enforces_public_case_boundaries():
    form = _load_yaml(CASE_FORM)
    text = _text(CASE_FORM).lower()
    ids = {item.get("id") for item in form["body"] if isinstance(item, dict)}

    assert {"language", "construct", "prompt_template", "expected_behavior", "provenance_review", "public_boundary"}.issubset(ids)
    assert "exactly one `{blank}`" in text
    assert "do not include private" in text
    assert "client" in text
    assert "holdout" in text
    assert "no model ranking" in text
    assert "not proof" in text


def test_agent_task_form_guides_adapter_reporting_work_without_private_data():
    form = _load_yaml(TASK_FORM)
    text = _text(TASK_FORM).lower()
    ids = {item.get("id") for item in form["body"] if isinstance(item, dict)}

    assert {"goal", "scope", "acceptance_criteria", "verification_commands", "privacy_claim_boundary"}.issubset(ids)
    assert "adapter" in text
    assert "report" in text
    assert "agent" in text
    assert "private/client data" in text
    assert "unsupported model claims" in text
    assert "uv run --with pytest python -m pytest -q" in text
    assert "uv run python -m fillblank_eval.leak_scan ." in text


def test_pr_template_has_validation_and_privacy_claim_checkboxes():
    text = _text(PR_TEMPLATE)

    for command in [
        "uv run --with pytest python -m pytest -q",
        "uv run python -m fillblank_eval.validator examples/public_sample.jsonl examples/public_dev.jsonl examples/public_top10_sample.jsonl",
        "uv run python -m fillblank_eval.duplicates examples/public_sample.jsonl examples/public_dev.jsonl examples/public_top10_sample.jsonl",
        "uv run python -m fillblank_eval.leak_scan .",
    ]:
        assert command in text
    for checkbox in [
        "No private/client data",
        "No unsupported model claims",
        "No public leaderboard or ranking claim",
        "No real provider/client output artifacts",
    ]:
        assert checkbox in text


def test_readme_links_to_contribution_task_guidance():
    readme = _text(README)
    contributing = _text(CONTRIBUTING)

    assert "CONTRIBUTING.md" in readme
    assert ".github/ISSUE_TEMPLATE/case-proposal.yml" in contributing
    assert ".github/ISSUE_TEMPLATE/agent-task.yml" in contributing
    assert ".github/pull_request_template.md" in contributing
    assert "private/client data" in contributing
    assert "unsupported model claims" in contributing
