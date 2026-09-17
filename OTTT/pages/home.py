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

    columns = st.columns(6, gap="medium")

    for index, movie in enumerate(movies[:12]):

        with columns[index % 6]:

            title = movie.get("title") or "Untitled"
            release_date = movie.get("release_date") or ""
            year = release_date[:4]

            rating = movie.get("rating", 0)
            poster = movie.get("poster_url")
            movie_id = movie.get("id")

            # -------------------------
            # Poster
            # -------------------------

            if poster:

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
            # Invisible movie button
            # -------------------------

            if movie_id:

                clicked = st.button(
                    "Open Movie",
                    key="movie_" + str(section_name) + "_" + str(movie_id),
                    use_container_width=True
                )

                if clicked:
                    st.session_state.selected_movie_id = str(movie_id)
                    st.rerun()

            # -------------------------
            # Movie title
            # -------------------------

            st.markdown(
                '<div class="movie-title">' +
                html.escape(title) +
                '</div>',
                unsafe_allow_html=True
            )

            # -------------------------
            # Movie metadata
            # -------------------------

            metadata = []

            if year:
                metadata.append(year)

            try:
                metadata.append(
                    "★ " + str(round(float(rating), 1))
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
        # Trending
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
        # Popular
        # -------------------------

        popular = get_popular()

        show_movies(
            popular.get("results", []),
            "Popular Movies"
        )

    except TMDBError as error:

        st.error(str(error))
