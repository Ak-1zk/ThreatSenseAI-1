"""
============================================================
SERVICE: Daily Threat Briefing
OWNER:   Person D
============================================================

Generates a daily cybersecurity threat briefing using
Gemini AI. Returns a Markdown-formatted summary of current
threats and actionable advice.
============================================================
"""

from backend.services.gemini_service import get_gemini_client, get_model_id


SYSTEM_INSTRUCTION = (
    "You are a cybersecurity analyst providing a daily threat briefing. "
    "Provide a concise summary (under 300 words) of the most important "
    "current cybersecurity threats, vulnerabilities, and security news. "
    "Use Markdown formatting with headers, bullet points, and bold text. "
    "Focus on actionable items that everyday users should be aware of."
)


import datetime

from google.genai import types

def generate_daily_briefing() -> str:
    """
    Generates a daily cybersecurity threat briefing.

    Returns:
        A Markdown-formatted string with threat intelligence.
    """
    client = get_gemini_client()
    today = datetime.date.today().strftime("%B %d, %Y")

    try:
        response = client.models.generate_content(
            model=get_model_id(),
            contents=f"Give me today's ({today}) cybersecurity threat briefing with the most important items.",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.7,
                max_output_tokens=500,
            ),
        )
        return response.text or "Unable to generate briefing."
    except Exception as e:
        print(f"Error in briefing service: {e}")
        raise e
