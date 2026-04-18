"""
Gap analysis for POP's snack strategy engine.

This module answers the portfolio question behind each trend:

    "Where is the market moving faster than POP's current product presence?"

The goal is not just to find high-growth trends. We also need to find
where POP has whitespace, whether the trend is still early enough to act,
and whether POP can realistically execute before the opportunity peaks.

What this module does:
- compare a trend's tags against POP's current product catalog
- classify POP presence as LOW, MEDIUM, or HIGH
- calculate a gap opportunity score
- reuse the feasibility layer from `constraints.py`
- recommend whether POP should develop, distribute, or deprioritize
- return plain-English reasoning for UI cards and downstream scoring
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Sequence

from constraints import evaluate_trend_constraints
from forecasting import forecast_trend_timing
from sample_data import POP_PRODUCTS, TRENDS


GENERIC_TAGS = {
    "category",
    "flavor",
    "flavor fusion",
    "functional",
    "natural",
    "salty",
    "savory",
    "snack",
    "sweet",
    "wellness",
}

POP_ADVANTAGE_TAGS = {
    "asian",
    "ginger",
    "herbal",
    "honey",
    "seaweed",
    "tea",
    "umami",
    "wellness",
}

LOW_PRESENCE = "LOW"
MEDIUM_PRESENCE = "MEDIUM"
HIGH_PRESENCE = "HIGH"

PRESENCE_SCORES = {
    LOW_PRESENCE: 8,
    MEDIUM_PRESENCE: 18,
    HIGH_PRESENCE: 28,
}

GAP_SCORES = {
    LOW_PRESENCE: 18,
    MEDIUM_PRESENCE: 10,
    HIGH_PRESENCE: 3,
}


def _normalize_tags(tags: Iterable[str]) -> set[str]:
    return {str(tag).strip().lower() for tag in tags if str(tag).strip()}


def _specific_tags(tags: Iterable[str]) -> set[str]:
    return {tag for tag in _normalize_tags(tags) if tag not in GENERIC_TAGS}


def _matching_products(trend_tags: set[str], pop_products: Sequence[Dict]) -> List[Dict[str, object]]:
    matches: List[Dict[str, object]] = []
    for product in pop_products:
        product_tags = _specific_tags(product.get("tags", []))
        overlap = sorted(trend_tags.intersection(product_tags))
        if overlap:
            matches.append(
                {
                    "name": product.get("name", "Unknown Product"),
                    "matched_tags": overlap,
                }
            )
    return matches


def classify_pop_presence(trend: Dict, pop_products: Sequence[Dict] | None = None) -> Dict[str, object]:
    """
    Measure POP's current presence against one trend.

    Presence is intentionally simple:
    - LOW: little overlap, meaning whitespace opportunity
    - MEDIUM: some adjacency, but POP is not established yet
    - HIGH: strong overlap, so the trend is less of a gap
    """
    pop_products = pop_products or POP_PRODUCTS
    trend_tags = _specific_tags(trend.get("tags", []))
    matches = _matching_products(trend_tags, pop_products)

    matched_tags = sorted(
        {
            tag
            for product in matches
            for tag in product.get("matched_tags", [])
            if isinstance(tag, str)
        }
    )
    whitespace_tags = sorted(trend_tags.difference(matched_tags))

    tag_coverage = len(matched_tags) / max(len(trend_tags), 1)
    product_coverage = len(matches) / max(len(pop_products), 1)

    if tag_coverage >= 0.67 or len(matches) >= 3:
        level = HIGH_PRESENCE
    elif tag_coverage >= 0.34 or len(matches) >= 1:
        level = MEDIUM_PRESENCE
    else:
        level = LOW_PRESENCE

    return {
        "pop_presence": level,
        "pop_presence_score": PRESENCE_SCORES[level],
        "tag_coverage_ratio": round(tag_coverage, 2),
        "product_coverage_ratio": round(product_coverage, 2),
        "match_count": len(matches),
        "matched_pop_products": matches,
        "matched_tags": matched_tags,
        "whitespace_tags": whitespace_tags,
    }


def calculate_gap_opportunity_score(trend: Dict, presence: Dict[str, object]) -> int:
    """
    Score the whitespace opportunity for POP.

    Higher scores mean:
    - POP has lower current presence
    - the trend still fits POP's ingredient or flavor strengths
    - there is a concrete tag-level whitespace to fill
    """
    trend_tags = _specific_tags(trend.get("tags", []))
    whitespace_tags = set(presence.get("whitespace_tags", []))
    strategic_fit_tags = trend_tags.intersection(POP_ADVANTAGE_TAGS)

    score = GAP_SCORES[str(presence["pop_presence"])]
    score += min(4, len(strategic_fit_tags) * 2)
    score += min(3, len(whitespace_tags))

    if str(trend.get("category", "")).lower() in {"sweet", "salty"}:
        score += 2

    return max(0, min(score, 25))


def _determine_action(trend: Dict, presence: Dict[str, object], feasibility: Dict[str, object]) -> str:
    if not feasibility.get("is_viable", False):
        return "deprioritize"

    timing_stage = str(trend.get("timing_stage", "")).upper()
    action_bias = str(trend.get("action_bias", "develop")).lower()
    whitespace_tags = set(presence.get("whitespace_tags", []))
    trend_tags = _specific_tags(trend.get("tags", []))
    strategic_fit = bool(trend_tags.intersection(POP_ADVANTAGE_TAGS))

    if action_bias == "distribute":
        return "distribute"
    if timing_stage == "LATE":
        return "distribute"
    if timing_stage == "EARLY" and (strategic_fit or whitespace_tags):
        return "develop"
    if presence.get("pop_presence") == HIGH_PRESENCE and timing_stage == "MID":
        return "distribute"
    return "develop"


def build_gap_reasoning(
    trend: Dict,
    presence: Dict[str, object],
    feasibility: Dict[str, object],
    recommended_action: str,
) -> str:
    """Create a concise explanation suitable for UI cards and stakeholder review."""
    trend_name = trend.get("name", "This trend")
    pop_presence = str(presence["pop_presence"]).lower()
    whitespace_tags = presence.get("whitespace_tags", [])
    match_count = int(presence.get("match_count", 0))
    timing_stage = str(trend.get("timing_stage", "")).upper()

    if whitespace_tags:
        whitespace_line = (
            f"Key whitespace for POP includes {', '.join(whitespace_tags[:3])}."
        )
    else:
        whitespace_line = "POP already covers much of this trend's flavor space."

    if match_count:
        overlap_line = (
            f"POP has {match_count} adjacent product match"
            f"{'' if match_count == 1 else 'es'}, so the trend is not starting from zero."
        )
    else:
        overlap_line = "POP has little direct overlap today, which creates a real gap opportunity."

    if recommended_action == "develop":
        action_line = (
            "The best move is to develop a differentiated POP-led product while the timing window is still open."
        )
    elif recommended_action == "distribute":
        action_line = (
            "The best move is to distribute or source quickly because speed matters more than long development cycles."
        )
    else:
        action_line = (
            "The opportunity should be deprioritized because POP is unlikely to capture it in time with acceptable risk."
        )

    return (
        f"{trend_name} shows {pop_presence} POP presence and is currently {timing_stage.lower()}-stage. "
        f"{overlap_line} {whitespace_line} "
        f"Feasibility is {str(feasibility.get('feasibility_status', 'moderate')).lower()} "
        f"at {feasibility.get('feasibility_score', 0)}/100. {action_line}"
    )


def analyze_trend_gap(trend: Dict, pop_products: Sequence[Dict] | None = None) -> Dict:
    """
    Analyze a single trend for POP whitespace and actionability.

    If timing fields are missing, this function first enriches the trend using
    `forecast_trend_timing`, then applies the feasibility screen from
    `constraints.py`, then layers on gap logic.
    """
    pop_products = pop_products or POP_PRODUCTS

    enriched_trend = (
        trend
        if "timing_stage" in trend and "action_bias" in trend
        else forecast_trend_timing(trend, pop_products=pop_products)
    )
    feasibility = evaluate_trend_constraints(enriched_trend, pop_products=pop_products)
    presence = classify_pop_presence(enriched_trend, pop_products=pop_products)

    trend_tags = _specific_tags(enriched_trend.get("tags", []))
    strategic_fit_tags = sorted(trend_tags.intersection(POP_ADVANTAGE_TAGS))
    gap_opportunity_score = calculate_gap_opportunity_score(enriched_trend, presence)
    recommended_action = _determine_action(enriched_trend, presence, feasibility)
    reasoning = build_gap_reasoning(
        trend=enriched_trend,
        presence=presence,
        feasibility=feasibility,
        recommended_action=recommended_action,
    )

    is_feasible = bool(feasibility.get("is_viable", False))

    return {
        **enriched_trend,
        "pop_presence": presence["pop_presence"],
        "pop_presence_score": presence["pop_presence_score"],
        "pop_match_count": presence["match_count"],
        "matched_pop_products": presence["matched_pop_products"],
        "matched_tags": presence["matched_tags"],
        "whitespace_tags": presence["whitespace_tags"],
        "strategic_fit_tags": strategic_fit_tags,
        "tag_coverage_ratio": presence["tag_coverage_ratio"],
        "product_coverage_ratio": presence["product_coverage_ratio"],
        "gap_opportunity_score": gap_opportunity_score,
        "is_feasible": is_feasible,
        "constraint_flags": feasibility["constraint_flags"],
        "feasibility_score": feasibility["feasibility_score"],
        "feasibility_status": feasibility["feasibility_status"],
        "constraint_checks": feasibility["constraint_checks"],
        "recommended_action": recommended_action,
        "constraint_recommendation": feasibility["constraint_recommendation"],
        "feasibility_summary": feasibility["feasibility_summary"],
        "reasoning": reasoning,
    }


def analyze_all_gaps(
    trends: Sequence[Dict],
    pop_products: Sequence[Dict] | None = None,
) -> List[Dict]:
    """Run gap analysis across a list of trends."""
    return [analyze_trend_gap(trend, pop_products=pop_products) for trend in trends]


def analyze_sample_gaps() -> List[Dict]:
    """Convenience helper for the mock prototype data."""
    return analyze_all_gaps(TRENDS, pop_products=POP_PRODUCTS)


__all__ = [
    "HIGH_PRESENCE",
    "LOW_PRESENCE",
    "MEDIUM_PRESENCE",
    "analyze_all_gaps",
    "analyze_sample_gaps",
    "analyze_trend_gap",
    "build_gap_reasoning",
    "calculate_gap_opportunity_score",
    "classify_pop_presence",
]
