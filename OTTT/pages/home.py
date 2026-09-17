import html
import streamlit as st

from services.tmdb_service import (
    TMDBError,
    get_now_playing,
    get_popular,
    get_trending,
    get_upcoming,
    search_movies,
)


def get_results(data):

    if isinstance(data, dict):
        return data.get("results", [])

    if isinstance(data, list):
        return data

    return []


def get_movie_title(movie):

    return (
        movie.get("title")
        or movie.get("name")
        or "Untitled"
    )


def get_movie_poster(movie):

    poster = movie.get("poster_url")

    if poster:
        return poster

    poster_path = movie.get("poster_path")

    if poster_path:
        return (
            "https://image.tmdb.org/t/p/w500"
            + poster_path
        )

    return None


def get_movie_year(movie):

    release_date = movie.get("release_date") or ""

    if release_date:
        return release_date[:4]

    return "N/A"


def get_movie_rating(movie):

    rating = movie.get("rating")

    if rating is None:
        rating = movie.get("vote_average")

    if rating is None:
        return "N/A"

    try:
        return str(round(float(rating), 1))
    except Exception:
        return "N/A"


def get_movie_language(movie):

    language = (
        movie.get("original_language")
        or movie.get("language")
    )

    if not language:
        return "N/A"

    return str(language).upper()


def movie_card(movie):

    movie_id = movie.get("id")

    title = get_movie_title(movie)
    poster = get_movie_poster(movie)
    year = get_movie_year(movie)
    rating = get_movie_rating(movie)
    language = get_movie_language(movie)

    # -----------------------------------------
    # CLICKABLE POSTER
    # -----------------------------------------

    if poster and movie_id:

        safe_title = html.escape(
            title,
            quote=True
        )

        # Native Streamlit Markdown image link.
        # This avoids raw HTML appearing on screen.
        poster_markdown = (
            f'[![{safe_title}]'
            f'({poster})]'
            f'(?movie_id={movie_id})'
        )

        st.markdown(
            poster_markdown
        )

    elif poster:

        st.image(
            poster,
            use_container_width=True
        )

    else:

        st.markdown(
            """
            <div class="poster-placeholder">
                NO POSTER
            </div>
            """,
            unsafe_allow_html=True
        )

    # -----------------------------------------
    # TITLE
    # -----------------------------------------

    st.markdown(
        f"""
        <div class="movie-card-title">
            {html.escape(title)}
        </div>
        """,
        unsafe_allow_html=True
    )

    # -----------------------------------------
    # META
    # -----------------------------------------

    st.markdown(
        f"""
        <div class="movie-card-meta">
            {html.escape(year)}
            <span>•</span>
            {html.escape(language)}
            <span>•</span>
            ★ {html.escape(rating)}
        </div>
        """,
        unsafe_allow_html=True
    )


def show_movies(
    title,
    subtitle,
    movies,
    limit=6
):

    if not movies:
        return

    st.markdown(
        f"""
        <div class="section-heading">

            <div>
                <h2>{html.escape(title)}</h2>

                <p>
                    {html.escape(subtitle)}
                </p>
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    columns = st.columns(
        6,
        gap="medium"
    )

    for index, movie in enumerate(
        movies[:limit]
    ):

        with columns[index % 6]:

            movie_card(movie)


def render_home():

    # =========================================
    # MOVIE SELECTION
    # =========================================

    movie_id = st.query_params.get(
        "movie_id"
    )

    if movie_id:

        st.session_state.selected_movie_id = str(
            movie_id
        )

        st.query_params.clear()

        st.rerun()

    # =========================================
    # HERO
    # =========================================

    st.markdown(
        """
        <div class="home-hero">

            <div class="hero-kicker">
                INDIA · MOVIES · OTT
            </div>

            <div class="hero-title">
                ReelRoute
            </div>

            <div class="hero-text">
                Every Movie. Every Platform. One Place.
            </div>

            <div class="hero-description">
                Discover movies, explore complete details,
                and find where they are available to watch
                in India.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    # =========================================
    # MAIN SEARCH
    # =========================================

    search_query = st.text_input(
        "Search movies",
        placeholder=(
            "Search any movie — "
            "Leo, Interstellar, Jailer..."
        ),
        key="home_search",
        label_visibility="collapsed"
    )

    # =========================================
    # SEARCH RESULTS
    # =========================================

    if search_query.strip():

        try:

            data = search_movies(
                search_query.strip()
            )

            movies = get_results(data)

        except TMDBError as error:

            st.error(str(error))
            return

        st.markdown(
            f"""
            <div class="search-result-heading">

                <div>
                    <span>SEARCH RESULTS FOR</span>
                    <strong>
                        {html.escape(
                            search_query.strip()
                        )}
                    </strong>
                </div>

                <div>
                    {len(movies)} movie(s)
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        if not movies:

            st.info(
                "No movies found. Try another title."
            )

            return

        columns = st.columns(
            6,
            gap="medium"
        )

        for index, movie in enumerate(
            movies[:18]
        ):

            with columns[index % 6]:

                movie_card(movie)

        return

    # =========================================
    # TRENDING
    # =========================================

    try:

        trending = get_results(
            get_trending()
        )

        show_movies(
            "Trending Now",
            "Movies people are discovering right now",
            trending,
            6
        )

    except TMDBError as error:

        st.error(
            "Trending movies could not be loaded."
        )

    # =========================================
    # RECENTLY RELEASED
    # =========================================

    try:

        recent = get_results(
            get_now_playing()
        )

        show_movies(
            "Recently Released",
            "Movies currently listed in theatrical releases",
            recent,
            6
        )

    except TMDBError as error:

        st.error(
            "Recently released movies could not be loaded."
        )

    # =========================================
    # POPULAR
    # =========================================

    try:

        popular = get_results(
            get_popular()
        )

        show_movies(
            "Popular Movies",
            "Popular titles from TMDB",
            popular,
            6
        )

    except TMDBError as error:

        st.error(
            "Popular movies could not be loaded."
        )

    # =========================================
    # UPCOMING
    # =========================================

    try:

        upcoming = get_results(
            get_upcoming()
        )

        show_movies(
            "Coming Soon",
            "Upcoming movies listed by TMDB",
            upcoming,
            6
        )

    except TMDBError as error:

        st.error(
            "Upcoming movies could not be loaded."
        )

    # =========================================
    # BROWSE BY LANGUAGE
    # =========================================

    st.markdown(
        """
        <div class="browse-section">

            <div class="section-heading">

                <div>
                    <h2>Browse by Language</h2>

                    <p>
                        Explore movies across different languages
                    </p>
                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True
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
    ]

    language_columns = st.columns(
        4,
        gap="medium"
    )

    for index, language in enumerate(
        languages
    ):

        with language_columns[index % 4]:

            st.markdown(
                f"""
                <div class="browse-card">
                    {html.escape(language)}
                </div>
                """,
                unsafe_allow_html=True
            )

    # =========================================
    # BROWSE BY PLATFORM
    # =========================================

    st.markdown(
        """
        <div class="browse-section">

            <div class="section-heading">

                <div>
                    <h2>Browse by Platform</h2>

                    <p>
                        Explore movies across popular OTT platforms
                    </p>
                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    platforms = [
        "Netflix",
        "Prime Video",
        "JioHotstar",
        "SonyLIV",
        "ZEE5",
        "Sun NXT",
        "Aha",
        "Apple TV+",
    ]

    platform_columns = st.columns(
        4,
        gap="medium"
    )

    for index, platform in enumerate(
        platforms
    ):

        with platform_columns[index % 4]:

            st.markdown(
                f"""
                <div class="browse-card platform-card">
                    {html.escape(platform)}
                </div>
                """,
                unsafe_allow_html=True
            )
