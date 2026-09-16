import streamlit as st
from services.tmdb_service import TMDBError, normalize_movie, search_movies
from utils.helpers import movie_card


def render_search():
    st.markdown('<div class="page-head"><div class="hero-kicker">DISCOVER</div><h1>Search movies</h1><p>Search TMDB instead of a fixed demo list. Year and original-language filters are sent to the API.</p></div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns([2.5, 1, 1])
    with c1:
        query = st.text_input("Movie title", placeholder="Enter a movie title...", key="search_query")
    with c2:
        year = st.number_input("Year", min_value=1900, max_value=2100, value=2026, step=1, key="search_year")
    with c3:
        language = st.text_input("Language code", placeholder="ta / en / hi", key="search_language")

    if not query.strip():
        st.markdown('<div class="empty-state"><h3>Start with a movie title</h3><p>Try <b>Leo</b>, <b>Interstellar</b>, <b>Jailer</b> or any other title.</p></div>', unsafe_allow_html=True)
        return

    try:
        results = search_movies(query.strip(), year=year if year else None, language=language.strip().lower() or None)
    except TMDBError as exc:
        st.error(str(exc))
        return

    movies = [normalize_movie(x) for x in results]
    st.markdown(f'<div class="result-line"><b>{len(movies)}</b> result(s)</div>', unsafe_allow_html=True)

    if not movies:
        st.warning("TMDB returned no matching movie.")
        return

    cols = st.columns(6, gap="medium")
    for i, movie in enumerate(movies):
        with cols[i % 6]:
            st.markdown('<div class="movie-card">', unsafe_allow_html=True)
            movie_card(movie, f"search_{i}")
            st.markdown('</div>', unsafe_allow_html=True)
