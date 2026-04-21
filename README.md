# random

Random AI is an AI tool that helps architects and engineers in East Africa design, check compliance, and prepare documentation quickly and efficiently.
It provides references to regional building codes, automated compliance checks, and sample workflows for engineers and architects.

What It Does
- Generate concept drawings adapted to tropical climates and local materials  
- Check designs against Uganda Building Code 2024 and South Sudan guidelines  
- Create simple reports, proposals, and compliance checklists  
- Support collaboration through GitHub workflows
  

Repo Structure

ai-architecture

├── docs/              (Regional building codes and standards references)
├── src/               (Core bot logic)
├── workflows/         (Predefined workflows (concepts, compliance, docs))
├── examples/          (Sample usage scripts)
├── tests/             (Unit tests)
├── README.md          (Project overview)
└── LICENSE           (License file)


Final Repo Structure (Extended)
ai-architecture-bot/
│
├── src/
│   ├── core/
│   │   ├── engine.py              # Workflow engine (runs stages)
│   │   ├── context.py             # Shared memory/state handler
│   │   └── dispatcher.py          # Routes tasks between stages
│   │
│   ├── stages/
│   │   ├── concept_stage.py       # Idea generation (design thinking)
│   │   ├── compliance_stage.py    # Rules, safety, building codes
│   │   ├── analysis_stage.py      # Climate, cost, feasibility logic
│   │   └── output_stage.py        # Final architectural plan output
│   │
│   ├── models/
│   │   ├── prompt_models.py       # Prompt templates for AI generation
│   │   └── design_schema.py       # Structure of architectural output
│   │
│   ├── utils/
│   │   ├── logger.py              # Debug + workflow tracking
│   │   ├── validators.py          # Input/output validation
│   │   └── helpers.py             # Small reusable tools
│   │
│   └── main.py                    # Entry point (run system here)
│
├── workflows/
│   ├── basic_design.json          # Simple architecture pipeline
│   ├── eco_building.json          # Eco-friendly workflow
│   └── urban_plan.json            # Large-scale city design flow
│
├── docs/
│   ├── building_codes/
│   │   ├── global_standards.md
│   │   ├── tropical_climate.md
│   │   └── fire_safety_rules.md
│   │
│   ├── system_design.md
│   └── architecture_notes.md
│
├── examples/
│   ├── run_basic.py
│   ├── run_eco.py
│   └── sample_inputs.json
│
├── tests/
│   ├── test_engine.py
│   ├── test_stages.py
│   └── test_workflows.py
│
├── config/
│   ├── settings.py               # Global config
│   └── api_keys.env.example
│
├── requirements.txt
├── README.md
└── .gitignore
