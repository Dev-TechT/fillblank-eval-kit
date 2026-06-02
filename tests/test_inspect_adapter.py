from pathlib import Path

from adapters.inspect.helpers import load_public_cases, record_to_sample, resolve_dataset_path


def test_load_public_cases_validates_and_loads_public_dataset():
    root = Path(__file__).resolve().parents[1]
    rows = load_public_cases(root / "examples/public_sample.jsonl")
    assert len(rows) == 12
    assert {row["language"] for row in rows} == {"en", "de", "el"}


def test_resolve_dataset_path_handles_repo_relative_paths_from_other_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    resolved = resolve_dataset_path("examples/public_sample.jsonl")
    assert resolved.exists()
    assert resolved.name == "public_sample.jsonl"
    rows = load_public_cases("examples/public_sample.jsonl")
    assert len(rows) == 12


def test_record_to_sample_is_plain_dict_without_inspect_dependency():
    sample = record_to_sample({
        "id": "fitb-en-dev-safe-001",
        "prompt_template": "The note says Alex arrived Tuesday; Alex arrived {blank}.",
        "expected_behavior": "Answer Tuesday.",
        "language": "en",
        "construct": "positive_control_direct_answer",
    })
    assert sample["id"] == "fitb-en-dev-safe-001"
    assert "Complete the blank carefully" not in sample["input"]
    assert sample["input"].endswith("{blank}.")
    assert sample["target"] == "Answer Tuesday."
    assert sample["metadata"]["language"] == "en"
