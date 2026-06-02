from __future__ import annotations

from fillblank_eval.scorer import score_output


def fillblank_pass_rate(items):
    """Experimental helper for future lm-eval integration.

    `items` is expected to be an iterable of generated strings or records with a
    `prediction`/`output` field. This helper intentionally returns only a simple
    pass rate and is not an official leaderboard metric.
    """
    scores = []
    for item in items:
        if isinstance(item, dict):
            output = item.get("prediction") or item.get("output") or item.get("completion") or ""
        else:
            output = str(item)
        scores.append(1.0 if score_output(output).score >= 2 else 0.0)
    return sum(scores) / len(scores) if scores else 0.0
