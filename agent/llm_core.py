# agent/llm_core.py
#
# HOW IT WORKS:
# We call the Groq API which hosts Llama 3.3 70B for free.
# Groq is extremely fast (runs on custom LPU hardware).
# We send a "system prompt" that tells the AI to act as a copywriter,
# and a "user prompt" containing all the brief details.
# We force the AI to reply ONLY in JSON so we can parse it in code.
#
# KEY CONCEPT — Prompt Engineering:
# The system prompt defines the AI's role and output format.
# The user prompt injects the actual data (product name, audience, etc.)
# Separating them makes the AI more reliable and focused.

import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()  # reads .env file into os.environ

# Module-level cache for the Groq client (lazy initialization)
_groq_client = None


def get_groq_client():
	"""
	Lazily initialize and return the Groq client.
	Supports both local development (.env) and Streamlit Cloud (st.secrets).

	Priority order:
	1. Streamlit secrets (st.secrets["GROQ_API_KEY"]) — for Streamlit Cloud
	2. Environment variable (os.environ.get("GROQ_API_KEY")) — for local .env

	Raises ValueError if API key is not found in either source.
	"""
	global _groq_client

	if _groq_client is not None:
		return _groq_client

	api_key = None

	# Try Streamlit secrets first (only available in Streamlit context)
	try:
		import streamlit as st
		if hasattr(st, 'secrets') and "GROQ_API_KEY" in st.secrets:
			api_key = st.secrets["GROQ_API_KEY"]
	except (ImportError, Exception):
		pass

	# Fall back to environment variable
	if api_key is None:
		api_key = os.environ.get("GROQ_API_KEY")

	if not api_key:
		raise ValueError(
			"❌ GROQ_API_KEY not found!\n\n"
			"Local setup: Add GROQ_API_KEY to .env file\n"
			"Streamlit Cloud: Add secret in Settings → Secrets\n"
			"Get a key: https://console.groq.com/keys"
		)

	_groq_client = Groq(api_key=api_key)
	return _groq_client

# Platform character limits — different platforms allow different copy lengths
PLATFORM_SPECS = {
    "Facebook Feed":      {"headline": 40, "body": 125, "cta": 20},
    "Instagram Square":   {"headline": 30, "body":  90, "cta": 20},
    "Instagram Story":    {"headline": 35, "body": 100, "cta": 20},
    "LinkedIn":           {"headline": 60, "body": 150, "cta": 25},
    "Twitter / X":        {"headline": 50, "body": 130, "cta": 20},
}

SYSTEM_PROMPT = """
You are a professional advertising copywriter and creative director with 15 years of experience.
You receive a structured creative brief and produce platform-optimised ad copy.

CRITICAL: You MUST respond with ONLY a valid JSON object. No explanation, no markdown fences, 
no text before or after. Just the raw JSON.

Required JSON schema:
{
  "headline": "short punchy headline matching the char limit",
  "body": "body copy within char limit",
  "cta": "call to action button text",
  "image_prompt": "detailed visual description for image generation (describe the scene, mood, colors, style — no text or words in the image)",
  "video_script": "30-second spoken voiceover script, natural conversational tone, ~75 words",
  "rationale": "1 sentence explaining the creative strategy"
}
"""

def validate_brief(brief: dict) -> None:
    """Validate that brief contains all required fields."""
    required = {
        "product_name", "product_description", "company_name", "brand_voice",
        "target_audience", "cta_goal", "ad_type", "platform", "tone"
    }
    missing = required - set(brief.keys())
    if missing:
        raise ValueError(f"Brief missing required fields: {missing}")


def validate_char_limits(result: dict, spec: dict) -> dict:
    """Ensure response respects character limits; truncate if needed."""
    for field in ["headline", "body", "cta"]:
        if field in result and isinstance(result[field], str):
            if len(result[field]) > spec[field]:
                result[field] = result[field][:spec[field]].rstrip()
    return result


def generate_ad_copy(brief: dict) -> dict:
    """
    Takes a brief dictionary with all user inputs.
    Returns a parsed dictionary with all ad copy fields.
    
    brief must contain:
      product_name, product_description, company_name, brand_voice,
      target_audience, cta_goal, ad_type, platform, tone, special_notes
    """
    # Validate input before making API call
    validate_brief(brief)
    
    spec = PLATFORM_SPECS.get(brief["platform"], PLATFORM_SPECS["Facebook Feed"])

    # Build the user prompt — inject all brief data as structured text
    user_prompt = f"""
Create an ad for this brief. RESPOND ONLY WITH THE JSON OBJECT.

=== CREATIVE BRIEF ===
Product name: {brief['product_name']}
What it does: {brief['product_description']}
Company: {brief['company_name']}
Brand personality: {brief['brand_voice']}
Target audience: {brief['target_audience']}
Goal / CTA: {brief['cta_goal']}
Platform: {brief['platform']}
Ad format: {brief['ad_type']}
Tone: {brief['tone']}
Special notes: {brief.get('special_notes', 'None')}

=== STRICT CHARACTER LIMITS ===
headline: maximum {spec['headline']} characters
body: maximum {spec['body']} characters  
cta: maximum {spec['cta']} characters

Do not exceed these limits. Count carefully.
"""

    # API call to Groq / Llama 3.3
    # temperature=0.7 means slightly creative but not random
    # max_tokens=1024 is plenty for the JSON response
    client = get_groq_client()  # Get lazily initialized client
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_prompt}
        ],
        temperature=0.7,
        max_tokens=1024,
    )

    raw = response.choices[0].message.content.strip()

    # Sometimes models wrap output in ```json ... ``` even when told not to
    # This strips those fences robustly
    if raw.startswith("```"):
        raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        result = json.loads(raw)
        # Validate and enforce character limits
        result = validate_char_limits(result, spec)
    except json.JSONDecodeError:
        # If JSON is broken, return a safe fallback so the app doesn't crash
        result = {
            "headline": brief['product_name'],
            "body": brief['product_description'][:100],
            "cta": brief['cta_goal'],
            "image_prompt": f"Professional product photo of {brief['product_name']}, studio lighting",
            "video_script": f"Introducing {brief['product_name']} by {brief['company_name']}. {brief['product_description']}",
            "rationale": "Fallback copy — model returned invalid JSON."
        }

    return result