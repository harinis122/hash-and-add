"""
Feasibility rules for POP's snack strategy engine.

This module answers the operational question behind each trend:

    "Can POP realistically execute this opportunity?"

It is intentionally heuristic and explainable. We are not trying to model
real manufacturing or FDA review in full detail. Instead, we provide a
business-friendly screening layer that checks whether a forecasted trend is
practical for POP's current snack strategy.

What this module checks:
- shelf stability
- scalability
- cost feasibility
- basic regulatory safety

What it returns:
- an overall feasibility score
- a feasibility status
- individual constraint checks with reasons
- constraint flags for risky trends
- plain-English summary for the UI and scoring layer
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Sequence

from sample_data import POP_PRODUCTS


MAX_CHECK_SCORE = 25
DEFAULT_PASSING_SCORE = 65

RISK_PENALTY = {
    "Low": 0,
    "Medium": 3,
    "High": 7,
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

HIGH_COMPLEXITY_TAGS = {
    "collagen",
    "fermented",
    "gut health",
    "meat",
    "probiotic",
    "protein",
}

HIGH_COST_TAGS = {
    "adaptogen",
    "collagen",
    "mushroom",
    "protein",
    "probiotic",
}

REGULATORY_SENSITIVITY_TAGS = {
    "adaptogen",
    "cbd",
    "collagen",
    "fermented",
    "functional",
    "gut health",
    "hemp",
    "kava",
    "probiotic",
}

RESTRICTED_TAGS = {
    "cbd",
    "hemp",
    "kratom",
}

LOW_SHELF_STABILITY_TAGS = {
    "fresh",
    "probiotic",
    "refrigerated",
    "yogurt",
}


def _normalize_tags(tags: Iterable[str]) -> set[str]:
    return {str(tag).strip().lower() for tag in tags if str(tag).strip()}


def _clamp_score(value: float, minimum: int = 0, maximum: int = MAX_CHECK_SCORE) -> int:
    return int(max(minimum, min(round(value), maximum)))


def _pop_overlap_count(trend: Dict, pop_products: Sequence[Dict]) -> int:
    existing_count = trend.get("pop_match_count")
    if isinstance(existing_count, int):
        return existing_count

    trend_tags = _normalize_tags(trend.get("tags", []))
    match_count = 0
    for product in pop_products:
        product_tags = _normalize_tags(product.get("tags", []))
        if trend_tags.intersection(product_tags):
            match_count += 1
    return match_count


def assess_shelf_stability(trend: Dict) -> Dict[str, object]:
    """
    Check whether the trend fits POP's shelf-stable snack requirement.

    Sweet and salty packaged snacks start from a strong baseline. The score
    falls when tags imply refrigeration, live cultures, or short shelf life.
    """
    tags = _normalize_tags(trend.get("tags", []))
    category = str(trend.get("category", "")).lower()

    score = 20 if category in {"sweet", "salty"} else 12
    reasons = ["Shelf-stable sweet/salty snacks fit POP's core category focus."]
    flags: List[str] = []

    unstable_tags = sorted(tags.intersection(LOW_SHELF_STABILITY_TAGS))
    if unstable_tags:
        score -= 10
        flags.append("Shelf-life risk")
        reasons.append(
            f"Tags like {', '.join(unstable_tags)} suggest shorter shelf life or cold-chain complexity."
        )

    if "fermented" in tags or "gut health" in tags:
        score -= 5
        flags.append("Stability validation needed")
        reasons.append(
            "Fermented and gut-health positioning often needs extra formulation work to stay stable on shelf."
        )

    if {"umami", "seaweed", "ginger", "tea"}.intersection(tags):
        score += 3
        reasons.append("Dry flavor formats already align with packaged, shelf-stable products.")

    score = _clamp_score(score)
    status = "Pass" if score >= 18 else "Watch" if score >= 12 else "Fail"
    return {
        "score": score,
        "status": status,
        "reason": " ".join(reasons),
        "flags": flags,
    }


def assess_scalability(trend: Dict, pop_products: Sequence[Dict] | None = None) -> Dict[str, object]:
    """
    Estimate how easily POP can source, make, and ship the trend at scale.

    Existing POP adjacency helps. High-complexity functional formats lower the
    score because they often require more technical sourcing or manufacturing.
    """
    pop_products = pop_products or POP_PRODUCTS
    tags = _normalize_tags(trend.get("tags", []))
    match_count = _pop_overlap_count(trend, pop_products)
    stage = str(trend.get("timing_stage", "")).upper()

    score = 17
    reasons = ["The trend is in POP's shelf-stable snack scope, so baseline scale-up is possible."]
    flags: List[str] = []

    complexity_tags = sorted(tags.intersection(HIGH_COMPLEXITY_TAGS))
    if complexity_tags:
        score -= min(8, len(complexity_tags) * 3)
        flags.append("Manufacturing complexity")
        reasons.append(
            f"Tags like {', '.join(complexity_tags)} raise sourcing or formulation complexity."
        )

    if match_count:
        score += min(6, match_count * 2)
        reasons.append(
            f"POP already has {match_count} adjacent product match"
            f"{'' if match_count == 1 else 'es'}, which reduces ramp-up friction."
        )
    else:
        score -= 3
        reasons.append("POP has limited direct adjacency, so supplier setup will likely take longer.")

    if stage == "LATE":
        score -= 2
        flags.append("Window may close before scale-up")
        reasons.append("Late-cycle trends leave less room for POP's slower execution process.")

    score = _clamp_score(score)
    status = "Pass" if score >= 17 else "Watch" if score >= 11 else "Fail"
    return {
        "score": score,
        "status": status,
        "reason": " ".join(reasons),
        "flags": flags,
    }


def assess_cost_feasibility(trend: Dict, pop_products: Sequence[Dict] | None = None) -> Dict[str, object]:
    """
    Estimate whether the idea can stay affordable for POP's mass-market model.

    The prototype assumes POP wants accessible price points, so premium
    functional ingredients reduce the score while POP-native ingredients help.
    """
    pop_products = pop_products or POP_PRODUCTS
    tags = _normalize_tags(trend.get("tags", []))
    match_count = _pop_overlap_count(trend, pop_products)

    score = 18
    reasons = ["The trend can start from a mainstream snack price point if ingredients stay simple."]
    flags: List[str] = []

    expensive_tags = sorted(tags.intersection(HIGH_COST_TAGS))
    if expensive_tags:
        score -= min(8, len(expensive_tags) * 3)
        flags.append("Cost pressure")
        reasons.append(
            f"Tags like {', '.join(expensive_tags)} often carry higher ingredient or processing costs."
        )

    if tags.intersection(POP_ADVANTAGE_TAGS):
        score += 3
        reasons.append("POP has existing flavor and sourcing familiarity in this ingredient space.")

    if match_count:
        score += 2
        reasons.append("Existing adjacency can reduce minimum-order and sourcing risk.")

    score -= RISK_PENALTY.get(str(trend.get("risk", "Medium")).title(), 3)
    score = _clamp_score(score)
    status = "Pass" if score >= 17 else "Watch" if score >= 11 else "Fail"
    return {
        "score": score,
        "status": status,
        "reason": " ".join(reasons),
        "flags": flags,
    }


def assess_regulatory_safety(trend: Dict) -> Dict[str, object]:
    """
    Apply a basic FDA-oriented screening rule.

    This does not replace legal review. It simply downgrades trends that are
    more likely to need claim controls, ingredient review, or additional
    regulatory diligence.
    """
    tags = _normalize_tags(trend.get("tags", []))
    score = 20
    reasons = ["The concept appears compatible with standard packaged-food labeling."]
    flags: List[str] = []

    restricted_tags = sorted(tags.intersection(RESTRICTED_TAGS))
    if restricted_tags:
        score = 0
        flags.append("Restricted ingredient concern")
        reasons.append(
            f"Tags like {', '.join(restricted_tags)} create major regulatory risk for POP."
        )
    else:
        sensitivity_tags = sorted(tags.intersection(REGULATORY_SENSITIVITY_TAGS))
        if sensitivity_tags:
            score -= min(8, len(sensitivity_tags) * 2)
            flags.append("Claim / compliance review needed")
            reasons.append(
                f"Tags like {', '.join(sensitivity_tags)} may need tighter claim language and compliance review."
            )

        score -= RISK_PENALTY.get(str(trend.get("risk", "Medium")).title(), 3)
        if str(trend.get("time_to_market_risk", "")).title() == "High":
            score -= 2
            reasons.append("Tighter timing raises execution pressure around review, labeling, and sourcing.")

    score = _clamp_score(score)
    status = "Pass" if score >= 16 else "Watch" if score >= 10 else "Fail"
    return {
        "score": score,
        "status": status,
        "reason": " ".join(reasons),
        "flags": flags,
    }


def calculate_feasibility_score(checks: Dict[str, Dict[str, object]]) -> int:
    """Combine all constraint checks into a single 0-100 feasibility score."""
    total = sum(int(check["score"]) for check in checks.values())
    return _clamp_score(total, minimum=0, maximum=100)


def feasibility_status_from_score(score: int) -> str:
    """Translate the overall score into an easy business label."""
    if score >= 80:
        return "Strong"
    if score >= DEFAULT_PASSING_SCORE:
        return "Moderate"
    if score >= 45:
        return "Borderline"
    return "Weak"


def build_feasibility_summary(
    trend: Dict,
    checks: Dict[str, Dict[str, object]],
    feasibility_score: int,
    feasibility_status: str,
) -> str:
    """Create a concise explanation that POP buyers can understand quickly."""
    watch_or_fail = [
        label.replace("_", " ")
        for label, check in checks.items()
        if check["status"] in {"Watch", "Fail"}
    ]
    if not watch_or_fail:
        constraint_line = "The main operating constraints look manageable for POP."
    else:
        constraint_line = (
            "Key watchouts are "
            + ", ".join(watch_or_fail[:-1] + ([f"and {watch_or_fail[-1]}"] if len(watch_or_fail) > 1 else watch_or_fail))
            + "."
        )

    action_bias = trend.get("action_bias", "develop")
    action_line = (
        "The current timing favors a fast distribution move."
        if action_bias == "distribute"
        else "The current timing still leaves room for POP to develop a differentiated product."
    )

    return (
        f"{trend.get('name', 'This trend')} has {feasibility_status.lower()} feasibility "
        f"for POP with a score of {feasibility_score}/100. "
        f"{constraint_line} {action_line}"
    )


def evaluate_trend_constraints(
    trend: Dict,
    pop_products: Sequence[Dict] | None = None,
    minimum_score: int = DEFAULT_PASSING_SCORE,
) -> Dict:
    """
    Enrich one forecasted trend with feasibility checks.

    The input is expected to be the forecasted trend record from
    `forecasting.py`, but the function also works on the raw mock trend data.
    """
    pop_products = pop_products or POP_PRODUCTS
    checks = {
        "shelf_stability": assess_shelf_stability(trend),
        "scalability": assess_scalability(trend, pop_products=pop_products),
        "cost_feasibility": assess_cost_feasibility(trend, pop_products=pop_products),
        "regulatory_safety": assess_regulatory_safety(trend),
    }

    feasibility_score = calculate_feasibility_score(checks)
    feasibility_status = feasibility_status_from_score(feasibility_score)
    all_flags = sorted(
        {
            flag
            for check in checks.values()
            for flag in check.get("flags", [])
            if isinstance(flag, str) and flag
        }
    )
    is_viable = feasibility_score >= minimum_score and all(
        check["status"] != "Fail" for check in checks.values()
    )

    recommendation = str(trend.get("action_bias", "develop"))
    if not is_viable and recommendation == "develop":
        recommendation = "distribute" if trend.get("timing_stage") == "MID" else "deprioritize"
    elif not is_viable:
        recommendation = "deprioritize"

    return {
        **trend,
        "constraint_checks": checks,
        "constraint_flags": all_flags,
        "feasibility_score": feasibility_score,
        "feasibility_status": feasibility_status,
        "is_viable": is_viable,
        "constraint_recommendation": recommendation,
        "feasibility_summary": build_feasibility_summary(
            trend=trend,
            checks=checks,
            feasibility_score=feasibility_score,
            feasibility_status=feasibility_status,
        ),
    }


def evaluate_all_constraints(
    trends: Sequence[Dict],
    pop_products: Sequence[Dict] | None = None,
    minimum_score: int = DEFAULT_PASSING_SCORE,
) -> List[Dict]:
    """Evaluate feasibility for every trend in a list."""
    return [
        evaluate_trend_constraints(
            trend,
            pop_products=pop_products,
            minimum_score=minimum_score,
        )
        for trend in trends
    ]


__all__ = [
    "DEFAULT_PASSING_SCORE",
    "assess_cost_feasibility",
    "assess_regulatory_safety",
    "assess_scalability",
    "assess_shelf_stability",
    "build_feasibility_summary",
    "calculate_feasibility_score",
    "evaluate_all_constraints",
    "evaluate_trend_constraints",
    "feasibility_status_from_score",
]
