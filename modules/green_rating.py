# =========================================================
# Green building rating (LEED/BREEAM approximate)
# =========================================================
from .solar import compute_solar_potential
from .water import compute_water_harvesting

def compute_green_rating(d, ec):
    score = 0
    window_ratio = d["windows"] / d["total_gfa"] if d["total_gfa"] > 0 else 0
    if window_ratio > 0.2:
        score += 10
    elif window_ratio > 0.15:
        score += 7
    else:
        score += 4
    water = compute_water_harvesting(d)
    if water["savings_percentage"] > 50:
        score += 15
    elif water["savings_percentage"] > 30:
        score += 10
    else:
        score += 5
    carbon = d["materials"]["embodied_carbon_t"] / d["total_gfa"] if d["total_gfa"] > 0 else 1
    if carbon < 0.3:
        score += 15
    elif carbon < 0.5:
        score += 10
    else:
        score += 5
    solar = compute_solar_potential(d)
    if solar["installed_capacity"] > 5:
        score += 15
    elif solar["installed_capacity"] > 2:
        score += 10
    else:
        score += 5
    score += 10  # waste management
    if window_ratio > 0.15:
        score += 10
    else:
        score += 5
    if d["structural"]["foundation"] in ["Raft Foundation", "Pile Foundation"]:
        score += 5
    score = min(100, score)
    if score >= 85:
        rating = "Platinum (LEED) / Excellent (BREEAM)"
    elif score >= 70:
        rating = "Gold / Very Good"
    elif score >= 55:
        rating = "Silver / Good"
    else:
        rating = "Certified / Pass"
    return {
        "score": score,
        "rating": rating
    }