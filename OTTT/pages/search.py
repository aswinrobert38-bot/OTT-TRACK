import html
import streamlit as st

from services.tmdb_service import (
    TMDBError,
    search_movies,
    search_tv,
    search_multi,
)


# =========================================================
# HELPERS
# =========================================================

def get_results(data):

    if isinstance(data, dict):

        return data.get(
            "results",
            []
        )

    if isinstance(data, list):

        return data

    return []


def get_title(item):

    return (
        item.get("title")
        or item.get("name")
        or "Untitled"
    )


def get_poster(item):

    poster = item.get(
        "poster_url"
    )

    if poster:
        return poster

    poster_path = item.get(
        "poster_path"
    )

    if poster_path:

        return (
            "https://image.tmdb.org/t/p/w500"
            + poster_path
        )

    return None


def get_year(item):

    date = (
        item.get("release_date")
        or item.get("first_air_date")
        or ""
    )

    if date:

        return date[:4]

    return "N/A"


def get_rating(item):

    rating = item.get(
        "rating"
    )

    if rating is None:

        rating = item.get(
            "vote_average"
        )

    try:

        return str(
            round(
                float(rating),
                1
            )
        )

    except Exception:

        return "N/A"


# =========================================================
# CARD
# =========================================================

def content_card(item, index):

    content_id = item.get(
        "id"
    )

    content_type = item.get(
        "content_type",
        "movie"
    )

    title = get_title(
        item
    )

    poster = get_poster(
        item
    )

    year = get_year(
        item
    )

    rating = get_rating(
        item
    )

    language = (
        item.get(
            "original_language"
        )
        or "N/A"
    )

    # -----------------------------------------------------
    # POSTER
    # -----------------------------------------------------

    if poster:

        st.image(
            poster,
            use_container_width=True
        )

        button_text = (
            "View Series Details"
            if content_type == "tv"
            else "View Movie Details"
        )

        if st.button(
            button_text,
            key=(
                f"search_content_"
                f"{content_id}_"
                f"{index}"
            ),
            use_container_width=True
        ):

            st.session_state.open_content = {
                "id": content_id,
                "type": content_type
            }

            st.session_state.open_movie_id = None

            st.rerun()

    else:

        st.info(
            "Poster unavailable"
        )

    # -----------------------------------------------------
    # TITLE
    # -----------------------------------------------------

    st.markdown(
        f"""
        <div class="movie-card-title">
            {html.escape(str(title))}
        </div>
        """,
        unsafe_allow_html=True
    )

    # -----------------------------------------------------
    # META
    # -----------------------------------------------------

    label = (
        "Series"
        if content_type == "tv"
        else "Movie"
    )

    st.markdown(
        f"""
        <div class="movie-card-meta">

            {html.escape(label)}

            <span>•</span>

            {html.escape(str(year))}

            <span>•</span>

            {html.escape(
                str(language).upper()
            )}

            <span>•</span>

            ★ {html.escape(rating)}

        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# SEARCH PAGE
# =========================================================

def render_search():

    st.markdown(
        """
        <div class="search-page-header">

            <div class="hero-kicker">
                DISCOVER
            </div>

            <h1>
                Find your next movie or series
            </h1>

            <p>
                Search movies and web series from across
                languages and years.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    # =====================================================
    # CONTENT TYPE
    # =====================================================

    content_type = st.radio(
        "Content",
        [
            "All",
            "Movies",
            "Web Series"
        ],
        horizontal=True,
        key="search_page_content_type"
    )

    # =====================================================
    # QUERY
    # =====================================================

    query = st.text_input(
        "Title",
        placeholder=(
            "Search for a movie or web series..."
        ),
        key="search_page_query",
        label_visibility="collapsed"
    )

    if not query.strip():

        st.markdown(
            """
            <div class="search-empty">

                <div class="search-empty-title">
                    Search the movie & series catalogue
                </div>

                <div class="search-empty-text">
                    Try Leo, Interstellar, Jailer,
                    Vikram or any web series.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        return

    # =====================================================
    # SEARCH
    # =====================================================

    try:

        if content_type == "Movies":

            data = search_movies(
                query.strip()
            )

        elif content_type == "Web Series":

            data = search_tv(
                query.strip()
            )

        else:

            data = search_multi(
                query.strip()
            )

        results = get_results(
            data
        )

    except TMDBError as error:

        st.error(
            str(error)
        )

        return

    # =====================================================
    # RESULTS HEADER
    # =====================================================

    st.markdown(
        f"""
        <div class="search-result-heading">

            <div>

                <span>RESULTS FOR</span>

                <strong>
                    {html.escape(query.strip())}
                </strong>

            </div>

            <div>
                {len(results)} result(s)
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    if not results:

        st.warning(
            "No matching movies or web series were found."
        )

        return

    # =====================================================
    # RESULTS
    # =====================================================

    columns = st.columns(
        6,
        gap="medium"
    )

    for index, item in enumerate(
        results[:24]
    ):

        with columns[
            index % 6
        ]:

            content_card(
                item,
                index
            )
