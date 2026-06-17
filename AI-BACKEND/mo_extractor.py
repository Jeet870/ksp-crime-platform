# mo_extractor.py
# Extracts Modus Operandi (crime method) from raw FIR text
# Uses Groq API (free tier: 14,400 requests/day, no credit card needed)

import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL_NAME = "llama-3.1-8b-instant"   # fast + generous free tier


def extract_mo(fir_text: str) -> dict:
    """
    Takes a raw FIR description text and returns a structured
    Modus Operandi (MO) JSON object.

    Returns dict with keys:
        method      - how the crime was committed
        entry_point - how criminal entered (if applicable)
        time_pattern- time of day pattern if mentioned
        target_type - residential / commercial / person / vehicle
        tools_used  - any tools or weapons mentioned
        crime_category - burglary / snatching / fraud / assault / theft / other
    """

    prompt = f"""You are a forensic crime analyst for Karnataka State Police.
Extract the Modus Operandi from this FIR description.

Return ONLY a valid JSON object with these exact keys:
{{
  "method": "brief description of how the crime was committed",
  "entry_point": "how the criminal entered or approached (write none if not applicable)",
  "time_pattern": "time of day or night pattern if mentioned (write unknown if not mentioned)",
  "target_type": "one of: residential / commercial / person / vehicle / financial / other",
  "tools_used": "any tools weapons or equipment mentioned (write none if not mentioned)",
  "crime_category": "one of: burglary / chain_snatching / cyber_fraud / vehicle_theft / assault / robbery / other"
}}

Do not add any explanation before or after the JSON.
Do not use markdown code blocks.
Return only the raw JSON object.

FIR Text:
{fir_text[:1000]}

JSON:"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
        temperature=0.2,
    )

    raw = response.choices[0].message.content.strip()

    # Clean up any accidental markdown the model might add
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        mo = json.loads(raw)
        # Validate all keys exist
        required = ["method","entry_point","time_pattern","target_type","tools_used","crime_category"]
        for key in required:
            if key not in mo:
                mo[key] = "unknown"
        return mo
    except json.JSONDecodeError:
        # If model returned bad JSON, retry once with stricter prompt
        return extract_mo_strict(fir_text)


def extract_mo_strict(fir_text: str) -> dict:
    """Fallback with a stricter prompt if the first attempt fails."""
    prompt = f"""Extract crime method from this text. Return ONLY JSON, nothing else.
Format: {{"method":"...","entry_point":"...","time_pattern":"...","target_type":"...","tools_used":"...","crime_category":"..."}}

Text: {fir_text[:500]}"""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.0,
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json","").replace("```","").strip()
        return json.loads(raw)
    except Exception:
        # Last resort: return a default structure
        return {
            "method": "unknown",
            "entry_point": "unknown",
            "time_pattern": "unknown",
            "target_type": "other",
            "tools_used": "none",
            "crime_category": "other"
        }


def mo_to_string(mo: dict) -> str:
    """
    Converts MO dict to a single descriptive string for embedding.
    This string is what gets converted into a vector.
    """
    return (
        f"Crime method: {mo.get('method', 'unknown')}. "
        f"Entry point: {mo.get('entry_point', 'unknown')}. "
        f"Time pattern: {mo.get('time_pattern', 'unknown')}. "
        f"Target type: {mo.get('target_type', 'unknown')}. "
        f"Tools used: {mo.get('tools_used', 'none')}. "
        f"Crime category: {mo.get('crime_category', 'other')}."
    )