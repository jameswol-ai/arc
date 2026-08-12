# =========================================================
# Water harvesting efficiency
# =========================================================
def compute_water_harvesting(d):
    roof_area = d["total_gfa"]
    rainfall_map = {
        "Kenya": 600,
        "Uganda": 1200,
        "Tanzania": 900,
        "South Sudan": 800,
        "Rwanda": 1200,
        "Ethiopia": 700
    }
    country = d["country"]
    rainfall_mm = rainfall_map.get(country, 800)
    runoff_coeff = 0.8
    rainfall_m = rainfall_mm / 1000
    harvestable = roof_area * rainfall_m * runoff_coeff
    typical_consumption = 100
    savings_pct = min(100, (harvestable / typical_consumption) * 100)
    return {
        "harvestable_volume": round(harvestable, 1),
        "savings_percentage": round(min(100, savings_pct), 1),
        "rainfall": rainfall_mm
    }