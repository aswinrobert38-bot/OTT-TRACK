import html
import streamlit as st

from streamlit_image_coordinates import streamlit_image_coordinates

from services.tmdb_service import (
    TMDBError,
    normalize_movie,
    search_movies
)


def open_movie(movie_id):

    if not movie_id:
        return

    st.session_state.selected_movie_id = str(movie_id)

    st.session_state.page = "search"

    st.rerun()


def render_search():

    # =========================================================
    # SEARCH HEADER
    # =========================================================

    query = st.session_state.get(
        "global_search",
        ""
    ).strip()


    st.markdown(
        """
        <div class="page-head">

            <div class="hero-kicker">
                DISCOVER
            </div>

            <h1>Search movies</h1>

            <p>
                Search movies from TMDB and explore
                where they are available.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )


    # =========================================================
    # FILTERS
    # =========================================================

    c1, c2 = st.columns([1, 1])


    with c1:

        year = st.number_input(
            "Year",
            min_value=1900,
            max_value=2100,
            value=2026,
            step=1,
            key="search_year"
        )


    with c2:

        language = st.text_input(
            "Language code",
            placeholder="ta / en / hi",
            key="search_language"
        )


    # =========================================================
    # QUERY CHECK
    # =========================================================

    if not query:

        st.markdown(
            """
            <div class="empty-state">

                <h3>
                    Start with a movie title
                </h3>

                <p>
                    Use the search bar above to find
                    movies.
                </p>

            </div>
            """,
            unsafe_allow_html=True
        )

        return


    # =========================================================
    # SEARCH TMDB
    # =========================================================

    try:

        results = search_movies(
            query,
            year=year if year else None,
            language=language.strip().lower()
            if language.strip()
            else None
        )

    except TMDBError as exc:

        st.error(str(exc))

        return


    # =========================================================
    # NORMALIZE
    # =========================================================

    movies = [
        normalize_movie(movie)
        for movie in results
    ]


    st.markdown(
        '<div class="result-line">'
        '<b>' +
        str(len(movies)) +
        '</b> result(s) for <b>' +
        html.escape(query) +
        '</b>'
        '</div>',
        unsafe_allow_html=True
    )


    if not movies:

        st.warning(
            "TMDB returned no matching movie."
        )

        return


    # =========================================================
    # MOVIE GRID
    # =========================================================

    columns = st.columns(6, gap="medium")


    for index, movie in enumerate(movies[:24]):

        with columns[index % 6]:

            title = (
                movie.get("title")
                or "Untitled"
            )


            release_date = (
                movie.get("release_date")
                or ""
            )


            year_text = release_date[:4]


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


            # =================================================
            # POSTER
            # =================================================

            if poster and movie_id:

                click_key = (
                    "search_poster_"
                    + str(
                        st.session_state.poster_version
                    )
                    + "_"
                    + str(movie_id)
                    + "_"
                    + str(index)
                )


                clicked = streamlit_image_coordinates(
                    poster,
                    key=click_key
                )


                if clicked is not None:

                    open_movie(movie_id)


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


            # =================================================
            # TITLE
            # =================================================

            st.markdown(
                '<div class="movie-title">' +
                html.escape(title) +
                '</div>',
                unsafe_allow_html=True
            )


            # =================================================
            # META
            # =================================================

            metadata = []


            if year_text:

                metadata.append(
                    year_text
                )


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


            st.markdown(
                '<div class="movie-meta">' +
                " • ".join(metadata) +
                '</div>',
                unsafe_allow_html=True
            )
