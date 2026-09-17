import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from pages.home import render_home
from pages.search import render_search
from pages.upcoming import render_upcoming
from pages.movie_details import render_movie_details


st.set_page_config(
    page_title="OTTTrack",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# PREMIUM UI
# =========================================================

st.markdown(
    """
    <style>

    /* ==============================
       MAIN BACKGROUND
       ============================== */

    .stApp {
        background:
            radial-gradient(
                circle at 10% 10%,
                rgba(124, 58, 237, 0.18),
                transparent 30%
            ),
            radial-gradient(
                circle at 90% 20%,
                rgba(236, 72, 153, 0.15),
                transparent 30%
            ),
            radial-gradient(
                circle at 50% 100%,
                rgba(59, 130, 246, 0.12),
                transparent 35%
            ),
            #08090d;

        color: #ffffff;
    }


    /* ==============================
       REMOVE STREAMLIT AUTO NAVIGATION
       ============================== */

    [data-testid="stSidebarNav"] {
        display: none;
    }


    /* ==============================
       SIDEBAR
       ============================== */

    section[data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #11121a 0%,
                #0a0b10 100%
            );

        border-right: 1px solid rgba(255,255,255,0.08);
    }


    section[data-testid="stSidebar"] > div {
        padding-top: 1.5rem;
    }


    /* ==============================
       OTTTRACK LOGO
       ============================== */

    .brand {
        font-size: 28px;
        font-weight: 900;
        letter-spacing: -1px;

        background: linear-gradient(
            90deg,
            #8b5cf6,
            #ec4899,
            #f97316
        );

        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;

        margin-bottom: 4px;
    }


    .brand-tagline {
        color: #8f93a3;
        font-size: 12px;
        margin-bottom: 30px;
    }


    /* ==============================
       SIDEBAR BUTTONS
       ============================== */

    section[data-testid="stSidebar"] .stButton button {

        background: transparent;

        border: 1px solid transparent;

        color: #aeb2c0;

        border-radius: 10px;

        text-align: left;

        font-size: 14px;

        transition: all 0.2s ease;
    }


    section[data-testid="stSidebar"] .stButton button:hover {

        background:
            linear-gradient(
                90deg,
                rgba(139,92,246,0.20),
                rgba(236,72,153,0.12)
            );

        border: 1px solid rgba(139,92,246,0.25);

        color: white;

        transform: translateX(3px);
    }


    /* ==============================
       HERO
       ============================== */

    .hero {

        position: relative;

        padding: 55px 50px;

        border-radius: 24px;

        overflow: hidden;

        background:
            linear-gradient(
                120deg,
                rgba(124,58,237,0.28),
                rgba(236,72,153,0.18),
                rgba(15,23,42,0.92)
            );

        border: 1px solid rgba(255,255,255,0.10);

        box-shadow:
            0 25px 70px rgba(0,0,0,0.45);

        margin-bottom: 40px;
    }


    .hero::before {

        content: "";

        position: absolute;

        width: 280px;
        height: 280px;

        right: -80px;
        top: -100px;

        background: #8b5cf6;

        opacity: 0.18;

        filter: blur(90px);

        border-radius: 50%;
    }


    .hero-title {

        position: relative;

        font-size: 52px;

        font-weight: 900;

        letter-spacing: -2px;

        background: linear-gradient(
            90deg,
            #ffffff,
            #d8b4fe,
            #f9a8d4
        );

        -webkit-background-clip: text;

        -webkit-text-fill-color: transparent;
    }


    .hero-text {

        position: relative;

        color: #b5b8c5;

        font-size: 18px;

        margin-top: 8px;
    }


    /* ==============================
       SECTION TITLE
       ============================== */

    .section-title {

        font-size: 25px;

        font-weight: 800;

        margin-top: 35px;

        margin-bottom: 18px;

        color: #ffffff;
    }


    /* ==============================
       MOVIE TITLE
       ============================== */

    .movie-title {

        font-size: 16px;

        font-weight: 700;

        color: #f4f4f5;

        margin-top: 10px;

        white-space: nowrap;

        overflow: hidden;

        text-overflow: ellipsis;
    }


    .movie-meta {

        font-size: 13px;

        color: #8f93a3;

        margin-top: 4px;

        margin-bottom: 10px;
    }


    /* ==============================
       MOVIE POSTER
       ============================== */

    [data-testid="stImage"] img {

        border-radius: 12px;

        transition:
            transform 0.25s ease,
            box-shadow 0.25s ease;

        border: 1px solid rgba(255,255,255,0.08);
    }


    [data-testid="stImage"] img:hover {

        transform: scale(1.025);

        box-shadow:
            0 15px 35px rgba(0,0,0,0.55);
    }


    /* ==============================
       VIEW DETAILS BUTTON
       ============================== */

    .stButton button {

        border-radius: 9px;

        border: 1px solid rgba(139,92,246,0.30);

        background:
            linear-gradient(
                135deg,
                rgba(139,92,246,0.18),
                rgba(236,72,153,0.12)
            );

        color: #eeeeff;

        font-weight: 600;

        transition: all 0.2s ease;
    }


    .stButton button:hover {

        border-color: #8b5cf6;

        background:
            linear-gradient(
                135deg,
                rgba(139,92,246,0.35),
                rgba(236,72,153,0.25)
            );

        color: white;

        transform: translateY(-1px);
    }


    /* ==============================
       INPUTS
       ============================== */

    .stTextInput input,
    .stSelectbox div[data-baseweb="select"],
    .stNumberInput input {

        background: #11131b !important;

        border: 1px solid #292c38 !important;

        border-radius: 10px !important;

        color: white !important;
    }


    .stTextInput input:focus {

        border-color: #8b5cf6 !important;

        box-shadow:
            0 0 0 1px #8b5cf6 !important;
    }


    /* ==============================
       METRICS
       ============================== */

    [data-testid="stMetric"] {

        background:
            linear-gradient(
                135deg,
                rgba(139,92,246,0.10),
                rgba(236,72,153,0.06)
            );

        border: 1px solid rgba(255,255,255,0.08);

        border-radius: 14px;

        padding: 15px;
    }


    /* ==============================
       DIVIDER
       ============================== */

    hr {

        border-color: rgba(255,255,255,0.08);
    }


    /* ==============================
       FALLBACK POSTER
       ============================== */

    .poster-fallback {

        height: 280px;

        border-radius: 12px;

        background:
            linear-gradient(
                135deg,
                #171923,
                #0e1016
            );

        border: 1px solid rgba(255,255,255,0.08);

        display: flex;

        align-items: center;

        justify-content: center;

        color: #666b7a;

        font-size: 12px;

        font-weight: 700;
    }


    /* ==============================
       SCROLLBAR
       ============================== */

    ::-webkit-scrollbar {

        width: 7px;
    }


    ::-webkit-scrollbar-track {

        background: #08090d;
    }


    ::-webkit-scrollbar-thumb {

        background: #292c38;

        border-radius: 10px;
    }


    ::-webkit-scrollbar-thumb:hover {

        background: #8b5cf6;
    }


    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SESSION STATE
# =========================================================

if "page" not in st.session_state:
    st.session_state.page = "home"

if "selected_movie_id" not in st.session_state:
    st.session_state.selected_movie_id = None


# =========================================================
# CUSTOM SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        '<div class="brand">OTTTrack</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="brand-tagline">'
        'Every Movie. Every Platform. One Place.'
        '</div>',
        unsafe_allow_html=True
    )


    if st.button(
        "⌂  Home",
        use_container_width=True
    ):

        st.session_state.page = "home"

        st.session_state.selected_movie_id = None

        st.rerun()


    if st.button(
        "⌕  Search Movies",
        use_container_width=True
    ):

        st.session_state.page = "search"

        st.session_state.selected_movie_id = None

        st.rerun()


    if st.button(
        "◷  Upcoming",
        use_container_width=True
    ):

        st.session_state.page = "upcoming"

        st.session_state.selected_movie_id = None

        st.rerun()


    st.divider()

    st.caption("OTTTrack")
    st.caption("Discover • Explore • Watch")


# =========================================================
# PAGE ROUTING
# =========================================================

if st.session_state.selected_movie_id is not None:

    render_movie_details(
        st.session_state.selected_movie_id
    )

elif st.session_state.page == "search":

    render_search()

elif st.session_state.page == "upcoming":

    render_upcoming()

else:

    render_home()
