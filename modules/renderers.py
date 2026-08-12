# =========================================================
# Rendering functions: floorplan, 3D, isometric, Gantt, radar, schedule
# =========================================================
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from .config import to_display_length, to_display_area

# ─── FLOORPLAN ────────────────────────────────────────────────
def render_floorplan(plan, span=6.0):
    corridor = next((r for r in plan if r["type"] == "Corridor"), plan[0])
    stairs = next((r for r in plan if r["type"] == "Stairs"), None)
    others = [r for r in plan if r not in (corridor, stairs)]
    unit_system = st.session_state.get("unit_system", "metric")
    fig = go.Figure()

    def add_room(x0, y0, x1, y1, color, name, w_m, d_m):
        w_d, _ = to_display_length(w_m, unit_system)
        d_d, _ = to_display_length(d_m, unit_system)
        unit = "ft" if unit_system == "imperial" else "m"
        fig.add_shape(type="rect", x0=x0, y0=y0, x1=x1, y1=y1,
                      fillcolor=color, line=dict(color="#555", width=2), opacity=0.7)
        fig.add_annotation(
            x=(x0 + x1) / 2, y=(y0 + y1) / 2,
            text=f"<b>{name}</b><br>{w_d}×{d_d} {unit}",
            showarrow=False, font=dict(size=10, color="#cccccc"),
            bgcolor="rgba(0,0,0,0.7)"
        )

    cl, cw = corridor["h"], corridor["w"]
    max_x = cl + 5
    max_y = cw + sum(r["h"] for r in others) + 5

    # Grid lines
    for x in np.arange(0, max_x + span, span):
        fig.add_shape(type="line", x0=x, y0=-max_y, x1=x, y1=max_y,
                      line=dict(color="rgba(100,100,100,0.2)", width=1), layer="below")
    for y in np.arange(-max_y, max_y, span):
        fig.add_shape(type="line", x0=0, y0=y, x1=max_x, y1=y,
                      line=dict(color="rgba(100,100,100,0.2)", width=1), layer="below")

    add_room(0, -cw/2, cl, cw/2, corridor["color"], corridor["name"], corridor["w"], corridor["h"])

    cx, side = 1.5, 1
    for room in others:
        rw, rd = room["w"], room["h"]
        if cx + rw > cl:
            cx, side = 1.5, -side
        y0 = cw/2 + 0.5 if side == 1 else -cw/2 - 0.5 - rd
        y1 = y0 + rd
        add_room(cx, y0, cx + rw, y1, room["color"], room["name"], rw, rd)

        door_x, door_y = cx + rw/2, cw/2 if side == 1 else -cw/2
        fig.add_shape(type="path",
                      path=f"M {door_x-0.3},{door_y} Q {door_x-0.3},{door_y+(0.6 if side==1 else -0.6)} {door_x+0.3},{door_y+(0.6 if side==1 else -0.6)} Q {door_x+0.3},{door_y} {door_x-0.3},{door_y}",
                      line=dict(color="#888", width=2), fillcolor="rgba(100,100,100,0.2)")
        fig.add_annotation(x=door_x, y=(y0+y1)/2, ax=door_x, ay=door_y,
                           xref="x", yref="y", axref="x", ayref="y",
                           text="", showarrow=True, arrowhead=3, arrowcolor="#888")
        cx += rw + 0.8
        side *= -1

    if stairs:
        sx = cl + 0.5
        add_room(sx, -cw/2, sx + stairs["w"], cw/2, stairs["color"], stairs["name"], stairs["w"], stairs["h"])
        fig.add_annotation(x=sx + stairs["w"]/2, y=0, ax=cl-0.5, ay=0,
                           xref="x", yref="y", axref="x", ayref="y",
                           text="", showarrow=True, arrowhead=3, arrowcolor="#888")

    fig.add_annotation(x=0.5, y=0, ax=-1, ay=0,
                       xref="x", yref="y", axref="x", ayref="y",
                       text="<b>ENTRANCE</b>", showarrow=True, arrowhead=3, arrowcolor="#888",
                       font=dict(color="#888"))

    fig.update_layout(
        title="🗺️ 2D Floor Plan",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False, scaleanchor="x", scaleratio=1),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=False,
        width=800,
        height=500
    )
    return fig

# ─── 3D MASSING ──────────────────────────────────────────────
def render_3d(plan, floors=1, span=6.0):
    traces = []
    min_x = min_y = float('inf')
    max_x = max_y = -float('inf')

    for i, r in enumerate(plan):
        xc = (i % 3) * 12
        yc = (i // 3) * 10
        min_x = min(min_x, xc - r["w"] / 2)
        max_x = max(max_x, xc + r["w"] / 2)
        min_y = min(min_y, yc - r["h"] / 2)
        max_y = max(max_y, yc + r["h"] / 2)

    gs = span * 2

    # Grid
    for x in range(int(min_x / gs) * int(gs), int(max_x / gs + 1) * int(gs) + 1, int(gs)):
        traces.append(go.Scatter3d(x=[x, x], y=[min_y, max_y], z=[0, 0],
                                   mode='lines', line=dict(color='#333', width=1), showlegend=False))
    for y in range(int(min_y / gs) * int(gs), int(max_y / gs + 1) * int(gs) + 1, int(gs)):
        traces.append(go.Scatter3d(x=[min_x, max_x], y=[y, y], z=[0, 0],
                                   mode='lines', line=dict(color='#333', width=1), showlegend=False))

    # Rooms
    for i, r in enumerate(plan):
        xc = (i % 3) * 12
        yc = (i // 3) * 10
        w, d, c = r["w"], r["h"], r["color"]
        for f in range(floors):
            zb = f * 3
            zt = zb + 2.7
            xb = [xc - w/2, xc + w/2, xc + w/2, xc - w/2, xc - w/2]
            yb = [yc - d/2, yc - d/2, yc + d/2, yc + d/2, yc - d/2]
            traces.append(go.Scatter3d(x=xb, y=yb, z=[zb] * 5, mode='lines',
                                       line=dict(color=c, width=2), showlegend=False))
            traces.append(go.Scatter3d(x=xb, y=yb, z=[zt] * 5, mode='lines',
                                       line=dict(color=c, width=2), showlegend=False))
            for cx, cy in [(xc - w/2, yc - d/2), (xc + w/2, yc - d/2),
                           (xc + w/2, yc + d/2), (xc - w/2, yc + d/2)]:
                traces.append(go.Scatter3d(x=[cx, cx], y=[cy, cy], z=[zb, zt],
                                           mode='lines', line=dict(color=c, width=2), showlegend=False))

    # Vertical grid lines (building outline)
    for gx in range(int(min_x / gs) * int(gs), int(max_x / gs + 1) * int(gs) + 1, int(gs)):
        for gy in range(int(min_y / gs) * int(gs), int(max_y / gs + 1) * int(gs) + 1, int(gs)):
            traces.append(go.Scatter3d(x=[gx, gx], y=[gy, gy], z=[0, floors * 3],
                                       mode='lines', line=dict(color='#555', width=2, dash='dot'), showlegend=False))

    fig = go.Figure(data=traces)
    fig.update_layout(
        scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False),
                   bgcolor='#0a0a0a'),
        paper_bgcolor='#0a0a0a',
        margin=dict(l=0, r=0, b=0, t=20),
        showlegend=False,
        title="3D Massing",
        title_font=dict(color='#aaaaaa', size=14)
    )
    return fig

# ─── ISOMETRIC (canvas) ──────────────────────────────────────
def render_isometric(plan, span=6.0):
    w_, h_ = 800, 380
    unit_system = st.session_state.get("unit_system", "metric")
    unit = "ft" if unit_system == "imperial" else "m"

    js = f"""
    ctx.strokeStyle='rgba(100,100,100,0.1)';
    ctx.lineWidth=1;
    const step={span*2};
    for(let x=0; x<{w_}; x+=step){{ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,{h_});ctx.stroke();}}
    for(let y=0; y<{h_}; y+=step){{ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo({w_},y);ctx.stroke();}}
    """

    for i, r in enumerate(plan):
        ox = (i % 3) * 170 + 100
        oy = (i // 3) * 110 + 130
        rw = min(115, int(r["w"] * 14))
        rh = min(95, int(r["h"] * 14))
        c = r["color"]

        wd, _ = to_display_length(r["w"], unit_system)
        hd, _ = to_display_length(r["h"], unit_system)

        js += f"""
        ctx.fillStyle='{c}';
        ctx.beginPath();
        ctx.moveTo({ox},{oy});
        ctx.lineTo({ox+rw},{oy-rh/2});
        ctx.lineTo({ox+rw+rw},{oy});
        ctx.lineTo({ox+rw},{oy+rh/2});
        ctx.closePath();
        ctx.fill();
        ctx.strokeStyle='rgba(200,200,200,0.3)';
        ctx.stroke();
        ctx.fillStyle='rgba(200,200,200,0.06)';
        ctx.beginPath();
        ctx.moveTo({ox},{oy});
        ctx.lineTo({ox},{oy-40});
        ctx.lineTo({ox+rw},{oy+rh/2-40});
        ctx.lineTo({ox+rw},{oy+rh/2});
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
        ctx.fillStyle='#ccc';
        ctx.font='bold 11px Space Grotesk';
        ctx.fillText('{r["name"]} ({wd}×{hd} {unit})',{ox+15},{oy-2});
        """
    return f"""
    <canvas width='{w_}' height='{h_}' style='max-width:100%;background:#0a0a0a;'></canvas>
    <script>
    const c=document.querySelector('canvas');
    const ctx=c.getContext('2d');
    {js}
    </script>
    """

# ─── GANTT CHART (for construction schedule) ────────────────
def gantt_chart(asset):
    gfa = asset["total_gfa"]
    fl = asset["floors"]
    s = datetime.today()
    tasks = [("Mobilization", 5), ("Substructure", int(gfa * 0.15))] + \
            [(f"Floor {i+1}", 20) for i in range(fl)] + \
            [("Roofing", 12), ("Finishes", int(gfa * 0.02)), ("Commissioning", 14), ("Handover", 3)]
    df = pd.DataFrame(tasks, columns=["Task", "Duration"])
    ends = [s]
    for d in df["Duration"]:
        ends.append(ends[-1] + timedelta(days=d))
    df["Start"] = ends[:-1]
    df["Finish"] = ends[1:]
    fig = px.timeline(df, x_start="Start", x_end="Finish", y="Task", title="📅 Gantt Chart")
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#aaaaaa')
    )
    return fig

# ─── RADAR CHART (AI scores) ────────────────────────────────
def radar_chart(scores):
    categories = ['Architecture', 'Structural', 'Sustainability', 'Cost Efficiency']
    values = [scores['arch'], scores['struct'], scores['sust'], scores['cost']]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        marker=dict(color='#888'),
        line=dict(color='#aaa')
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(range=[0, 100], gridcolor='#333')),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#aaaaaa'),
        margin=dict(l=40, r=40, t=20, b=20)
    )
    return fig

# ─── SCHEDULE GANTT (with predecessors) ──────────────────────
def plot_schedule_gantt(df):
    fig = px.timeline(
        df,
        x_start="Start",
        x_end="Finish",
        y="Task",
        color="Predecessors",
        title="📅 Construction Schedule"
    )
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#aaaaaa')
    )
    return fig