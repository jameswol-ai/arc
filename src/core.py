import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("API_KEY"))

def generate_response(prompt, context=""):
    system_prompt = """
    You are an Architectural AI assistant.
    You help with:
    - Building design concepts
    - Space planning
    - Construction methods
    - Compliance with building standards
    - Generating documentation ideas
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": context + "\n" + prompt}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content
