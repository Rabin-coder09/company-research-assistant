import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

TARGET_KEYWORDS = ["about", "product", "service", "solution", "contact", "pricing"]
SKIP_KEYWORDS = ["login", "signin", "sign-in", "signup", "sign-up", "cart", "account", ".pdf", ".jpg", ".png", "mailto:", "tel:"]


def get_soup(url):
    """Fetch a URL and return a BeautifulSoup object."""
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    return BeautifulSoup(response.text, "lxml")


def normalize_url(url):
    """Strip trailing slashes and fragments for dedup comparison."""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path.rstrip('/')}"


def discover_pages(base_url, max_pages=6):
    """Find important internal pages (about, products, contact, etc.)."""
    try:
        soup = get_soup(base_url)
    except Exception as e:
        print(f"Failed to fetch base URL: {e}")
        return [base_url]

    domain = urlparse(base_url).netloc
    seen = {normalize_url(base_url)}
    candidates = []

    for a in soup.find_all("a", href=True):
        href = urljoin(base_url, a["href"])
        parsed = urlparse(href)

        if parsed.netloc != domain:
            continue

        low = href.lower()
        if any(skip in low for skip in SKIP_KEYWORDS):
            continue

        norm = normalize_url(href)
        if norm in seen:
            continue

        if any(keyword in low for keyword in TARGET_KEYWORDS):
            candidates.append(href)
            seen.add(norm)

        if len(candidates) >= max_pages:
            break

    return [base_url] + candidates


def extract_text(url, char_limit=4000):
    """Extract clean visible text from a page."""
    try:
        soup = get_soup(url)
        for tag in soup(["script", "style", "nav", "footer", "noscript", "svg"]):
            tag.decompose()
        text = " ".join(soup.stripped_strings)
        return text[:char_limit]
    except Exception as e:
        print(f"Failed to extract from {url}: {e}")
        return ""


def crawl_site(base_url, max_pages=6):
    """Crawl the site and return a dict of {url: extracted_text}."""
    pages = discover_pages(base_url, max_pages=max_pages)
    results = {}
    for url in pages:
        text = extract_text(url)
        if text:
            results[url] = text
    return results