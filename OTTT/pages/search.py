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


def get_movie_title(movie):

    return (
        movie.get("title")
        or movie.get("name")
        or "Untitled"
    )


def get_movie_poster(movie):

    poster = movie.get("poster_url")

    if poster:
        return poster

    poster_path = movie.get("poster_path")

    if poster_path:

        return (
            "https://image.tmdb.org/t/p/w500"
            + poster_path
        )

    return None


def movie_card(movie):

    movie_id = movie.get("id")

    title = get_movie_title(movie)

    poster = get_movie_poster(movie)

    release_date = (
        movie.get("release_date")
        or ""
    )

    year = (
        release_date[:4]
        if release_date
        else "N/A"
    )

    rating = movie.get(
        "rating"
    )

    if rating is None:

        rating = movie.get(
            "vote_average"
        )

    try:

        rating_text = str(
            round(float(rating), 1)
        )

    except Exception:

        rating_text = "N/A"

    language = (
        movie.get(
            "original_language"
        )
        or "N/A"
    )

    # -----------------------------------------
    # CLICKABLE POSTER
    # -----------------------------------------

    if poster and movie_id:

        safe_title = html.escape(
            title,
            quote=True
        )

        st.image(
            poster,
            use_container_width=True
        )

        if st.button(
            "View movie details",
            key=f"search_movie_{movie_id}",
            use_container_width=True
        ):
            st.session_state.open_movie_id = movie_id
            st.rerun()

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
    # META
    # -----------------------------------------

    st.markdown(
        f"""
        <div class="movie-card-meta">

            {html.escape(year)}

            <span>•</span>

            {html.escape(
                str(language).upper()
            )}

            <span>•</span>

            ★ {html.escape(rating_text)}

        </div>
        """,
        unsafe_allow_html=True
    )


def render_search():

    # =========================================
    # HEADER
    # =========================================

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

    # =========================================
    # SEARCH
    # =========================================

    query = st.text_input(
        "Movie title",
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
                    Try Leo, Interstellar,
                    Jailer, Vikram or any other movie.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        return

    # =========================================
    # SEARCH API
    # =========================================

    try:

        data = search_movies(
            query.strip()
        )

        movies = get_results(data)

    except TMDBError as error:

        st.error(str(error))
        return

    # =========================================
    # RESULTS HEADER
    # =========================================

    st.markdown(
        f"""
        <div class="search-result-heading">

            <div>

                <span>RESULTS FOR</span>

                <strong>
                    {html.escape(
                        query.strip()
                    )}
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

    # =========================================
    # MOVIES
    # =========================================

    columns = st.columns(
        6,
        gap="medium"
    )

    for index, movie in enumerate(
        movies[:24]
    ):

        with columns[index % 6]:

            movie_card(movie)
