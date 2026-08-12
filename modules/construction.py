# =========================================================
# Construction schedule generation
# =========================================================
from datetime import datetime, timedelta
import pandas as pd

def compute_construction_schedule(d):
    floors = d["floors"]
    gfa = d["total_gfa"]
    tasks = [
        {"id": "A", "name": "Mobilization", "duration": 5, "predecessors": []},
        {"id": "B", "name": "Site Clearance", "duration": 3, "predecessors": ["A"]},
        {"id": "C", "name": "Excavation", "duration": max(3, int(gfa / 200)), "predecessors": ["B"]},
        {"id": "D", "name": "Foundation", "duration": max(4, int(gfa / 150)), "predecessors": ["C"]},
        {"id": "E", "name": "Substructure Columns", "duration": max(3, floors), "predecessors": ["D"]},
        {"id": "F", "name": "Ground Floor Slab", "duration": max(4, int(gfa / 300)), "predecessors": ["E"]},
        {"id": "G1", "name": "Floor 1 Columns", "duration": 3, "predecessors": ["F"]},
        {"id": "G2", "name": "Floor 1 Slab", "duration": 4, "predecessors": ["G1"]},
        {"id": "H1", "name": "Floor 2 Columns", "duration": 3, "predecessors": ["G2"]},
        {"id": "H2", "name": "Floor 2 Slab", "duration": 4, "predecessors": ["H1"]},
        {"id": "I", "name": "Roof", "duration": max(5, int(gfa / 400)), "predecessors": ["H2" if floors >= 2 else "G2"]},
        {"id": "J", "name": "Finishes", "duration": max(6, int(gfa / 200)), "predecessors": ["I"]},
        {"id": "K", "name": "MEP Installation", "duration": max(5, int(gfa / 250)), "predecessors": ["F"]},
        {"id": "L", "name": "External Works", "duration": 5, "predecessors": ["J"]},
        {"id": "M", "name": "Commissioning", "duration": 4, "predecessors": ["J", "K", "L"]},
        {"id": "N", "name": "Handover", "duration": 2, "predecessors": ["M"]},
    ]
    start = datetime.today()
    task_dict = {t["id"]: t for t in tasks}
    visited = set()
    ordered = []
    def visit(n):
        if n in visited: return
        visited.add(n)
        for pred in task_dict[n]["predecessors"]:
            if pred in task_dict:
                visit(pred)
        ordered.append(n)
    for t in tasks:
        if t["id"] not in visited:
            visit(t["id"])
    finish = {}
    schedule = []
    for tid in ordered:
        t = task_dict[tid]
        pred_finish = [finish[p] for p in t["predecessors"] if p in finish]
        if pred_finish:
            start_date = max(pred_finish)
        else:
            start_date = start
        finish_date = start_date + timedelta(days=t["duration"])
        finish[tid] = finish_date
        schedule.append({
            "Task": t["name"],
            "Duration": t["duration"],
            "Start": start_date,
            "Finish": finish_date,
            "Predecessors": ", ".join(t["predecessors"])
        })
    return pd.DataFrame(schedule)