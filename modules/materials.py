# =========================================================
# Material quantities and embodied carbon
# =========================================================

CARBON_FACTORS = {"concrete": 0.12, "steel": 1.85, "brick": 0.24, "finish": 5.0}

def compute_materials(d):
    """
    Compute material quantities and embodied carbon for a building concept.
    
    Parameters
    ----------
    d : dict
        Building concept dictionary (must have 'total_gfa' key).
    
    Returns
    -------
    dict
        Contains concrete_volume (m³), steel_weight (kg), brick_units,
        finish_area (m²), embodied_carbon_kg and embodied_carbon_t.
    """
    gfa = d["total_gfa"]
    
    # Rough material intensities per m² of GFA (based on typical East African construction)
    concrete_per_m2 = 0.25      # m³ concrete per m²
    steel_per_m2 = 60           # kg steel per m²
    brick_per_m2 = 40           # units of brick per m²
    finish_per_m2 = 1.0         # m² of finish per m² (floor area)
    
    concrete_vol = concrete_per_m2 * gfa
    steel_weight = steel_per_m2 * gfa
    brick_units = brick_per_m2 * gfa
    finish_area = finish_per_m2 * gfa
    
    # Embodied carbon calculations (kg CO₂e)
    # Concrete: assume density 2400 kg/m³, carbon factor 0.12 kg CO₂e/kg concrete
    carbon_concrete = concrete_vol * 2400 * CARBON_FACTORS["concrete"]
    # Steel: carbon factor 1.85 kg CO₂e/kg steel
    carbon_steel = steel_weight * CARBON_FACTORS["steel"]
    # Brick: 0.24 kg CO₂e per brick
    carbon_brick = brick_units * CARBON_FACTORS["brick"]
    # Finishes: 5.0 kg CO₂e per m²
    carbon_finish = finish_area * CARBON_FACTORS["finish"]
    
    total_embodied_carbon = carbon_concrete + carbon_steel + carbon_brick + carbon_finish
    
    return {
        "concrete_volume": round(concrete_vol, 1),
        "steel_weight": round(steel_weight, 0),
        "brick_units": round(brick_units, 0),
        "finish_area": round(finish_area, 1),
        "embodied_carbon_kg": round(total_embodied_carbon, 0),
        "embodied_carbon_t": round(total_embodied_carbon / 1000, 2)
    }