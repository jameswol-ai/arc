# =========================================================
# Unit conversion constants and helpers
# =========================================================
M2_TO_FT2 = 10.7639
M_TO_FT = 3.28084

def to_display_length(m, unit_system="metric"):
    if unit_system == "imperial":
        return (round(m * M_TO_FT, 1), "ft")
    return (round(m, 1), "m")

def to_display_area(m2, unit_system="metric"):
    if unit_system == "imperial":
        return (round(m2 * M2_TO_FT2, 1), "sq ft")
    return (round(m2, 1), "m²")