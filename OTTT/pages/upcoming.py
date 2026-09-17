import streamlit as st

from services.tmdb_service import (
    TMDBError,
    get_upcoming
)


def render_upcoming():

    st.title("Upcoming Movies")

    st.write(
        "Movies that are scheduled to release soon."
    )

    try:

        data = get_upcoming()

        movies = data.get(
            "results",
            []
        )

    except TMDBError as error:

        st.error(str(error))
        return

    if not movies:

        st.info("No upcoming movies found.")
        return

    columns = st.columns(6)

    for index, movie in enumerate(movies[:20]):

        with columns[index % 6]:

            title = movie.get(
                "title",
                "Untitled"
            )

            release_date = movie.get(
                "release_date",
                ""
            )

            year = release_date[:4]

            rating = movie.get(
                "rating",
                0
            )

            poster = movie.get(
                "poster_url"
            )

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

            if st.button(
                "View Details",
                key="upcoming_" + str(movie.get("id")),
                use_container_width=True
            ):

                st.session_state.selected_movie_id = movie.get("id")

                st.rerun()
