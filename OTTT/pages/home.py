import streamlit as st

from services.tmdb_service import (
    TMDBError,
    get_now_playing,
    get_popular,
    get_trending,
    search_movies
)


# =========================================================
# EXTRACT MOVIE RESULTS SAFELY
# =========================================================

def get_movie_list(data):

    if isinstance(data, dict):

        results = data.get(
            "results",
            []
        )

        if isinstance(results, list):
            return results

        return []

    if isinstance(data, list):
        return data

    return []


# =========================================================
# PREPARE MOVIE DATA
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

    # -----------------------------------------
    # Poster URL
    # -----------------------------------------

    poster = movie.get(
        "poster_url"
    )

    if not poster:

        poster_path = movie.get(
            "poster_path"
        )

        if poster_path:

            poster = (
                "https://image.tmdb.org/t/p/w500"
                + poster_path
            )

    # -----------------------------------------
    # Rating
    # -----------------------------------------

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
        "poster_url": poster,
        "rating": rating
    }


# =========================================================
# MOVIE GRID
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

    # -----------------------------------------------------
    # Five movies per row
    # -----------------------------------------------------

    columns = st.columns(
        5,
        gap="medium"
    )

    for index, movie in enumerate(
        prepared_movies[:10]
    ):

        with columns[index % 5]:

            # =============================================
            # POSTER
            # =============================================

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

            # =============================================
            # TITLE
            # =============================================

            title = movie.get(
                "title",
                "Untitled"
            )

            st.markdown(
                f"**{title}**"
            )

            # =============================================
            # YEAR + RATING
            # =============================================

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

            # =============================================
            # OPEN MOVIE
            # =============================================

            movie_id = movie.get(
                "id"
            )

            if movie_id:

                # IMPORTANT:
                # Section name is included so the same movie
                # can appear in multiple sections without
                # creating duplicate Streamlit keys.

                safe_section = (
                    section_name
                    .replace(" ", "_")
                    .replace("/", "_")
                )

                button_key = (
                    f"open_movie_"
                    f"{safe_section}_"
                    f"{movie_id}_"
                    f"{index}"
                )

                if st.button(
                    "Open Movie",
                    key=button_key,
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

    # =====================================================
    # HERO
    # =====================================================

    st.title(
        "ReelRoute"
    )

    st.markdown(
        "### Every Movie. Every Platform. One Place."
    )

    st.caption(
        "Discover movies and find where to watch them."
    )

    st.divider()

    # =====================================================
    # SEARCH BAR
    # =====================================================

    st.markdown(
        "### Search Movies"
    )

    search_col, button_col = st.columns(
        [5, 1],
        gap="medium"
    )

    with search_col:

        query = st.text_input(
            "Movie Search",
            placeholder=(
                "Search for a movie..."
            ),
            label_visibility="collapsed",
            key="home_search"
        )

    with button_col:

        search_clicked = st.button(
            "Search",
            use_container_width=True,
            key="home_search_button"
        )

    # =====================================================
    # SEARCH RESULTS
    # =====================================================

    if search_clicked:

        if not query.strip():

            st.warning(
                "Enter a movie title."
            )

            return

        try:

            search_data = search_movies(
                query.strip()
            )

            results = get_movie_list(
                search_data
            )

            st.divider()

            st.markdown(
                "### Search Results"
            )

            st.caption(
                f"{len(results)} result(s) for "
                f'"{query.strip()}"'
            )

            if not results:

                st.warning(
                    "No movies found."
                )

                return

            show_movies(
                results,
                "Search Results"
            )

            return

        except TMDBError as error:

            st.error(
                "Search error"
            )

            st.code(
                str(error)
            )

            return

        except Exception as error:

            st.error(
                "Search could not be completed."
            )

            st.code(
                str(error)
            )

            return

    # =====================================================
    # TRENDING MOVIES
    # =====================================================

    try:

        trending_data = get_trending()

        trending_movies = get_movie_list(
            trending_data
        )

        show_movies(
            trending_movies,
            "Trending Movies"
        )

    except TMDBError as error:

        st.error(
            "Trending Movies error"
        )

        st.code(
            str(error)
        )

    except Exception as error:

        st.error(
            "Trending Movies could not be loaded."
        )

        st.code(
            str(error)
        )

    st.divider()

    # =====================================================
    # NOW PLAYING
    # =====================================================

    try:

        now_playing_data = get_now_playing()

        now_playing_movies = get_movie_list(
            now_playing_data
        )

        show_movies(
            now_playing_movies,
            "Now Playing"
        )

    except TMDBError as error:

        st.error(
            "Now Playing error"
        )

        st.code(
            str(error)
        )

    except Exception as error:

        st.error(
            "Now Playing could not be loaded."
        )

        st.code(
            str(error)
        )

    st.divider()

    # =====================================================
    # POPULAR MOVIES
    # =====================================================

    try:

        popular_data = get_popular()

        popular_movies = get_movie_list(
            popular_data
        )

        show_movies(
            popular_movies,
            "Popular Movies"
        )

    except TMDBError as error:

        st.error(
            "Popular Movies error"
        )

        st.code(
            str(error)
        )

    except Exception as error:

        st.error(
            "Popular Movies could not be loaded."
        )

        st.code(
            str(error)
        )
