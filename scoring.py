"""
Final scoring logic for POP's snack strategy engine.

This module is the orchestration layer that puts everything together.

It answers the business question:

    "Which opportunities should POP prioritize first?"

What it combines:
- trend strength
- trend momentum / timing advantage
- POP whitespace opportunity
- feasibility
- saturation and execution penalties

The scoring intentionally stays simple and explainable for a hackathon
prototype. The goal is not statistical perfection. The goal is to produce a
ranked list that reflects POP's real-world constraints:

- early-stage trends are more valuable than late ones
- POP must favor realistic, shelf-stable, mass-market opportunities
- low POP presence is a bonus when the trend is still actionable
- late or high-risk trends should be penalized
"""

from __future__ import annotations

from typing import Dict, List, Sequence

from gap_analysis import analyze_all_gaps, analyze_sample_gaps
from sample_data import POP_PRODUCTS, TRENDS


FINAL_SCORE_WEIGHTS = {
    "trend_strength": 0.30,
    "trend_momentum": 0.30,
    "feasibility": 0.20,
    "gap_opportunity": 0.20,
}

MAX_SATURATION_PENALTY = 30

TIME_TO_MARKET_RISK_PENALTY = {
    "Low": 0,
    "Medium": 4,
    "High": 8,
}

TIMING_STAGE_PENALTY = {
    "EARLY": 0,
    "MID": 4,
    "LATE": 10,
}

POP_PRESENCE_PENALTY = {
    "LOW": 6,
    "MEDIUM": 2,
    "HIGH": 1,
}


def _clamp(value: float, minimum: int, maximum: int) -> int:
    return int(max(minimum, min(round(value), maximum)))


def calculate_trend_strength_score(trend: Dict) -> int:
    """
    Score current demand strength from the growth curve on a 0-100 scale.

    This is the "how strong is this trend right now?" component. The score
    favors current demand, then uses average demand and recent movement as
    supporting signals. A trend can be promising without being maxed out.
    """
    growth = [float(value) for value in trend.get("growth", [])]
    if not growth:
        return 0

    latest_value = float(trend.get("trend_momentum", {}).get("latest_value", growth[-1]))
    average_value = float(
        trend.get("trend_momentum", {}).get("average_value", sum(growth) / len(growth))
    )
    recent_change = float(
        trend.get("trend_momentum", {}).get(
            "recent_change",
            growth[-1] - growth[-2] if len(growth) >= 2 else 0.0,
        )
    )
    momentum_ratio = float(trend.get("trend_momentum", {}).get("momentum_ratio", 1.0))

    recent_growth_score = min(max(recent_change * 5.0, 0.0), 100.0)
    acceleration_score = min(max(50.0 + ((momentum_ratio - 1.0) * 50.0), 0.0), 100.0)

    strength = (
        (latest_value * 0.45)
        + (average_value * 0.25)
        + (recent_growth_score * 0.20)
        + (acceleration_score * 0.10)
    )
    return _clamp(strength, 0, 100)


def calculate_trend_momentum_score(trend: Dict) -> int:
    """
    Convert timing into a 0-100 strategic momentum score.

    This is not just popularity. It rewards acceleration, runway before the
    trend peaks, and POP's ability to act before the window closes.
    """
    timing_stage = str(trend.get("timing_stage", "")).upper()
    time_to_peak = float(trend.get("time_to_peak_periods", 0))
    risk = str(trend.get("time_to_market_risk", "Medium")).title()
    momentum_ratio = float(trend.get("trend_momentum", {}).get("momentum_ratio", 1.0))

    stage_score = {
        "EARLY": 88.0,
        "MID": 68.0,
        "LATE": 35.0,
    }.get(timing_stage, 55.0)
    acceleration_score = min(max(50.0 + ((momentum_ratio - 1.0) * 50.0), 0.0), 100.0)
    runway_score = min(max((time_to_peak / 6.0) * 100.0, 0.0), 100.0)
    risk_score = {
        "Low": 90.0,
        "Medium": 65.0,
        "High": 35.0,
    }.get(risk, 65.0)

    momentum = (
        (stage_score * 0.45)
        + (acceleration_score * 0.25)
        + (runway_score * 0.20)
        + (risk_score * 0.10)
    )
    return _clamp(momentum, 0, 100)


def calculate_feasibility_component(trend: Dict) -> int:
    """
    Return the raw 0-100 feasibility score for weighted final scoring.
    """
    feasibility_score = float(trend.get("feasibility_score", 0))
    return _clamp(feasibility_score, 0, 100)


def calculate_gap_component(trend: Dict) -> int:
    """
    Return the raw 0-100 portfolio gap opportunity score for weighted scoring.
    """
    gap_opportunity_score = float(trend.get("gap_opportunity_score", 0))
    return _clamp(gap_opportunity_score, 0, 100)


def calculate_weighted_contribution(score: int, weight: float) -> int:
    """Convert a 0-100 score into its weighted final-score contribution."""
    return _clamp(float(score) * weight, 0, 100)


def calculate_saturation_penalty(trend: Dict) -> int:
    """
    Penalize trends that are harder for POP to capture in time.

    The penalty increases when:
    - the trend is late-cycle
    - time-to-market risk is high
    - POP has low adjacency, meaning POP would need to branch out
    - the opportunity is not feasible
    """
    timing_stage = str(trend.get("timing_stage", "")).upper()
    time_to_market_risk = str(trend.get("time_to_market_risk", "")).title()
    pop_presence = str(trend.get("pop_presence", "")).upper()
    branch_out_worthy = bool(trend.get("branch_out_worthy", False))
    extension_friendly = bool(trend.get("extension_friendly", False))
    match_count = int(trend.get("pop_match_count", 0))

    penalty = 0
    penalty += TIMING_STAGE_PENALTY.get(timing_stage, 4)
    penalty += TIME_TO_MARKET_RISK_PENALTY.get(time_to_market_risk, 4)
    penalty += POP_PRESENCE_PENALTY.get(pop_presence, 3)

    if pop_presence == "LOW" and extension_friendly:
        penalty += 2
    elif pop_presence == "LOW" and not branch_out_worthy:
        penalty += 7
    elif pop_presence == "LOW" and branch_out_worthy:
        penalty += 1

    if match_count == 0 and not extension_friendly:
        penalty += 3

    if str(trend.get("recommended_action", "")).lower() == "deprioritize":
        penalty += 4

    if not trend.get("is_feasible", False):
        penalty += 5

    return _clamp(penalty, 0, MAX_SATURATION_PENALTY)


def determine_opportunity_level(final_score: int, recommended_action: str) -> str:
    """Map the final score to a simple stakeholder-friendly label."""
    if final_score >= 70:
        return "High"
    if final_score >= 45:
        return "Medium"
    if recommended_action == "deprioritize" and final_score < 45:
        return "Low"
    if final_score >= 30:
        return "Medium"
    return "Low"


def build_scoring_reasoning(
    trend: Dict,
    trend_strength_score: int,
    trend_momentum_score: int,
    feasibility_component: int,
    gap_component: int,
    saturation_penalty: int,
    final_score: int,
) -> str:
    """Create a concise explanation of why the final score landed where it did."""
    recommended_action = trend.get("recommended_action", "develop")
    timing_stage = str(trend.get("timing_stage", "")).lower()
    pop_presence = str(trend.get("pop_presence", "")).lower()
    branch_out_worthy = bool(trend.get("branch_out_worthy", False))
    extension_friendly = bool(trend.get("extension_friendly", False))

    if pop_presence == "low" and not branch_out_worthy:
        if extension_friendly:
            adjacency_line = "The score is still penalized for low direct overlap, but this looks more like a realistic reformulation or line extension than a true branch-out."
        else:
            adjacency_line = "The score is held back because POP has limited adjacency and this is not strong enough to justify branching out."
    elif pop_presence == "low":
        adjacency_line = "The score still carries branch-out risk, but the trend is strong enough to earn an exception."
    else:
        adjacency_line = "The score benefits from adjacency to POP's existing portfolio, which supports safer product tweaks."

    return (
        f"{trend.get('name', 'This trend')} scores {final_score}/100 for POP. "
        f"The weighted average uses trend strength at {trend_strength_score}/100, "
        f"timing momentum at {trend_momentum_score}/100, feasibility at {feasibility_component}/100, "
        f"and portfolio-fit opportunity at {gap_component}/100. "
        f"A penalty of {saturation_penalty} is applied because the trend is {timing_stage}-stage "
        f"with {pop_presence} POP presence and {str(trend.get('time_to_market_risk', 'Medium')).lower()} "
        f"time-to-market risk. {adjacency_line} The best move is to {recommended_action}."
    )


def score_trend(trend: Dict) -> Dict:
    """
    Score one fully analyzed trend for POP.

    The input is expected to come from `gap_analysis.py`, but any dictionary
    with the required fields will work.
    """
    trend_strength_score = calculate_trend_strength_score(trend)
    trend_momentum_score = calculate_trend_momentum_score(trend)
    feasibility_component = calculate_feasibility_component(trend)
    gap_component = calculate_gap_component(trend)
    saturation_penalty = calculate_saturation_penalty(trend)

    weighted_contributions = {
        "trend_strength": calculate_weighted_contribution(
            trend_strength_score,
            FINAL_SCORE_WEIGHTS["trend_strength"],
        ),
        "trend_momentum": calculate_weighted_contribution(
            trend_momentum_score,
            FINAL_SCORE_WEIGHTS["trend_momentum"],
        ),
        "feasibility": calculate_weighted_contribution(
            feasibility_component,
            FINAL_SCORE_WEIGHTS["feasibility"],
        ),
        "gap_opportunity": calculate_weighted_contribution(
            gap_component,
            FINAL_SCORE_WEIGHTS["gap_opportunity"],
        ),
    }
    base_score = sum(weighted_contributions.values())
    final_score = _clamp(base_score - saturation_penalty, 0, 100)

    recommended_action = str(trend.get("recommended_action", "develop")).lower()
    opportunity_level = determine_opportunity_level(final_score, recommended_action)

    return {
        **trend,
        "trend_strength_score": trend_strength_score,
        "trend_momentum_score": trend_momentum_score,
        "feasibility_component": feasibility_component,
        "gap_component_score": gap_component,
        "weighted_score_before_penalty": base_score,
        "weighted_score_contributions": weighted_contributions,
        "saturation_penalty": saturation_penalty,
        "final_score": final_score,
        "opportunity_level": opportunity_level,
        "scoring_summary": build_scoring_reasoning(
            trend=trend,
            trend_strength_score=trend_strength_score,
            trend_momentum_score=trend_momentum_score,
            feasibility_component=feasibility_component,
            gap_component=gap_component,
            saturation_penalty=saturation_penalty,
            final_score=final_score,
        ),
    }


def score_all_trends(
    trends: Sequence[Dict] | None = None,
    pop_products: Sequence[Dict] | None = None,
    *,
    already_analyzed: bool = False,
) -> List[Dict]:
    """
    Score every trend and return them ranked from best to worst.

    By default, raw trends are first enriched through `gap_analysis.py`.
    Pass `already_analyzed=True` if the input already contains the expected
    gap-analysis fields.
    """
    trends = list(trends or TRENDS)
    pop_products = pop_products or POP_PRODUCTS
    analyzed_trends = trends if already_analyzed else analyze_all_gaps(trends, pop_products=pop_products)
    scored = [score_trend(trend) for trend in analyzed_trends]
    return sorted(scored, key=lambda item: item["final_score"], reverse=True)


def score_sample_trends(pop_products: Sequence[Dict] | None = None) -> List[Dict]:
    """Convenience helper for the mock POP prototype data."""
    pop_products = pop_products or POP_PRODUCTS
    return score_all_trends(
        TRENDS,
        pop_products=pop_products,
        already_analyzed=False,
    )


__all__ = [
    "build_scoring_reasoning",
    "calculate_feasibility_component",
    "calculate_gap_component",
    "calculate_saturation_penalty",
    "calculate_trend_momentum_score",
    "calculate_trend_strength_score",
    "calculate_weighted_contribution",
    "determine_opportunity_level",
    "FINAL_SCORE_WEIGHTS",
    "score_all_trends",
    "score_sample_trends",
    "score_trend",
]
