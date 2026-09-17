import streamlit as st

from services.tmdb_service import (
    TMDBError,
    get_now_playing,
    get_popular,
    get_trending
)


def show_movies(movies, section_name):

    st.markdown(
        "## " + section_name
    )

    if not movies:
        st.info("No movies available.")
        return

    columns = st.columns(6)

    for index, movie in enumerate(movies[:12]):

        with columns[index % 6]:

            title = movie.get("title") or "Untitled"

            release_date = (
                movie.get("release_date")
                or ""
            )

            year = release_date[:4]

            rating = movie.get(
                "rating",
                0
            )

            poster = movie.get(
                "poster_url"
            )

            movie_id = movie.get(
                "id"
            )

            # -------------------------
            # Movie Poster
            # -------------------------

            if poster:

                st.image(
                    poster,
                    use_container_width=True
                )

            else:

                st.markdown(
                    "### No Poster"
                )

            # -------------------------
            # Movie Title
            # -------------------------

            st.markdown(
                "**" + title + "**"
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
                    str(
                        round(
                            float(rating),
                            1
                        )
                    )
                )

            except Exception:
                pass

            if metadata:

                st.caption(
                    " • ".join(metadata)
                )

            # -------------------------
            # Open Movie
            # -------------------------

            if movie_id:

                if st.button(
                    "Open Movie",
                    key=f"movie_{movie_id}_{index}",
                    use_container_width=True
                ):

                    st.session_state.selected_movie_id = movie_id

                    st.rerun()


def render_home():

    # -------------------------
    # Hero
    # -------------------------

    st.markdown(
        "# ReelRoute"
    )

    st.markdown(
        "### Every Movie. Every Platform. One Place."
    )

    st.divider()

    try:

        # -------------------------
        # Trending Movies
        # -------------------------

        trending = get_trending()

        show_movies(
            trending.get(
                "results",
                []
            ),
            "Trending Movies"
        )

        # -------------------------
        # Now Playing
        # -------------------------

        now_playing = get_now_playing()

        show_movies(
            now_playing.get(
                "results",
                []
            ),
            "Now Playing"
        )

        # -------------------------
        # Popular Movies
        # -------------------------

        popular = get_popular()

        show_movies(
            popular.get(
                "results",
                []
            ),
            "Popular Movies"
        )

    except TMDBError as error:

        st.error(
            str(error)
        )
