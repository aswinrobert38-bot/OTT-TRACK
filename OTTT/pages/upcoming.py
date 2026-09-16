import streamlit as st
from services.tmdb_service import TMDBError, get_upcoming, normalize_movie
from utils.helpers import movie_card


def render_upcoming():
    st.markdown('<div class="page-head"><div class="hero-kicker">WHAT’S NEXT</div><h1>Upcoming movies</h1><p>Live upcoming titles from TMDB for the India region.</p></div>', unsafe_allow_html=True)
    try:
        movies = [normalize_movie(x) for x in get_upcoming()]
    except TMDBError as exc:
        st.error(str(exc))
        return

    cols = st.columns(6, gap="medium")
    for i, movie in enumerate(movies):
        with cols[i % 6]:
            st.markdown('<div class="movie-card">', unsafe_allow_html=True)
            movie_card(movie, f"upcoming_{i}")
            st.markdown('</div>', unsafe_allow_html=True)
