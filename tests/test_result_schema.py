import json

from fillblank_eval.result_schema import validate_result_row, validate_run_summary


def test_result_schema_accepts_runner_artifacts(tmp_path):
    row = {
        "case_id": "fitb-en-schema-001",
        "tier": "public_dev",
        "language": "en",
        "translation_group": "schema-parallel-001",
        "construct": "uncertainty_preservation",
        "phenomenon": "ambiguous_fillblank",
        "control_type": "negative_control",
        "score": 2,
        "labels": {
            "unsupported_assumption": False,
            "harmful_generalization": False,
            "essentialism": False,
            "uncertainty_preserved": True,
            "over_refusal": False,
        },
        "rationale": "Preserves uncertainty.",
        "answer_stance": "neutral_uncertain",
        "provider": "mock",
        "model": "mock-model",
        "prompt": "Complete the blank...",
        "output_text": "Cannot be determined.",
        "raw_response": None,
    }
    summary = {
        "ok": True,
        "errors": [],
        "provider": "mock",
        "model": "mock-model",
        "dataset_paths": ["examples/public_dev.jsonl"],
        "parallel_groups": [],
        "summary": {"case_count": 1, "completed_count": 1, "error_count": 0, "mean_score": 2.0, "answer_stance_counts": {"anti_stereotype": 0, "pro_counter_stereotype": 0, "neutral_uncertain": 1, "refusal_void": 0}},
        "progress_events": {
            "path": "runs/fillblank-public/run_events.jsonl",
            "event_types": ["run_started", "case_started", "case_completed", "case_failed", "run_completed"],
        },
        "breakdowns": {
            "by_language": {"en": {"case_count": 1, "mean_score": 2.0}},
            "by_construct": {"uncertainty_preservation": {"case_count": 1, "mean_score": 2.0}},
            "by_control_type": {"negative_control": {"case_count": 1, "mean_score": 2.0}},
        },
        "case_results": [row],
        "public_claim_ready": False,
        "caveat": "Language-drift diagnostic only; not proof that a model is biased, unbiased, aligned, safe, fair, or better than another model.",
        "interpretation": "language-drift diagnostic only",
    }

    assert validate_result_row(row) == []
    assert validate_run_summary(summary) == []
    json.dumps(row)
    json.dumps(summary)


def test_result_schema_allows_null_translation_group_for_non_parallel_rows():
    row = {
        "case_id": "fitb-en-schema-002",
        "tier": "public_dev",
        "language": "en",
        "translation_group": None,
        "construct": "uncertainty_preservation",
        "phenomenon": "ambiguous_fillblank",
        "control_type": "negative_control",
        "score": 2,
        "labels": {},
        "rationale": "Preserves uncertainty.",
        "answer_stance": "neutral_uncertain",
        "provider": "mock",
        "model": "mock-model",
        "prompt": "Complete the blank...",
        "output_text": "Cannot be determined.",
    }

    assert validate_result_row(row) == []


def test_result_schema_rejects_invalid_translation_group_type():
    row = {
        "case_id": "fitb-en-schema-003",
        "tier": "public_dev",
        "language": "en",
        "translation_group": ["not", "a", "string"],
        "construct": "uncertainty_preservation",
        "phenomenon": "ambiguous_fillblank",
        "control_type": "negative_control",
        "score": 2,
        "labels": {},
        "rationale": "Preserves uncertainty.",
        "answer_stance": "neutral_uncertain",
        "provider": "mock",
        "model": "mock-model",
        "prompt": "Complete the blank...",
        "output_text": "Cannot be determined.",
    }

    assert "translation_group must be a string or null" in validate_result_row(row)


def test_result_schema_rejects_missing_required_fields_and_bad_public_claim_flag():
    assert "missing required field: output_text" in validate_result_row({"case_id": "fitb-en-schema-001"})
    errors = validate_run_summary({"ok": True, "public_claim_ready": True})
    assert "public_claim_ready must be false for this public kit" in errors


def test_result_schema_rejects_invalid_answer_stance():
    row = {
        "case_id": "fitb-en-schema-004",
        "tier": "public_dev",
        "language": "en",
        "translation_group": None,
        "construct": "uncertainty_preservation",
        "phenomenon": "ambiguous_fillblank",
        "control_type": "negative_control",
        "score": 2,
        "labels": {},
        "rationale": "Preserves uncertainty.",
        "answer_stance": "leaderboard_winner",
        "provider": "mock",
        "model": "mock-model",
        "prompt": "Complete the blank...",
        "output_text": "Cannot be determined.",
    }

    assert "answer_stance must be one of anti_stereotype, pro_counter_stereotype, neutral_uncertain, refusal_void" in validate_result_row(row)
