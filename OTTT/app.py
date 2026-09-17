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
# GLOBAL CSS
# =========================================================

st.markdown(
    """
    <style>

    /* =====================================================
       GLOBAL
       ===================================================== */

    .stApp {
        background: #07080c;
        color: #f4f5f7;
    }

    .block-container {
        max-width: 1500px;
        padding: 30px 42px 70px;
    }


    /* =====================================================
       SIDEBAR
       ===================================================== */

    [data-testid="stSidebar"] {
        background: #0b0d12;
        border-right: 1px solid #1c1f28;
    }

    [data-testid="stSidebar"] .block-container {
        padding: 28px 18px;
    }


    [data-testid="stSidebarNav"] {
        display: none;
    }


    /* =====================================================
       SEARCH
       ===================================================== */

    [data-testid="stForm"] {
        background: #0d1016;
        border: 1px solid #20232d;
        border-radius: 16px;
        padding: 10px;
        margin: 10px 0 30px;
    }

    [data-testid="stTextInput"] input {
        background: #10131a !important;
        border: 1px solid #252936 !important;
        color: #ffffff !important;
        border-radius: 11px !important;
        min-height: 46px;
    }

    [data-testid="stFormSubmitButton"] button {
        min-height: 46px;
        border-radius: 11px;
        background: #7658d9;
        border: 1px solid #8d76e5;
        color: white;
        font-weight: 700;
    }

    [data-testid="stFormSubmitButton"] button:hover {
        background: #856ce5;
    }


    /* =====================================================
       MOVIE POSTERS
       ===================================================== */

    a {
        text-decoration: none !important;
    }

    a img {
        width: 100%;
        aspect-ratio: 2 / 3;
        object-fit: cover;
        border-radius: 12px;
        transition: transform .18s ease,
                    opacity .18s ease;
    }

    a img:hover {
        transform: translateY(-5px);
        opacity: .86;
    }


    /* =====================================================
       MOVIE TITLE
       ===================================================== */

    .movie-title {
        font-size: 14px;
        font-weight: 700;
        margin-top: 8px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .movie-meta {
        color: #777e8e;
        font-size: 11px;
        margin-top: 4px;
        margin-bottom: 18px;
    }


    /* =====================================================
       DETAILS
       ===================================================== */

    .details-title {
        font-size: 52px;
        font-weight: 800;
        letter-spacing: -2px;
        line-height: 1;
        margin-bottom: 12px;
    }

    .details-description {
        color: #9299a9;
        line-height: 1.7;
        font-size: 14px;
    }


    /* =====================================================
       INFO BOXES
       ===================================================== */

    .info-box {
        background: #0d1016;
        border: 1px solid #1e222c;
        border-radius: 14px;
        padding: 15px;
        min-height: 82px;
        margin-bottom: 12px;
    }

    .info-label {
        color: #656c7b;
        font-size: 9px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .info-value {
        color: #f0f1f4;
        font-size: 14px;
        font-weight: 650;
        margin-top: 7px;
    }


    /* =====================================================
       OTT
       ===================================================== */

    .ott-card {
        background: #0d1016;
        border: 1px solid #1d212b;
        border-radius: 14px;
        padding: 15px;
        margin-bottom: 10px;
    }


    /* =====================================================
       BROWSE
       ===================================================== */

    .browse-card {
        background: #0d1016;
        border: 1px solid #1d212b;
        border-radius: 13px;
        padding: 17px;
        text-align: center;
        margin-bottom: 12px;
        font-weight: 600;
    }


    /* =====================================================
       MOBILE
       ===================================================== */

    @media(max-width: 900px) {

        .block-container {
            padding: 18px;
        }

        .details-title {
            font-size: 38px;
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
# POSTER CLICK HANDLER
# =========================================================

movie_id = st.query_params.get("movie_id")

if movie_id:

    st.session_state.selected_movie_id = str(movie_id)

    st.query_params.clear()

    st.rerun()


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        "## ReelRoute"
    )

    st.caption(
        "MOVIE & OTT DISCOVERY"
    )

    st.divider()

    st.markdown(
        "### About"
    )

    st.caption(
        "Search movies, explore complete movie information "
        "and check India-specific OTT availability."
    )

    st.divider()

    st.markdown(
        ""
    )

    if get_token():

        st.success(
            ""
        )

    else:

        st.error(
            "TMDB token missing"
        )

        st.caption(
            "Add TMDB_API_KEY to your .env file."
        )

    st.divider()

    st.caption(
        "ReelRoute"
    )

    st.caption(
        "Every Movie. Every Platform. One Place."
    )


# =========================================================
# SINGLE PAGE ROUTING
# =========================================================

if st.session_state.selected_movie_id is not None:

    render_movie_details(
        st.session_state.selected_movie_id
    )

else:

    render_home()
