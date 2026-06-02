import re
from pathlib import Path

from test_language_coverage import TOP10_TOTAL_SPEAKER_LANGUAGES, _rows

ROOT = Path(__file__).resolve().parents[1]
CHECKLIST = ROOT / "docs" / "top10-language-pilot-review-checklist.md"
STATUS_DOC = ROOT / "docs" / "top10-language-pilot-review-status.md"
TOP10_DATASET = ROOT / "examples" / "public_top10_sample.jsonl"

ALLOWED_REVIEW_STATUSES = {
    "unreviewed",
    "competent_reviewed",
    "native_reviewed",
    "needs_rewrite",
    "reject",
}


def test_top10_review_checklist_defines_required_rubric_and_boundaries():
    text = CHECKLIST.read_text(encoding="utf-8")

    for status in sorted(ALLOWED_REVIEW_STATUSES):
        assert f"`{status}`" in text
    for required in [
        "Naturalness",
        "Cultural and locale fit",
        "Grammar around `{blank}`",
        "Construct preservation",
        "Safety and measurement risk",
    ]:
        assert required in text
    assert "Do not commit private reviewer notes" in text
    assert "never mark the exact public row as private holdout" in text
    assert "not proof of safety/fairness/alignment" in text
    assert "no leaderboard/public ranking framing" in text


def test_top10_review_status_tracks_every_language_with_allowed_status():
    text = STATUS_DOC.read_text(encoding="utf-8")
    rows = _rows(TOP10_DATASET)
    case_ids = {row["id"] for row in rows}

    assert "not native-reviewed evidence" in text
    assert "no strong language-specific claims" in text
    for language in TOP10_TOTAL_SPEAKER_LANGUAGES:
        assert f"(`{language}`)" in text
    for case_id in case_ids:
        assert case_id in text

    table_lines = [line for line in text.splitlines() if line.startswith("|") and "fitb-" in line]
    assert len(table_lines) == 10
    seen_languages = set()
    seen_case_ids = set()
    for line in table_lines:
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        language_cell, case_id_cell, status_cell = cells[:3]
        language_match = re.search(r"`([a-z]{2})`", language_cell)
        case_match = re.search(r"`([^`]+)`", case_id_cell)
        status_match = re.fullmatch(r"`([^`]+)`", status_cell)
        assert language_match, line
        assert case_match, line
        assert status_match, line
        seen_languages.add(language_match.group(1))
        seen_case_ids.add(case_match.group(1))
        assert status_match.group(1) in ALLOWED_REVIEW_STATUSES

    assert seen_languages == TOP10_TOTAL_SPEAKER_LANGUAGES
    assert seen_case_ids == case_ids


def test_top10_dataset_keeps_translation_assisted_caveat_until_review_complete():
    for row in _rows(TOP10_DATASET):
        assert row["review"]["review_status"] == "translation_assisted_public_sample"
        assert "needs native/competent review" in row["review"]["reviewer_notes"].lower()
        assert "needs native/competent review" in row["notes"].lower()
        assert row["review"]["public_release_ok"] is True
