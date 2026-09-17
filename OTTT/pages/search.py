import html
import streamlit as st

from services.tmdb_service import (
    TMDBError,
    normalize_movie,
    search_movies
)


def render_search():

    st.markdown(
        """
        <div class="page-head">

            <div class="hero-kicker">
                DISCOVER
            </div>

            <h1>Search Results</h1>

            <p>
                Search movies from TMDB and explore where they are available.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    # -------------------------
    # Filters
    # -------------------------

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

    # -------------------------
    # Get search text
    # -------------------------

    query = st.session_state.get(
        "global_search",
        ""
    )

    if not query.strip():

        st.markdown(
            """
            <div class="empty-state">

                <h3>
                    Search for a movie
                </h3>

                <p>
                    Use the search bar above to find movies.
                </p>

            </div>
            """,
            unsafe_allow_html=True
        )

        return

    # -------------------------
    # Search TMDB
    # -------------------------

    try:

        results = search_movies(
            query.strip(),
            year=year if year else None,
            language=language.strip().lower() or None
        )

    except TMDBError as exc:

        st.error(str(exc))
        return

    movies = [
        normalize_movie(movie)
        for movie in results
    ]

    st.markdown(
        '<div class="result-line"><b>' +
        str(len(movies)) +
        '</b> result(s)</div>',
        unsafe_allow_html=True
    )

    if not movies:

        st.warning(
            "TMDB returned no matching movie."
        )

        return

    # -------------------------
    # Movie grid
    # -------------------------

    cols = st.columns(
        6,
        gap="medium"
    )

    for index, movie in enumerate(movies):

        with cols[index % 6]:

            title = movie.get(
                "title",
                "Untitled"
            )

            poster = movie.get(
                "poster_url"
            )

            movie_id = movie.get(
                "id"
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

            # -------------------------
            # Click movie
            # -------------------------

            if movie_id:

                if st.button(
                    "Open Movie",
                    key="search_movie_" + str(movie_id),
                    use_container_width=True
                ):

                    st.session_state.selected_movie_id = str(
                        movie_id
                    )

                    st.rerun()

            # -------------------------
            # Title
            # -------------------------

            st.markdown(
                '<div class="movie-title">' +
                html.escape(title) +
                '</div>',
                unsafe_allow_html=True
            )
