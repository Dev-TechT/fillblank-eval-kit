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
        f"This run is a behavior/alignment-relevant profile on this fill-in-the-blank benchmark "
        f"only: {case_count} public cases, mean heuristic score {mean_score}. "
        f"Heuristic labels flagged unsupported assumptions={unsupported}, harmful generalizations={harmful}, "
        f"and over-refusals={over_refusal}. It is not an alignment proof, not a safety certification, "
        f"and not a leaderboard result; compare runs only with the same data split, scorer version, and caveats. "
        f"{PUBLIC_CAVEAT}"
    )
