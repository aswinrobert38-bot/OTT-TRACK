import streamlit as st

from services.tmdb_service import (
    TMDBError,
    get_now_playing,
    get_popular,
    get_trending,
    get_upcoming,
    search_movies,
)


# =========================================================
# HELPERS
# =========================================================

def get_results(data):

    if isinstance(data, dict):
        return data.get("results", [])

    if isinstance(data, list):
        return data

    return []


def get_title(movie):

    return (
        movie.get("title")
        or movie.get("name")
        or "Untitled"
    )


def get_poster(movie):

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


def get_year(movie):

    release_date = (
        movie.get("release_date")
        or movie.get("first_air_date")
        or ""
    )

    if release_date:
        return release_date[:4]

    return "N/A"


def get_rating(movie):

    rating = movie.get("rating")

    if rating is None:
        rating = movie.get("vote_average")

    if rating is None:
        return "N/A"

    try:
        return str(
            round(float(rating), 1)
        )

    except Exception:
        return "N/A"


def get_language(movie):

    language = (
        movie.get("original_language")
        or movie.get("language")
    )

    if not language:
        return "N/A"

    return str(language).upper()


# =========================================================
# MOVIE CARD
# =========================================================

def movie_card(movie):

    movie_id = movie.get("id")

    title = get_title(movie)

    poster = get_poster(movie)

    year = get_year(movie)

    rating = get_rating(movie)

    language = get_language(movie)


    # -----------------------------------------------------
    # POSTER
    # -----------------------------------------------------

    if poster and movie_id:

        st.markdown(
            f"[![{title}]({poster})](?movie_id={movie_id})"
        )

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
        f"**{title}**"
    )


    # -----------------------------------------------------
    # META
    # -----------------------------------------------------

    st.caption(
        f"{year}  •  {language}  •  ★ {rating}"
    )


# =========================================================
# MOVIE SECTION
# =========================================================

def show_movies(
    title,
    description,
    movies,
    limit=6
):

    if not movies:
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


    for index, movie in enumerate(
        movies[:limit]
    ):

        with columns[index % 6]:

            movie_card(
                movie
            )


# =========================================================
# SEARCH RESULTS
# =========================================================

def show_search_results(
    query,
    movies
):

    st.divider()

    st.subheader(
        "Search Results"
    )

    st.caption(
        f'{len(movies)} result(s) for "{query}"'
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
        movies[:24]
    ):

        with columns[index % 6]:

            movie_card(
                movie
            )


# =========================================================
# MAIN HOME PAGE
# =========================================================

def render_home():

    # =====================================================
    # HEADER
    # =====================================================

    st.title(
        "ReelRoute"
    )

    st.subheader(
        "Every Movie. Every Platform. One Place."
    )

    st.caption(
        "Discover movies, explore complete details, "
        "and find where to watch them in India."
    )


    # =====================================================
    # SEARCH BAR
    # =====================================================

    with st.form(
        "main_movie_search",
        clear_on_submit=False
    ):

        search_col, button_col = st.columns(
            [6, 1],
            vertical_alignment="bottom"
        )


        with search_col:

            query = st.text_input(
                "Movie Search",
                placeholder=(
                    "Search any movie — "
                    "Spider-Man, Leo, Jailer, Interstellar..."
                ),
                label_visibility="collapsed"
            )


        with button_col:

            search_clicked = st.form_submit_button(
                "Search",
                use_container_width=True
            )


    # =====================================================
    # SEARCH
    # =====================================================

    if search_clicked:

        if not query.strip():

            st.warning(
                "Please enter a movie name."
            )

        else:

            try:

                data = search_movies(
                    query.strip()
                )

                movies = get_results(
                    data
                )

                show_search_results(
                    query.strip(),
                    movies
                )

            except TMDBError as error:

                st.error(
                    str(error)
                )


    # =====================================================
    # TRENDING
    # =====================================================

    try:

        trending = get_results(
            get_trending()
        )

        show_movies(
            "Trending Now",
            "Movies people are discovering right now.",
            trending,
            6
        )

    except TMDBError:

        st.warning(
            "Trending movies could not be loaded."
        )


    # =====================================================
    # RECENTLY RELEASED
    # =====================================================

    try:

        recently_released = get_results(
            get_now_playing()
        )

        show_movies(
            "Recently Released",
            "Movies currently listed in theatrical releases.",
            recently_released,
            6
        )

    except TMDBError:

        st.warning(
            "Recently released movies could not be loaded."
        )


    # =====================================================
    # POPULAR
    # =====================================================

    try:

        popular = get_results(
            get_popular()
        )

        show_movies(
            "Popular Movies",
            "Popular titles from TMDB.",
            popular,
            6
        )

    except TMDBError:

        st.warning(
            "Popular movies could not be loaded."
        )


    # =====================================================
    # COMING SOON
    # =====================================================

    try:

        upcoming = get_results(
            get_upcoming()
        )

        show_movies(
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
    # AVAILABLE LANGUAGES
    # =====================================================

    st.divider()

    st.subheader(
        "Available Languages"
    )

    st.caption(
        "Languages represented in the movie catalogue."
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


    language_columns = st.columns(
        4,
        gap="medium"
    )


    for index, language in enumerate(
        languages
    ):

        with language_columns[index % 4]:

            st.markdown(
                f"**{language}**"
            )


    # =====================================================
    # AVAILABLE OTT PLATFORMS
    # =====================================================

    st.divider()

    st.subheader(
        "Available OTT Platforms"
    )

    st.caption(
        "Platforms returned by TMDB for India-specific availability."
    )


    platforms = [
        "Netflix",
        "Prime Video",
        "JioHotstar",
        "SonyLIV",
        "ZEE5",
        "Sun NXT",
        "Aha",
        "Apple TV",
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
                f"**{platform}**"
            )
