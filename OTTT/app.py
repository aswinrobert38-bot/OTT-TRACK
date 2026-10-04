import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from pages.home import render_home
from pages.movie_details import render_movie_details
from services.tmdb_service import get_token

st.set_page_config(
    page_title="ReelRoute — Movies & Series",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------------------------------------------------------
# SESSION STATE — one navigation source of truth
# -----------------------------------------------------------------------------
if "open_content" not in st.session_state:
    st.session_state.open_content = None
if "search_results" not in st.session_state:
    st.session_state.search_results = []
if "search_query" not in st.session_state:
    st.session_state.search_query = ""

# Migrate old state only if it exists, so older pages cannot silently open a
# stale movie. New navigation always uses open_content = {id, type}.
if st.session_state.get("open_content") is None:
    legacy_id = st.session_state.get("selected_movie_id")
    if legacy_id:
        st.session_state.open_content = {"id": legacy_id, "type": "movie"}

st.markdown(
    """
    <style>
    :root {
        --rr-bg: #07090D;
        --rr-surface: #11151C;
        --rr-surface-2: #171C25;
        --rr-border: #252B36;
        --rr-primary: #7C5CFF;
        --rr-secondary: #20D7D7;
        --rr-text: #F5F7FA;
        --rr-muted: #8B93A5;
        --rr-success: #35D07F;
    }

    html, body, [data-testid="stAppViewContainer"] {
        background: var(--rr-bg) !important;
    }

    .stApp {
        background:
            radial-gradient(circle at 15% -10%, rgba(124,92,255,.16), transparent 32%),
            radial-gradient(circle at 92% 8%, rgba(32,215,215,.08), transparent 26%),
            var(--rr-bg) !important;
        color: var(--rr-text) !important;
    }

    [data-testid="stHeader"] {
        background: rgba(7,9,13,.72) !important;
        backdrop-filter: blur(18px);
    }

    .block-container {
        max-width: 1540px !important;
        padding: 22px clamp(16px, 3vw, 44px) 72px !important;
    }

    #MainMenu, footer { visibility: hidden; }

    [data-testid="stSidebar"] {
        background: #0B0E13 !important;
        border-right: 1px solid var(--rr-border) !important;
    }

    [data-testid="stSidebarNav"] { display: none !important; }

    /* Top navigation */
    .rr-nav {
        display:flex;
        align-items:center;
        justify-content:space-between;
        gap:18px;
        padding: 10px 0 20px;
    }
    .rr-brand {
        display:flex;
        align-items:center;
        gap:10px;
        color:var(--rr-text);
        font-size:22px;
        font-weight:900;
        letter-spacing:-.7px;
    }
    .rr-brand-mark {
        width:34px;height:34px;border-radius:11px;
        display:grid;place-items:center;
        background:linear-gradient(135deg,var(--rr-primary),var(--rr-secondary));
        color:#fff; box-shadow:0 8px 28px rgba(124,92,255,.28);
    }
    .rr-nav-copy { color:var(--rr-muted); font-size:12px; font-weight:650; }

    .rr-hero {
        position:relative;
        min-height:360px;
        overflow:hidden;
        border:1px solid var(--rr-border);
        border-radius:28px;
        padding:clamp(28px,5vw,64px);
        display:flex;align-items:flex-end;
        background:
          radial-gradient(circle at 80% 20%, rgba(124,92,255,.32), transparent 28%),
          linear-gradient(115deg, #10151E 0%, #0B0E14 58%, #080A0F 100%);
        box-shadow:0 28px 80px rgba(0,0,0,.34);
        margin-bottom:28px;
    }
    .rr-hero::after {
        content:""; position:absolute; inset:0;
        background:linear-gradient(90deg,rgba(7,9,13,.96) 0%,rgba(7,9,13,.72) 43%,rgba(7,9,13,.18) 100%);
        pointer-events:none;
    }
    .rr-hero-content { position:relative; z-index:2; max-width:720px; }
    .rr-eyebrow { color:var(--rr-secondary); text-transform:uppercase; letter-spacing:2px; font-size:11px; font-weight:850; }
    .rr-hero h1 { margin:8px 0 10px; font-size:clamp(36px,6vw,70px); line-height:.98; letter-spacing:-3px; color:#fff; font-weight:950; }
    .rr-hero p { color:#AAB2C0; max-width:650px; font-size:15px; line-height:1.65; margin:0; }

    .rr-section-head { display:flex; align-items:end; justify-content:space-between; gap:15px; margin:34px 0 14px; }
    .rr-section-title { color:#fff; font-size:25px; font-weight:900; letter-spacing:-.8px; margin:0; }
    .rr-section-subtitle { color:var(--rr-muted); font-size:12px; margin-top:4px; }

    .rr-type-pill {
        display:inline-flex; align-items:center; gap:6px;
        border:1px solid var(--rr-border); background:rgba(17,21,28,.9);
        color:#C8CED9; border-radius:999px; padding:5px 9px;
        font-size:10px; font-weight:800; text-transform:uppercase; letter-spacing:.7px;
    }

    .rr-card {
        background:var(--rr-surface); border:1px solid var(--rr-border);
        border-radius:18px; overflow:hidden; height:100%;
        transition:transform .22s ease,border-color .22s ease,box-shadow .22s ease,background .22s ease;
    }
    .rr-card:hover { transform:translateY(-6px); border-color:#3A4352; background:var(--rr-surface-2); box-shadow:0 20px 42px rgba(0,0,0,.32); }
    .rr-poster-wrap { position:relative; aspect-ratio:2/3; overflow:hidden; background:#0D1117; }
    .rr-poster-wrap img { width:100%; height:100%; object-fit:cover; display:block; transition:transform .35s ease; }
    .rr-card:hover .rr-poster-wrap img { transform:scale(1.035); }
    .rr-card-info { padding:12px 13px 14px; }
    .rr-card-title { color:#F8FAFC; font-size:14px; line-height:1.3; font-weight:820; min-height:36px; }
    .rr-card-meta { color:var(--rr-muted); font-size:11px; margin-top:7px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    .rr-card-rating { color:#DDE3EC; }
    .rr-rating { color:#FFD36B; }

    /* Make Streamlit's card buttons part of the card visually */
    div[data-testid="stVerticalBlock"] .rr-card + div { margin-top:-58px; position:relative; z-index:3; padding:0 10px 10px; }
    .rr-view-button button {
        border:1px solid rgba(255,255,255,.10) !important;
        background:rgba(7,9,13,.82) !important; color:#fff !important;
        border-radius:11px !important; font-weight:800 !important; font-size:12px !important;
        min-height:36px !important; backdrop-filter:blur(12px);
    }
    .rr-view-button button:hover { border-color:var(--rr-primary) !important; background:rgba(124,92,255,.88) !important; }

    .stButton > button {
        border:1px solid var(--rr-border) !important;
        background:var(--rr-surface) !important;
        color:var(--rr-text) !important;
        border-radius:11px !important;
        font-weight:750 !important;
    }
    .stButton > button:hover { border-color:var(--rr-primary) !important; color:#fff !important; }

    [data-testid="stTextInput"] input, [data-testid="stSelectbox"] div,
    [data-testid="stRadio"] label { color:#fff !important; }
    [data-testid="stTextInput"] input {
        background:#0E1218 !important; border:1px solid var(--rr-border) !important;
        border-radius:13px !important; min-height:48px !important;
    }
    [data-testid="stTextInput"] input:focus { border-color:var(--rr-primary) !important; box-shadow:0 0 0 1px rgba(124,92,255,.25) !important; }

    .rr-search-shell {
        background:rgba(17,21,28,.88); border:1px solid var(--rr-border);
        border-radius:18px; padding:14px; margin:12px 0 24px;
        box-shadow:0 14px 35px rgba(0,0,0,.22);
    }

    .rr-details-hero {
        position:relative; overflow:hidden; border:1px solid var(--rr-border); border-radius:26px;
        min-height:440px; background:#0B0E13; margin-bottom:24px;
    }
    .rr-details-backdrop { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; opacity:.44; }
    .rr-details-shade { position:absolute; inset:0; background:linear-gradient(90deg,#07090D 3%,rgba(7,9,13,.92) 35%,rgba(7,9,13,.48) 75%,rgba(7,9,13,.78)); }
    .rr-details-content { position:relative; z-index:2; display:grid; grid-template-columns:minmax(170px,260px) 1fr; gap:30px; align-items:end; min-height:440px; padding:32px; }
    .rr-details-poster { width:100%; border-radius:17px; border:1px solid rgba(255,255,255,.10); box-shadow:0 22px 50px rgba(0,0,0,.45); }
    .rr-details-title { font-size:clamp(34px,5vw,62px); font-weight:950; letter-spacing:-2.5px; line-height:1; color:#fff; margin:8px 0 14px; }
    .rr-details-overview { color:#B4BBC8; font-size:14px; line-height:1.75; max-width:850px; }
    .rr-chip-row { display:flex; flex-wrap:wrap; gap:7px; margin:15px 0; }
    .rr-chip { border:1px solid var(--rr-border); background:rgba(17,21,28,.78); color:#C8CED9; border-radius:999px; padding:6px 10px; font-size:11px; }
    .rr-detail-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:10px; margin-top:20px; }
    .rr-stat { background:rgba(17,21,28,.88); border:1px solid var(--rr-border); border-radius:13px; padding:12px; }
    .rr-stat-label { color:var(--rr-muted); font-size:10px; text-transform:uppercase; letter-spacing:.7px; }
    .rr-stat-value { color:#fff; font-weight:800; margin-top:5px; font-size:13px; }

    .rr-panel { background:var(--rr-surface); border:1px solid var(--rr-border); border-radius:20px; padding:22px; margin-top:18px; }
    .rr-panel-title { color:#fff; font-size:22px; font-weight:900; margin-bottom:4px; }
    .rr-panel-copy { color:var(--rr-muted); font-size:12px; margin-bottom:16px; }

    .rr-ott-card {
        display:flex; align-items:center; gap:13px; min-height:76px; padding:11px 13px;
        border-radius:15px; border:1px solid var(--rr-border); background:#0E1218;
        text-decoration:none !important; color:#fff !important;
        transition:transform .2s ease,border-color .2s ease,background .2s ease;
    }
    .rr-ott-card:hover { transform:translateY(-3px); border-color:var(--rr-secondary); background:#151B23; }
    .rr-ott-logo { width:48px; height:48px; border-radius:12px; object-fit:cover; background:#202631; flex:0 0 auto; }
    .rr-ott-name { font-size:13px; font-weight:850; }
    .rr-ott-type { color:var(--rr-muted); font-size:10px; margin-top:4px; }
    .rr-ott-arrow { margin-left:auto; color:var(--rr-secondary); font-size:18px; }

    .rr-empty { padding:35px 15px; text-align:center; color:var(--rr-muted); border:1px dashed var(--rr-border); border-radius:16px; }
    .rr-footer { margin-top:55px; padding-top:20px; border-top:1px solid var(--rr-border); color:#697283; font-size:11px; text-align:center; }

    @media (max-width: 850px) {
        .block-container { padding:14px 12px 48px !important; }
        .rr-hero { min-height:330px; border-radius:21px; padding:25px; }
        .rr-hero h1 { letter-spacing:-1.8px; }
        .rr-details-content { grid-template-columns:110px 1fr; gap:17px; padding:20px; min-height:390px; }
        .rr-details-hero { min-height:390px; }
        .rr-detail-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }
    }
    @media (max-width: 560px) {
        .rr-nav-copy { display:none; }
        .rr-details-content { grid-template-columns:1fr; align-items:end; min-height:650px; padding:18px; }
        .rr-details-poster { width:145px; }
        .rr-details-title { font-size:36px; }
        .rr-detail-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }
        .rr-section-title { font-size:21px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def clear_navigation():
    st.session_state.open_content = None
    st.session_state.pop("selected_movie_id", None)
    st.session_state.pop("open_movie_id", None)


# -----------------------------------------------------------------------------
# Top navigation
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="rr-nav">
        <div class="rr-brand"><span class="rr-brand-mark">▶</span>ReelRoute</div>
        <div class="rr-nav-copy">MOVIES • SERIES • INDIA OTT AVAILABILITY</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Routing — only open_content controls the details page.
# -----------------------------------------------------------------------------
selected_content = st.session_state.get("open_content")

if selected_content:
    content_id = selected_content.get("id")
    content_type = selected_content.get("type", "movie")

    if content_id:
        render_movie_details(content_id, content_type)
    else:
        st.error("Unable to open this content.")
        if st.button("← Back to ReelRoute"):
            clear_navigation()
            st.rerun()
else:
    render_home()

st.markdown(
    '<div class="rr-footer">ReelRoute • TMDB-powered discovery • India OTT availability via TMDB/JustWatch data</div>',
    unsafe_allow_html=True,
)
