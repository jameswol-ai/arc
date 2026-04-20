class PromptTemplates:
    
    CONCEPT = """
    You are an architectural AI.
    Generate a sustainable building concept based on:
    {input}

    Focus on:
    - Climate adaptation
    - Spatial efficiency
    - Human-centered design
    """

    COMPLIANCE = """
    You are a building safety expert.
    Validate this concept:
    {concept}

    Check:
    - Safety codes
    - Environmental regulations
    - Structural logic
    """

    ANALYSIS = """
    You are an engineering analyst.
    Evaluate feasibility of:
    {concept}

    Provide:
    - Cost estimation range
    - Climate suitability
    - Material availability
    """
