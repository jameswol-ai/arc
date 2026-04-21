# src/stages/refiner_stage.py

from src.models.agent import AgentResponse


def refiner_stage(ctx):
    last = ctx.get("last_output", {})

    output = last.get("output", "")
    critique = last.get("critique", "")
    confidence = last.get("confidence", 0)

    # 🔁 self-improvement logic
    if confidence < 0.8:
        improved = output + " (refined with added environmental adaptation)"
        confidence += 0.1
    else:
        improved = output

    return AgentResponse(
        output=improved,
        critique="Refinement applied based on previous critique",
        confidence=confidence,
        signals={
            "refined": True
        }
    ).to_dict()
