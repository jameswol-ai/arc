# =========================================================
# Cost: BOQ and cost by trade
# =========================================================
import pandas as pd
from .forex import get_fx

def compute_boq(d, country):
    # This function is used in the main generation, so we'll keep it here.
    # But we also need forex.
    gfa = d["total_gfa"]
    fx = get_fx(country)
    soil_m = d.get("soil_multiplier", 1.0)
    items = [
        ("Site Clearance & Excavation", int(gfa*0.2), 80*soil_m),
        ("Substructure (Foundations)", int(gfa*0.15), 150*soil_m),
        ("Superstructure Concrete", int(gfa*0.35), 210),
        ("Steel Reinforcement", int(gfa*0.35*0.12), 1200),
        ("Masonry Blocks", int(gfa*38), 2.5),
        ("Floor Finishes", int(gfa), 40),
        ("Wall Finishes", int(gfa*2), 25),
        ("Ceiling Finishes", int(gfa), 15),
        ("Doors & Windows", d["doors"] + d["windows"], 350),
        ("MEP (Electrical, Plumbing)", int(gfa*0.1), 500),
        ("External Works", int(gfa*0.05), 200)
    ]
    total_usd = sum(q * (u * fx["multiplier"]) for _, q, u in items)
    total_local = total_usd * fx["rate"]
    breakdown = [{"Item": item, "Qty": qty, "Unit USD": round(u * fx["multiplier"], 2), "Total USD": round(qty * u * fx["multiplier"], 0)} for item, qty, u in items]
    return total_usd, total_local, fx, breakdown

def compute_cost_by_trade(d, country):
    fx = get_fx(country)
    trades = {
        "Excavation": {"items": ["Site Clearance & Excavation"], "labour_pct": 0.4, "equip_pct": 0.3},
        "Concrete": {"items": ["Substructure (Foundations)", "Superstructure Concrete"], "labour_pct": 0.3, "equip_pct": 0.1},
        "Rebar": {"items": ["Steel Reinforcement"], "labour_pct": 0.2, "equip_pct": 0.05},
        "Masonry": {"items": ["Masonry Blocks"], "labour_pct": 0.4, "equip_pct": 0.1},
        "Finishes": {"items": ["Floor Finishes", "Wall Finishes", "Ceiling Finishes"], "labour_pct": 0.5, "equip_pct": 0.05},
        "Doors & Windows": {"items": ["Doors & Windows"], "labour_pct": 0.2, "equip_pct": 0.02},
        "MEP": {"items": ["MEP (Electrical, Plumbing)"], "labour_pct": 0.35, "equip_pct": 0.1},
        "External": {"items": ["External Works"], "labour_pct": 0.4, "equip_pct": 0.2},
    }
    trade_cost = {}
    for trade, info in trades.items():
        total = 0
        for item_name in info["items"]:
            for boq_item in d["boq_breakdown"]:
                if boq_item["Item"] == item_name:
                    total += boq_item["Total USD"]
                    break
        labour = total * info["labour_pct"]
        equip = total * info["equip_pct"]
        trade_cost[trade] = {
            "Material": total - labour - equip,
            "Labour": labour,
            "Equipment": equip,
            "Total": total
        }
    df = pd.DataFrame(trade_cost).T.reset_index().rename(columns={"index": "Trade"})
    df["Total Local"] = df["Total"] * fx["rate"]
    return df