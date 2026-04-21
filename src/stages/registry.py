# src/stages/registry.py

from src.stages.refiner_stage import refiner_stage

STAGE_REGISTRY.update({
    "refiner": refiner_stage
})
