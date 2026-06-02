import json
from pathlib import Path

from fillblank_eval.run_cli import DEFAULT_PUBLIC_DATASETS
from fillblank_eval.validator import LANGUAGES, validate_dataset

TOP10_TOTAL_SPEAKER_LANGUAGES = {"en", "zh", "hi", "es", "ar", "fr", "bn", "pt", "id", "ur"}
LEGACY_PUBLIC_LANGUAGES = {"de", "el"}


def _rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_validator_allows_top10_total_speaker_languages():
    assert TOP10_TOTAL_SPEAKER_LANGUAGES.issubset(LANGUAGES)
    assert LEGACY_PUBLIC_LANGUAGES.issubset(LANGUAGES)


def test_public_top10_sample_validates_and_covers_each_language_once():
    root = Path(__file__).resolve().parents[1]
    path = root / "examples/public_top10_sample.jsonl"

    result = validate_dataset(path, public_mode=True)

    assert result.ok, result.errors
    assert set(result.languages or []) == TOP10_TOTAL_SPEAKER_LANGUAGES
    rows = _rows(path)
    assert len(rows) == 10
    assert {row["language"] for row in rows} == TOP10_TOTAL_SPEAKER_LANGUAGES
    assert all("translation-assisted public sample" in row["review"]["reviewer_notes"].lower() for row in rows)
    assert all("needs native/competent review" in row["notes"].lower() for row in rows)
    assert {row["translation_group"] for row in rows} == {"top10-app-001"}


def test_default_runner_includes_top10_public_sample():
    names = {path.name for path in DEFAULT_PUBLIC_DATASETS}
    assert "public_top10_sample.jsonl" in names
