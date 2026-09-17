import streamlit as st

from services.tmdb_service import (
    TMDBError,
    get_now_playing,
    get_popular,
    get_trending,
    normalize_movie,
    search_movies
)


def show_movies(movies, section_name):

    st.markdown(
        f"""
        <h2 style="
            margin-top: 30px;
            margin-bottom: 20px;
            color: white;
            font-size: 26px;
        ">
            {section_name}
        </h2>
        """,
        unsafe_allow_html=True
    )

    if not movies:
        st.info("No movies available.")
        return

    # 5 columns instead of 6
    columns = st.columns(
        5,
        gap="medium"
    )

    for index, movie in enumerate(movies[:10]):

        with columns[index % 5]:

            title = movie.get(
                "title"
            ) or "Untitled"

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

            # =========================
            # POSTER
            # =========================

            if poster:

                st.image(
                    poster,
                    use_container_width=True
                )

            else:

                st.markdown(
                    """
                    <div style="
                        height: 300px;
                        border-radius: 12px;
                        background: #15161d;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        color: #777;
                        font-size: 13px;
                        margin-bottom: 10px;
                    ">
                        NO POSTER
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # =========================
            # TITLE
            # =========================

            st.markdown(
                f"""
                <div style="
                    min-height: 48px;
                    margin-top: 8px;
                    color: white;
                    font-size: 15px;
                    font-weight: 700;
                    line-height: 1.4;
                ">
                    {title}
                </div>
                """,
                unsafe_allow_html=True
            )

            # =========================
            # YEAR + RATING
            # =========================

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

                st.markdown(
                    f"""
                    <div style="
                        color: #9b9daa;
                        font-size: 13px;
                        margin-top: 5px;
                        margin-bottom: 12px;
                    ">
                        {" • ".join(metadata)}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # =========================
            # OPEN MOVIE
            # =========================

            if movie_id:

                if st.button(
                    "Open Movie",
                    key=f"home_movie_{movie_id}_{index}",
                    use_container_width=True
                ):

                    st.session_state.selected_movie_id = movie_id

                    st.rerun()


def render_home():

    # =========================================================
    # HERO
    # =========================================================

    st.markdown(
        """
        <div style="
            padding: 38px 42px;
            border-radius: 22px;
            background:
                linear-gradient(
                    120deg,
                    rgba(124,58,237,0.28),
                    rgba(236,72,153,0.18),
                    rgba(15,23,42,0.92)
                );
            border: 1px solid rgba(255,255,255,0.10);
            margin-bottom: 25px;
        ">

            <div style="
                font-size: 46px;
                font-weight: 900;
                color: white;
                letter-spacing: -1px;
            ">
                ReelRoute
            </div>

            <div style="
                margin-top: 8px;
                color: #b5b8c5;
                font-size: 17px;
            ">
                Every Movie. Every Platform. One Place.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    # =========================================================
    # SEARCH BAR
    # =========================================================

    st.markdown(
        """
        <div style="
            font-size: 22px;
            font-weight: 700;
            color: white;
            margin-bottom: 10px;
        ">
            Search Movies
        </div>
        """,
        unsafe_allow_html=True
    )

    search_col, button_col = st.columns(
        [5, 1],
        gap="medium"
    )

    with search_col:

        query = st.text_input(
            "Search",
            placeholder="Search for a movie...",
            label_visibility="collapsed",
            key="home_search"
        )

    with button_col:

        search_clicked = st.button(
            "Search",
            use_container_width=True,
            key="home_search_button"
        )

    # =========================================================
    # SEARCH RESULTS
    # =========================================================

    if search_clicked and query.strip():

        try:

            results = search_movies(
                query.strip()
            )

            movies = [
                normalize_movie(item)
                for item in results
            ]

            st.divider()

            show_movies(
                movies,
                "Search Results"
            )

            return

        except TMDBError as error:

            st.error(
                str(error)
            )

            return

    # =========================================================
    # DEFAULT HOME CONTENT
    # =========================================================

    try:

        # -------------------------
        # Trending
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
        # Popular
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
