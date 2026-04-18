"""
Forecasting utilities for POP's snack trend strategy engine.

This module answers the timing question behind every opportunity:

    "Is this trend early enough for POP to act before competitors?"

POP is slower to execute than many competitors because of regulatory,
labeling, sourcing, and operational constraints. That means a trend's
current popularity is not enough on its own. We also need to estimate
where the trend sits in its lifecycle and whether POP still has enough
time to respond before the market peaks or becomes saturated.

What this module does:
- reads trend growth series
- classifies timing as EARLY, MID, or LATE
- produces a timing advantage score
- estimates time-to-market risk for POP
- returns plain-language reasoning for the UI and downstream scoring

The functions here intentionally stay simple and explainable because this
project is a hackathon prototype using mock data.
"""

from __future__ import annotations

from statistics import mean
from typing import Dict, Iterable, List, Sequence

from sample_data import POP_PRODUCTS, TRENDS


EARLY = "EARLY"
MID = "MID"
LATE = "LATE"

TREND_LABELS = {
    EARLY: {
        "timing_advantage_score": 30,
        "window": "High strategic value",
        "guidance": "Act now while POP still has room to build or source ahead of the market peak.",
    },
    MID: {
        "timing_advantage_score": 18,
        "window": "Medium strategic value",
        "guidance": "Move quickly. The trend is viable, but the execution window is narrowing.",
    },
    LATE: {
        "timing_advantage_score": 6,
        "window": "Low strategic value",
        "guidance": "Deprioritize unless POP can distribute an existing product immediately.",
    },
}

GENERIC_TAGS = {
    "sweet",
    "salty",
    "functional",
    "natural",
    "wellness",
    "snack",
}


def _validate_growth(growth: Sequence[float]) -> List[float]:
    """Normalize and validate a growth series. Make sure it has enough data points and no negative values."""
    if len(growth) < 3:
        raise ValueError("Growth data must contain at least three time points.")

    normalized = [float(value) for value in growth]
    if any(value < 0 for value in normalized):
        raise ValueError("Growth values must be non-negative.")
    return normalized


def _deltas(growth: Sequence[float]) -> List[float]:
    """Return period-over-period changes."""
    return [growth[index + 1] - growth[index] for index in range(len(growth) - 1)]


def _safe_mean(values: Sequence[float]) -> float:
    return mean(values) if values else 0.0


def _compute_presence_overlap(trend_tags: Iterable[str], products: Sequence[Dict]) -> Dict[str, object]:
    """
    Measure how much POP already overlaps with the trend.

    Timing does not depend on POP presence, but the explanation should
    reflect whether POP has adjacent products that could speed execution.
    """
    normalized_trend_tags = {
        tag.lower() for tag in trend_tags if tag.lower() not in GENERIC_TAGS
    }
    matching_products = []

    for product in products:
        product_tags = {
            tag.lower() for tag in product.get("tags", []) if tag.lower() not in GENERIC_TAGS
        }
        overlap = normalized_trend_tags.intersection(product_tags)
        if overlap:
            matching_products.append(
                {
                    "name": product.get("name", "Unknown Product"),
                    "matched_tags": sorted(overlap),
                }
            )

    return {
        "matching_products": matching_products,
        "match_count": len(matching_products),
        "has_execution_head_start": bool(matching_products),
    }


def determine_trend_timing(growth: Sequence[float]) -> Dict[str, float | str]:
    """
    Classify a trend as EARLY, MID, or LATE using simple curve heuristics.

    Heuristic summary:
    - EARLY: still building, lower absolute penetration, meaningful runway left
    - MID: strong and still growing, but not as early as before
    - LATE: high penetration with slowing momentum, closer to saturation
    """
    series = _validate_growth(growth)
    growth_changes = _deltas(series)

    latest_value = series[-1]
    max_value = max(series) or 1.0
    average_value = _safe_mean(series)
    early_change = _safe_mean(growth_changes[:2])
    recent_change = _safe_mean(growth_changes[-2:])
    slope_ratio = recent_change / max(early_change, 1.0)
    latest_vs_average = latest_value / max(average_value, 1.0)

    # A simple saturation proxy: very high current level + decelerating slope.
    is_slowing = slope_ratio < 0.9
    is_accelerating = slope_ratio > 1.1

    if latest_value < 45 and latest_vs_average < 1.4:
        stage = EARLY
    elif latest_value >= 65 and is_slowing:
        stage = LATE
    elif latest_value >= 70 and not is_accelerating:
        stage = LATE
    else:
        stage = MID

    projected_next_change = max(recent_change - max(early_change - recent_change, 0), 0)
    time_to_peak_periods = round(max((100 - latest_value) / max(projected_next_change, 1.0), 0), 1)

    return {
        "stage": stage,
        "latest_value": round(latest_value, 2),
        "average_value": round(average_value, 2),
        "early_change": round(early_change, 2),
        "recent_change": round(recent_change, 2),
        "momentum_ratio": round(slope_ratio, 2),
        "time_to_peak_periods": time_to_peak_periods,
    }


def assess_time_to_market_risk(stage: str, has_execution_head_start: bool) -> str:
    """
    Translate timing into POP-specific execution risk.

    POP can move slightly faster when a trend overlaps with existing products
    or ingredients, because the team can distribute or adapt adjacent items
    rather than inventing something from scratch.
    """
    if stage == EARLY:
        return "Medium" if has_execution_head_start else "Low"
    if stage == MID:
        return "Medium" if has_execution_head_start else "High"
    return "High"


def build_timing_reasoning(
    trend_name: str,
    timing_data: Dict[str, float | str],
    presence_data: Dict[str, object],
) -> str:
    """Create a short explanation that a non-technical POP stakeholder can understand."""
    stage = str(timing_data["stage"])
    recent_change = float(timing_data["recent_change"])
    latest_value = float(timing_data["latest_value"])
    match_count = int(presence_data["match_count"])

    if stage == EARLY:
        stage_reason = (
            f"{trend_name} is still in an early build phase. "
            f"Current strength is moderate at {latest_value:.0f}, which suggests room to grow before saturation."
        )
    elif stage == MID:
        stage_reason = (
            f"{trend_name} is in the middle of its growth cycle. "
            f"It already shows solid demand at {latest_value:.0f}, so POP needs to move quickly."
        )
    else:
        stage_reason = (
            f"{trend_name} looks late-cycle. "
            f"Demand is already high at {latest_value:.0f}, which reduces POP's timing advantage."
        )

    momentum_reason = f"Recent growth increased by about {recent_change:.0f} points per period."

    if match_count:
        presence_reason = (
            f"POP already has {match_count} adjacent product match"
            f"{'' if match_count == 1 else 'es'}, which can shorten execution time."
        )
    else:
        presence_reason = "POP has no close product overlap, so acting will require more lead time."

    return " ".join([stage_reason, momentum_reason, presence_reason])


def forecast_trend_timing(trend: Dict, pop_products: Sequence[Dict] | None = None) -> Dict:
    """
    Forecast one trend's timing and execution window for POP.

    Returns a single enriched trend record that downstream modules can use
    for scoring, gap analysis, and UI rendering.
    """
    pop_products = pop_products or POP_PRODUCTS
    timing_data = determine_trend_timing(trend.get("growth", []))
    presence_data = _compute_presence_overlap(trend.get("tags", []), pop_products)

    stage = str(timing_data["stage"])
    stage_metadata = TREND_LABELS[stage]
    time_to_market_risk = assess_time_to_market_risk(
        stage=stage,
        has_execution_head_start=bool(presence_data["has_execution_head_start"]),
    )

    action_bias = "develop"
    if stage == MID and not presence_data["has_execution_head_start"]:
        action_bias = "distribute"
    elif stage == LATE:
        action_bias = "distribute"

    explanation = build_timing_reasoning(
        trend_name=trend.get("name", "Unknown Trend"),
        timing_data=timing_data,
        presence_data=presence_data,
    )

    return {
        **trend,
        "timing_stage": stage,
        "timing_window": stage_metadata["window"],
        "timing_advantage_score": stage_metadata["timing_advantage_score"],
        "time_to_peak_periods": timing_data["time_to_peak_periods"],
        "time_to_market_risk": time_to_market_risk,
        "recommended_speed": "Move now" if stage != LATE else "Only pursue if POP can move immediately",
        "action_bias": action_bias,
        "pop_match_count": presence_data["match_count"],
        "pop_matching_products": presence_data["matching_products"],
        "forecast_summary": explanation,
        "timing_guidance": stage_metadata["guidance"],
        "trend_momentum": {
            "latest_value": timing_data["latest_value"],
            "average_value": timing_data["average_value"],
            "early_change": timing_data["early_change"],
            "recent_change": timing_data["recent_change"],
            "momentum_ratio": timing_data["momentum_ratio"],
        },
    }


def forecast_all_trends(
    trends: Sequence[Dict] | None = None,
    pop_products: Sequence[Dict] | None = None,
) -> List[Dict]:
    """Forecast timing for every trend in the dataset."""
    trends = trends or TRENDS
    pop_products = pop_products or POP_PRODUCTS
    return [forecast_trend_timing(trend, pop_products=pop_products) for trend in trends]


def summarize_timing_counts(forecasts: Sequence[Dict]) -> Dict[str, int]:
    """Provide a quick count of how many trends fall into each timing stage."""
    summary = {EARLY: 0, MID: 0, LATE: 0}
    for forecast in forecasts:
        stage = forecast.get("timing_stage")
        if stage in summary:
            summary[stage] += 1
    return summary


__all__ = [
    "EARLY",
    "MID",
    "LATE",
    "assess_time_to_market_risk",
    "determine_trend_timing",
    "forecast_all_trends",
    "forecast_trend_timing",
    "summarize_timing_counts",
]



'''
Expected return value:
{
    "name": "Salty Protein Snacks",
    "category": "salty",
    "growth": [10, 20, 35, 50, 70],
    "description": "...",
    "risk": "Medium",
    "tags": ["protein", "sweet", "salty", "functional"],

    "timing_stage": "MID",
    "timing_window": "Medium strategic value",
    "timing_advantage_score": 18,
    "time_to_peak_periods": 1.7,
    "time_to_market_risk": "High",
    "recommended_speed": "Move now",
    "action_bias": "distribute",
    "pop_match_count": 0,
    "pop_matching_products": [],
    "forecast_summary": "...plain English explanation...",
    "timing_guidance": "Move quickly. The trend is viable, but the execution window is narrowing.",
    "trend_momentum": {
        "latest_value": 70.0,
        "average_value": 37.0,
        "early_change": 12.5,
        "recent_change": 17.5,
        "momentum_ratio": 1.4
    }


'''