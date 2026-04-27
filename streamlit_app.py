# random/streamlit_app.py 

import streamlit as st from dataclasses import dataclass, field from typing import List, Dict, Any, Optional import random

=========================

🌱 LIVING STATE LAYER

=========================

@dataclass class LivingState: memory: List[Dict[str, Any]] = field(default_factory=list) emotion_tone: str = "neutral" last_output: Optional[Any] = None evolution_score: int = 0

def observe(self, event: Dict[str, Any]):
    self.memory.append(event)
    self.evolution_score += 1

def reflect(self) -> Dict[str, Any]:
    return {
        "memory_depth": len(self.memory),
        "tone": self.emotion_tone,
        "evolution": self.evolution_score
    }

=========================

🎭 NARRATIVE LAYER

=========================

class NarrativeLayer: def narrate(self, stage: str, output: Any) -> str: return f"🌿 {stage} breathes through the system: {output}"

=========================

🧬 EXPANSION ENGINE

=========================

class ExpansionEngine: def maybe_expand(self, state: LivingState) -> Optional[Dict[str, Any]]: if state.evolution_score > 0 and state.evolution_score % 5 == 0: return { "name": "emergent_thinking", "type": "auto_generated_stage" } return None

=========================

🧠 SELF-EDIT ENGINE

=========================

class SelfEditEngine: def mutate(self, workflow: List[Dict[str, Any]], state: LivingState) -> List[Dict[str, Any]]: """ The system rewrites its own structure based on memory + evolution. """ new_workflow = list(workflow)

# 🧬 Rule 1: Evolution unlocks new stage
    if state.evolution_score > 3:
        new_stage = {
            "name": "adaptive_reasoning",
            "type": "self_generated"
        }
        if new_stage not in new_workflow:
            new_workflow.insert(1, new_stage)

    # 🌪 Rule 2: Random mutation (controlled chaos)
    if state.evolution_score > 6:
        if random.random() > 0.5:
            new_workflow.append({
                "name": "chaos_reflection",
                "type": "mutation"
            })

    # 🧠 Rule 3: Memory echo stage injection
    if len(state.memory) > 4:
        new_workflow.append({
            "name": "memory_echo",
            "type": "reflective"
        })

    return new_workflow

=========================

⚙️ WORKFLOW ENGINE (ALIVE + SELF-EDITING)

=========================

class WorkflowEngine: def init(self): self.base_workflow = [ {"name": "concept_stage"}, {"name": "climate_check"}, {"name": "eco_design"} ] self.state = LivingState() self.narrator = NarrativeLayer() self.expander = ExpansionEngine() self.self_editor = SelfEditEngine()

def execute_stage(self, stage: Dict[str, Any], input_data: str) -> str:
    return f"processed({stage['name']}) on '{input_data}'"

def run(self, input_data: str):
    workflow = self.self_editor.mutate(self.base_workflow, self.state)
    results = []

    for stage in workflow:
        output = self.execute_stage(stage, input_data)

        self.state.observe({
            "stage": stage["name"],
            "output": output
        })

        narrated = self.narrator.narrate(stage["name"], output)
        results.append(narrated)

        new_stage = self.expander.maybe_expand(self.state)
        if new_stage:
            workflow.append(new_stage)

    return results, self.state.reflect()

=========================

🖥️ STREAMLIT UI

=========================

st.set_page_config(page_title="Random Alive Self-Editing System", layout="wide")

st.title("🌱 Random: Self-Editing Living System v3") st.caption("A workflow engine that grows, remembers, narrates, AND rewrites itself.")

if "engine" not in st.session_state: st.session_state.engine = WorkflowEngine()

engine = st.session_state.engine

input_data = st.text_input("Enter architecture prompt:", "design a tropical smart city")

col1, col2 = st.columns(2)

with col1: run_btn = st.button("Run Alive Workflow") edit_btn = st.button("Self-Edit Cycle")

if run_btn: with st.spinner("The system is thinking… evolving… rewriting itself 🌿🧠"): results, reflection = engine.run(input_data)

st.subheader("🌿 Narrative Output")
for r in results:
    st.write(r)

st.subheader("🧠 System Reflection")
st.json(reflection)

if edit_btn: with st.spinner("System is rewriting its own structure… 🧬"): engine.base_workflow = engine.self_editor.mutate(engine.base_workflow, engine.state)

st.success("Workflow has self-edited its architecture.")
st.json(engine.base_workflow)

with col2: if st.button("Show Memory"): st.subheader("🧬 Memory Trace") st.json(engine.state.memory)

if st.button("Reset Life Cycle"): st.session_state.engine = WorkflowEngine() st.success("System reset. The organism has been reborn.")
