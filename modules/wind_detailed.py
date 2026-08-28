def compute_detailed_wind(d, country):
    wind_speeds = {
        "Kenya": 25, "Uganda": 22, "Tanzania": 28,
        "South Sudan": 20, "Rwanda": 18, "Ethiopia": 24
    }
    v_b0 = wind_speeds.get(country, 22)
    z0 = 0.05
    kr = 0.19 * (z0 / 0.05) ** 0.07
    z = d["floors"] * d["structural"]["storey_height"]
    if z < 2:
        z = 2
    cr = kr * (z / z0) ** 0.07
    co = 1.0
    rho = 1.25
    qb = 0.5 * rho * (v_b0 ** 2) / 1000
    qp = qb * (cr ** 2) * (co ** 2)
    cf = 0.8
    Aref = d["total_gfa"] ** 0.5 * z
    F_wind = qp * cf * Aref
    return {
        "v_b0": v_b0,
        "z0": z0,
        "kr": round(kr, 3),
        "cr": round(cr, 3),
        "qb": round(qb, 3),
        "qp": round(qp, 3),
        "cf": cf,
        "F_wind": round(F_wind, 0)
    }