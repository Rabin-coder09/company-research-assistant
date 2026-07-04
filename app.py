import streamlit as st
import os
from dotenv import load_dotenv

from modules.search import resolve_official_website, serper_search
from modules.crawler import crawl_site
from modules.ai import analyze_company, DEFAULT_MODEL
from modules.competitors import get_competitors
from modules.pdf_report import generate_pdf
from modules.discord_notify import send_report_to_discord

load_dotenv()

st.set_page_config(
    page_title="AI Company Research Assistant",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------------------------
# CUSTOM CSS — modern, ChatGPT-style dark accent theme
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main {
        background: linear-gradient(180deg, #fafbff 0%, #f4f6fb 100%);
    }

    /* Hero header */
    .hero-title {
        font-size: 2.6rem;
        font-weight: 800;
        background: linear-gradient(90deg, #6366f1, #8b5cf6, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .hero-subtitle {
        color: #6b7280;
        font-size: 1.05rem;
        margin-top: 4px;
        margin-bottom: 28px;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1b2e 0%, #171425 100%);
    }
    section[data-testid="stSidebar"] * {
        color: #e5e7eb !important;
    }
    section[data-testid="stSidebar"] input, 
    section[data-testid="stSidebar"] select,
    section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
        background-color: #2a2640 !important;
        color: #f3f4f6 !important;
        border-radius: 10px !important;
        border: 1px solid #3f3a5c !important;
    }
    section[data-testid="stSidebar"] button {
        background: linear-gradient(90deg, #6366f1, #8b5cf6) !important;
        color: white !important;
        border-radius: 10px !important;
        border: none !important;
        font-weight: 600 !important;
    }

    /* Result cards */
    .result-card {
        background: white;
        border-radius: 18px;
        padding: 28px 32px;
        margin-bottom: 24px;
        box-shadow: 0 4px 24px rgba(99, 102, 241, 0.08);
        border: 1px solid #eef0f7;
    }
    .company-name {
        font-size: 1.8rem;
        font-weight: 800;
        color: #1f2937;
        margin-bottom: 4px;
    }
    .field-label {
        color: #9ca3af;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 14px;
        margin-bottom: 4px;
    }
    .field-value {
        color: #374151;
        font-size: 0.98rem;
    }
    .section-heading {
        font-size: 1.05rem;
        font-weight: 700;
        color: #4338ca;
        margin-top: 22px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .pill-list li {
        margin-bottom: 6px;
        color: #374151;
        line-height: 1.5;
    }
    .competitor-chip {
        display: inline-flex;
        align-items: center;
        background: #f3f4f6;
        border-radius: 999px;
        padding: 6px 16px;
        margin: 4px 6px 4px 0;
        font-size: 0.88rem;
        color: #374151;
        border: 1px solid #e5e7eb;
    }
    .competitor-chip a {
        margin-left: 6px;
        color: #6366f1;
        text-decoration: none;
        font-weight: 600;
    }

    /* Status banner */
    .status-banner {
        background: linear-gradient(90deg, #eef2ff, #f5f3ff);
        border: 1px solid #c7d2fe;
        border-radius: 12px;
        padding: 12px 18px;
        margin-bottom: 14px;
        color: #4338ca;
        font-weight: 500;
    }

    /* Chat input styling */
    .stChatInput textarea, .stChatInput input {
        border-radius: 14px !important;
    }

    div[data-testid="stDownloadButton"] button {
        background: linear-gradient(90deg, #6366f1, #8b5cf6) !important;
        color: white !important;
        border-radius: 10px !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 10px 22px !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## ⚙️ Settings")

    model = st.selectbox(
        "AI Model (OpenRouter)",
        [
            "openrouter/free",
            "openai/gpt-oss-20b:free",
            "meta-llama/llama-3.3-70b-instruct:free",
            "openai/gpt-4o-mini",
            "anthropic/claude-3.5-sonnet",
        ],
        index=0
    )

    st.markdown("---")
    st.markdown("### 💬 Discord Integration")
    st.caption("Bonus feature — reports auto-post to your channel")

    discord_bot_token = st.text_input(
        "Discord Bot Token", value=os.getenv("DISCORD_BOT_TOKEN", ""), type="password"
    )
    discord_channel_id = st.text_input(
        "Discord Channel ID", value=os.getenv("DISCORD_CHANNEL_ID", "")
    )

    st.markdown("---")
    st.markdown("### 👤 Applicant Details")
    applicant_name = st.text_input("Applicant Name")
    applicant_email = st.text_input("Applicant Email")

    if st.button("💾 Save Configuration", use_container_width=True):
        st.success("Configuration saved for this session.")

    st.markdown("---")
    st.caption("Built for the Relu Consultancy AI hackathon 🚀")

# ---------------------------------------------------------------------------
# MAIN HEADER
# ---------------------------------------------------------------------------
st.markdown('<div class="hero-title">🔍 AI Company Research Assistant</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-subtitle">Enter a company name or website URL — I\'ll crawl, research, '
    'and generate a full competitor + insights report.</div>',
    unsafe_allow_html=True
)

# ---------------------------------------------------------------------------
# CHAT INPUT + PIPELINE
# ---------------------------------------------------------------------------
query = st.chat_input("e.g. Stripe or https://stripe.com")

if query:
    progress = st.empty()
    try:
        # Step 1: resolve website
        progress.markdown('<div class="status-banner">🔎 Resolving official website...</div>', unsafe_allow_html=True)
        if query.strip().startswith("http"):
            website = query.strip()
        else:
            website = resolve_official_website(query.strip())

        if not website:
            progress.empty()
            st.error("Could not find an official website for this company.")
            st.stop()

        # Step 2: crawl
        progress.markdown(f'<div class="status-banner">🕷️ Crawling {website} ...</div>', unsafe_allow_html=True)
        pages = crawl_site(website)
        full_text = " ".join(pages.values())

        if not full_text:
            progress.empty()
            st.error("Could not extract content from the website.")
            st.stop()

        # Step 3: AI analysis (with search context fallback for JS-heavy sites)
        progress.markdown('<div class="status-banner">🤖 Analyzing with AI...</div>', unsafe_allow_html=True)
        try:
            search_data = serper_search(f"{query} company products services overview")
            search_snippets = "\n".join(
                f"{item.get('title','')}: {item.get('snippet','')}"
                for item in search_data.get("organic", [])
            )
        except Exception:
            search_snippets = ""

        company_data = analyze_company(full_text, query, model=model, search_context=search_snippets)
        company_data["name"] = query if not query.startswith("http") else website
        company_data["website"] = website

        # Step 4: competitors
        progress.markdown('<div class="status-banner">🏢 Identifying competitors...</div>', unsafe_allow_html=True)
        competitors = get_competitors(company_data["name"], model=model)

        # Step 5: PDF
        progress.markdown('<div class="status-banner">📄 Generating PDF report...</div>', unsafe_allow_html=True)
        safe_name = "".join(c if c.isalnum() else "_" for c in company_data["name"])
        pdf_filename = f"report_{safe_name}.pdf"
        pdf_path = generate_pdf(company_data, competitors, pdf_filename)

        progress.empty()

        # Step 6: Discord (optional)
        discord_status = None
        if discord_bot_token and discord_channel_id:
            discord_status = send_report_to_discord(
                discord_bot_token, discord_channel_id,
                applicant_name or "Unknown", applicant_email or "Unknown",
                company_data["name"], company_data["website"], pdf_path
            )

        st.session_state.messages.append({
            "query": query,
            "data": company_data,
            "competitors": competitors,
            "pdf_path": pdf_path,
            "discord_status": discord_status
        })

    except Exception as e:
        progress.empty()
        st.error(f"Something went wrong: {e}")

# ---------------------------------------------------------------------------
# DISPLAY RESULTS
# ---------------------------------------------------------------------------
for idx, msg in enumerate(reversed(st.session_state.messages)):
    data = msg["data"]

    st.markdown('<div class="result-card">', unsafe_allow_html=True)

    st.markdown(f'<div class="company-name">📊 {data.get("name", "Company")}</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="field-label">Website</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="field-value">🔗 <a href="{data.get("website","#")}" target="_blank">{data.get("website","N/A")}</a></div>', unsafe_allow_html=True)
    with col_b:
        st.markdown('<div class="field-label">Phone</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="field-value">📞 {data.get("phone") or "N/A"}</div>', unsafe_allow_html=True)

    st.markdown('<div class="field-label">Address</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="field-value">📍 {data.get("address") or "N/A"}</div>', unsafe_allow_html=True)

    if data.get("summary"):
        st.markdown('<div class="section-heading">🧠 Company Summary</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="field-value">{data["summary"]}</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-heading">🛠️ Products / Services</div>', unsafe_allow_html=True)
        products = data.get("products_services", [])
        if products:
            items = "".join(f"<li>{p}</li>" for p in products)
            st.markdown(f'<ul class="pill-list">{items}</ul>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="field-value">No data available.</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-heading">⚠️ AI-Generated Pain Points</div>', unsafe_allow_html=True)
        pain_points = data.get("pain_points", [])
        if pain_points:
            items = "".join(f"<li>{p}</li>" for p in pain_points)
            st.markdown(f'<ul class="pill-list">{items}</ul>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="field-value">No data available.</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-heading">🏁 Competitors</div>', unsafe_allow_html=True)
    if msg["competitors"]:
        chips = ""
        for c in msg["competitors"]:
            website_link = c.get("website", "N/A")
            if website_link and website_link != "N/A":
                chips += f'<span class="competitor-chip">{c["name"]} <a href="{website_link}" target="_blank">visit ↗</a></span>'
            else:
                chips += f'<span class="competitor-chip">{c["name"]}</span>'
        st.markdown(chips, unsafe_allow_html=True)
    else:
        st.markdown('<div class="field-value">No competitors identified.</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    with open(msg["pdf_path"], "rb") as f:
        st.download_button(
            "📄 Download PDF Report",
            f,
            file_name=os.path.basename(msg["pdf_path"]),
            mime="application/pdf",
            key=f"download_{idx}"
        )

    if msg["discord_status"]:
        if msg["discord_status"]["success"]:
            st.success("✅ Report sent to Discord successfully.")
        else:
            st.warning(f"⚠️ Discord notification failed: {msg['discord_status']['error']}")

    st.markdown('</div>', unsafe_allow_html=True)