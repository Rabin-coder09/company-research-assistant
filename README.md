# 🔍 AI Company Research Assistant

An AI-powered application that researches any company by name or website URL, crawls its site, analyzes it with AI, identifies competitors, and generates a downloadable PDF report — all through a modern, ChatGPT-style interface.

**Repo:** https://github.com/Rabin-coder09/company-research-assistant

## Features

- Accepts company name OR website URL as input
- Automatically resolves official website from company name (via Serper.dev)
- Crawls key pages (About, Products, Services, Contact, Pricing)
- Falls back to search-based context when a site is JavaScript-heavy and yields little static content
- AI-powered analysis (OpenRouter) generating company summary, products/services, and pain points
- Competitor identification using live search data, cross-checked against real URLs
- One-click downloadable PDF report
- Discord bot integration (bonus) — auto-sends report + applicant details to a configured channel
- Model selection — choose any OpenRouter-supported model, with automatic fallback if a free model is rate-limited or deprecated
- Polished, custom-styled UI (gradient theme, card layout, competitor chips)

## Tech Stack

- **Frontend/Backend:** Streamlit
- **Search:** Serper.dev API
- **AI:** OpenRouter API (model-agnostic, with `openrouter/free` auto-routing for resilience)
- **Web Crawling:** requests + BeautifulSoup
- **PDF Generation:** ReportLab
- **Notifications:** Discord Bot API

## Setup Instructions

1. Clone the repository:
```bash
   git clone https://github.com/Rabin-coder09/company-research-assistant.git
   cd company-research-assistant
```

2. Create and activate a virtual environment:
```bash
   conda create -n company-research python=3.11 -y
   conda activate company-research
```

3. Install dependencies:
```bash
   pip install -r requirements.txt
```

4. Set up environment variables (copy `.env.example` to `.env` and fill in your keys — see below).

5. Run the app:
```bash
   streamlit run app.py
```

6. Open `http://localhost:8501` in your browser.

## Environment Variables

Create a `.env` file in the project root (use `.env.example` as a template):
SERPER_API_KEY=your_serper_api_key
OPENROUTER_API_KEY=your_openrouter_api_key
DISCORD_BOT_TOKEN=your_discord_bot_token
DISCORD_CHANNEL_ID=your_discord_channel_id
- **SERPER_API_KEY** — get from https://serper.dev (free tier: ~2,500 queries)
- **OPENROUTER_API_KEY** — get from https://openrouter.ai/keys (free models available, no credit card required)
- **DISCORD_BOT_TOKEN / DISCORD_CHANNEL_ID** — optional, only needed for the Discord bonus feature. Can also be entered directly in the app's sidebar at runtime.

## How It Works

1. User enters a company name or website URL in the chat interface.
2. If a name is given, Serper.dev resolves the official website.
3. The crawler discovers and extracts content from key internal pages (About, Products, Contact, Pricing, etc.), skipping duplicates and login pages.
4. If crawled content is sparse (common on JS-heavy sites), Serper search snippets are used as additional AI context.
5. OpenRouter AI analyzes the combined content to generate a company summary, products/services list, and pain points.
6. Serper is queried again for competitor mentions; the AI structures these into a competitor list, validated against real URLs from search results.
7. A professional PDF report is generated and made available for one-click download.
8. If Discord is configured, the report PDF and applicant details are automatically posted to the specified channel via the Discord Bot API.

## Known Limitations

- Crawling is limited to static HTML; heavily JavaScript-rendered sites may return limited page content, mitigated by falling back to search-based context.
- Free-tier AI models on OpenRouter can have variable availability/rate limits; the app uses OpenRouter's `openrouter/free` auto-router plus named fallback models to stay resilient.
- No database, authentication, or report history — all processing happens in-memory per session, per the assignment's requirements.

## Deployment

**Live URL:** [add your deployed link here once live]

Deployed on Streamlit Community Cloud. To deploy your own copy:
1. Push this repo to GitHub (already done ✅).
2. Go to https://share.streamlit.io and connect your GitHub repo.
3. Set `app.py` as the entry point.
4. Under App Settings → Secrets, add your keys in TOML format:
```toml
   SERPER_API_KEY = "your_key"
   OPENROUTER_API_KEY = "your_key"
   DISCORD_BOT_TOKEN = "your_key"
   DISCORD_CHANNEL_ID = "your_id"
```

## Author

Rabin Pal
