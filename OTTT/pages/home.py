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


def movie_card(movie, key_prefix):
    movie_id = movie.get("id")
    title = movie.get("title") or movie.get("name") or "Untitled"

    release_date = movie.get("release_date") or ""
    year = release_date[:4] if release_date else "N/A"

    rating = movie.get("rating")

    if rating is None:
        rating = movie.get("vote_average", 0)

    try:
        rating_text = str(round(float(rating), 1))
    except Exception:
        rating_text = "N/A"

    language = (
        movie.get("original_language")
        or movie.get("language")
        or "N/A"
    )

    poster = movie.get("poster_url")

    if not poster:
        poster_path = movie.get("poster_path")

        if poster_path:
            poster = (
                "https://image.tmdb.org/t/p/w500"
                + poster_path
            )

    # -----------------------------------------
    # POSTER
    # -----------------------------------------

    if poster and movie_id:

        poster_html = f"""
        <a
            href="?movie_id={movie_id}"
            class="movie-poster-link"
            title="{html.escape(title, quote=True)}"
        >
            <img
                src="{html.escape(poster, quote=True)}"
                class="movie-poster"
            >
        </a>
        """

        st.markdown(
            poster_html,
            unsafe_allow_html=True
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
            {html.escape(language.upper())}
            <span>•</span>
            ★ {html.escape(rating_text)}
        </div>
        """,
        unsafe_allow_html=True
    )


def show_movies(title, subtitle, movies, key_prefix, limit=6):

    if not movies:
        return

    st.markdown(
        f"""
        <div class="section-heading">
            <div>
                <h2>{html.escape(title)}</h2>
                <p>{html.escape(subtitle)}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    columns = st.columns(6, gap="medium")

    for index, movie in enumerate(movies[:limit]):

        with columns[index % 6]:

            movie_card(
                movie,
                f"{key_prefix}_{index}"
            )


def get_results(data):

    if isinstance(data, dict):
        return data.get("results", [])

    if isinstance(data, list):
        return data

    return []


def render_home():

    # -----------------------------------------
    # CHECK FOR CLICKED MOVIE
    # -----------------------------------------

    movie_id = st.query_params.get("movie_id")

    if movie_id:

        st.session_state.selected_movie_id = str(movie_id)

        st.query_params.clear()

        st.rerun()

    # -----------------------------------------
    # HERO
    # -----------------------------------------

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
                Discover movies, explore details and find where
                they are available to watch in India.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    # -----------------------------------------
    # SEARCH
    # -----------------------------------------

    search_query = st.text_input(
        "Search movies",
        placeholder="Search movies like Leo, Interstellar, Jailer...",
        key="home_search",
        label_visibility="collapsed"
    )

    if search_query.strip():

        try:

            results = search_movies(
                search_query.strip()
            )

            movies = get_results(results)

        except TMDBError as error:

            st.error(str(error))
            return

        st.markdown(
            f"""
            <div class="search-result-heading">
                <span>SEARCH RESULTS</span>
                <strong>{len(movies)}</strong>
            </div>
            """,
            unsafe_allow_html=True
        )

        if not movies:

            st.info(
                "No movies found. Try another title."
            )

            return

        columns = st.columns(6, gap="medium")

        for index, movie in enumerate(movies[:18]):

            with columns[index % 6]:

                movie_card(
                    movie,
                    f"home_search_{index}"
                )

        return

    # -----------------------------------------
    # HOME CONTENT
    # -----------------------------------------

    try:

        trending_data = get_trending()

        show_movies(
            "Trending Now",
            "Movies people are discovering right now",
            get_results(trending_data),
            "trending",
            6
        )

        now_playing_data = get_now_playing()

        show_movies(
            "Recently Released",
            "Movies currently listed in theatrical releases",
            get_results(now_playing_data),
            "recent",
            6
        )

        popular_data = get_popular()

        show_movies(
            "Popular Movies",
            "Popular titles from TMDB",
            get_results(popular_data),
            "popular",
            6
        )

        upcoming_data = get_upcoming()

        show_movies(
            "Coming Soon",
            "Upcoming movies listed by TMDB",
            get_results(upcoming_data),
            "upcoming",
            6
        )

    except TMDBError as error:

        st.error(str(error))

        st.info(
            "Make sure your TMDB token is configured correctly."
        )

    # -----------------------------------------
    # BROWSE BY LANGUAGE
    # -----------------------------------------

    st.markdown(
        """
        <div class="browse-section">
            <div class="section-heading">
                <div>
                    <h2>Browse by Language</h2>
                    <p>Explore movies across different languages</p>
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

    language_columns = st.columns(4, gap="medium")

    for index, language in enumerate(languages):

        with language_columns[index % 4]:

            st.markdown(
                f"""
                <div class="browse-card">
                    {language}
                </div>
                """,
                unsafe_allow_html=True
            )

    # -----------------------------------------
    # BROWSE BY PLATFORM
    # -----------------------------------------

    st.markdown(
        """
        <div class="browse-section">
            <div class="section-heading">
                <div>
                    <h2>Browse by Platform</h2>
                    <p>Explore movies available across popular OTT platforms</p>
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

    platform_columns = st.columns(4, gap="medium")

    for index, platform in enumerate(platforms):

        with platform_columns[index % 4]:

            st.markdown(
                f"""
                <div class="browse-card platform-card">
                    {platform}
                </div>
                """,
                unsafe_allow_html=True
            )
