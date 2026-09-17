
import streamlit as st

from components.movie_card import movie_card

from services.tmdb_service import (
    TMDBError,
    get_now_playing,
    get_popular,
    get_trending,
    get_upcoming,
    search_movies,
)


def _section(title, subtitle, movies, key_prefix):

    if not movies:
        return

    st.markdown(
        '<div class="section-heading">'
        '<h2>' + title + '</h2>'
        '<span>' + subtitle + '</span>'
        '</div>',
        unsafe_allow_html=True
    )

    cols = st.columns(6, gap="medium")

    for i, movie in enumerate(movies[:6]):

        with cols[i]:

            movie_card(
                movie,
                key_suffix=key_prefix + "_" + str(i)
            )


def render_home():

    st.markdown(
        '<div class="hero">'
        '<div class="hero-kicker">INDIA · MOVIES · OTT</div>'
        '<h1>One search.<br>Every movie.</h1>'
        '<p>'
        'Search real movie data, open a full details page, '
        'and check current India streaming availability '
        'without invented OTT dates.'
        '</p>'
        '</div>',
        unsafe_allow_html=True
    )


    query = st.text_input(
        "Search",
        placeholder="Search any movie — Leo, Interstellar, Vikram...",
        label_visibility="collapsed",
        key="home_search"
    )


    if query.strip():

        try:

            data = search_movies(
                query.strip(),
                page=1
            )

            results = data.get("results", [])

        except TMDBError as exc:

            st.error(str(exc))
            return


        st.markdown(
            '<div class="result-line">'
            + str(len(results))
            + ' results for <b>'
            + query.strip()
            + '</b></div>',
            unsafe_allow_html=True
        )


        if not results:

            st.markdown(
                '<div class="empty-state">'
                '<h3>No movies found</h3>'
                '<p>Try another movie title.</p>'
                '</div>',
                unsafe_allow_html=True
            )

            return


        cols = st.columns(6, gap="medium")


        for i, movie in enumerate(results[:18]):

            with cols[i % 6]:

                movie_card(
                    movie,
                    key_suffix="home_results_" + str(i)
                )


        return


    try:

        trending_data = get_trending()
        now_playing_data = get_now_playing()
        popular_data = get_popular()
        upcoming_data = get_upcoming()


        _section(
            "Trending this week",
            "Popular movies people are discovering now",
            trending_data.get("results", []),
            "trend"
        )


        _section(
            "Now playing in India",
            "Movies currently listed in Indian theatrical releases",
            now_playing_data.get("results", []),
            "now"
        )


        _section(
            "Popular",
            "High-interest movies from TMDB",
            popular_data.get("results", []),
            "popular"
        )


        _section(
            "Upcoming",
            "Upcoming titles listed by TMDB for India",
            upcoming_data.get("results", []),
            "upcoming"
        )


    except TMDBError as exc:

        st.error(str(exc))

        st.info(
            "Add a valid TMDB API Read Access Token "
            "to TMDB_TOKEN in the .env file, "
            "or add TMDB_TOKEN to Streamlit Cloud Secrets."
        )

