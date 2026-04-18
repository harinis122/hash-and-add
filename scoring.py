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

from statistics import mean
from typing import Dict, List, Sequence

from gap_analysis import analyze_all_gaps, analyze_sample_gaps
from sample_data import TRENDS


MAX_TREND_STRENGTH = 25
MAX_FEASIBILITY_COMPONENT = 25
MAX_SATURATION_PENALTY = 20

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
    "LOW": 0,
    "MEDIUM": 3,
    "HIGH": 7,
}


def _clamp(value: float, minimum: int, maximum: int) -> int:
    return int(max(minimum, min(round(value), maximum)))


def calculate_trend_strength_score(trend: Dict) -> int:
    """
    Score current demand strength from the growth curve.

    This is the "how strong is this trend right now?" component. We reward:
    - strong latest demand
    - solid average demand across the series
    - healthy recent acceleration
    """
    growth = [float(value) for value in trend.get("growth", [])]
    if not growth:
        return 0

    latest_value = float(trend.get("trend_momentum", {}).get("latest_value", growth[-1]))
    average_value = float(trend.get("trend_momentum", {}).get("average_value", mean(growth)))
    recent_change = float(
        trend.get("trend_momentum", {}).get(
            "recent_change",
            growth[-1] - growth[-2] if len(growth) >= 2 else 0.0,
        )
    )

    strength = (latest_value * 0.18) + (average_value * 0.08) + (recent_change * 0.45)
    return _clamp(strength, 0, MAX_TREND_STRENGTH)


def calculate_trend_momentum_score(trend: Dict) -> int:
    """
    Reuse the forecast timing advantage as the momentum component.

    This keeps the score aligned with POP's most important constraint:
    early timing is strategically more valuable than peak popularity.
    """
    return _clamp(float(trend.get("timing_advantage_score", 0)), 0, 30)


def calculate_feasibility_component(trend: Dict) -> int:
    """
    Normalize the 0-100 feasibility score into a 0-25 scoring component.

    The raw feasibility score is still preserved on the output, but the final
    opportunity score needs balanced components so one field does not dominate.
    """
    feasibility_score = float(trend.get("feasibility_score", 0))
    return _clamp((feasibility_score / 100) * MAX_FEASIBILITY_COMPONENT, 0, MAX_FEASIBILITY_COMPONENT)


def calculate_saturation_penalty(trend: Dict) -> int:
    """
    Penalize trends that are harder for POP to capture in time.

    The penalty increases when:
    - the trend is late-cycle
    - time-to-market risk is high
    - POP already has high presence, meaning the whitespace is smaller
    - the opportunity is not feasible
    """
    timing_stage = str(trend.get("timing_stage", "")).upper()
    time_to_market_risk = str(trend.get("time_to_market_risk", "")).title()
    pop_presence = str(trend.get("pop_presence", "")).upper()

    penalty = 0
    penalty += TIMING_STAGE_PENALTY.get(timing_stage, 4)
    penalty += TIME_TO_MARKET_RISK_PENALTY.get(time_to_market_risk, 4)
    penalty += POP_PRESENCE_PENALTY.get(pop_presence, 3)

    if not trend.get("is_feasible", False):
        penalty += 5

    return _clamp(penalty, 0, MAX_SATURATION_PENALTY)


def determine_opportunity_level(final_score: int, recommended_action: str) -> str:
    """Map the final score to a simple stakeholder-friendly label."""
    if recommended_action == "deprioritize":
        return "Low"
    if final_score >= 60:
        return "High"
    if final_score >= 40:
        return "Medium"
    return "Low"


def build_scoring_reasoning(
    trend: Dict,
    trend_strength_score: int,
    trend_momentum_score: int,
    feasibility_component: int,
    saturation_penalty: int,
    final_score: int,
) -> str:
    """Create a concise explanation of why the final score landed where it did."""
    recommended_action = trend.get("recommended_action", "develop")
    timing_stage = str(trend.get("timing_stage", "")).lower()
    pop_presence = str(trend.get("pop_presence", "")).lower()

    return (
        f"{trend.get('name', 'This trend')} scores {final_score}/100 for POP. "
        f"Trend strength contributes {trend_strength_score}, timing momentum contributes {trend_momentum_score}, "
        f"feasibility contributes {feasibility_component}, and whitespace contributes "
        f"{trend.get('gap_opportunity_score', 0)}. "
        f"A penalty of {saturation_penalty} is applied because the trend is {timing_stage}-stage "
        f"with {pop_presence} POP presence and {str(trend.get('time_to_market_risk', 'Medium')).lower()} "
        f"time-to-market risk. The best move is to {recommended_action}."
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
    gap_opportunity_score = _clamp(float(trend.get("gap_opportunity_score", 0)), 0, 25)
    saturation_penalty = calculate_saturation_penalty(trend)

    base_score = (
        trend_strength_score
        + trend_momentum_score
        + feasibility_component
        + gap_opportunity_score
    )
    final_score = _clamp(base_score - saturation_penalty, 0, 100)

    recommended_action = str(trend.get("recommended_action", "develop")).lower()
    opportunity_level = determine_opportunity_level(final_score, recommended_action)

    return {
        **trend,
        "trend_strength_score": trend_strength_score,
        "trend_momentum_score": trend_momentum_score,
        "feasibility_component": feasibility_component,
        "saturation_penalty": saturation_penalty,
        "final_score": final_score,
        "opportunity_level": opportunity_level,
        "scoring_summary": build_scoring_reasoning(
            trend=trend,
            trend_strength_score=trend_strength_score,
            trend_momentum_score=trend_momentum_score,
            feasibility_component=feasibility_component,
            saturation_penalty=saturation_penalty,
            final_score=final_score,
        ),
    }


def score_all_trends(
    trends: Sequence[Dict] | None = None,
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
    analyzed_trends = trends if already_analyzed else analyze_all_gaps(trends)
    scored = [score_trend(trend) for trend in analyzed_trends]
    return sorted(scored, key=lambda item: item["final_score"], reverse=True)


def score_sample_trends() -> List[Dict]:
    """Convenience helper for the mock POP prototype data."""
    return score_all_trends(analyze_sample_gaps(), already_analyzed=True)


__all__ = [
    "build_scoring_reasoning",
    "calculate_feasibility_component",
    "calculate_saturation_penalty",
    "calculate_trend_momentum_score",
    "calculate_trend_strength_score",
    "determine_opportunity_level",
    "score_all_trends",
    "score_sample_trends",
    "score_trend",
]
