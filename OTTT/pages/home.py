import html
import streamlit as st

from services.tmdb_service import (
    TMDBError,
    get_now_playing,
    get_popular,
    get_trending
)


def show_movies(movies, section_name):

    st.markdown(
        '<div class="section-title">' +
        html.escape(section_name) +
        '</div>',
        unsafe_allow_html=True
    )

    if not movies:
        st.info("No movies available.")
        return

    columns = st.columns(6)

    for index, movie in enumerate(movies[:12]):

        with columns[index % 6]:

            title = movie.get("title") or "Untitled"

            release_date = movie.get("release_date") or ""
            year = release_date[:4]

            rating = movie.get("rating", 0)

            poster = movie.get("poster_url")
            movie_id = movie.get("id")

            # -------------------------
            # Clickable Poster
            # -------------------------

            if poster and movie_id:

                poster_html = f"""
                <a href="?movie_id={movie_id}" class="poster-link">
                    <img
                        src="{html.escape(poster, quote=True)}"
                        class="clickable-poster"
                    >
                </a>
                """

                st.markdown(
                    poster_html,
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
                    <div class="poster-fallback">
                        NO POSTER
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # -------------------------
            # Movie Title
            # -------------------------

            st.markdown(
                '<div class="movie-title">' +
                html.escape(title) +
                '</div>',
                unsafe_allow_html=True
            )

            # -------------------------
            # Movie Metadata
            # -------------------------

            metadata = []

            if year:
                metadata.append(year)

            try:
                metadata.append(
                    "★ " +
                    str(round(float(rating), 1))
                )
            except Exception:
                pass

            st.markdown(
                '<div class="movie-meta">' +
                " • ".join(metadata) +
                '</div>',
                unsafe_allow_html=True
            )


def render_home():

    # -------------------------
    # Detect clicked movie
    # -------------------------

    movie_id = st.query_params.get("movie_id")

    if movie_id:

        st.session_state.selected_movie_id = movie_id

        # Remove query parameter after storing the movie ID
        st.query_params.clear()

        st.rerun()

    # -------------------------
    # Hero
    # -------------------------

    st.markdown(
        """
        <div class="hero">

            <div class="hero-title">
                ReelRoute
            </div>

            <div class="hero-text">
                Every Movie. Every Platform. One Place.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    try:

        # -------------------------
        # Trending Movies
        # -------------------------

        trending = get_trending()

        show_movies(
            trending.get("results", []),
            "Trending Movies"
        )

        # -------------------------
        # Now Playing
        # -------------------------

        now_playing = get_now_playing()

        show_movies(
            now_playing.get("results", []),
            "Now Playing"
        )

        # -------------------------
        # Popular Movies
        # -------------------------

        popular = get_popular()

        show_movies(
            popular.get("results", []),
            "Popular Movies"
        )

    except TMDBError as error:

        st.error(str(error))
