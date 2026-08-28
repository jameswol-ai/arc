import random
from .aec_engine import generate_spatial_model, run_eurocode_analysis
from .cost import compute_boq

def optimise_cost(domain, typology, country, soil_name, room_types, min_gfa=500, max_plot=5000):
    best = None
    best_cost = float('inf')
    for _ in range(20):
        plot = random.randint(200, max_plot)
        floors = random.randint(1, 8)
        gfa = plot * 0.6 * floors
        if gfa < min_gfa:
            continue
        d = generate_spatial_model(domain, typology, plot, floors, baths=2, country=country,
                                   soil_name=soil_name, room_types=room_types, seed=random.randint(0,1000))
        ec = run_eurocode_analysis(d, domain)
        if ec['uls_status'] != "PASS ✅":
            continue
        total_usd, _, _, _ = compute_boq(d, country)
        if total_usd < best_cost:
            best_cost = total_usd
            best = d
    return best, best_cost
