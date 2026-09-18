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
        return str(round(float(rating), 1))
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


def get_movie_languages(movie):
    """
    Get actual language metadata when available.
    Does not invent provider-specific languages.
    """

    languages = movie.get("spoken_languages")

    if isinstance(languages, list):

        result = []

        for item in languages:

            if isinstance(item, dict):

                name = (
                    item.get("english_name")
                    or item.get("name")
                    or item.get("iso_639_1")
                )

                if name and name not in result:
                    result.append(str(name))

        if result:
            return result

    original_language = movie.get("original_language")

    if original_language:
        return [str(original_language).upper()]

    return []


# =========================================================
# MOVIE CARD
# =========================================================

def movie_card(movie, key_suffix=""):

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

        safe_title = html.escape(
            str(title),
            quote=True
        )

        safe_poster = html.escape(
            str(poster),
            quote=True
        )

        # Display poster
        st.image(
            poster,
            use_container_width=True
        )

        # -------------------------------------------------
        # MOVIE DETAILS BUTTON
        # -------------------------------------------------

        if st.button(
            "View movie details",
            key=f"home_movie_{movie_id}_{key_suffix}",
            use_container_width=True
        ):

            # Store selected movie ID
            st.session_state.open_movie_id = movie_id

            # Force app.py to process the dialog
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

    st.subheader(title)

    st.caption(description)

    columns = st.columns(
        6,
        gap="medium"
    )

    for index, movie in enumerate(
        movies[:limit]
    ):

        with columns[index % 6]:

            movie_card(
                movie,
                key_suffix=(
                    f"section_{index}_"
                    f"{title.replace(' ', '_')}"
                )
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
                movie,
                key_suffix=f"search_{index}"
            )


# =========================================================
# AVAILABLE LANGUAGES
# =========================================================

def show_available_languages():

    st.divider()

    st.subheader(
        "Available Languages"
    )

    st.caption(
        "Browse the movie catalogue by language."
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

    for index, language in enumerate(languages):

        with columns[index % 4]:

            st.markdown(
                f"""
                <div class="language-card">
                    {html.escape(language)}
                </div>
                """,
                unsafe_allow_html=True
            )


# =========================================================
# SEARCH AREA
# =========================================================

def search_area():

    st.markdown(
        """
        <div class="search-heading">
            Search Movies
        </div>
        """,
        unsafe_allow_html=True
    )

    st.caption(
        "Search for any movie and explore its details and OTT availability."
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
                "Movie name",
                placeholder="Search any movie...",
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
                "Please enter a movie name."
            )

            return

        try:

            data = search_movies(
                query.strip()
            )

            movies = get_results(data)

            # Keep search results in session state so they survive
            # the rerun caused by clicking a movie.
            st.session_state.search_query = query.strip()
            st.session_state.search_results = movies

        except TMDBError:

            st.error(
                "Unable to search movies right now. "
                "Please check your TMDB connection."
            )

            return

        except Exception as error:

            st.error(
                f"Search failed: {error}"
            )

            return

    # -----------------------------------------------------
    # SHOW SAVED SEARCH RESULTS ON EVERY RERUN
    # -----------------------------------------------------

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
# HOME PAGE
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
            Every Movie. Every Platform. One Place.
        </div>
        """,
        unsafe_allow_html=True
    )

    # =====================================================
    # SEARCH
    # =====================================================

    search_area()

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
            "Popular movie titles from TMDB.",
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

    show_available_languages()

    # =====================================================
    # OTT AVAILABILITY INFORMATION
    # =====================================================

    st.divider()

    st.subheader(
        "OTT Availability"
    )

    st.caption(
        "Movie availability varies by country and platform. "
        "The movie details page shows the provider data returned by TMDB."
    )

    st.info(
        "Select a movie to view its available streaming, "
        "rental, and purchase platforms."
    )
