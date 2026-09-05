# =========================================================
# Arc presentation renderers: floorplan, 3D, isometric, Gantt, radar
# =========================================================
from __future__ import annotations

import html
import json
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from .config import to_display_length


def _safe_plan(plan):
    """Return a renderer-safe room list without mutating the source plan."""
    if not isinstance(plan, (list, tuple)):
        return []
    safe = []
    for index, room in enumerate(plan):
        if not isinstance(room, dict):
            continue
        try:
            w = max(0.5, float(room.get("w", 1.0)))
            h = max(0.5, float(room.get("h", 1.0)))
        except (TypeError, ValueError):
            continue
        item = dict(room)
        item["w"] = w
        item["h"] = h
        item["type"] = str(item.get("type", "Space"))
        item["name"] = str(item.get("name", f"Space {index + 1}"))
        item["color"] = str(item.get("color", "#334155"))
        safe.append(item)
    return safe


def _base_layout(fig, height=None):
    """Apply the Arc presentation language consistently to Plotly figures."""
    kwargs = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#cbd5e1", size=12),
        margin=dict(l=24, r=24, t=52, b=28),
        hoverlabel=dict(bgcolor="#111827", font_size=12),
    )
    if height:
        kwargs["height"] = height
    fig.update_layout(**kwargs)
    return fig


# ─── FLOORPLAN ────────────────────────────────────────────────
def render_floorplan(plan, span=6.0):
    """Render a readable floor plan with dimensions, circulation and legend."""
    rooms = _safe_plan(plan)
    if not rooms:
        rooms = [{"name": "Planning Area", "type": "Corridor", "w": 6.0, "h": 2.0, "color": "#334155"}]

    corridor = next((r for r in rooms if r["type"].lower() == "corridor"), None)
    if corridor is None:
        corridor = next((r for r in rooms if "corridor" in r["name"].lower()), None)
    if corridor is None:
        corridor = {"name": "Main Circulation", "type": "Corridor", "w": 1.5,
                    "h": max(6.0, sum(r["h"] for r in rooms) * 0.35), "color": "#334155"}
        rooms.insert(0, corridor)

    stairs = next((r for r in rooms if r["type"].lower() == "stairs"), None)
    if stairs is None:
        stairs = next((r for r in rooms if "stair" in r["name"].lower()), None)

    others = [r for r in rooms if r is not corridor and r is not stairs]
    unit_system = st.session_state.get("unit_system", "metric")
    unit = "ft" if unit_system == "imperial" else "m"
    fig = go.Figure()

    def add_room(x0, y0, x1, y1, color, name, w_m, d_m, room_type):
        w_d, _ = to_display_length(w_m, unit_system)
        d_d, _ = to_display_length(d_m, unit_system)
        fig.add_shape(type="rect", x0=x0, y0=y0, x1=x1, y1=y1,
                      fillcolor=color, line=dict(color="#64748b", width=1.5), opacity=0.78)
        area = w_m * d_m
        fig.add_annotation(
            x=(x0 + x1) / 2, y=(y0 + y1) / 2,
            text=f"<b>{html.escape(name)}</b><br><span style='font-size:10px'>{html.escape(room_type)} · {w_d}×{d_d} {unit}<br>{area:.1f} m²</span>",
            showarrow=False, font=dict(size=10, color="#e2e8f0"),
            bgcolor="rgba(15,23,42,0.90)", bordercolor="#475569", borderwidth=1,
        )

    cl = max(1.5, corridor["h"])
    cw = max(1.2, corridor["w"])
    max_x = max(cl + 5, sum(r["w"] + 0.8 for r in others) + 3)
    max_y = max(cw + 5, cw + sum(r["h"] for r in others) * 0.45 + 5)
    grid_step = max(1.0, float(span))

    for x in np.arange(0, max_x + grid_step, grid_step):
        fig.add_shape(type="line", x0=x, y0=-max_y, x1=x, y1=max_y,
                      line=dict(color="rgba(100,116,139,0.18)", width=1), layer="below")
    for y in np.arange(-max_y, max_y + grid_step, grid_step):
        fig.add_shape(type="line", x0=0, y0=y, x1=max_x, y1=y,
                      line=dict(color="rgba(100,116,139,0.18)", width=1), layer="below")

    add_room(0, -cw / 2, cl, cw / 2, corridor["color"], corridor["name"], corridor["w"], corridor["h"], "Circulation")

    cx, side = 1.5, 1
    for room in others:
        rw, rd = room["w"], room["h"]
        if cx + rw > cl and cx > 1.5:
            cx, side = 1.5, -side
        y0 = cw / 2 + 0.5 if side == 1 else -cw / 2 - 0.5 - rd
        y1 = y0 + rd
        add_room(cx, y0, cx + rw, y1, room["color"], room["name"], rw, rd, room["type"])
        door_x, door_y = cx + rw / 2, cw / 2 if side == 1 else -cw / 2
        fig.add_annotation(x=door_x, y=(y0 + y1) / 2, ax=door_x, ay=door_y,
                           xref="x", yref="y", axref="x", ayref="y",
                           text="", showarrow=True, arrowhead=3, arrowcolor="#94a3b8")
        cx += rw + 0.8
        side *= -1

    if stairs:
        sx = cl + 0.5
        sh = max(cw, stairs["h"])
        add_room(sx, -sh / 2, sx + stairs["w"], sh / 2,
                 stairs["color"], stairs["name"], stairs["w"], stairs["h"], "Vertical Core")

    fig.add_annotation(x=0.5, y=0, ax=-1, ay=0, xref="x", yref="y", axref="x", ayref="y",
                       text="<b>ENTRANCE</b>", showarrow=True, arrowhead=3,
                       arrowcolor="#f59e0b", font=dict(color="#f59e0b"))
    total_area = sum(r["w"] * r["h"] for r in rooms)
    fig.update_layout(
        title=dict(text=f"2D Floor Plan <sup>• {len(rooms)} spaces • {total_area:.1f} m² modelled</sup>", x=0.02),
        xaxis=dict(visible=False), yaxis=dict(visible=False, scaleanchor="x", scaleratio=1),
        showlegend=False, height=520, margin=dict(l=20, r=20, t=52, b=20),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


# ─── 3D MASSING ──────────────────────────────────────────────
def render_3d(plan, floors=1, span=6.0):
    rooms = _safe_plan(plan)
    if not rooms:
        return go.Figure().update_layout(title="3D Massing: no rooms available")
    floors = max(1, int(floors))
    traces = []
    min_x = min_y = float("inf")
    max_x = max_y = -float("inf")
    for i, r in enumerate(rooms):
        xc, yc = (i % 3) * 12, (i // 3) * 10
        min_x, max_x = min(min_x, xc - r["w"] / 2), max(max_x, xc + r["w"] / 2)
        min_y, max_y = min(min_y, yc - r["h"] / 2), max(max_y, yc + r["h"] / 2)
    gs = max(1.0, float(span) * 2)
    for x in np.arange(np.floor(min_x / gs) * gs, np.ceil(max_x / gs) * gs + gs, gs):
        traces.append(go.Scatter3d(x=[x, x], y=[min_y, max_y], z=[0, 0], mode="lines",
                                   line=dict(color="#334155", width=1), showlegend=False, hoverinfo="skip"))
    for y in np.arange(np.floor(min_y / gs) * gs, np.ceil(max_y / gs) * gs + gs, gs):
        traces.append(go.Scatter3d(x=[min_x, max_x], y=[y, y], z=[0, 0], mode="lines",
                                   line=dict(color="#334155", width=1), showlegend=False, hoverinfo="skip"))
    for i, r in enumerate(rooms):
        xc, yc = (i % 3) * 12, (i // 3) * 10
        w, d, c = r["w"], r["h"], r["color"]
        for f in range(floors):
            zb, zt = f * 3, f * 3 + 2.7
            xb = [xc - w/2, xc + w/2, xc + w/2, xc - w/2, xc - w/2]
            yb = [yc - d/2, yc - d/2, yc + d/2, yc + d/2, yc - d/2]
            traces.append(go.Scatter3d(x=xb, y=yb, z=[zb] * 5, mode="lines",
                                       line=dict(color=c, width=2), name=r["name"],
                                       legendgroup=r["type"], hovertemplate=f"{html.escape(r['name'])}<br>Floor {f+1}<br>{w:.2f} × {d:.2f} m<extra></extra>"))
            traces.append(go.Scatter3d(x=xb, y=yb, z=[zt] * 5, mode="lines",
                                       line=dict(color=c, width=2), showlegend=False, hoverinfo="skip"))
            for vx, vy in [(xc-w/2, yc-d/2), (xc+w/2, yc-d/2), (xc+w/2, yc+d/2), (xc-w/2, yc+d/2)]:
                traces.append(go.Scatter3d(x=[vx, vx], y=[vy, vy], z=[zb, zt], mode="lines",
                                           line=dict(color=c, width=2), showlegend=False, hoverinfo="skip"))
    fig = go.Figure(data=traces)
    fig.update_layout(
        scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False),
                   bgcolor="#0f172a", aspectmode="data"),
        paper_bgcolor="#0f172a", margin=dict(l=0, r=0, b=0, t=44), showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
        title=dict(text=f"3D Massing <sup>• {floors} floors • {len(rooms)} spaces</sup>", x=0.02),
        height=500,
    )
    return fig


# ─── ISOMETRIC ───────────────────────────────────────────────
def render_isometric(plan, span=6.0):
    rooms = _safe_plan(plan)
    w_, h_ = 800, 380
    unit_system = st.session_state.get("unit_system", "metric")
    unit = "ft" if unit_system == "imperial" else "m"
    step = max(1.0, float(span) * 2)
    commands = [
        f"const step={step};",
        f"ctx.strokeStyle='rgba(148,163,184,0.15)';ctx.lineWidth=1;",
        f"for(let x=0;x<{w_};x+=step){{ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,{h_});ctx.stroke();}}",
        f"for(let y=0;y<{h_};y+=step){{ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo({w_},y);ctx.stroke();}}",
    ]
    labels = []
    for i, r in enumerate(rooms):
        ox, oy = (i % 3) * 170 + 100, (i // 3) * 110 + 130
        rw, rh = min(115, max(8, int(r["w"] * 14))), min(95, max(8, int(r["h"] * 14)))
        wd, _ = to_display_length(r["w"], unit_system)
        hd, _ = to_display_length(r["h"], unit_system)
        commands.append(
            f"ctx.fillStyle={json.dumps(r['color'])};ctx.beginPath();ctx.moveTo({ox},{oy});"
            f"ctx.lineTo({ox+rw},{oy-rh/2});ctx.lineTo({ox+rw*2},{oy});ctx.lineTo({ox+rw},{oy+rh/2});"
            "ctx.closePath();ctx.fill();ctx.strokeStyle='rgba(226,232,240,0.3)';ctx.stroke();"
        )
        labels.append((ox + 10, oy - 2, f"{r['name']} ({wd}×{hd} {unit})"))
    for x, y, label in labels:
        commands.append(f"ctx.fillStyle='#e2e8f0';ctx.font='bold 11px sans-serif';ctx.fillText({json.dumps(label)},{x},{y});")
    script = "".join(commands)
    return (f"<canvas width='{w_}' height='{h_}' style='max-width:100%;background:#0f172a;border-radius:10px;'></canvas>"
            f"<script>const c=document.currentScript.previousElementSibling;const ctx=c.getContext('2d');{script}</script>")


# ─── GANTT ───────────────────────────────────────────────────
def gantt_chart(asset):
    gfa = max(0, float(asset.get("total_gfa", 0)))
    fl = max(1, int(asset.get("floors", 1)))
    start = datetime.today()
    tasks = [("Mobilization", 5), ("Substructure", max(1, int(gfa * 0.15)))] + [(f"Floor {i+1}", 20) for i in range(fl)] + [("Roofing", 12), ("Finishes", max(1, int(gfa * 0.02))), ("Commissioning", 14), ("Handover", 3)]
    df = pd.DataFrame(tasks, columns=["Task", "Duration"])
    ends = [start]
    for duration in df["Duration"]:
        ends.append(ends[-1] + timedelta(days=int(duration)))
    df["Start"], df["Finish"] = ends[:-1], ends[1:]
    df["Days"] = (df["Finish"] - df["Start"]).dt.days
    fig = px.timeline(df, x_start="Start", x_end="Finish", y="Task", hover_data={"Days": True, "Start": "|%d %b %Y", "Finish": "|%d %b %Y"}, title="Construction Gantt")
    fig.update_yaxes(autorange="reversed")
    return _base_layout(fig, 460)


# ─── RADAR ──────────────────────────────────────────────────
def radar_chart(scores):
    """Present all five Arc intelligence dimensions plus composite context."""
    categories = ["Architecture", "Structural", "Sustainability", "Cost", "Metric Design"]
    keys = ("arch", "struct", "sust", "cost", "metric")
    values = [float(scores.get(k, 0)) for k in keys]
    closed_values = values + [values[0]]
    closed_categories = categories + [categories[0]]
    fig = go.Figure(go.Scatterpolar(
        r=closed_values, theta=closed_categories, fill="toself",
        line=dict(color="#f59e0b", width=2), marker=dict(size=7),
        hovertemplate="%{theta}: %{r:.0f}/100<extra></extra>",
    ))
    composite = scores.get("composite")
    title = "AI Design Profile"
    if composite is not None:
        title += f" <sup>• Composite {float(composite):.0f}/100</sup>"
    fig.update_layout(
        title=dict(text=title, x=0.02),
        polar=dict(radialaxis=dict(range=[0, 100], gridcolor="#475569", tickfont=dict(size=9)),
                   angularaxis=dict(gridcolor="#334155")),
    )
    return _base_layout(fig, 420)


# ─── SCHEDULE GANTT ──────────────────────────────────────────
def plot_schedule_gantt(df):
    required = {"Start", "Finish", "Task"}
    if not isinstance(df, pd.DataFrame) or not required.issubset(df.columns) or df.empty:
        return go.Figure().update_layout(title="Construction Schedule: no schedule data")
    frame = df.copy()
    frame["Start"] = pd.to_datetime(frame["Start"], errors="coerce")
    frame["Finish"] = pd.to_datetime(frame["Finish"], errors="coerce")
    frame = frame.dropna(subset=["Start", "Finish"])
    if frame.empty:
        return go.Figure().update_layout(title="Construction Schedule: no valid dates")
    frame["Days"] = (frame["Finish"] - frame["Start"]).dt.total_seconds() / 86400
    color_column = "Phase" if "Phase" in frame.columns else None
    hover = {"Days": ":.0f", "Start": "|%d %b %Y", "Finish": "|%d %b %Y"}
    if "Duration" in frame.columns:
        hover["Duration"] = True
    if "Predecessors" in frame.columns:
        hover["Predecessors"] = True
    fig = px.timeline(frame, x_start="Start", x_end="Finish", y="Task", color=color_column,
                      hover_data=hover, title="Construction Schedule")
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(showgrid=True, gridcolor="rgba(100,116,139,0.18)")
    return _base_layout(fig, max(420, 60 + len(frame) * 32))
