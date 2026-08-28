# app.py – Flask backend for Vercel
# Uses the same modules as the Streamlit app
# All functions return JSON

from flask import Flask, request, jsonify, render_template
import random, json, requests
import numpy as np
import pandas as pd
from datetime import datetime

# ─── Import all AEC modules ──────────────────────────────────
# (These are the same as in your Streamlit app)
from modules.config import M2_TO_FT2, format_length, format_area
from modules.soil import REGION_SOIL_OPTIONS, get_soil_category, get_soil_multiplier, get_soil_bearing_capacity
from modules.aec_engine import (
    ARCH_DOMAINS, generate_spatial_model, run_eurocode_analysis,
    calculate_ai_scores, compute_wind_load, compute_seismic_check
)
from modules.materials import compute_materials
from modules.structural import compute_structural_design
from modules.construction import compute_construction_schedule
from modules.cost import compute_boq, compute_cost_by_trade
from modules.forex import STATIC_FX, get_fx, init_fx
from modules.solar import compute_solar_potential
from modules.water import compute_water_harvesting
from modules.green_rating import compute_green_rating
from modules.ram_ai import ram_ai

app = Flask(__name__)

# ─── Helper to force metric (frontend handles conversions) ───
# We always return metric values; the frontend will convert based on user preference.
# Override format functions to ignore unit system.
def format_length_m(m):
    return f"{round(m, 1)} m"

def format_area_m(m2):
    return f"{round(m2, 1)} m²"

# ─── Routes ──────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/forex')
def forex():
    # Ensure forex is initialised
    init_fx()
    rates = {c: get_fx(c)["rate"] for c in STATIC_FX.keys()}
    return jsonify(rates)

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.json
    domain = data.get('domain', 'Residential')
    typology = data.get('typology', 'Luxury Villa')
    plot = int(data.get('plot_size', 800))
    floors = int(data.get('floors', 3))
    baths = int(data.get('baths', 2))
    country = data.get('country', 'Kenya')
    soil_name = data.get('soil_name', 'Nairobi Red Coffee Clay')
    room_types = data.get('room_types', ['Bedroom', 'Bathroom', 'Living Room', 'Kitchen'])

    concepts = []
    for i in range(4):
        d = generate_spatial_model(
            domain, typology,
            plot + random.randint(-400, 400),
            max(1, floors + random.randint(-2, 2)),
            max(1, baths + random.randint(-2, 2)),
            country, soil_name,
            room_types=room_types,
            seed=i
        )
        d["plan"] = d["rooms"]
        ec = run_eurocode_analysis(d, domain)
        d["eurocode"] = ec
        total_usd, total_local, fx, boq_breakdown = compute_boq(d, country)
        arch, struct, sust, cost, comp = calculate_ai_scores(d, ec, total_usd, "")
        materials = compute_materials(d)
        d["scores"] = {"arch": arch, "struct": struct, "sust": sust, "cost": cost, "composite": comp}
        d["total_usd"] = total_usd
        d["total_local"] = total_local
        d["fx"] = fx
        d["boq_breakdown"] = boq_breakdown
        d["materials"] = materials

        # Build serializable response
        concepts.append({
            "id": d["id"],
            "type": d["type"],
            "floors": d["floors"],
            "total_gfa": d["total_gfa"],
            "floor_area": d["floor_area"],
            "country": d["country"],
            "soil_name": d["soil_name"],
            "scores": d["scores"],
            "total_usd": d["total_usd"],
            "total_local": d["total_local"],
            "eurocode": d["eurocode"],
            "rooms": d["rooms"],
            "structural": d["structural"],
            "materials": d["materials"],
            "boq_breakdown": d["boq_breakdown"],
            "fx": d["fx"]
        })

    concepts.sort(key=lambda x: x["scores"]["composite"], reverse=True)
    return jsonify(concepts)

@app.route('/api/ram', methods=['POST'])
def ram_endpoint():
    data = request.json
    q = data.get('q', '')
    country = data.get('country', 'Kenya')
    domain = data.get('domain', 'Residential')
    response = ram_ai(q, country, domain)
    return jsonify({"response": response})

# Optional: serve static assets if needed
# (Plotly.js and other libraries are loaded from CDN in the frontend)

if __name__ == '__main__':
    app.run(debug=True)