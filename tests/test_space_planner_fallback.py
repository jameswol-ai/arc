from modules.space_planner import _adjacency_score, generate_metric_plan


def test_adjacency_score_accepts_unplaced_legacy_rooms():
    rooms = [
        {"type": "Bedroom", "w": 3.0, "h": 3.6},
        {"type": "Bathroom", "w": 1.8, "h": 2.4},
    ]
    assert _adjacency_score(rooms) == 0.0


def test_fallback_plan_has_coordinates():
    plan = generate_metric_plan(
        domain="Industrial",
        plot_size=200.0,
        floors=1,
        room_types=["Manufacturing", "Loading Bay", "Storage"],
        baths=2,
        seed=1,
        candidates=1,
    )
    assert plan["rooms"]
    assert all("x" in room and "y" in room for room in plan["rooms"])
    assert isinstance(plan["metric_planning_score"], float)
