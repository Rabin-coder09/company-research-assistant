import requests
import os
import json
import time
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

FALLBACK_MODELS = [
    "openrouter/free",
    "openai/gpt-oss-20b:free",
    "meta-llama/llama-3.3-70b-instruct:free",
]

DEFAULT_MODEL = FALLBACK_MODELS[0]


def call_openrouter(prompt, model=DEFAULT_MODEL, max_retries=2):
    """Send a prompt to OpenRouter. Retries on rate-limit, falls back to other free models if needed."""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    models_to_try = [model] + [m for m in FALLBACK_MODELS if m != model]

    last_error = None

    for candidate_model in models_to_try:
        payload = {
            "model": candidate_model,
            "messages": [{"role": "user", "content": prompt}]
        }

        for attempt in range(max_retries):
            try:
                response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=60)
            except requests.exceptions.RequestException as e:
                last_error = str(e)
                continue

            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]

            if response.status_code == 429:
                # Rate limited - wait and retry same model once, then move to next model
                last_error = f"Rate limited on {candidate_model}"
                time.sleep(3)
                continue

            if response.status_code == 404:
                # Model unavailable - break out and try next model in the list
                last_error = f"Model unavailable: {candidate_model}"
                break

            # Any other error - record and try next model
            last_error = f"{candidate_model} returned {response.status_code}: {response.text[:200]}"
            break

    raise Exception(f"All fallback models failed. Last error: {last_error}")


def clean_json_response(raw_text):
    """Strip markdown code fences and parse JSON safely."""
    text = raw_text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find the first { ... } block as a fallback
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            try:
                return json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                pass
        return None


def analyze_company(crawled_text, company_name, model=DEFAULT_MODEL, search_context=""):
    """Ask the AI to summarize the company from crawled text, with search results as backup context."""
    combined_context = crawled_text[:6000]
    if search_context:
        combined_context += "\n\nAdditional context from web search:\n" + search_context[:2000]

    prompt = f"""You are a business analyst. Based on the following information about the company "{company_name}", extract structured information.

Information:
{combined_context}

If the website content is mostly navigation, cookie notices, or legal boilerplate with no real business information, rely more heavily on the search context provided.

Return ONLY valid JSON, no explanation, no markdown, in exactly this structure:
{{
  "summary": "2-3 sentence company summary",
  "products_services": ["item1", "item2"],
  "pain_points": ["pain point 1", "pain point 2", "pain point 3"],
  "phone": "phone number if found, else empty string",
  "address": "address if found, else empty string"
}}
"""
    raw = call_openrouter(prompt, model=model)
    parsed = clean_json_response(raw)

    if parsed is None:
        parsed = {
            "summary": raw[:500],
            "products_services": [],
            "pain_points": [],
            "phone": "",
            "address": ""
        }
    return parsed


def find_competitors(company_name, search_snippets, model=DEFAULT_MODEL):
    """Ask the AI to identify competitors from search snippet text."""
    prompt = f"""Based on the following search results about competitors of "{company_name}", identify up to 5 real competitor companies.

Search results:
{search_snippets[:4000]}

Return ONLY valid JSON, no explanation, no markdown, as a list in exactly this structure:
[
  {{"name": "Competitor Name", "website": "https://example.com"}}
]
"""
    raw = call_openrouter(prompt, model=model)
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("[")
        end = text.rfind("]")
        if start != -1 and end != -1:
            try:
                return json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                pass
        return []