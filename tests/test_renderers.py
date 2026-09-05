import plotly.graph_objects as go

from modules.renderers import render_3d, render_floorplan, render_isometric


def test_floorplan_handles_empty_plan():
    fig = render_floorplan([])
    assert isinstance(fig, go.Figure)
    assert len(fig.layout.shapes) > 0


def test_floorplan_handles_metric_planner_room_names():
    plan = [
        {"type": "Corridor", "name": "Metric Main Corridor", "w": 1.5, "h": 8.0, "color": "#334155"},
        {"type": "Stairs", "name": "Metric Stair Core", "w": 2.0, "h": 7.0, "color": "#475569"},
        {"type": "Bedroom", "name": "Bedroom 1", "w": 3.0, "h": 3.6, "color": "#334155"},
    ]
    fig = render_floorplan(plan)
    assert isinstance(fig, go.Figure)
    assert len(fig.layout.annotations) >= 2


def test_3d_and_isometric_handle_empty_plan():
    assert isinstance(render_3d([]), go.Figure)
    html = render_isometric([])
    assert "canvas" in html
