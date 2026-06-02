from fillblank_eval.interpretation import build_interpretation
from fillblank_eval.report import build_html_report, build_markdown_report


def _result() -> dict:
    return {
        "ok": True,
        "provider": "mock",
        "model": "mock-model",
        "dataset_paths": ["examples/public_sample.jsonl"],
        "public_claim_ready": False,
        "summary": {
            "case_count": 2,
            "completed_count": 2,
            "error_count": 0,
            "mean_score": 2.5,
            "unsupported_assumption": 0,
            "harmful_generalization": 0,
            "essentialism": 0,
            "uncertainty_preserved": 2,
            "over_refusal": 0,
        },
        "breakdowns": {
            "by_language": {"en": {"case_count": 1, "mean_score": 3.0}, "de": {"case_count": 1, "mean_score": 2.0}},
            "by_construct": {"uncertainty_preservation": {"case_count": 2, "mean_score": 2.5}},
            "by_control_type": {"negative_control": {"case_count": 2, "mean_score": 2.5}},
        },
        "case_results": [
            {
                "case_id": "fitb-en-test-001",
                "language": "en",
                "construct": "uncertainty_preservation",
                "control_type": "negative_control",
                "score": 3,
                "labels": {"uncertainty_preserved": True},
                "rationale": "Preserves uncertainty.",
            }
        ],
        "errors": [],
        "caveat": "Behavior/alignment-relevant profile only; not an alignment proof. No public model ranking claims.",
    }


def test_interpretation_avoids_alignment_overclaim():
    text = build_interpretation(_result())

    assert "behavior/alignment-relevant profile" in text
    assert "not an alignment proof" in text
    assert "leaderboard" in text.lower()


def test_markdown_report_includes_breakdowns_and_caveats():
    markdown = build_markdown_report(_result())

    assert "# Fillblank eval report" in markdown
    assert "Provider: `mock`" in markdown
    assert "Model: `mock-model`" in markdown
    assert "## Language breakdown" in markdown
    assert "| en | 1 | 3.0 |" in markdown
    assert "## Construct breakdown" in markdown
    assert "## How to read this" in markdown
    assert "not an alignment proof" in markdown


def test_html_report_escapes_content_and_includes_summary():
    result = _result()
    result["case_results"][0]["rationale"] = "<script>alert('x')</script>"

    html = build_html_report(result)

    assert "<html" in html
    assert "&lt;script&gt;alert" in html
    assert "<script>alert" not in html
    assert "Language breakdown" in html
