# nlp_utils.py

from typing import List
import json


def extract_keywords(
    text: str,
    openai_key: str | None = None,
    gemini_key: str | None = None
) -> List[str]:

    if gemini_key:
        return _extract_with_gemini(text, gemini_key)

    if openai_key:
        return _extract_with_openai(text, openai_key)

    raise ValueError("No valid API key provided for keyword extraction.")


# =========================================
# GEMINI
# =========================================

def _extract_with_gemini(text: str, api_key: str) -> List[str]:
    from google import genai

    client = genai.Client(api_key=api_key)

    prompt = f"""
Extract 5-8 short cinematic stock video search keywords from this lyric:

{text}

Return only a JSON list of strings.
"""

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt
    )

    raw = response.text.strip()

    try:
        keywords = json.loads(raw)
        return keywords
    except Exception:
        # Fallback if Gemini wraps output in markdown
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)


# =========================================
# OPENAI
# =========================================

def _extract_with_openai(text: str, api_key: str) -> List[str]:
    from openai import OpenAI

    client = OpenAI(api_key=api_key)

    prompt = f"""
Extract 5-8 short cinematic stock video search keywords from this lyric:

{text}

Return only a JSON list of strings.
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    raw = response.output_text.strip()

    try:
        return json.loads(raw)
    except Exception:
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)