# =========================================================
# Solar potential analysis
# =========================================================
def compute_solar_potential(d):
    roof_area = d["total_gfa"]
    irradiation = 1800
    pv_efficiency = 0.18
    capacity_factor = 0.15
    installed_capacity = roof_area * pv_efficiency * 0.1
    annual_energy = installed_capacity * 8760 * capacity_factor
    grid_emission = 0.5
    co2_savings = annual_energy * grid_emission / 1000
    return {
        "roof_area": round(roof_area, 1),
        "installed_capacity": round(installed_capacity, 2),
        "annual_energy": round(annual_energy, 0),
        "co2_savings": round(co2_savings, 2)
    }