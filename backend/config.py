"""
Configuration module — loads environment variables.
"""

import os
from dotenv import load_dotenv

# Load .env from the project root (parent of backend/)
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env.local'))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.0-flash-lite-001"
