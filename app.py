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
    page_title="Company Research AI",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------------------------
# CUSTOM CSS — dark developer-tool theme
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background-color: #0a0a0f;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0d0d13;
        border-right: 1px solid #1f1f2b;
    }
    section[data-testid="stSidebar"] * {
        color: #e5e5eb !important;
    }
    section[data-testid="stSidebar"] input,
    section[data-testid="stSidebar"] select,
    section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
        background-color: #14141c !important;
        color: #e5e5eb !important;
        border-radius: 8px !important;
        border: 1px solid #2a2a38 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.85rem !important;
    }
    .sidebar-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        color: #6b7280;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-top: 18px;
        margin-bottom: 6px;
    }
    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 24px;
    }
    .sidebar-brand-icon {
        width: 38px;
        height: 38px;
        background: linear-gradient(135deg, #6366f1, #3b82f6);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
    }
    .sidebar-brand-title {
        font-weight: 800;
        font-size: 1.05rem;
        color: #f5f5f7;
        line-height: 1.1;
    }
    .sidebar-brand-sub {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.65rem;
        color: #6b7280;
        letter-spacing: 0.1em;
    }

    /* Buttons - default (New Research / Save Configuration) */
    section[data-testid="stSidebar"] button {
        background-color: #f5b301 !important;
        color: #0a0a0f !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 700 !important;
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Segmented tab buttons override */
    section[data-testid="stSidebar"] button[kind="secondary"] {
        background-color: #14141c !important;
        color: #9ca3af !important;
        border: 1px solid #2a2a38 !important;
        font-weight: 600 !important;
    }
    section[data-testid="stSidebar"] button[kind="primary"] {
        background-color: #f5b301 !important;
        color: #0a0a0f !important;
        border: none !important;
    }

    /* Hero */
    .hero-wrap {
        text-align: center;
        padding: 60px 20px 20px 20px;
    }
    .hero-tag {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: #f5b301;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        margin-bottom: 16px;
    }
    .hero-title {
        font-size: 3.2rem;
        font-weight: 800;
        color: #f5f5f7;
        line-height: 1.15;
        margin-bottom: 20px;
    }
    .hero-subtitle {
        color: #9ca3af;
        font-size: 1.05rem;
        max-width: 640px;
        margin: 0 auto 28px auto;
        line-height: 1.6;
    }
    .example-pill {
        display: inline-block;
        background-color: #14141c;
        border: 1px solid #2a2a38;
        border-radius: 8px;
        padding: 8px 18px;
        margin: 0 6px 10px 6px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        color: #d1d5db;
    }

    /* Top header bar */
    .top-header {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 18px 0;
        border-bottom: 1px solid #1f1f2b;
        margin-bottom: 10px;
    }
    .top-header-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #f5f5f7;
    }
    .live-badge {
        background-color: #052e1f;
        color: #34d399;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        padding: 3px 10px;
        border-radius: 999px;
        border: 1px solid #065f37;
    }

    /* Result card */
    .result-card {
        background-color: #101018;
        border: 1px solid #1f1f2b;
        border-radius: 14px;
        padding: 28px 32px;
        margin-bottom: 24px;
    }
    .result-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 4px;
    }
    .result-company-name {
        font-size: 1.5rem;
        font-weight: 800;
        color: #f5f5f7;
    }
    .result-website {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        color: #f5b301;
    }
    .complete-badge {
        background-color: #052e1f;
        color: #34d399;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.68rem;
        padding: 4px 12px;
        border-radius: 999px;
        border: 1px solid #065f37;
        letter-spacing: 0.05em;
        white-space: nowrap;
    }

    .info-box {
        background-color: #0d0d13;
        border: 1px solid #1f1f2b;
        border-radius: 10px;
        padding: 14px 18px;
        margin-top: 16px;
    }
    .info-box-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.68rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 4px;
    }
    .info-box-value {
        color: #e5e5eb;
        font-size: 0.95rem;
    }

    .section-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 22px;
        margin-bottom: 10px;
    }

    .tag-pill {
        display: inline-block;
        background-color: #1a1a2e;
        color: #c7d2fe;
        border: 1px solid #312e6b;
        border-radius: 7px;
        padding: 6px 14px;
        margin: 0 8px 8px 0;
        font-size: 0.85rem;
    }

    .pain-point-item {
        color: #d1d5db;
        font-size: 0.92rem;
        line-height: 1.6;
        margin-bottom: 8px;
        padding-left: 14px;
        border-left: 2px solid #f5b301;
    }

    .competitor-card {
        background-color: #14141c;
        border: 1px solid #2a2a38;
        border-radius: 10px;
        padding: 12px 16px;
        display: inline-block;
        margin: 0 10px 10px 0;
        min-width: 160px;
    }
    .competitor-name {
        color: #f5f5f7;
        font-weight: 600;
        font-size: 0.92rem;
        margin-bottom: 3px;
    }
    .competitor-link {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        color: #f5b301;
        text-decoration: none;
    }

    .status-line {
        font-family: 'JetBrains Mono', monospace;
        color: #f5b301;
        font-size: 0.9rem;
        padding: 10px 0;
    }

    div[data-testid="stDownloadButton"] button {
        background-color: #f5b301 !important;
        color: #0a0a0f !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 700 !important;
        font-family: 'JetBrains Mono', monospace !important;
    }

    .stChatInput textarea, .stChatInput input {
        background-color: #101018 !important;
        border: 1px solid #2a2a38 !important;
        border-radius: 12px !important;
        color: #f5f5f7 !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "active_tab" not in st.session_state:
    st.session_state.active_tab = "API"

# ---------------------------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="sidebar-brand-icon">🔍</div>
        <div>
            <div class="sidebar-brand-title">Company Research AI</div>
            <div class="sidebar-brand-sub">AI-POWERED INTELLIGENCE</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("+ New Research", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    # ---- Segmented tab control (custom, replaces st.radio) ----
    tab_col1, tab_col2 = st.columns(2)
    with tab_col1:
        if st.button(
            "API", key="tab_api_btn", use_container_width=True,
            type="primary" if st.session_state.active_tab == "API" else "secondary"
        ):
            st.session_state.active_tab = "API"
            st.rerun()
    with tab_col2:
        if st.button(
            "DISCORD", key="tab_discord_btn", use_container_width=True,
            type="primary" if st.session_state.active_tab == "DISCORD" else "secondary"
        ):
            st.session_state.active_tab = "DISCORD"
            st.rerun()

    tab = st.session_state.active_tab

    if tab == "API":
        st.markdown('<div class="sidebar-label">OpenRouter API Key</div>', unsafe_allow_html=True)
        openrouter_key_input = st.text_input(
            "openrouter_key", value=os.getenv("OPENROUTER_API_KEY", ""),
            type="password", label_visibility="collapsed", placeholder="sk-or-v1-..."
        )

        st.markdown('<div class="sidebar-label">Serper.dev API Key</div>', unsafe_allow_html=True)
        serper_key_input = st.text_input(
            "serper_key", value=os.getenv("SERPER_API_KEY", ""),
            type="password", label_visibility="collapsed", placeholder="Your Serper key..."
        )

        st.markdown('<div class="sidebar-label">AI Model</div>', unsafe_allow_html=True)
        model = st.selectbox(
            "model",
            [
                "openrouter/free",
                "openai/gpt-oss-20b:free",
                "meta-llama/llama-3.3-70b-instruct:free",
                "openai/gpt-4o-mini",
                "anthropic/claude-3.5-sonnet",
            ],
            index=0, label_visibility="collapsed"
        )

        discord_bot_token = os.getenv("DISCORD_BOT_TOKEN", "")
        discord_channel_id = os.getenv("DISCORD_CHANNEL_ID", "")
        applicant_name = st.session_state.get("applicant_name", "")
        applicant_email = st.session_state.get("applicant_email", "")

    else:
        st.markdown("""
        <div style="background-color:#14141c; border:1px solid #2a2a38; border-radius:10px; padding:14px; margin-bottom:16px;">
            <div style="color:#a5b4fc; font-weight:600; font-size:0.85rem; margin-bottom:4px;">Discord Bot Integration</div>
            <div style="color:#9ca3af; font-size:0.8rem; line-height:1.4;">After research completes, the report auto-sends to your configured channel.</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="sidebar-label">Bot Token</div>', unsafe_allow_html=True)
        discord_bot_token = st.text_input(
            "bot_token", value=os.getenv("DISCORD_BOT_TOKEN", ""),
            type="password", label_visibility="collapsed"
        )

        st.markdown('<div class="sidebar-label">Channel ID</div>', unsafe_allow_html=True)
        discord_channel_id = st.text_input(
            "channel_id", value=os.getenv("DISCORD_CHANNEL_ID", ""),
            label_visibility="collapsed"
        )

        st.markdown('<div class="sidebar-label">Applicant Details</div>', unsafe_allow_html=True)
        applicant_name = st.text_input("Full Name", key="applicant_name")
        applicant_email = st.text_input("Email Address", key="applicant_email")

        openrouter_key_input = os.getenv("OPENROUTER_API_KEY", "")
        serper_key_input = os.getenv("SERPER_API_KEY", "")
        model = st.session_state.get("model", "openrouter/free")

    if st.button("Save Configuration", use_container_width=True):
        st.success("Saved ✓")

    st.markdown("---")
    st.markdown('<div class="sidebar-label">How it works</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.82rem; color:#9ca3af; line-height:2;">
    <b style="color:#f5b301;">1</b> Enter a company name or URL<br>
    <b style="color:#f5b301;">2</b> Serper.dev searches and crawls it<br>
    <b style="color:#f5b301;">3</b> OpenRouter AI generates insights<br>
    <b style="color:#f5b301;">4</b> Download a professional PDF report
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("OPENROUTER · SERPER · REPORTLAB")

# Apply manually entered keys to environment for this session
if openrouter_key_input:
    os.environ["OPENROUTER_API_KEY"] = openrouter_key_input
if serper_key_input:
    os.environ["SERPER_API_KEY"] = serper_key_input

# ---------------------------------------------------------------------------
# TOP HEADER
# ---------------------------------------------------------------------------
st.markdown("""
<div class="top-header">
    <div class="top-header-title">Company Research</div>
    <div class="live-badge">● LIVE</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# HERO (only show when no research done yet)
# ---------------------------------------------------------------------------
if not st.session_state.messages:
    st.markdown("""
    <div class="hero-wrap">
        <div class="hero-tag">AI-POWERED INTELLIGENCE</div>
        <div class="hero-title">Know any company<br>in minutes.</div>
        <div class="hero-subtitle">Enter a company name or website URL to get AI-powered insights, competitor analysis, pain points, and a professional PDF report.</div>
        <div>
            <span class="example-pill">e.g. Stripe</span>
            <span class="example-pill">e.g. Tesla</span>
            <span class="example-pill">e.g. https://openai.com</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# CHAT INPUT + PIPELINE
# ---------------------------------------------------------------------------
query = st.chat_input("Enter a company name (e.g. Stripe) or website URL (e.g. https://stripe.com)...")

if query:
    status = st.empty()
    try:
        status.markdown('<div class="status-line">🔎 Resolving official website...</div>', unsafe_allow_html=True)
        if query.strip().startswith("http"):
            website = query.strip()
        else:
            website = resolve_official_website(query.strip())

        if not website:
            status.empty()
            st.error("Could not find an official website for this company.")
            st.stop()

        status.markdown(f'<div class="status-line">🕷️ Crawling {website} ...</div>', unsafe_allow_html=True)
        pages = crawl_site(website)
        full_text = " ".join(pages.values())

        if not full_text:
            status.empty()
            st.error("Could not extract content from the website.")
            st.stop()

        status.markdown('<div class="status-line">🤖 Analyzing with AI...</div>', unsafe_allow_html=True)
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

        status.markdown('<div class="status-line">🏢 Identifying competitors...</div>', unsafe_allow_html=True)
        competitors = get_competitors(company_data["name"], model=model)

        status.markdown('<div class="status-line">📄 Generating PDF report...</div>', unsafe_allow_html=True)
        safe_name = "".join(c if c.isalnum() else "_" for c in company_data["name"])
        pdf_filename = f"report_{safe_name}.pdf"
        pdf_path = generate_pdf(company_data, competitors, pdf_filename)

        status.empty()

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
        st.rerun()

    except Exception as e:
        status.empty()
        st.error(f"Something went wrong: {e}")

# ---------------------------------------------------------------------------
# DISPLAY RESULTS
# ---------------------------------------------------------------------------
for idx, msg in enumerate(reversed(st.session_state.messages)):
    data = msg["data"]

    st.markdown('<div class="result-card">', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="result-header">
        <div>
            <div class="result-company-name">{data.get('name', 'Company')}</div>
            <a class="result-website" href="{data.get('website','#')}" target="_blank">{data.get('website','N/A')}</a>
        </div>
        <div class="complete-badge">RESEARCH COMPLETE</div>
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"""
        <div class="info-box">
            <div class="info-box-label">Phone</div>
            <div class="info-box-value">{data.get('phone') or 'Not publicly listed'}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_b:
        st.markdown(f"""
        <div class="info-box">
            <div class="info-box-label">Address</div>
            <div class="info-box-value">{data.get('address') or 'Not publicly listed'}</div>
        </div>
        """, unsafe_allow_html=True)

    if data.get("summary"):
        st.markdown('<div class="section-label">Company Summary</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-box-value">{data["summary"]}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-label">Products & Services</div>', unsafe_allow_html=True)
    products = data.get("products_services", [])
    if products:
        pills = "".join(f'<span class="tag-pill">{p}</span>' for p in products)
        st.markdown(pills, unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-box-value">No data available.</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-label">AI-Generated Pain Points</div>', unsafe_allow_html=True)
    pain_points = data.get("pain_points", [])
    if pain_points:
        for p in pain_points:
            st.markdown(f'<div class="pain-point-item">{p}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-box-value">No data available.</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-label">Competitors</div>', unsafe_allow_html=True)
    if msg["competitors"]:
        cards = ""
        for c in msg["competitors"]:
            website_link = c.get("website", "N/A")
            cards += f"""
            <div class="competitor-card">
                <div class="competitor-name">{c['name']}</div>
                <a class="competitor-link" href="{website_link}" target="_blank">{website_link}</a>
            </div>
            """
        st.markdown(cards, unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-box-value">No competitors identified.</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    dl_col, discord_col = st.columns([1, 1])
    with dl_col:
        with open(msg["pdf_path"], "rb") as f:
            st.download_button(
                "⬇ Download PDF Report",
                f,
                file_name=os.path.basename(msg["pdf_path"]),
                mime="application/pdf",
                key=f"download_{idx}"
            )
    with discord_col:
        if msg["discord_status"]:
            if msg["discord_status"]["success"]:
                st.success("✓ Sent to Discord")
            else:
                st.warning(f"Discord failed: {msg['discord_status']['error']}")

    st.markdown('</div>', unsafe_allow_html=True)