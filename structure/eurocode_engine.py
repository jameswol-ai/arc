import math

# =========================================================
# 🏗️ EUROCODE-LIKE STRUCTURAL CHECK ENGINE (SIMPLIFIED)
# =========================================================

# Partial safety factors (simplified Eurocode style)
GAMMA_G = 1.35   # permanent loads
GAMMA_Q = 1.50   # variable loads


# =========================
# LOAD COMBINATION (ULS)
# =========================
def ultimate_limit_state(dead_load, live_load):
    """
    Eurocode-style ultimate load combination:
    1.35G + 1.5Q
    """
    return GAMMA_G * dead_load + GAMMA_Q * live_load


# =========================
# BEAM DEFLECTION CHECK
# =========================
def beam_deflection(span_m, load_kN, E=25e6, I=8e-6):
    """
    Simplified mid-span deflection (simply supported beam)
    δ = (5 w L^4) / (384 E I)
    """
    w = load_kN * 1000  # convert to N approx
    delta = (5 * w * span_m**4) / (384 * E * I)
    return delta


def check_deflection(span_m, load_kN):
    delta = beam_deflection(span_m, load_kN)

    limit = span_m / 250  # Eurocode typical serviceability limit
    return {
        "deflection_mm": delta * 1000,
        "limit_mm": limit * 1000,
        "pass": delta < limit
    }


# =========================
# COLUMN BUCKLING (EULER)
# =========================
def euler_buckling_capacity(E=25e6, I=8e-6, L=3.0):
    """
    Pcr = (π² E I) / (L²)
    """
    return (math.pi**2 * E * I) / (L**2)


def check_column(load_kN, height_m):
    capacity = euler_buckling_capacity(L=height_m)

    utilization = (load_kN * 1000) / capacity

    return {
        "capacity_kN": capacity / 1000,
        "utilization": utilization,
        "safe": utilization < 1.0
    }


# =========================
# SLAB THICKNESS RULE (HEURISTIC Eurocode-style)
# =========================
def slab_thickness(span_m):
    """
    Rule-of-thumb (Eurocode practice approximation):
    simply supported slab: L/20
    continuous slab: L/26
    """
    return {
        "simply_supported_mm": (span_m / 20) * 1000,
        "continuous_mm": (span_m / 26) * 1000
    }


# =========================
# GLOBAL STRUCTURAL CHECK
# =========================
def structural_assessment(span, dead, live, height):
    uls = ultimate_limit_state(dead, live)
    beam = check_deflection(span, uls)
    column = check_column(uls, height)

    return {
        "ULS_load_kN": uls,
        "beam_check": beam,
        "column_check": column,
        "global_safe": beam["pass"] and column["safe"]
    }

def validate_structure(load: float, capacity: float):
    return {
        "safe": capacity > load,
        "utilization": load / capacity if capacity else 0
    }
