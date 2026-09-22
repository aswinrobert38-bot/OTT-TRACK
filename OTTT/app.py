import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from pages.home import render_home
from pages.movie_details import render_movie_details
from services.tmdb_service import get_token


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="ReelRoute",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# SESSION STATE
# =========================================================

if "open_content" not in st.session_state:
    st.session_state.open_content = None

if "open_movie_id" not in st.session_state:
    st.session_state.open_movie_id = None


# =========================================================
# GLOBAL CSS — UI ONLY
# =========================================================

st.markdown(
    """
    <style>

    /* =====================================================
       REELROUTE DASHBOARD THEME
       ===================================================== */

    :root {
        --bg: #11151d;
        --panel: #191d25;
        --panel-light: #20252e;
        --border: #303641;

        --text: #f4f6f8;
        --muted: #858d9c;

        --cyan: #20d7d7;
        --blue: #3c91ff;
        --pink: #ff4fa3;
        --purple: #874dff;
    }


    /* =====================================================
       MAIN APP BACKGROUND
       ===================================================== */

    .stApp {
        background:
            radial-gradient(
                circle at 8% 0%,
                rgba(60, 145, 255, 0.08),
                transparent 30%
            ),
            radial-gradient(
                circle at 95% 15%,
                rgba(255, 79, 163, 0.06),
                transparent 28%
            ),
            #11151d !important;

        color: var(--text);
    }


    .main {
        background: transparent !important;
    }


    .block-container {
        max-width: 1500px !important;

        padding:
            28px
            38px
            60px !important;
    }


    /* =====================================================
       SIDEBAR
       ===================================================== */

    [data-testid="stSidebar"] {
        background:
            #151920 !important;

        border-right:
            1px solid
            rgba(255,255,255,0.06);

        box-shadow:
            8px 0 30px
            rgba(0,0,0,0.22);
    }


    [data-testid="stSidebar"] .block-container {
        padding:
            24px 18px !important;
    }


    [data-testid="stSidebarNav"] {
        display: none !important;
    }


    /* =====================================================
       SIDEBAR BRAND
       ===================================================== */

    [data-testid="stSidebar"] h2 {
        color: #ffffff !important;

        font-size: 22px !important;

        font-weight: 850 !important;

        letter-spacing: -0.5px;
    }


    [data-testid="stSidebar"] p {
        color: #7f8795;
    }


    /* =====================================================
       HERO / PAGE TITLE
       ===================================================== */

    .hero-title {
        font-size: 46px;

        font-weight: 850;

        letter-spacing: -2px;

        color: #ffffff;

        line-height: 1.05;

        margin-top: 5px;

        margin-bottom: 5px;
    }


    .hero-text {
        color: #858d9c;

        font-size: 14px;

        margin-bottom: 24px;
    }


    /* =====================================================
       SEARCH PANEL
       ===================================================== */

    [data-testid="stForm"] {
        background:
            #191d25 !important;

        border:
            1px solid
            #303641 !important;

        border-radius:
            12px !important;

        padding:
            10px !important;

        margin:
            10px 0 28px !important;

        box-shadow:
            0 10px 30px
            rgba(0,0,0,0.20) !important;
    }


    /* =====================================================
       SEARCH INPUT
       ===================================================== */

    [data-testid="stTextInput"] input {
        background:
            #11151d !important;

        color:
            #ffffff !important;

        border:
            1px solid
            #303641 !important;

        border-radius:
            9px !important;

        min-height:
            44px !important;

        font-size:
            13px !important;
    }


    [data-testid="stTextInput"] input::placeholder {
        color:
            #626b7a !important;
    }


    [data-testid="stTextInput"] input:focus {
        border-color:
            var(--cyan) !important;

        box-shadow:
            0 0 0 1px
            rgba(32,215,215,0.20) !important;
    }


    /* =====================================================
       SEARCH BUTTON
       ===================================================== */

    [data-testid="stFormSubmitButton"] button {
        min-height:
            44px !important;

        border:
            none !important;

        border-radius:
            9px !important;

        background:
            linear-gradient(
                90deg,
                #3c91ff,
                #20d7d7
            ) !important;

        color:
            #ffffff !important;

        font-weight:
            750 !important;

        box-shadow:
            0 7px 18px
            rgba(32,215,215,0.12);
    }


    [data-testid="stFormSubmitButton"] button:hover {
        filter:
            brightness(1.08);

        transform:
            translateY(-1px);
    }


    /* =====================================================
       SELECTBOX
       ===================================================== */

    [data-testid="stSelectbox"] > div > div {
        background:
            #11151d !important;

        border:
            1px solid
            #303641 !important;

        border-radius:
            9px !important;

        color:
            #f4f6f8 !important;
    }


    /* =====================================================
       SECTION HEADINGS
       ===================================================== */

    .section-header {
        margin-top:
            30px;

        margin-bottom:
            14px;

        padding-bottom:
            10px;

        border-bottom:
            1px solid
            rgba(255,255,255,0.05);
    }


    .section-title {
        color:
            #f4f6f8;

        font-size:
            20px;

        font-weight:
            800;

        letter-spacing:
            -0.4px;
    }


    .section-subtitle {
        color:
            #707987;

        font-size:
            11px;

        margin-top:
            3px;
    }


    /* =====================================================
       MOVIE / SERIES CARD
       ===================================================== */

    .movie-card {
        background:
            #191d25;

        border:
            1px solid
            #303641;

        border-radius:
            12px;

        padding:
            7px;

        transition:
            transform 0.2s ease,
            border-color 0.2s ease,
            box-shadow 0.2s ease;
    }


    .movie-card:hover {
        transform:
            translateY(-5px);

        border-color:
            rgba(32,215,215,0.45);

        box-shadow:
            0 14px 30px
            rgba(0,0,0,0.32);
    }


    /* =====================================================
       POSTER
       ===================================================== */

    .poster-image {
        width:
            100%;

        aspect-ratio:
            2 / 3;

        object-fit:
            cover;

        border-radius:
            8px;

        display:
            block;

        box-shadow:
            0 8px 20px
            rgba(0,0,0,0.28);
    }


    /* =====================================================
       POSTER CLICK BUTTON
       ===================================================== */

    .poster-click-area button {
        width:
            100% !important;

        min-height:
            330px !important;

        padding:
            0 !important;

        margin:
            0 !important;

        border-radius:
            9px !important;

        border:
            1px solid
            rgba(255,255,255,0.04) !important;

        background:
            transparent !important;

        color:
            transparent !important;

        font-size:
            0 !important;

        overflow:
            hidden !important;

        transition:
            transform 0.2s ease,
            border-color 0.2s ease,
            box-shadow 0.2s ease !important;
    }


    .poster-click-area button:hover {
        transform:
            translateY(-4px)
            scale(1.01);

        border-color:
            rgba(32,215,215,0.55) !important;

        box-shadow:
            0 12px 28px
            rgba(0,0,0,0.32);
    }


    .poster-click-area button p {
        display:
            none !important;
    }


    /* =====================================================
       MOVIE TITLE
       ===================================================== */

    .movie-title {
        color:
            #f1f3f6 !important;

        font-size:
            13px !important;

        font-weight:
            700 !important;

        margin-top:
            8px !important;

        white-space:
            nowrap;

        overflow:
            hidden;

        text-overflow:
            ellipsis;
    }


    .movie-meta {
        color:
            #737c8b !important;

        font-size:
            10px !important;

        margin-top:
            3px !important;

        margin-bottom:
            16px !important;
    }


    /* =====================================================
       CONTENT TYPE BADGE
       ===================================================== */

    .content-badge {
        display:
            inline-block;

        padding:
            4px 8px;

        border-radius:
            5px;

        background:
            rgba(60,145,255,0.12);

        border:
            1px solid
            rgba(60,145,255,0.22);

        color:
            #63a8ff;

        font-size:
            9px;

        font-weight:
            800;

        letter-spacing:
            0.5px;
    }


    /* =====================================================
       BROWSE CARDS
       ===================================================== */

    .browse-card {
        background:
            #191d25;

        border:
            1px solid
            #303641;

        border-radius:
            11px;

        padding:
            18px;

        text-align:
            center;

        margin-bottom:
            12px;

        color:
            #e8ebef;

        font-weight:
            650;

        transition:
            transform 0.2s ease,
            border-color 0.2s ease;
    }


    .browse-card:hover {
        transform:
            translateY(-3px);

        border-color:
            rgba(255,79,163,0.45);
    }


    /* =====================================================
       LANGUAGE CARDS
       ===================================================== */

    .language-card {
        background:
            #191d25;

        border:
            1px solid
            #303641;

        border-radius:
            9px;

        padding:
            13px;

        text-align:
            center;

        color:
            #dce1e7;

        font-size:
            12px;

        transition:
            transform 0.2s ease,
            border-color 0.2s ease;
    }


    .language-card:hover {
        transform:
            translateY(-2px);

        border-color:
            rgba(135,77,255,0.55);
    }


    /* =====================================================
       DETAILS PAGE
       ===================================================== */

    .details-panel {
        background:
            #191d25;

        border:
            1px solid
            #303641;

        border-radius:
            14px;

        padding:
            24px;

        box-shadow:
            0 15px 40px
            rgba(0,0,0,0.22);
    }


    .details-title {
        font-size:
            44px;

        font-weight:
            850;

        letter-spacing:
            -1.5px;

        line-height:
            1.05;

        color:
            #ffffff;

        margin-bottom:
            12px;
    }


    .details-description {
        color:
            #929aaa;

        line-height:
            1.7;

        font-size:
            13px;
    }


    /* =====================================================
       INFORMATION BOXES
       ===================================================== */

    .info-box {
        background:
            #20252e;

        border:
            1px solid
            #303641;

        border-radius:
            9px;

        padding:
            14px;

        min-height:
            72px;

        margin-bottom:
            10px;
    }


    .info-label {
        color:
            #697281;

        font-size:
            9px;

        font-weight:
            800;

        text-transform:
            uppercase;

        letter-spacing:
            1px;
    }


    .info-value {
        color:
            #f0f2f5;

        font-size:
            13px;

        font-weight:
            650;

        margin-top:
            5px;
    }


    /* =====================================================
       OTT CARDS
       ===================================================== */

    .ott-card {
        display:
            block;

        background:
            #20252e;

        border:
            1px solid
            #343b47;

        border-radius:
            10px;

        padding:
            14px;

        margin-bottom:
            9px;

        transition:
            transform 0.18s ease,
            border-color 0.18s ease,
            box-shadow 0.18s ease;
    }


    .ott-card:hover {
        transform:
            translateY(-2px);

        border-color:
            var(--cyan);

        box-shadow:
            0 8px 20px
            rgba(0,0,0,0.25);
    }


    /* =====================================================
       NORMAL BUTTONS
       ===================================================== */

    .stButton > button {
        border-radius:
            8px !important;

        border:
            1px solid
            #343a45 !important;

        background:
            #1b2028 !important;

        color:
            #e9ecf1 !important;

        transition:
            all 0.18s ease !important;
    }


    .stButton > button:hover {
        border-color:
            rgba(32,215,215,0.55) !important;

        background:
            #222832 !important;
    }


    /* =====================================================
       BACK BUTTON
       ===================================================== */

    .details-back button {
        border:
            1px solid
            #343a45 !important;

        background:
            #1b2028 !important;

        color:
            #e9ecf1 !important;
    }


    /* =====================================================
       STREAMLIT METRICS
       ===================================================== */

    [data-testid="stMetric"] {
        background:
            #191d25;

        border:
            1px solid
            #303641;

        border-radius:
            10px;

        padding:
            14px;
    }


    /* =====================================================
       DIVIDERS
       ===================================================== */

    hr {
        border-color:
            #2b3039 !important;
    }


    /* =====================================================
       HEADINGS
       ===================================================== */

    h1,
    h2,
    h3 {
        color:
            #f4f6f8 !important;

        letter-spacing:
            -0.5px;
    }


    /* =====================================================
       CAPTIONS
       ===================================================== */

    .stCaption,
    [data-testid="stCaptionContainer"] {
        color:
            #737c8b !important;
    }


    /* =====================================================
       SCROLLBAR
       ===================================================== */

    ::-webkit-scrollbar {
        width:
            7px;

        height:
            7px;
    }


    ::-webkit-scrollbar-track {
        background:
            #11151d;
    }


    ::-webkit-scrollbar-thumb {
        background:
            #343b47;

        border-radius:
            10px;
    }


    ::-webkit-scrollbar-thumb:hover {
        background:
            #4c5665;
    }


    /* =====================================================
       MOBILE
       ===================================================== */

    @media(max-width: 900px) {

        .block-container {
            padding:
                18px !important;
        }

        .hero-title {
            font-size:
                36px;
        }

        .details-title {
            font-size:
                34px;
        }

        .poster-click-area button {
            min-height:
                300px !important;
        }

    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## ReelRoute")

    st.caption("MOVIE & OTT DISCOVERY")

    st.divider()

    st.markdown("### About")

    st.caption(
        "Search movies and web series, explore complete "
        "content information and check India-specific "
        "OTT availability."
    )

    st.divider()

    # -----------------------------------------------------
    # TMDB CONNECTION STATUS
    # -----------------------------------------------------

    try:

        token = get_token()

        if token:
            st.success("TMDB CONNECTED")
        else:
            st.error("TMDB TOKEN MISSING")

    except Exception:

        st.error("TMDB TOKEN MISSING")

        st.caption(
            "Add TMDB_API_KEY to your .env file."
        )

    st.divider()

    st.caption("ReelRoute")

    st.caption(
        "Every Movie. Every Platform. One Place."
    )


# =========================================================
# ROUTING
# =========================================================

selected_content = st.session_state.get(
    "open_content"
)


# =========================================================
# CONTENT DETAILS PAGE
# =========================================================

if selected_content:

    content_id = selected_content.get("id")

    content_type = selected_content.get(
        "type",
        "movie"
    )

    if content_id:

        render_movie_details(
            content_id,
            content_type
        )

    else:

        st.error("Unable to open this content.")

        if st.button("← Back to Home"):

            st.session_state.open_content = None

            st.session_state.open_movie_id = None

            st.rerun()


# =========================================================
# HOME PAGE
# =========================================================

else:

    render_home()
