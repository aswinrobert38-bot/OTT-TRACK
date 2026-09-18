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
        background:
            radial-gradient(
                circle at 12% 8%,
                rgba(118, 76, 255, .16),
                transparent 30%
            ),
            radial-gradient(
                circle at 88% 18%,
                rgba(0, 201, 255, .10),
                transparent 28%
            ),
            linear-gradient(
                135deg,
                #05060a 0%,
                #090b12 48%,
                #07080d 100%
            );

        color: #f7f8fb;
    }

    .block-container {
        max-width: 1500px;
        padding: 30px 42px 70px;
    }


    /* =====================================================
       SIDEBAR
       ===================================================== */

    [data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #0b0d15 0%,
                #080a10 55%,
                #06070c 100%
            );

        border-right:
            1px solid rgba(135, 105, 255, .22);

        box-shadow:
            8px 0 35px rgba(0, 0, 0, .25);
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
        background:
            linear-gradient(
                135deg,
                rgba(18, 21, 31, .96),
                rgba(11, 14, 22, .96)
            );

        border:
            1px solid rgba(126, 91, 255, .28);

        border-radius: 18px;

        padding: 10px;

        margin: 10px 0 30px;

        box-shadow:
            0 12px 35px rgba(0, 0, 0, .24);
    }

    [data-testid="stTextInput"] input {
        background: #0f121b !important;

        border:
            1px solid #292d3b !important;

        color: #ffffff !important;

        border-radius: 12px !important;

        min-height: 46px;
    }

    [data-testid="stTextInput"] input:focus {
        border-color: #8b6cff !important;

        box-shadow:
            0 0 0 1px
            rgba(139, 108, 255, .45) !important;
    }

    [data-testid="stFormSubmitButton"] button {
        min-height: 46px;

        border-radius: 12px;

        background:
            linear-gradient(
                135deg,
                #7658d9,
                #9b62ff
            );

        border:
            1px solid #a783ff;

        color: white;

        font-weight: 750;

        box-shadow:
            0 8px 22px
            rgba(118, 88, 217, .28);
    }

    [data-testid="stFormSubmitButton"] button:hover {
        background:
            linear-gradient(
                135deg,
                #856ce5,
                #aa73ff
            );
    }


    /* =====================================================
       MOVIE POSTER BUTTON
       ===================================================== */

    .poster-click-area button {
        width: 100% !important;

        height: 100% !important;

        min-height: 360px !important;

        padding: 0 !important;

        margin: 0 !important;

        border-radius: 15px !important;

        border:
            1px solid
            rgba(255, 255, 255, .08) !important;

        background:
            transparent !important;

        color: transparent !important;

        font-size: 0 !important;

        overflow: hidden !important;

        box-shadow:
            0 10px 25px
            rgba(0, 0, 0, .30);

        transition:
            transform .22s ease,
            box-shadow .22s ease,
            border-color .22s ease;
    }

    .poster-click-area button:hover {
        transform:
            translateY(-7px)
            scale(1.015);

        border-color:
            rgba(151, 119, 255, .70) !important;

        box-shadow:
            0 18px 38px
            rgba(71, 46, 150, .40);
    }

    .poster-click-area button p {
        display: none !important;
    }


    /* =====================================================
       POSTER IMAGE
       ===================================================== */

    .poster-image {
        width: 100%;

        aspect-ratio: 2 / 3;

        object-fit: cover;

        border-radius: 15px;

        display: block;

        box-shadow:
            0 10px 25px
            rgba(0, 0, 0, .30);
    }


    /* =====================================================
       MOVIE TITLE
       ===================================================== */

    .movie-title {
        font-size: 14px;

        font-weight: 750;

        margin-top: 9px;

        color: #f3f4f8;

        white-space: nowrap;

        overflow: hidden;

        text-overflow: ellipsis;
    }

    .movie-meta {
        color: #858da0;

        font-size: 11px;

        margin-top: 4px;

        margin-bottom: 18px;
    }


    /* =====================================================
       DETAILS
       ===================================================== */

    .details-title {
        font-size: 52px;

        font-weight: 850;

        letter-spacing: -2px;

        line-height: 1;

        margin-bottom: 12px;

        background:
            linear-gradient(
                90deg,
                #ffffff 0%,
                #cfc6ff 55%,
                #8fe8ff 100%
            );

        -webkit-background-clip: text;

        -webkit-text-fill-color: transparent;
    }

    .details-description {
        color: #a3aabd;

        line-height: 1.75;

        font-size: 14px;
    }


    /* =====================================================
       INFO BOXES
       ===================================================== */

    .info-box {
        background:
            linear-gradient(
                145deg,
                rgba(18, 21, 31, .98),
                rgba(11, 14, 22, .98)
            );

        border:
            1px solid
            rgba(139, 108, 255, .20);

        border-radius: 15px;

        padding: 15px;

        min-height: 82px;

        margin-bottom: 12px;

        box-shadow:
            0 8px 25px
            rgba(0, 0, 0, .18);
    }

    .info-label {
        color: #777f93;

        font-size: 9px;

        font-weight: 750;

        text-transform: uppercase;

        letter-spacing: 1px;
    }

    .info-value {
        color: #f3f4f8;

        font-size: 14px;

        font-weight: 650;

        margin-top: 7px;
    }


    /* =====================================================
       OTT
       ===================================================== */

    .ott-card {
        background:
            linear-gradient(
                135deg,
                rgba(19, 22, 32, .98),
                rgba(10, 13, 21, .98)
            );

        border:
            1px solid
            rgba(92, 207, 255, .16);

        border-radius: 15px;

        padding: 15px;

        margin-bottom: 10px;

        box-shadow:
            0 8px 24px
            rgba(0, 0, 0, .20);
    }


    /* =====================================================
       BROWSE
       ===================================================== */

    .browse-card {
        background:
            linear-gradient(
                145deg,
                rgba(18, 21, 31, .98),
                rgba(10, 13, 21, .98)
            );

        border:
            1px solid
            rgba(139, 108, 255, .18);

        border-radius: 14px;

        padding: 17px;

        text-align: center;

        margin-bottom: 12px;

        font-weight: 650;

        box-shadow:
            0 8px 22px
            rgba(0, 0, 0, .18);
    }


    /* =====================================================
       NORMAL BUTTONS
       ===================================================== */

    .stButton > button {
        border-radius: 11px !important;

        border:
            1px solid
            rgba(139, 108, 255, .24) !important;

        background:
            rgba(18, 21, 31, .90) !important;

        color:
            #f3f4f8 !important;
    }


    /* =====================================================
       DIVIDERS
       ===================================================== */

    hr {
        border-color:
            rgba(139, 108, 255, .14) !important;
    }


    /* =====================================================
       HEADINGS
       ===================================================== */

    h1,
    h2,
    h3 {
        letter-spacing: -.5px;
    }


    /* =====================================================
       DIALOG
       ===================================================== */

    [data-testid="stDialog"] {
        background:
            linear-gradient(
                145deg,
                #0c0f17,
                #080a10
            ) !important;
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

        .poster-click-area button {
            min-height: 300px !important;
        }

    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# MOVIE DETAILS DIALOG
# =========================================================

@st.dialog(
    "Movie Details",
    width="large"
)
def open_movie_details(movie_id):

    render_movie_details(movie_id)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## ReelRoute")

    st.caption("MOVIE & OTT DISCOVERY")

    st.divider()

    st.markdown("### About")

    st.caption(
        "Search movies, explore complete movie information "
        "and check India-specific OTT availability."
    )

    st.divider()

    if get_token():

        st.success("DB CONNECTED")

    else:

        st.error("TMDB token missing")

        st.caption(
            "Add TMDB_API_KEY to your .env file."
        )

    st.divider()

    st.caption("ReelRoute")

    st.caption(
        "Every Movie. Every Platform. One Place."
    )


# =========================================================
# MOVIE SELECTION STATE
# =========================================================

if "open_movie_id" not in st.session_state:
    st.session_state.open_movie_id = None


# =========================================================
# HOME
# =========================================================

render_home()


# =========================================================
# OPEN SELECTED MOVIE
# =========================================================

if st.session_state.open_movie_id is not None:

    movie_id = st.session_state.open_movie_id

    st.session_state.open_movie_id = None

    open_movie_details(movie_id)
