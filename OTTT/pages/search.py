import html
import streamlit as st

from services.tmdb_service import (
    TMDBError,
    search_movies,
)


def get_results(data):

    if isinstance(data, dict):
        return data.get("results", [])

    if isinstance(data, list):
        return data

    return []


def display_movie(movie):

    movie_id = movie.get("id")

    title = (
        movie.get("title")
        or movie.get("name")
        or "Untitled"
    )

    release_date = movie.get("release_date") or ""

    year = (
        release_date[:4]
        if release_date
        else "N/A"
    )

    rating = movie.get("rating")

    if rating is None:
        rating = movie.get("vote_average", 0)

    try:
        rating_text = str(
            round(float(rating), 1)
        )
    except Exception:
        rating_text = "N/A"

    language = (
        movie.get("original_language")
        or "N/A"
    )

    poster = movie.get("poster_url")

    if not poster:

        poster_path = movie.get(
            "poster_path"
        )

        if poster_path:

            poster = (
                "https://image.tmdb.org/t/p/w500"
                + poster_path
            )

    # -----------------------------------------
    # CLICKABLE POSTER
    # -----------------------------------------

    if poster and movie_id:

        st.markdown(
            f"""
            <a
                href="?movie_id={movie_id}"
                class="movie-poster-link"
                title="{html.escape(title, quote=True)}"
            >
                <img
                    src="{html.escape(poster, quote=True)}"
                    class="movie-poster"
                >
            </a>
            """,
            unsafe_allow_html=True
        )

    elif poster:

        st.image(
            poster,
            use_container_width=True
        )

    else:

        st.markdown(
            """
            <div class="poster-placeholder">
                NO POSTER
            </div>
            """,
            unsafe_allow_html=True
        )

    # -----------------------------------------
    # TITLE
    # -----------------------------------------

    st.markdown(
        f"""
        <div class="movie-card-title">
            {html.escape(title)}
        </div>
        """,
        unsafe_allow_html=True
    )

    # -----------------------------------------
    # INFORMATION
    # -----------------------------------------

    st.markdown(
        f"""
        <div class="movie-card-meta">
            {html.escape(year)}
            <span>•</span>
            {html.escape(language.upper())}
            <span>•</span>
            ★ {html.escape(rating_text)}
        </div>
        """,
        unsafe_allow_html=True
    )


def render_search():

    # -----------------------------------------
    # PAGE HEADER
    # -----------------------------------------

    st.markdown(
        """
        <div class="search-page-header">

            <div class="hero-kicker">
                DISCOVER
            </div>

            <h1>
                Find your next movie
            </h1>

            <p>
                Search movies from across languages and years.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    # -----------------------------------------
    # SEARCH BOX
    # -----------------------------------------

    query = st.text_input(
        "Search movie",
        placeholder="Search for a movie...",
        key="search_page_query",
        label_visibility="collapsed"
    )

    if not query.strip():

        st.markdown(
            """
            <div class="search-empty">

                <div class="search-empty-title">
                    Search the movie catalogue
                </div>

                <div class="search-empty-text">
                    Try movie names such as Leo,
                    Interstellar, Jailer or Vikram.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        return

    # -----------------------------------------
    # API SEARCH
    # -----------------------------------------

    try:

        data = search_movies(
            query.strip()
        )

        movies = get_results(data)

    except TMDBError as error:

        st.error(str(error))
        return

    # -----------------------------------------
    # RESULT COUNT
    # -----------------------------------------

    st.markdown(
        f"""
        <div class="search-result-heading">

            <div>
                <span>RESULTS FOR</span>
                <strong>
                    {html.escape(query.strip())}
                </strong>
            </div>

            <div>
                {len(movies)} movie(s)
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    if not movies:

        st.warning(
            "No matching movies were found."
        )

        return

    # -----------------------------------------
    # MOVIES
    # -----------------------------------------

    columns = st.columns(
        6,
        gap="medium"
    )

    for index, movie in enumerate(
        movies[:24]
    ):

        with columns[index % 6]:

            display_movie(movie)
