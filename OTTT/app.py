import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from pages.home import render_home
from pages.search import render_search
from pages.upcoming import render_upcoming
from pages.movie_details import render_movie_details
from services.tmdb_service import TMDBError, get_token


st.set_page_config(
    page_title="OTTTrack",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

* {
    font-family: Inter, sans-serif;
}

.stApp {
    background: #07080c;
    color: #f4f5f7;
}

.block-container {
    max-width: 1500px;
    padding: 28px 42px 70px;
}

[data-testid="stSidebar"] {
    background: #0b0d12;
    border-right: 1px solid #1b1e26;
}

[data-testid="stSidebar"] .block-container {
    padding: 28px 18px;
}

.brand {
    font-size: 28px;
    font-weight: 800;
    letter-spacing: -1.2px;
    margin-bottom: 2px;
}

.brand span {
    color: #9b7cff;
}

.brand-sub {
    color: #777d8c;
    font-size: 11px;
    margin-bottom: 25px;
}

.nav-label {
    color: #555c6c;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.4px;
    margin: 20px 0 8px;
}

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
        linear-gradient(135deg, #141722, #0b0d12);
    display: flex;
    flex-direction: column;
    justify-content: center;
    margin-bottom: 30px;
}

.hero-kicker {
    color: #a78bfa;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.7px;
}

.hero h1 {
    font-size: clamp(42px, 5.3vw, 72px);
    line-height: .98;
    letter-spacing: -3px;
    margin: 12px 0 18px;
}

.hero p,
.page-head p {
    max-width: 720px;
    color: #9299a9;
    font-size: 15px;
    line-height: 1.65;
}

.page-head {
    padding: 8px 0 24px;
}

.page-head h1 {
    font-size: 44px;
    letter-spacing: -2px;
    margin: 8px 0;
}

.section-heading {
    display: flex;
    justify-content: space-between;
    align-items: end;
    gap: 20px;
    margin: 34px 0 15px;
}

.section-heading h2 {
    margin: 0;
    font-size: 22px;
    letter-spacing: -.6px;
}

.section-heading span {
    color: #686f80;
    font-size: 12px;
    text-align: right;
}

.movie-card {
    background: #0e1016;
    border: 1px solid #1c1f28;
    border-radius: 17px;
    padding: 10px;
    height: 100%;
    transition: .18s ease;
}

.movie-card:hover {
    transform: translateY(-4px);
    border-color: #493d72;
}

.movie-card img {
    border-radius: 11px;
    aspect-ratio: 2/3;
    object-fit: cover;
}

.movie-title {
    font-weight: 700;
    font-size: 14px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-top: 10px;
}

.movie-meta {
    color: #777e8e;
    font-size: 11px;
    margin: 5px 0 10px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.poster-fallback {
    aspect-ratio: 2/3;
    width: 100%;
    border-radius: 11px;
    background: linear-gradient(145deg, #181b25, #0c0e13);
    border: 1px solid #252936;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #5e6575;
    font-weight: 800;
    text-align: center;
    font-size: 13px;
}

.poster-fallback.large {
    min-height: 500px;
}

.poster-fallback span {
    letter-spacing: 1px;
}

button[kind="secondary"],
.stButton > button {
    background: #11141b;
    border: 1px solid #242833;
    color: #eef0f4;
    border-radius: 10px;
}

.stButton > button:hover {
    border-color: #8166dd;
    color: white;
}

.stTextInput input,
.stNumberInput input {
    background: #10131a !important;
    border: 1px solid #252936 !important;
    color: #fff !important;
    border-radius: 12px !important;
}

[data-testid="stTextInput"] label,
[data-testid="stNumberInput"] label {
    color: #777e8e;
    font-size: 11px;
}

.result-line {
    margin: 18px 0;
    color: #8b92a2;
    font-size: 13px;
}

.empty-state {
    border: 1px dashed #292d38;
    background: #0d0f15;
    padding: 42px;
    border-radius: 18px;
    text-align: center;
    margin-top: 20px;
}

.empty-state h3 {
    margin: 0 0 8px;
}

.empty-state p {
    color: #777e8e;
    margin: 0;
}

.info-card {
    background: #0e1016;
    border: 1px solid #1e222c;
    border-radius: 15px;
    padding: 16px;
    min-height: 78px;
}

.info-label,
.mini-label {
    color: #666d7c;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-size: 9px;
    font-weight: 700;
}

.info-value,
.mini-value {
    margin-top: 7px;
    font-weight: 650;
    font-size: 13px;
}

.detail-title {
    font-size: 56px;
    letter-spacing: -2.5px;
    margin: 7px 0;
}

.tagline-detail {
    color: #8b92a1;
    font-style: italic;
}

.detail-rating {
    font-size: 16px;
    font-weight: 700;
    margin: 14px 0;
}

.detail-rating span {
    color: #656c7b;
    font-size: 11px;
    font-weight: 500;
}

.detail-section {
    margin-top: 42px;
}

.ott-row {
    display: flex;
    align-items: center;
    background: #0d1016;
    border: 1px solid #1d212b;
    border-radius: 16px;
    padding: 14px;
    margin: 10px 0;
}

.ott-name {
    font-weight: 750;
    margin-top: -47px;
    margin-left: 62px;
}

.ott-type {
    color: #6d7483;
    font-size: 11px;
    margin-left: 62px;
    margin-top: 3px;
}

.badge {
    display: inline-block;
    padding: 5px 9px;
    border-radius: 999px;
    font-size: 9px;
    font-weight: 800;
    letter-spacing: .4px;
}

.badge-green {
    color: #63dfaa;
    background: #10251d;
}

.badge-yellow {
    color: #e8c35f;
    background: #292313;
}

.badge-gray {
    color: #9aa1af;
    background: #1b1e25;
}

.stCaption {
    color: #666d7c;
}

@media(max-width:900px) {

    .block-container {
        padding: 18px;
    }

    .hero {
        padding: 32px;
    }

    .section-heading {
        display: block;
    }

    .section-heading span {
        text-align: left;
        display: block;
        margin-top: 5px;
    }

    .detail-title {
        font-size: 42px;
    }

}

</style>
""", unsafe_allow_html=True)


if "page" not in st.session_state:
    st.session_state.page = "home"

if "selected_movie_id" not in st.session_state:
    st.session_state.selected_movie_id = None


with st.sidebar:

    st.markdown(
        '<div class="brand">OTT<span>Track</span></div>'
        '<div class="brand-sub">MOVIE & OTT RELEASE TRACKER</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="nav-label">BROWSE</div>',
        unsafe_allow_html=True
    )

    if st.button("⌂  Home", use_container_width=True):
        st.session_state.page = "home"
        st.session_state.selected_movie_id = None
        st.rerun()

    if st.button("⌕  Search", use_container_width=True):
        st.session_state.page = "search"
        st.session_state.selected_movie_id = None
        st.rerun()

    if st.button("◷  Upcoming", use_container_width=True):
        st.session_state.page = "upcoming"
        st.session_state.selected_movie_id = None
        st.rerun()

    st.markdown(
        '<div class="nav-label">DATA</div>',
        unsafe_allow_html=True
    )

    try:
        get_token()
        st.success("TMDB connected")

    except TMDBError:
        st.error("TMDB token missing")
        st.caption(
            "Add TMDB_TOKEN to .env or Streamlit Cloud Secrets."
        )


page = st.session_state.get("page", "home")


if st.session_state.selected_movie_id is not None:
    render_movie_details(
        st.session_state.selected_movie_id
    )

elif page == "search":
    render_search()

elif page == "upcoming":
    render_upcoming()

else:
    render_home()

