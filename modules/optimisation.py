import random

from .aec_engine import generate_spatial_model, run_eurocode_analysis
from .cost import compute_boq


def _is_fallback_design(design):
    """Return True when the planner had to use its fallback layout."""
    planning = design.get("planning", {}) if isinstance(design, dict) else {}
    return str(planning.get("status", "")).upper() == "FALLBACK"


def _annotate_optimisation(design, *, confidence, status, reason, candidates):
    """Attach transparent optimisation metadata without changing the API."""
    design["optimisation"] = {
        "confidence": confidence,
        "status": status,
        "reason": reason,
        "candidate_count": candidates,
    }
    return design


def optimise_cost(
    domain,
    typology,
    country,
    soil_name,
    room_types,
    min_gfa=500,
    max_plot=5000,
):
    """Find the lowest-cost structurally acceptable concept.

    Fallback layouts are retained only as a last resort. A fallback concept
    can never displace a valid metric-planned concept simply because it costs
    less. The existing ``(design, cost)`` return shape is preserved.
    """
    best_valid = None
    best_valid_cost = float("inf")
    best_fallback = None
    best_fallback_cost = float("inf")
    valid_candidates = 0
    fallback_candidates = 0

    for _ in range(20):
        plot = random.randint(200, max_plot)
        floors = random.randint(1, 8)
        gfa = plot * 0.6 * floors
        if gfa < min_gfa:
            continue

        try:
            d = generate_spatial_model(
                domain,
                typology,
                plot,
                floors,
                baths=2,
                country=country,
                soil_name=soil_name,
                room_types=room_types,
                seed=random.randint(0, 1000),
            )
            ec = run_eurocode_analysis(d, domain)
        except (KeyError, TypeError, ValueError, ZeroDivisionError):
            continue

        if not isinstance(ec, dict) or ec.get("uls_status") != "PASS ✅":
            continue

        try:
            total_usd, _, _, _ = compute_boq(d, country)
            total_usd = float(total_usd)
        except (KeyError, TypeError, ValueError, ZeroDivisionError):
            continue

        if _is_fallback_design(d):
            fallback_candidates += 1
            if total_usd < best_fallback_cost:
                best_fallback_cost = total_usd
                best_fallback = d
        else:
            valid_candidates += 1
            if total_usd < best_valid_cost:
                best_valid_cost = total_usd
                best_valid = d

    if best_valid is not None:
        return (
            _annotate_optimisation(
                best_valid,
                confidence="HIGH",
                status="VALID",
                reason="Selected from structurally acceptable, metric-planned candidates.",
                candidates=valid_candidates,
            ),
            best_valid_cost,
        )

    if best_fallback is not None:
        return (
            _annotate_optimisation(
                best_fallback,
                confidence="LOW",
                status="FALLBACK",
                reason=(
                    "No valid metric-planned candidate passed the structural gate; "
                    "the lowest-cost fallback candidate was retained for review."
                ),
                candidates=fallback_candidates,
            ),
            best_fallback_cost,
        )

    return None, float("inf")
