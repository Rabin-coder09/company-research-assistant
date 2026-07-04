import requests
import os
from dotenv import load_dotenv

load_dotenv()

SERPER_API_KEY = os.getenv("SERPER_API_KEY")


def serper_search(query, num=5):
    """Run a search query via Serper.dev and return raw JSON results."""
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {"q": query, "num": num}

    response = requests.post(url, headers=headers, json=payload, timeout=15)
    response.raise_for_status()
    return response.json()


def resolve_official_website(company_name):
    """Given a company name, find its most likely official website."""
    data = serper_search(f"{company_name} official website")
    organic = data.get("organic", [])
    if not organic:
        return None
    return organic[0].get("link")


def search_contact_info(company_name):
    """Search for phone/address info if not found on the website."""
    data = serper_search(f"{company_name} phone number address contact")
    return data.get("organic", [])


def search_competitors_raw(company_name, hint=""):
    """Search for competitor info as raw search snippets."""
    query = f"top competitors of {company_name} {hint}".strip()
    data = serper_search(query)
    return data.get("organic", [])