import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from pages.home import render_home
from pages.movie_details import render_movie_details
from services.tmdb_service import get_token


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="ReelRoute",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# GLOBAL CSS
# =========================================================

st.markdown(
    """
    <style>

    /* =====================================================
       MAIN APP
       ===================================================== */

    .stApp {
        background: #07080c;
        color: #f4f5f7;
    }

    .block-container {
        max-width: 1500px;
        padding: 28px 42px 70px;
    }


    /* =====================================================
       SIDEBAR
       ===================================================== */

    [data-testid="stSidebar"] {
        background: #0b0d12;
        border-right: 1px solid #1b1e26;
    }

    [data-testid="stSidebar"] .block-container {
        padding: 28px 18px;
    }


    /* =====================================================
       REMOVE STREAMLIT DEFAULT PAGE NAVIGATION
       ===================================================== */

    [data-testid="stSidebarNav"] {
        display: none;
    }


    /* =====================================================
       SIDEBAR BRAND
       ===================================================== */

    .sidebar-brand {
        font-size: 28px;
        font-weight: 800;
        letter-spacing: -1.2px;
        margin-bottom: 4px;
    }

    .sidebar-subtitle {
        color: #777d8c;
        font-size: 10px;
        letter-spacing: 1px;
        line-height: 1.5;
    }


    /* =====================================================
       HERO
       ===================================================== */

    .hero {
        padding: 54px 52px;
        min-height: 320px;
        border: 1px solid #20232d;
        border-radius: 28px;

        background:
            radial-gradient(
                circle at 80% 20%,
                rgba(145,112,255,.18),
                transparent 32%
            ),
            linear-gradient(
                135deg,
                #141722,
                #0b0d12
            );

        display: flex;
        flex-direction: column;
        justify-content: center;

        margin-bottom: 28px;
    }

    .hero-kicker {
        color: #a78bfa;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 1.7px;
    }

    .hero-title {
        font-size: clamp(42px, 5.3vw, 72px);
        font-weight: 800;
        line-height: .98;
        letter-spacing: -3px;
        margin: 12px 0 18px;
    }

    .hero-text {
        color: #9299a9;
        font-size: 15px;
        line-height: 1.65;
        max-width: 720px;
    }


    /* =====================================================
       SEARCH AREA
       ===================================================== */

    [data-testid="stForm"] {
        background: #0d1016;
        border: 1px solid #20232d;
        border-radius: 18px;
        padding: 10px;
        margin-bottom: 28px;
    }

    [data-testid="stTextInput"] input {
        background: #10131a !important;
        border: 1px solid #252936 !important;
        color: white !important;
        border-radius: 12px !important;
        min-height: 46px;
    }

    [data-testid="stTextInput"] input:focus {
        border-color: #8166dd !important;
    }

    [data-testid="stFormSubmitButton"] button {
        min-height: 46px;
        border-radius: 12px;
        background: #7658d9;
        border: 1px solid #8b73e6;
        color: white;
        font-weight: 700;
    }

    [data-testid="stFormSubmitButton"] button:hover {
        background: #846be3;
        border-color: #a18cf0;
    }


    /* =====================================================
       SECTIONS
       ===================================================== */

    .section-heading {
        margin-top: 36px;
        margin-bottom: 16px;
    }

    .section-heading h2 {
        margin-bottom: 4px;
        font-size: 24px;
        letter-spacing: -.7px;
    }

    .section-heading p {
        margin: 0;
        color: #6f7686;
        font-size: 12px;
    }


    /* =====================================================
       MOVIE CARDS
       ===================================================== */

    .movie-title {
        margin-top: 8px;
        font-size: 14px;
        font-weight: 700;

        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .movie-meta {
        color: #777e8e;
        font-size: 11px;
        margin-top: 4px;

        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }


    /* =====================================================
       POSTER LINKS
       ===================================================== */

    a {
        text-decoration: none !important;
    }

    a img {
        border-radius: 11px;
        width: 100%;
        aspect-ratio: 2 / 3;
        object-fit: cover;
        transition: transform .18s ease,
                    opacity .18s ease;
    }

    a img:hover {
        transform: translateY(-4px);
        opacity: .88;
    }


    /* =====================================================
       BROWSE CARDS
       ===================================================== */

    .browse-card {
        background: #0e1016;
        border: 1px solid #1c1f28;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 12px;
        text-align: center;
        color: #e8eaf0;
        font-size: 13px;
        font-weight: 600;
    }


    /* =====================================================
       SEARCH RESULTS
       ===================================================== */

    .search-result-box {
        background: #0d1016;
        border: 1px solid #20232d;
        border-radius: 16px;
        padding: 16px 18px;
        margin: 12px 0 24px;
    }

    .search-result-label {
        color: #777e8e;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1px;
    }

    .search-result-title {
        color: white;
        font-size: 20px;
        font-weight: 700;
        margin-top: 4px;
    }


    /* =====================================================
       DETAILS
       ===================================================== */

    .details-title {
        font-size: 52px;
        font-weight: 800;
        letter-spacing: -2.5px;
        margin-bottom: 8px;
    }

    .details-subtitle {
        color: #8b92a1;
        font-size: 14px;
        line-height: 1.7;
    }

    .detail-box {
        background: #0e1016;
        border: 1px solid #1e222c;
        border-radius: 14px;
        padding: 15px;
        margin-bottom: 12px;
    }

    .detail-label {
        color: #666d7c;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 9px;
        font-weight: 700;
    }

    .detail-value {
        margin-top: 6px;
        font-size: 14px;
        font-weight: 650;
    }


    /* =====================================================
       OTT
       ===================================================== */

    .ott-box {
        background: #0d1016;
        border: 1px solid #1d212b;
        border-radius: 15px;
        padding: 14px;
        margin-bottom: 10px;
    }


    /* =====================================================
       MOBILE
       ===================================================== */

    @media(max-width: 900px) {

        .block-container {
            padding: 18px;
        }

        .hero {
            padding: 32px;
        }

        .hero-title {
            font-size: 46px;
        }

        .details-title {
            font-size: 40px;
        }

    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SESSION STATE
# =========================================================

if "selected_movie_id" not in st.session_state:
    st.session_state.selected_movie_id = None


# =========================================================
# MOVIE CLICK HANDLER
# =========================================================

movie_id = st.query_params.get("movie_id")

if movie_id:

    st.session_state.selected_movie_id = str(movie_id)

    st.query_params.clear()

    st.rerun()


# =========================================================
# SIDEBAR
# ONLY BRAND + STATUS
# =========================================================

with st.sidebar:

    st.markdown(
        "### ReelRoute"
    )

    st.caption(
        "MOVIE & OTT DISCOVERY PLATFORM"
    )

    st.divider()

    st.markdown(
        "#### About"
    )

    st.caption(
        "Discover movies, explore their details "
        "and find OTT availability in India."
    )

    st.divider()

    st.markdown(
        "#### Data"
    )

    if get_token():

        st.success(
            "TMDB connected"
        )

    else:

        st.error(
            "TMDB token missing"
        )

        st.caption(
            "Add TMDB_API_KEY to .env and restart the app."
        )

    st.divider()

    st.caption(
        "ReelRoute"
    )

    st.caption(
        "Every Movie. Every Platform. One Place."
    )


# =========================================================
# SINGLE-PAGE APPLICATION
# =========================================================

if st.session_state.selected_movie_id is not None:

    render_movie_details(
        st.session_state.selected_movie_id
    )

else:

    render_home()
