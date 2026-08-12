# =========================================================
# Structural member sizing and rebar estimates
# =========================================================
import numpy as np
from .soil import get_soil_bearing_capacity

def compute_structural_design(d, ec):
    span = d["structural"]["span"]
    gfa = d["total_gfa"]
    soil_bearing = get_soil_bearing_capacity(d["soil_name"])
    col_width = max(0.3, span / 15)
    col_depth = col_width
    beam_depth = max(0.3, span / 12)
    beam_width = beam_depth / 2
    slab_thickness = max(0.15, span / 30)
    total_load = gfa * 10
    footing_width = max(0.5, total_load / (soil_bearing * 1000))
    fy = 500
    m_ed = float(ec["m_ed"].split()[0])
    d_beam = beam_depth - 0.05
    if d_beam > 0 and m_ed > 0:
        as_beam = (m_ed * 10**6) / (0.87 * fy * 0.9 * d_beam * 1000)
    else:
        as_beam = 0
    as_beam = max(0, as_beam)
    as_col = 0.01 * (col_width * 1000) * (col_depth * 1000)
    as_slab = 0.002 * (slab_thickness * 1000) * 1000
    as_footing = 0.0015 * (footing_width * 1000) * (slab_thickness * 1000)
    def bar_count(area, dia):
        bar_area = np.pi * (dia/2)**2
        return max(1, int(area / bar_area + 0.5))
    return {
        "column_width": round(col_width, 2),
        "column_depth": round(col_depth, 2),
        "beam_width": round(beam_width, 2),
        "beam_depth": round(beam_depth, 2),
        "slab_thickness": round(slab_thickness, 2),
        "footing_width": round(footing_width, 2),
        "footing_depth": 0.3,
        "as_beam": round(as_beam, 0),
        "as_column": round(as_col, 0),
        "as_slab": round(as_slab, 0),
        "as_footing": round(as_footing, 0),
        "beam_bars": bar_count(as_beam, 20),
        "column_bars": bar_count(as_col, 25),
        "slab_bars": bar_count(as_slab, 12),
        "footing_bars": bar_count(as_footing, 16)
    }