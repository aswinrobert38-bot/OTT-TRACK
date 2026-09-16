import streamlit as st
from services.tmdb_service import TMDBError, get_now_playing, get_popular, get_trending, get_upcoming, normalize_movie, search_movies
from utils.helpers import movie_card


def _section(title, subtitle, raw_movies, key_prefix):
    movies = [normalize_movie(x) for x in raw_movies if x.get("poster_path") or x.get("title")]
    if not movies:
        return
    st.markdown(f'<div class="section-heading"><h2>{title}</h2><span>{subtitle}</span></div>', unsafe_allow_html=True)
    cols = st.columns(6, gap="medium")
    for i, movie in enumerate(movies[:6]):
        with cols[i]:
            st.markdown('<div class="movie-card">', unsafe_allow_html=True)
            movie_card(movie, f"{key_prefix}_{i}")
            st.markdown('</div>', unsafe_allow_html=True)


def render_home():
    st.markdown(
        '<div class="hero"><div class="hero-kicker">INDIA · MOVIES · OTT</div>'
        '<h1>One search.<br>Every movie.</h1>'
        '<p>Search real movie data, open a full details page, and check current India streaming availability without invented OTT dates.</p></div>',
        unsafe_allow_html=True,
    )

    query = st.text_input("Search", placeholder="Search any movie — Leo, Interstellar, Vikram...", label_visibility="collapsed", key="home_search")
    if query.strip():
        try:
            results = [normalize_movie(x) for x in search_movies(query.strip())]
        except TMDBError as exc:
            st.error(str(exc))
            return
        st.markdown(f'<div class="result-line">{len(results)} results for <b>{query.strip()}</b></div>', unsafe_allow_html=True)
        cols = st.columns(6, gap="medium")
        for i, movie in enumerate(results[:18]):
            with cols[i % 6]:
                st.markdown('<div class="movie-card">', unsafe_allow_html=True)
                movie_card(movie, f"home_results_{i}")
                st.markdown('</div>', unsafe_allow_html=True)
        return

    try:
        _section("Trending this week", "Popular movies people are discovering now", get_trending(), "trend")
        _section("Now playing in India", "Movies currently listed in Indian theatrical releases", get_now_playing(), "now")
        _section("Popular", "High-interest movies from TMDB", get_popular(), "popular")
        _section("Upcoming", "Upcoming titles listed by TMDB for India", get_upcoming(), "upcoming")
    except TMDBError as exc:
        st.error(str(exc))
        st.info("Add a valid TMDB API Read Access Token to the .env file, then restart Streamlit.")
