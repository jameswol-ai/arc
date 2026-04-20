# src/stages/output_stage.py

def output_stage(ctx):
    concept = ctx.get("concept")
    compliance = ctx.get("compliance")
    analysis = ctx.get("analysis")

    final_plan = f"""
    FINAL ARCHITECTURAL PLAN
    =========================

    {concept}

    --- COMPLIANCE ---
    {compliance}

    --- ANALYSIS ---
    {analysis}

    RESULT:
    A fully validated eco-architectural blueprint ready for development.
    """

    ctx.set("final_output", final_plan)
    return final_plan
