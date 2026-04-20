import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # 🌍 General App Config
    APP_NAME = "AI Architectural Bot"
    ENV = os.getenv("ENV", "development")

    # 🧠 Engine Config
    DEFAULT_WORKFLOW = os.getenv("DEFAULT_WORKFLOW", "basic_design")
    DEBUG_MODE = os.getenv("DEBUG_MODE", "True") == "True"

    # 🌿 Climate / Design Defaults
    DEFAULT_CLIMATE = os.getenv("DEFAULT_CLIMATE", "tropical")
    DEFAULT_BUDGET_LEVEL = os.getenv("DEFAULT_BUDGET_LEVEL", "low")

    # 🔌 API Keys (loaded from env)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MAPS_API_KEY = os.getenv("MAPS_API_KEY", "")
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")

    # 🧪 Testing Flags
    RUN_MOCK_STAGES = os.getenv("RUN_MOCK_STAGES", "False") == "True"


settings = Settings()
