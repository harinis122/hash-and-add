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

RELATED_TAG_MAP = {
    "low sugar": {
        "functional",
        "ginger",
        "honey",
        "natural",
        "sweet",
        "tea",
        "wellness",
    },
}

EXTENSION_FRIENDLY_TAGS = {
    "asian",
    "chili",
    "ginger",
    "honey",
    "low sugar",
    "sea salt",
    "seaweed",
    "spicy",
    "tea",
    "umami",
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

ADJACENT_EXTENSION_SCORES = {
    LOW_PRESENCE: 4,
    MEDIUM_PRESENCE: 16,
    HIGH_PRESENCE: 13,
}

BRANCH_OUT_STRENGTH_THRESHOLD = 78
BRANCH_OUT_RECENT_GROWTH_THRESHOLD = 15


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


def _related_overlap(trend_tags: set[str], product_tags: set[str]) -> List[str]:
    related_matches: set[str] = set()
    for trend_tag in trend_tags:
        related_tags = RELATED_TAG_MAP.get(trend_tag, set())
        if product_tags.intersection(related_tags):
            related_matches.add(trend_tag)
    return sorted(related_matches)


def _trend_signal_strength(trend: Dict) -> Dict[str, float]:
    """
    Estimate how strong the raw market upside looks.

    This is intentionally lightweight so gap analysis can make a portfolio
    decision without importing the final scoring layer and creating a cycle.
    """
    growth = [float(value) for value in trend.get("growth", [])]
    if not growth:
        return {"latest_value": 0.0, "recent_change": 0.0}

    latest_value = float(trend.get("trend_momentum", {}).get("latest_value", growth[-1]))
    if len(growth) >= 2:
        fallback_recent = growth[-1] - growth[-2]
    else:
        fallback_recent = 0.0
    recent_change = float(
        trend.get("trend_momentum", {}).get("recent_change", fallback_recent)
    )

    return {
        "latest_value": latest_value,
        "recent_change": recent_change,
    }


def _is_branch_out_worthy(trend: Dict, presence: Dict[str, object]) -> bool:
    """
    Decide whether POP should accept branching into a weaker adjacency area.

    POP is slow to execute, so whitespace alone is not enough. Branching out
    should only happen when the trend is unusually strong and hard to ignore.
    """
    if presence.get("pop_presence") != LOW_PRESENCE:
        return False

    signal = _trend_signal_strength(trend)
    latest_value = signal["latest_value"]
    recent_change = signal["recent_change"]
    timing_stage = str(trend.get("timing_stage", "")).upper()
    timing_advantage = float(trend.get("timing_advantage_score", 0))

    return (
        latest_value >= BRANCH_OUT_STRENGTH_THRESHOLD
        and recent_change >= BRANCH_OUT_RECENT_GROWTH_THRESHOLD
        and timing_stage in {"EARLY", "MID"}
        and timing_advantage >= 18
    )


def _is_extension_friendly(trend: Dict, presence: Dict[str, object]) -> bool:
    """
    Identify trends that are still realistic product tweaks for POP.

    Some low-overlap trends are not true branch-outs. "Low sugar" is a good
    example: POP may not sell a product tagged that way today, but reducing
    sugar in an existing sweet product is still closer to reformulation than
    entering a brand-new capability area.
    """
    category = str(trend.get("category", "")).lower()
    trend_tags = _specific_tags(trend.get("tags", []))
    whitespace_tags = set(presence.get("whitespace_tags", []))
    strategic_fit_tags = trend_tags.intersection(POP_ADVANTAGE_TAGS)
    extension_tags = trend_tags.intersection(EXTENSION_FRIENDLY_TAGS)
    feasibility_score = float(trend.get("feasibility_score", 0))
    timing_stage = str(trend.get("timing_stage", "")).upper()

    if category not in {"sweet", "salty"}:
        return False
    if strategic_fit_tags:
        return True
    if whitespace_tags and whitespace_tags.issubset(EXTENSION_FRIENDLY_TAGS):
        return True
    return bool(extension_tags) and feasibility_score >= 65 and timing_stage in {"EARLY", "MID"}


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
    soft_matches: List[Dict[str, object]] = []

    for product in pop_products:
        product_tags = _normalize_tags(product.get("tags", []))
        related = _related_overlap(trend_tags, product_tags)
        if related:
            soft_matches.append(
                {
                    "name": product.get("name", "Unknown Product"),
                    "matched_tags": related,
                }
            )

    matched_tags = sorted(
        {
            tag
            for product in matches
            for tag in product.get("matched_tags", [])
            if isinstance(tag, str)
        }
    )
    whitespace_tags = sorted(trend_tags.difference(matched_tags))
    soft_matched_tags = sorted(
        {
            tag
            for product in soft_matches
            for tag in product.get("matched_tags", [])
            if isinstance(tag, str)
        }
    )

    tag_coverage = len(matched_tags) / max(len(trend_tags), 1)
    product_coverage = len(matches) / max(len(pop_products), 1)
    soft_tag_coverage = len(soft_matched_tags) / max(len(trend_tags), 1)

    if tag_coverage >= 0.67 or len(matches) >= 3:
        level = HIGH_PRESENCE
    elif tag_coverage >= 0.34 or len(matches) >= 1:
        level = MEDIUM_PRESENCE
    elif soft_tag_coverage >= 0.34 or len(soft_matches) >= 2:
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
        "soft_match_count": len(soft_matches),
        "soft_matched_pop_products": soft_matches,
        "soft_matched_tags": soft_matched_tags,
        "soft_tag_coverage_ratio": round(soft_tag_coverage, 2),
        "whitespace_tags": whitespace_tags,
    }


def calculate_gap_opportunity_score(trend: Dict, presence: Dict[str, object]) -> int:
    """
    Score the portfolio opportunity for POP.

    Higher scores mean:
    - the trend can be expressed as a safe extension of existing POP products
    - POP has some adjacency to move faster
    - true whitespace gets rewarded only when the upside is unusually high
    """
    trend_tags = _specific_tags(trend.get("tags", []))
    whitespace_tags = set(presence.get("whitespace_tags", []))
    strategic_fit_tags = trend_tags.intersection(POP_ADVANTAGE_TAGS)
    pop_presence = str(presence["pop_presence"])
    match_count = int(presence.get("match_count", 0))
    soft_match_count = int(presence.get("soft_match_count", 0))
    branch_out_worthy = _is_branch_out_worthy(trend, presence)
    extension_friendly = _is_extension_friendly(trend, presence)

    score = ADJACENT_EXTENSION_SCORES[pop_presence]
    score += min(6, match_count * 2)
    score += min(4, soft_match_count)
    score += min(4, len(strategic_fit_tags) * 2)
    score += int(round(float(presence.get("tag_coverage_ratio", 0)) * 4))
    score += int(round(float(presence.get("soft_tag_coverage_ratio", 0)) * 3))

    if str(trend.get("category", "")).lower() in {"sweet", "salty"}:
        score += 2

    if whitespace_tags and match_count:
        score += min(4, len(whitespace_tags))

    if pop_presence == LOW_PRESENCE:
        score -= 8
        if extension_friendly:
            score += 9
        if branch_out_worthy:
            score += GAP_SCORES[LOW_PRESENCE]
            score += min(3, len(whitespace_tags))

    return max(0, min(score, 25))


def _determine_action(trend: Dict, presence: Dict[str, object], feasibility: Dict[str, object]) -> str:
    if not feasibility.get("is_viable", False):
        return "deprioritize"

    timing_stage = str(trend.get("timing_stage", "")).upper()
    action_bias = str(trend.get("action_bias", "develop")).lower()
    whitespace_tags = set(presence.get("whitespace_tags", []))
    trend_tags = _specific_tags(trend.get("tags", []))
    strategic_fit = bool(trend_tags.intersection(POP_ADVANTAGE_TAGS))
    match_count = int(presence.get("match_count", 0))
    soft_match_count = int(presence.get("soft_match_count", 0))
    branch_out_worthy = _is_branch_out_worthy(trend, presence)
    extension_friendly = _is_extension_friendly(trend, presence)

    if timing_stage == "LATE":
        return "distribute" if match_count else "deprioritize"

    if presence.get("pop_presence") == LOW_PRESENCE and not branch_out_worthy:
        if extension_friendly:
            return "develop" if action_bias != "distribute" else "distribute"
        return "deprioritize"

    if presence.get("pop_presence") == LOW_PRESENCE and branch_out_worthy:
        return "distribute" if action_bias == "distribute" else "develop"

    if match_count and whitespace_tags:
        return "develop"

    if soft_match_count and extension_friendly:
        return "develop" if action_bias != "distribute" else "distribute"

    if action_bias == "distribute" and not strategic_fit:
        return "distribute"

    if strategic_fit or match_count:
        return "develop"

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
    soft_match_count = int(presence.get("soft_match_count", 0))
    timing_stage = str(trend.get("timing_stage", "")).upper()
    branch_out_worthy = _is_branch_out_worthy(trend, presence)
    extension_friendly = _is_extension_friendly(trend, presence)

    if whitespace_tags:
        whitespace_line = (
            f"Key whitespace for POP includes {', '.join(whitespace_tags[:3])}."
        )
    else:
        whitespace_line = "POP already covers much of this trend's flavor space."

    if match_count:
        overlap_line = (
            f"POP has {match_count} adjacent product match"
            f"{'' if match_count == 1 else 'es'}, so this can be approached as a tweak to the current portfolio instead of a full branch-out."
        )
    else:
        overlap_line = (
            "POP has little direct overlap today, so this would require moving into a newer area."
        )
        if soft_match_count:
            overlap_line = (
                f"POP has limited direct overlap today, but {soft_match_count} existing product"
                f"{'' if soft_match_count == 1 else 's'} suggest a related portfolio adjacency."
            )

    if branch_out_worthy:
        safety_line = (
            "Even though adjacency is limited, the trend is strong enough to justify a measured branch-out."
        )
    elif extension_friendly:
        safety_line = (
            "Even with limited direct overlap, this still looks like a realistic tweak to POP's existing snack portfolio rather than a full new capability jump."
        )
    elif match_count:
        safety_line = (
            "That makes the safer strategy to modernize an existing POP product with trend-relevant tweaks."
        )
    else:
        safety_line = (
            "Because POP is slower to execute, the safer move is to avoid this unless the upside becomes exceptional."
        )

    if recommended_action == "develop":
        action_line = (
            "The best move is to develop a POP-led extension of an existing product while the timing window is still open."
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
        f"{overlap_line} {safety_line} {whitespace_line} "
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
    branch_out_worthy = _is_branch_out_worthy(enriched_trend, presence)
    extension_friendly = _is_extension_friendly(enriched_trend, presence)
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
        "soft_match_count": presence["soft_match_count"],
        "soft_matched_pop_products": presence["soft_matched_pop_products"],
        "soft_matched_tags": presence["soft_matched_tags"],
        "whitespace_tags": presence["whitespace_tags"],
        "strategic_fit_tags": strategic_fit_tags,
        "branch_out_worthy": branch_out_worthy,
        "extension_friendly": extension_friendly,
        "tag_coverage_ratio": presence["tag_coverage_ratio"],
        "soft_tag_coverage_ratio": presence["soft_tag_coverage_ratio"],
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
