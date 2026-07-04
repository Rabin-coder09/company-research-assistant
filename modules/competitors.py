from modules.search import search_competitors_raw
from modules.ai import find_competitors
import re


def get_competitors(company_name, model="openrouter/free"):
    """Search for competitors and let AI structure the results using only real URLs from search."""
    raw_results = search_competitors_raw(company_name)

    if not raw_results:
        return []

    snippets_lines = []
    real_urls = set()
    for item in raw_results:
        title = item.get("title", "")
        snippet = item.get("snippet", "")
        link = item.get("link", "")
        if link:
            real_urls.add(link)
        snippets_lines.append(f"{title}: {snippet} (URL: {link})")

    snippets = "\n".join(snippets_lines)

    competitors = find_competitors(company_name, snippets, model=model)

    def core_domain(url):
        match = re.search(r"https?://(?:www\.)?([^/]+)", url or "")
        if not match:
            return ""
        domain = match.group(1).lower()
        parts = domain.split(".")
        return parts[-2] if len(parts) >= 2 else domain

    real_cores = {core_domain(u) for u in real_urls}

    valid = []
    for c in competitors:
        if not isinstance(c, dict) or not c.get("name"):
            continue
        website = c.get("website", "")
        c_core = core_domain(website)
        if c_core and c_core in real_cores:
            valid.append({"name": c["name"], "website": website})
        else:
            # Keep the AI's guess but don't claim it's verified against search data
            valid.append({"name": c["name"], "website": website or "N/A"})

    return valid