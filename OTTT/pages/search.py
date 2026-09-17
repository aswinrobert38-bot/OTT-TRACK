import html
import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates

from services.tmdb_service import (
    TMDBError,
    normalize_movie,
    search_movies
)


def render_search():

    # =========================================================
    # SEARCH HEADER
    # =========================================================

    st.markdown(
        """
        <div class="page-head">

            <div class="hero-kicker">
                DISCOVER
            </div>

            <h1>
                Search movies
            </h1>

            <p>
                Search TMDB instead of a fixed demo list.
                Year and original-language filters are sent to the API.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    # =========================================================
    # SEARCH CONTROLS
    # =========================================================

    c1, c2, c3 = st.columns([2.5, 1, 1])

    with c1:

        query = st.text_input(
            "Movie title",
            placeholder="Enter a movie title...",
            key="search_query"
        )

    with c2:

        year = st.number_input(
            "Year",
            min_value=1900,
            max_value=2100,
            value=2026,
            step=1,
            key="search_year"
        )

    with c3:

        language = st.text_input(
            "Language code",
            placeholder="ta / en / hi",
            key="search_language"
        )

    # =========================================================
    # EMPTY SEARCH
    # =========================================================

    if not query.strip():

        st.markdown(
            """
            <div class="empty-state">

                <h3>
                    Start with a movie title
                </h3>

                <p>
                    Try <b>Leo</b>,
                    <b>Interstellar</b>,
                    <b>Jailer</b>
                    or any other title.
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

    # =========================================================
    # RESULT COUNT
    # =========================================================

    st.markdown(
        f"""
        <div class="result-line">
            <b>{len(movies)}</b> result(s)
        </div>
        """,
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

    cols = st.columns(6, gap="medium")

    for i, movie in enumerate(movies):

        with cols[i % 6]:

            title = movie.get("title") or "Untitled"
            poster = movie.get("poster_url")
            movie_id = movie.get("id")

            release_date = (
                movie.get("release_date")
                or ""
            )

            year_text = release_date[:4]

            rating = movie.get("rating", 0)

            # =================================================
            # CLICKABLE POSTER
            # =================================================

            if poster and movie_id:

                clicked = streamlit_image_coordinates(
                    poster,
                    width=220,
                    key="search_poster_" + str(movie_id)
                )

                if clicked:

                    st.session_state.selected_movie_id = str(
                        movie_id
                    )

                    st.session_state.page = "search"

                    st.rerun()

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
                metadata.append(year_text)

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
