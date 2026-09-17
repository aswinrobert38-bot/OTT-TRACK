import os
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
    layout="wide"
)


st.markdown(
    """
    <style>
        .stApp {
            background-color: #0b0b0f;
            color: white;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        .movie-title {
            font-size: 18px;
            font-weight: 700;
            margin-top: 8px;
            color: white;
        }

        .movie-meta {
            font-size: 13px;
            color: #aaaaaa;
            margin-bottom: 10px;
        }

        .section-title {
            font-size: 28px;
            font-weight: 700;
            margin-top: 30px;
            margin-bottom: 18px;
        }

        .hero {
            padding: 45px;
            border-radius: 18px;
            background: linear-gradient(
                135deg,
                #171722,
                #0d0d12
            );
            margin-bottom: 30px;
        }

        .hero-title {
            font-size: 48px;
            font-weight: 800;
        }

        .hero-text {
            font-size: 18px;
            color: #bdbdbd;
        }

        .poster-fallback {
            height: 280px;
            background: #18181f;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #777777;
        }
    </style>
    """,
    unsafe_allow_html=True
)


if "page" not in st.session_state:
    st.session_state.page = "home"

if "selected_movie_id" not in st.session_state:
    st.session_state.selected_movie_id = None


with st.sidebar:

    st.title("🎬 OTTTrack")

    if st.button("Home", use_container_width=True):
        st.session_state.page = "home"
        st.session_state.selected_movie_id = None
        st.rerun()

    if st.button("Search Movies", use_container_width=True):
        st.session_state.page = "search"
        st.session_state.selected_movie_id = None
        st.rerun()

    if st.button("Upcoming", use_container_width=True):
        st.session_state.page = "upcoming"
        st.session_state.selected_movie_id = None
        st.rerun()

    st.divider()

    st.caption("Every Movie. Every Platform. One Place.")


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
