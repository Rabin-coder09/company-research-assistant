# AI Company Research Assistant

An AI-powered application that researches any company by name or website URL, crawls its site, analyzes it with AI, identifies competitors, and generates a downloadable PDF report — all through a ChatGPT-style interface.

## Features

- Accepts company name OR website URL as input
- Automatically resolves official website from company name (via Serper.dev)
- Crawls key pages (About, Products, Services, Contact, Pricing)
- AI-powered analysis (OpenRouter) generating company summary, products/services, and pain points
- Competitor identification using live search data
- One-click downloadable PDF report
- Discord bot integration (bonus) — auto-sends report + applicant details to a configured channel
- Model selection — choose any OpenRouter-supported model

## Tech Stack

- **Frontend/Backend:** Streamlit
- **Search:** Serper.dev API
- **AI:** OpenRouter API (model-agnostic)
- **Web Crawling:** requests + BeautifulSoup
- **PDF Generation:** ReportLab
- **Notifications:** Discord Bot API

## Setup Instructions

1. Clone the repository:
```bash
   git clone <your-repo-url>
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

4. Set up environment variables (see below).

5. Run the app:
```bash
   streamlit run app.py
```

6. Open `http://localhost:8501` in your browser.

## Environment Variables

Create a `.env` file in the project root with:
SERPER_API_KEY=your_serper_api_key
OPENROUTER_API_KEY=your_openrouter_api_key
DISCORD_BOT_TOKEN=your_discord_bot_token
DISCORD_CHANNEL_ID=your_discord_channel_id
- **SERPER_API_KEY** — get from https://serper.dev
- **OPENROUTER_API_KEY** — get from https://openrouter.ai/keys
- **DISCORD_BOT_TOKEN / DISCORD_CHANNEL_ID** — optional, only needed for the Discord bonus feature. Can also be entered directly in the app's sidebar at runtime.

## How It Works

1. User enters a company name or website URL in the chat interface.
2. If a name is given, Serper.dev is used to resolve the official website.
3. The crawler discovers and extracts content from key internal pages.
4. If crawled content is sparse (common on JS-heavy sites), Serper search snippets are used as additional context.
5. OpenRouter AI analyzes the combined content to generate a summary, products/services list, and pain points.
6. Serper is queried again to find real competitor URLs, which the AI structures into a competitor list.
7. A professional PDF report is generated and made available for download.
8. If Discord is configured, the report and applicant details are automatically posted to the specified channel.

## Known Limitations

- Crawling is limited to static HTML; JavaScript-rendered content on some sites (e.g. Tesla.com) may return limited data, mitigated by falling back to search-based context.
- Free-tier AI models on OpenRouter can have variable availability; the app uses OpenRouter's `openrouter/free` auto-router plus fallback models to stay resilient.
- No database or authentication — all processing is done in-memory per session.

## Deployment

Live URL: [add your deployed link here]

Deployed on Streamlit Community Cloud. To deploy your own copy:
1. Push this repo to GitHub.
2. Go to https://share.streamlit.io, connect your GitHub repo.
3. Set `app.py` as the entry point.
4. Add your environment variables under App Settings → Secrets, in TOML format:
```toml
   SERPER_API_KEY = "your_key"
   OPENROUTER_API_KEY = "your_key"
   DISCORD_BOT_TOKEN = "your_key"
   DISCORD_CHANNEL_ID = "your_id"
```