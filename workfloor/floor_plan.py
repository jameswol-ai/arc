def generate_floor_plan(user_input):
    return f"""
You are an architectural planner.

Design a floor plan based on:
{user_input}

Return:
- Number of rooms
- Spatial layout logic (public/private zoning)
- Room relationships (adjacency)
- Suggested circulation flow
- Basic dimension assumptions
"""
