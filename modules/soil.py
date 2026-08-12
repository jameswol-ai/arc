# =========================================================
# Soil data and helper functions
# =========================================================
SOIL_TYPES = {
    "Nairobi Red Coffee Clay":             {"multiplier": 1.0,  "cat": "Medium", "region": "Kenya"},
    "Kampala Red Lateritic Clay":          {"multiplier": 1.6,  "cat": "Soft",   "region": "Uganda"},
    "Wetland Silts (Kampala)":             {"multiplier": 1.7,  "cat": "Very Soft","region": "Uganda"},
    "Dar Coastal Sand / Coral Limestone":  {"multiplier": 0.85, "cat": "Rock",   "region": "Tanzania"},
    "Juba Black Cotton Soil (Expansive)":  {"multiplier": 1.8,  "cat": "Very Soft","region": "South Sudan"},
    "Kigali Volcanic Andosols":            {"multiplier": 0.7,  "cat": "Rock",   "region": "Rwanda"},
    "Addis Clayey Soils & Volcanic Tuff":  {"multiplier": 1.5,  "cat": "Soft",   "region": "Ethiopia"},
    "Generic Firm Sandy Gravel":           {"multiplier": 1.0,  "cat": "Medium", "region": "All"},
    "Generic Soft Silt / Clay":            {"multiplier": 1.5,  "cat": "Soft",   "region": "All"},
    "Generic Hard Rock / Laterite":        {"multiplier": 0.7,  "cat": "Rock",   "region": "All"},
}

REGION_SOIL_OPTIONS = {
    "Kenya":       ["Nairobi Red Coffee Clay", "Generic Firm Sandy Gravel", "Generic Soft Silt / Clay", "Generic Hard Rock / Laterite"],
    "Uganda":      ["Kampala Red Lateritic Clay", "Wetland Silts (Kampala)", "Generic Firm Sandy Gravel", "Generic Hard Rock / Laterite"],
    "Tanzania":    ["Dar Coastal Sand / Coral Limestone", "Generic Firm Sandy Gravel", "Generic Soft Silt / Clay"],
    "South Sudan": ["Juba Black Cotton Soil (Expansive)", "Generic Firm Sandy Gravel", "Generic Hard Rock / Laterite"],
    "Rwanda":      ["Kigali Volcanic Andosols", "Generic Firm Sandy Gravel", "Generic Soft Silt / Clay"],
    "Ethiopia":    ["Addis Clayey Soils & Volcanic Tuff", "Generic Firm Sandy Gravel", "Generic Hard Rock / Laterite"],
}

def get_soil_multiplier(soil_name):
    return SOIL_TYPES.get(soil_name, {"multiplier": 1.0})["multiplier"]

def get_soil_category(soil_name):
    return SOIL_TYPES.get(soil_name, {"cat": "Medium"})["cat"]

def get_soil_bearing_capacity(soil_name):
    cat = get_soil_category(soil_name)
    if cat == "Rock": return 300
    elif cat == "Medium": return 150
    elif cat == "Soft": return 100
    elif cat == "Very Soft": return 75
    else: return 120