def apply_building_rules(design_input):
    return f"""
You are a building compliance assistant.

Check the design below against general safe building principles:

{design_input}

Evaluate:
- Minimum room usability
- Ventilation logic
- Safety spacing
- Accessibility considerations
- Structural realism warnings

Flag issues clearly.
"""
