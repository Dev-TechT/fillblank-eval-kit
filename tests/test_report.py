from fillblank_eval.interpretation import build_interpretation
from fillblank_eval.report import build_html_report, build_markdown_report


def _result() -> dict:
    return {
        "ok": True,
        "provider": "mock",
        "model": "mock-model",
        "dataset_paths": ["examples/public_sample.jsonl"],
        "parallel_groups": [
            {
                "translation_group": "top10-app-001",
                "case_count": 2,
                "languages": ["en", "de"],
                "mean_score": 2.5,
                "score_range": 1,
                "answer_stances": ["neutral_uncertain", "pro_counter_stereotype"],
                "answer_stance_counts": {
                    "anti_stereotype": 0,
                    "pro_counter_stereotype": 1,
                    "neutral_uncertain": 1,
                    "refusal_void": 0,
                },
                "stance_diversity": 2,
                "drift_signal": "medium",
                "unsupported_assumption": 0,
                "harmful_generalization": 0,
                "essentialism": 0,
                "uncertainty_preserved": 2,
                "over_refusal": 0,
            }
        ],
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
            "answer_stance_counts": {
                "anti_stereotype": 0,
                "pro_counter_stereotype": 1,
                "neutral_uncertain": 1,
                "refusal_void": 0,
            },
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
        "caveat": "Language-drift diagnostic only; not proof that a model is biased, unbiased, aligned, safe, fair, or better than another model.",
    }


def test_interpretation_avoids_alignment_overclaim():
    text = build_interpretation(_result())

    assert "language-drift diagnostic" in text
    assert "same model changes stance" in text
    assert "not proof that a model is biased" in text


def test_markdown_report_includes_breakdowns_and_caveats():
    markdown = build_markdown_report(_result())

    assert "# Multilingual bias drift report" in markdown
    assert "Provider: `mock`" in markdown
    assert "Model: `mock-model`" in markdown
    assert "## Language breakdown" in markdown
    assert "| en | 1 | 3.0 |" in markdown
    assert "## Construct breakdown" in markdown
    assert "## Parallel translation groups" in markdown
    assert "| top10-app-001 | 2 | en, de |" in markdown
    assert "| stance | cases |" in markdown
    assert "## How to read this" in markdown
    assert "not proof that a model is biased" in markdown


def test_html_report_escapes_content_and_includes_summary():
    result = _result()
    result["case_results"][0]["rationale"] = "<script>alert('x')</script>"

    html = build_html_report(result)

    assert "<html" in html
    assert "&lt;script&gt;alert" in html
    assert "<script>alert" not in html
    assert "Language breakdown" in html
    assert "Answer stance breakdown" in html
    assert "noindex,nofollow" in html
    assert "Parallel translation groups" in html
