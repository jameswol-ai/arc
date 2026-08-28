# modules/seismic_advanced.py
def compute_advanced_seismic(d, country):
    seismic_zones = {
        "Kenya": 0.25, "Uganda": 0.20, "Tanzania": 0.30,
        "South Sudan": 0.15, "Rwanda": 0.35, "Ethiopia": 0.25
    }
    z = seismic_zones.get(country, 0.20)
    # Soil type (from soil_name) – simplified
    soil_category = d.get("soil_category", "Medium")
    # Soil factors per EC8
    S = {"Rock": 1.0, "Medium": 1.2, "Soft": 1.4, "Very Soft": 1.6}.get(soil_category, 1.2)
    # Importance factor (residential = 1.0)
    I = 1.0
    # Damping correction factor (assume 5% damping)
    eta = 1.0
    # Ground acceleration (ag) – simplified
    ag = z * 0.4 * 9.81  # m/s²
    # Design ground acceleration
    agd = ag * S * I
    # Spectral response (simplified plateau)
    T = 0.5  # assume period 0.5s
    Sd = agd * eta * 2.5  # simplified
    # Base shear
    W = d["total_gfa"] * 10  # kN
    V = Sd * W / (T * 0.5)  # rough
    return {
        "ag": round(ag, 3),
        "agd": round(agd, 3),
        "Sd": round(Sd, 3),
        "base_shear": round(V, 0),
        "T": T,
        "soil_factor": S
    }