import streamlit as st

from services.tmdb_service import (
    TMDBError,
    get_now_playing,
    get_popular,
    get_trending,
    search_movies
)


# =========================================================
# MOVIE DATA HELPER
# =========================================================

def prepare_movie(movie):

    if not isinstance(movie, dict):
        return None

    movie_id = movie.get("id")

    title = (
        movie.get("title")
        or movie.get("name")
        or "Untitled"
    )

    release_date = (
        movie.get("release_date")
        or movie.get("first_air_date")
        or ""
    )

    poster_url = movie.get("poster_url")

    if not poster_url:

        poster_path = movie.get(
            "poster_path"
        )

        if poster_path:

            poster_url = (
                "https://image.tmdb.org/t/p/w500"
                + poster_path
            )

    rating = movie.get(
        "rating"
    )

    if rating is None:

        rating = movie.get(
            "vote_average",
            0
        )

    return {
        "id": movie_id,
        "title": title,
        "release_date": release_date,
        "poster_url": poster_url,
        "rating": rating
    }


# =========================================================
# MOVIE CARD
# =========================================================

def show_movies(
    movies,
    section_name
):

    st.markdown(
        f"## {section_name}"
    )

    if not movies:

        st.info(
            "No movies available."
        )

        return

    prepared_movies = []

    for movie in movies:

        prepared = prepare_movie(
            movie
        )

        if prepared:
            prepared_movies.append(
                prepared
            )

    if not prepared_movies:

        st.info(
            "No movie data available."
        )

        return

    # Five cards per row
    columns = st.columns(
        5,
        gap="medium"
    )

    for index, movie in enumerate(
        prepared_movies[:10]
    ):

        with columns[index % 5]:

            # =================================================
            # POSTER
            # =================================================

            poster = movie.get(
                "poster_url"
            )

            if poster:

                st.image(
                    poster,
                    use_container_width=True
                )

            else:

                st.info(
                    "No poster"
                )

            # =================================================
            # TITLE
            # =================================================

            title = movie.get(
                "title",
                "Untitled"
            )

            st.markdown(
                f"**{title}**"
            )

            # =================================================
            # YEAR
            # =================================================

            release_date = movie.get(
                "release_date",
                ""
            )

            year = release_date[:4]

            rating = movie.get(
                "rating",
                0
            )

            try:

                rating_text = (
                    "★ "
                    + str(
                        round(
                            float(rating),
                            1
                        )
                    )
                )

            except Exception:

                rating_text = "★ N/A"

            if year:

                st.caption(
                    f"{year} • {rating_text}"
                )

            else:

                st.caption(
                    rating_text
                )

            # =================================================
            # OPEN MOVIE
            # =================================================

            movie_id = movie.get(
                "id"
            )

            if movie_id:

                if st.button(
                    "Open Movie",
                    key=f"open_{movie_id}_{index}",
                    use_container_width=True
                ):

                    st.session_state.selected_movie_id = (
                        movie_id
                    )

                    st.rerun()


# =========================================================
# HOME PAGE
# =========================================================

def render_home():

    # =========================================================
    # HERO
    # =========================================================

    st.title(
        "ReelRoute"
    )

    st.subheader(
        "Every Movie. Every Platform. One Place."
    )

    st.caption(
        "Discover movies, explore details, and find where to watch."
    )

    st.divider()

    # =========================================================
    # SEARCH
    # =========================================================

    st.markdown(
        "### Search Movies"
    )

    with st.form(
        "home_search_form"
    ):

        search_col, button_col = st.columns(
            [5, 1],
            gap="medium"
        )

        with search_col:

            query = st.text_input(
                "Movie",
                placeholder=(
                    "Search for a movie..."
                ),
                label_visibility="collapsed"
            )

        with button_col:

            search_clicked = st.form_submit_button(
                "Search",
                use_container_width=True
            )

    # =========================================================
    # SEARCH RESULTS
    # =========================================================

    if search_clicked:

        if not query.strip():

            st.warning(
                "Enter a movie title to search."
            )

            return

        try:

            raw_results = search_movies(
                query.strip()
            )

            # Make sure the result is iterable
            if isinstance(
                raw_results,
                dict
            ):

                results = raw_results.get(
                    "results",
                    []
                )

            elif isinstance(
                raw_results,
                list
            ):

                results = raw_results

            else:

                results = []

            valid_results = []

            for item in results:

                prepared = prepare_movie(
                    item
                )

                if prepared:

                    valid_results.append(
                        prepared
                    )

            st.divider()

            st.markdown(
                f"### Search Results"
            )

            st.caption(
                f"{len(valid_results)} result(s) for "
                f'"{query.strip()}"'
            )

            if not valid_results:

                st.warning(
                    "TMDB returned no matching movies."
                )

                return

            show_movies(
                valid_results,
                "Movies"
            )

            return

        except TMDBError as error:

            st.error(
                str(error)
            )

            return

        except Exception as error:

            st.error(
                "Search failed. Please try again."
            )

            st.caption(
                str(error)
            )

            return

    # =========================================================
    # DEFAULT HOME CONTENT
    # =========================================================

    try:

        # -----------------------------------------------------
        # TRENDING
        # -----------------------------------------------------

        trending = get_trending()

        show_movies(
            trending.get(
                "results",
                []
            ),
            "Trending Movies"
        )

        st.divider()

        # -----------------------------------------------------
        # NOW PLAYING
        # -----------------------------------------------------

        now_playing = get_now_playing()

        show_movies(
            now_playing.get(
                "results",
                []
            ),
            "Now Playing"
        )

        st.divider()

        # -----------------------------------------------------
        # POPULAR
        # -----------------------------------------------------

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

    except Exception as error:

        st.error(
            "Unable to load movies."
        )

        st.caption(
            str(error)
        )
