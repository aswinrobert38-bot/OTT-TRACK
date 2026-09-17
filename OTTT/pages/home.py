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
        section_name +
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

            release_date = (
                movie.get("release_date") or ""
            )

            year = release_date[:4]

            rating = movie.get("rating", 0)

            poster = movie.get("poster_url")

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

            st.markdown(
                '<div class="movie-title">' +
                title +
                '</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                '<div class="movie-meta">' +
                year +
                " • ★ " +
                str(round(float(rating), 1)) +
                '</div>',
                unsafe_allow_html=True
            )

            if st.button(
                "View Details",
                key="home_" + str(movie.get("id")),
                use_container_width=True
            ):

                st.session_state.selected_movie_id = movie.get("id")

                st.rerun()


def render_home():

    st.markdown(
        """
        <div class="hero">
            <div class="hero-title">
                OTTTrack
            </div>

            <div class="hero-text">
                Every Movie. Every Platform. One Place.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    try:

        trending = get_trending()

        show_movies(
            trending.get("results", []),
            "Trending Movies"
        )

        now_playing = get_now_playing()

        show_movies(
            now_playing.get("results", []),
            "Now Playing"
        )

        popular = get_popular()

        show_movies(
            popular.get("results", []),
            "Popular Movies"
        )

    except TMDBError as error:

        st.error(str(error))
