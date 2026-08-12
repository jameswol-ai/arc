# =========================================================
# Ram AI knowledge base
# =========================================================
import random

WISDOM = {
    "soil": ["For soft clay, use raft/pile foundations. Black cotton soil expands when wet—add moisture barrier.",
             "Lateritic soils (Uganda/Rwanda) need erosion protection; strip footings with cover.",
             "Rock sites: pad foundations, but blasting may add 15‑20% cost."],
    "foundation": ["Rift Valley seismic zones: continuous reinforcement, avoid soft storeys.",
                   "Coastal areas (Mombasa, Dar): corrosion‑resistant steel, low w/c ratio."],
    "cost": ["Cement in landlocked countries can be 30% higher; consider alternative binders.",
             "Steel is often imported—hedge with pre‑order agreements."],
    "sustainability": ["Orient long facades to prevailing winds (Indian Ocean monsoon).",
                       "Rainwater harvesting: first‑flush diverters in semi‑arid regions."],
    "default": ["Start with site analysis—soil, climate, materials dictate 70% of design.",
                "Labour affordable but skilled scarce; train and detail simply.",
                "Allow vertical expansion in rapidly urbanising areas."]
}
TIPS = {"Kenya":"Nairobi altitude reduces curing time.", "Uganda":"Termite attack risk on timber.",
        "Tanzania":"Sulphate‑resistant cement for coral limestone.", "South Sudan":"Compaction/soil replacement needed.",
        "Rwanda":"Volcanic soil stable; focus on cooling.", "Ethiopia":"Seismic ductile detailing per Eurocode 8."}

def ram_ai(q, country, domain):
    q = q.lower()
    pool = WISDOM.get("soil" if "soil" in q or "ground" in q else
                      "foundation" if "foundation" in q else
                      "cost" if "cost" in q or "budget" in q else
                      "sustainability" if any(w in q for w in ("sustain","green","eco")) else "default")
    return f"**Ram AI:** {random.choice(pool)}\n\n📌 *{country}*: {TIPS.get(country, '')}"