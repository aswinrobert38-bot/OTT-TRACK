import html
import streamlit as st

from services.tmdb_service import (
    TMDBError,

    get_now_playing,
    get_popular,
    get_trending,
    get_upcoming,

    get_popular_tv,
    get_trending_tv,
    get_airing_today_tv,

    search_movies,
    search_multi,
    search_tv,
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

    release_date = (
        item.get("release_date")
        or item.get("first_air_date")
        or ""
    )

    if release_date:

        return release_date[:4]

    return "N/A"


def get_rating(item):

    rating = item.get(
        "rating"
    )

    if rating is None:

        rating = item.get(
            "vote_average"
        )

    if rating is None:

        return "N/A"

    try:

        return str(
            round(
                float(rating),
                1
            )
        )

    except Exception:

        return "N/A"


def get_language(item):

    language = (
        item.get("original_language")
        or item.get("language")
    )

    if not language:

        return "N/A"

    return str(
        language
    ).upper()


# =========================================================
# CONTENT CARD
# =========================================================

def content_card(
    item,
    key_suffix=""
):

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

    language = get_language(
        item
    )

    # -----------------------------------------------------
    # POSTER
    # -----------------------------------------------------

    if poster and content_id:

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
                f"home_content_"
                f"{content_id}_"
                f"{key_suffix}"
            ),
            use_container_width=True
        ):

            st.session_state.open_content = {
                "id": content_id,
                "type": content_type
            }

            st.session_state.open_movie_id = None

            st.rerun()

    elif poster:

        st.image(
            poster,
            use_container_width=True
        )

    else:

        st.info(
            "Poster unavailable"
        )

    # -----------------------------------------------------
    # TITLE
    # -----------------------------------------------------

    st.markdown(
        f"**{html.escape(str(title))}**"
    )

    # -----------------------------------------------------
    # META
    # -----------------------------------------------------

    content_label = (
        "Series"
        if content_type == "tv"
        else "Movie"
    )

    st.caption(
        f"{content_label}  •  "
        f"{year}  •  "
        f"{language}  •  "
        f"★ {rating}"
    )


# =========================================================
# CONTENT SECTION
# =========================================================

def show_content(
    title,
    description,
    items,
    limit=6
):

    if not items:

        st.info(
            f"No titles available for {title}."
        )

        return

    st.subheader(
        title
    )

    st.caption(
        description
    )

    columns = st.columns(
        6,
        gap="medium"
    )

    for index, item in enumerate(
        items[:limit]
    ):

        with columns[
            index % 6
        ]:

            content_card(
                item,
                key_suffix=(
                    f"{title.replace(' ', '_')}"
                    f"_{index}"
                )
            )


# =========================================================
# SEARCH RESULTS
# =========================================================

def show_search_results(
    query,
    results
):

    st.divider()

    st.subheader(
        "Search Results"
    )

    st.caption(
        f'{len(results)} result(s) for "{query}"'
    )

    if not results:

        st.info(
            "No movies or web series found."
        )

        return

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
                key_suffix=f"search_{index}"
            )


# =========================================================
# SEARCH
# =========================================================

def search_area():

    st.markdown(
        """
        <div class="search-heading">
            Search Movies & Series
        </div>
        """,
        unsafe_allow_html=True
    )

    st.caption(
        "Search movies and web series and explore "
        "their details and India OTT availability."
    )

    content_type = st.radio(
        "Content",
        [
            "All",
            "Movies",
            "Web Series"
        ],
        horizontal=True,
        key="home_content_type"
    )

    with st.form(
        "movie_search_form",
        clear_on_submit=False
    ):

        col1, col2 = st.columns(
            [5, 1],
            gap="small"
        )

        with col1:

            query = st.text_input(
                "Title",
                placeholder=(
                    "Search any movie or web series..."
                ),
                label_visibility="collapsed",
                key="movie_search_query"
            )

        with col2:

            search_clicked = st.form_submit_button(
                "Search",
                use_container_width=True
            )

    if search_clicked:

        if not query.strip():

            st.warning(
                "Please enter a title."
            )

            return

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

            st.session_state.search_query = (
                query.strip()
            )

            st.session_state.search_results = (
                get_results(data)
            )

        except TMDBError:

            st.error(
                "Unable to search right now. "
                "Please check your TMDB connection."
            )

            return

        except Exception as error:

            st.error(
                f"Search failed: {error}"
            )

            return

    saved_results = st.session_state.get(
        "search_results",
        []
    )

    saved_query = st.session_state.get(
        "search_query",
        ""
    )

    if saved_query:

        show_search_results(
            saved_query,
            saved_results
        )


# =========================================================
# LANGUAGES
# =========================================================

def show_available_languages():

    st.divider()

    st.subheader(
        "Available Languages"
    )

    st.caption(
        "Browse the catalogue by language."
    )

    languages = [
        "Tamil",
        "Telugu",
        "Malayalam",
        "Kannada",
        "Hindi",
        "English",
        "Bengali",
        "Marathi",
        "Punjabi",
        "Gujarati",
        "Bhojpuri",
        "Odia",
    ]

    columns = st.columns(
        4,
        gap="small"
    )

    for index, language in enumerate(
        languages
    ):

        with columns[
            index % 4
        ]:

            st.markdown(
                f"""
                <div class="language-card">
                    {html.escape(language)}
                </div>
                """,
                unsafe_allow_html=True
            )


# =========================================================
# HOME
# =========================================================

def render_home():

    # =====================================================
    # HERO
    # =====================================================

    st.markdown(
        """
        <div class="hero-title">
            ReelRoute
        </div>

        <div class="hero-text">
            Every Movie & Series.
            Every Platform. One Place.
        </div>
        """,
        unsafe_allow_html=True
    )

    # =====================================================
    # SEARCH
    # =====================================================

    search_area()

    # =====================================================
    # MOVIES
    # =====================================================

    st.markdown("## Movies")

    # -----------------------------------------------------
    # TRENDING MOVIES
    # -----------------------------------------------------

    try:

        trending_movies = get_results(
            get_trending()
        )

        show_content(
            "Trending Movies",
            "Movies people are discovering right now.",
            trending_movies,
            6
        )

    except TMDBError:

        st.warning(
            "Trending movies could not be loaded."
        )

    # -----------------------------------------------------
    # RECENT MOVIES
    # -----------------------------------------------------

    try:

        recent_movies = get_results(
            get_now_playing()
        )

        show_content(
            "Recently Released Movies",
            "Movies currently listed in theatrical releases.",
            recent_movies,
            6
        )

    except TMDBError:

        st.warning(
            "Recently released movies could not be loaded."
        )

    # -----------------------------------------------------
    # POPULAR MOVIES
    # -----------------------------------------------------

    try:

        popular_movies = get_results(
            get_popular()
        )

        show_content(
            "Popular Movies",
            "Popular movie titles from TMDB.",
            popular_movies,
            6
        )

    except TMDBError:

        st.warning(
            "Popular movies could not be loaded."
        )

    # =====================================================
    # WEB SERIES
    # =====================================================

    st.divider()

    st.markdown("## Web Series")

    # -----------------------------------------------------
    # TRENDING SERIES
    # -----------------------------------------------------

    try:

        trending_series = get_results(
            get_trending_tv()
        )

        show_content(
            "Trending Web Series",
            "Web series people are discovering right now.",
            trending_series,
            6
        )

    except TMDBError:

        st.warning(
            "Trending web series could not be loaded."
        )

    # -----------------------------------------------------
    # POPULAR SERIES
    # -----------------------------------------------------

    try:

        popular_series = get_results(
            get_popular_tv()
        )

        show_content(
            "Popular Web Series",
            "Popular TV and web series from TMDB.",
            popular_series,
            6
        )

    except TMDBError:

        st.warning(
            "Popular web series could not be loaded."
        )

    # -----------------------------------------------------
    # AIRING TODAY
    # -----------------------------------------------------

    try:

        airing_series = get_results(
            get_airing_today_tv()
        )

        show_content(
            "Airing Today",
            "Series currently airing today.",
            airing_series,
            6
        )

    except TMDBError:

        st.warning(
            "Airing web series could not be loaded."
        )

    # =====================================================
    # UPCOMING MOVIES
    # =====================================================

    st.divider()

    try:

        upcoming = get_results(
            get_upcoming()
        )

        show_content(
            "Coming Soon",
            "Upcoming movies listed by TMDB.",
            upcoming,
            6
        )

    except TMDBError:

        st.warning(
            "Upcoming movies could not be loaded."
        )

    # =====================================================
    # LANGUAGES
    # =====================================================

    show_available_languages()

    # =====================================================
    # OTT
    # =====================================================

    st.divider()

    st.subheader(
        "OTT Availability"
    )

    st.caption(
        "Movie and web-series availability varies by "
        "country and platform."
    )

    st.info(
        "Open any movie or series to view its available "
        "streaming, rental, and purchase platforms in India."
    )
