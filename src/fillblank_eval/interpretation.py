from __future__ import annotations

from .validator import PUBLIC_CAVEAT


def build_interpretation(result: dict) -> str:
    summary = result.get("summary") or {}
    case_count = summary.get("case_count", 0)
    mean_score = summary.get("mean_score", 0)
    unsupported = summary.get("unsupported_assumption", 0)
    harmful = summary.get("harmful_generalization", 0)
    over_refusal = summary.get("over_refusal", 0)
    return (
        f"This run is a language-drift diagnostic on this multilingual benchmark only: "
        f"{case_count} public cases, mean heuristic score {mean_score}. "
        f"Heuristic labels flagged unsupported assumptions={unsupported}, harmful generalizations={harmful}, "
        f"and over-refusals={over_refusal}. The main signal is whether the same model changes stance "
        f"across language versions of the same underlying question. It is not proof that a model is "
        f"biased, unbiased, safe, fair, or better than another model; compare runs only with the same "
        f"data split, scorer version, model settings, and caveats. {PUBLIC_CAVEAT}"
    )
