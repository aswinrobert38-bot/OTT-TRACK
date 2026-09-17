import streamlit as st

from services.tmdb_service import (
    TMDBError,
    get_movie_details,
    get_watch_providers,
)


# =========================================================
# HELPERS
# =========================================================

def safe_text(value, default="Not available"):

    if value is None:
        return default

    text = str(value).strip()

    if not text:
        return default

    return text


def get_languages(movie):

    spoken_languages = movie.get(
        "spoken_languages",
        []
    )

    languages = []

    for language in spoken_languages:

        name = (
            language.get("english_name")
            or language.get("name")
        )

        if name and name not in languages:

            languages.append(name)

    return languages


def get_genres(movie):

    genres = movie.get(
        "genres",
        []
    )

    names = []

    for genre in genres:

        name = genre.get("name")

        if name:

            names.append(name)

    return names


def get_directors(movie):

    credits = movie.get(
        "credits",
        {}
    )

    crew = credits.get(
        "crew",
        []
    )

    directors = []

    for person in crew:

        if (
            person.get("job") == "Director"
            and person.get("name")
        ):

            if person["name"] not in directors:

                directors.append(
                    person["name"]
                )

    return directors


def get_cast(movie):

    credits = movie.get(
        "credits",
        {}
    )

    cast = credits.get(
        "cast",
        []
    )

    names = []

    for person in cast[:12]:

        name = person.get(
            "name"
        )

        if name:

            names.append(
                name
            )

    return names


# =========================================================
# PROVIDER SECTION
# =========================================================

def show_provider_section(
    title,
    providers,
    availability_type
):

    if not providers:
        return


    st.markdown(
        f"### {title}"
    )


    for provider in providers:

        provider_name = provider.get(
            "provider_name",
            "Unknown platform"
        )

        logo_path = provider.get(
            "logo_path"
        )


        col1, col2 = st.columns(
            [1, 5]
        )


        with col1:

            if logo_path:

                logo_url = (
                    "https://image.tmdb.org/t/p/w92"
                    + logo_path
                )

                st.image(
                    logo_url,
                    width=55
                )


        with col2:

            st.markdown(
                f"**{provider_name}**"
            )

            st.caption(
                availability_type
            )


# =========================================================
# MOVIE DETAILS
# =========================================================

def render_movie_details(movie_id):

    # =====================================================
    # BACK
    # =====================================================

    if st.button(
        "← Back to Movies",
        key="back_movie"
    ):

        st.session_state.selected_movie_id = None

        st.query_params.clear()

        st.rerun()


    # =====================================================
    # GET MOVIE
    # =====================================================

    try:

        movie = get_movie_details(
            movie_id
        )

    except TMDBError as error:

        st.error(
            str(error)
        )

        return


    # =====================================================
    # BASIC DATA
    # =====================================================

    title = safe_text(
        movie.get("title"),
        "Untitled"
    )

    overview = safe_text(
        movie.get("overview"),
        "No description available."
    )

    poster = movie.get(
        "poster_url"
    )

    backdrop = movie.get(
        "backdrop_url"
    )

    rating = movie.get(
        "rating"
    )

    release_date = safe_text(
        movie.get("release_date")
    )

    original_language = safe_text(
        movie.get("original_language")
    )

    runtime = movie.get(
        "runtime"
    )

    genres = get_genres(
        movie
    )

    languages = get_languages(
        movie
    )

    directors = get_directors(
        movie
    )

    cast = get_cast(
        movie
    )


    # =====================================================
    # BACKDROP
    # =====================================================

    if backdrop:

        st.image(
            backdrop,
            use_container_width=True
        )


    # =====================================================
    # TITLE
    # =====================================================

    st.title(
        title
    )


    # =====================================================
    # BASIC METRICS
    # =====================================================

    col1, col2, col3, col4 = st.columns(
        4
    )


    with col1:

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

            rating_text = "N/A"


        st.metric(
            "Rating",
            rating_text
        )


    with col2:

        st.metric(
            "Release",
            release_date
        )


    with col3:

        st.metric(
            "Language",
            original_language.upper()
        )


    with col4:

        runtime_text = (
            str(runtime) + " min"
            if runtime
            else "N/A"
        )

        st.metric(
            "Runtime",
            runtime_text
        )


    st.divider()


    # =====================================================
    # POSTER + INFORMATION
    # =====================================================

    poster_col, information_col = st.columns(
        [1, 2],
        gap="large"
    )


    with poster_col:

        if poster:

            st.image(
                poster,
                use_container_width=True
            )

        else:

            st.info(
                "Poster unavailable."
            )


    with information_col:

        st.subheader(
            "About the Movie"
        )

        st.write(
            overview
        )


        if genres:

            st.markdown(
                "**Genres:** "
                + ", ".join(genres)
            )


        tagline = movie.get(
            "tagline"
        )

        if tagline:

            st.markdown(
                "**Tagline:** "
                + str(tagline)
            )


    # =====================================================
    # LANGUAGE INFORMATION
    # =====================================================

    st.divider()

    st.subheader(
        "Language Information"
    )


    language_col1, language_col2 = st.columns(
        2
    )


    with language_col1:

        st.markdown(
            "**Original Language**"
        )

        st.write(
            original_language.upper()
        )


    with language_col2:

        st.markdown(
            "**Spoken Languages**"
        )

        if languages:

            st.write(
                " • ".join(languages)
            )

        else:

            st.write(
                "Not available"
            )


    # =====================================================
    # CAST & CREW
    # =====================================================

    st.divider()

    st.subheader(
        "Cast & Crew"
    )


    if directors:

        st.markdown(
            "**Director:** "
            + ", ".join(directors)
        )


    if cast:

        st.markdown(
            "**Cast:** "
            + ", ".join(cast)
        )


    # =====================================================
    # TRAILER
    # =====================================================

    videos = movie.get(
        "videos",
        {}
    )

    video_results = videos.get(
        "results",
        []
    )

    trailer = None


    for video in video_results:

        if (
            video.get("site") == "YouTube"
            and video.get("type") == "Trailer"
        ):

            trailer = video

            break


    if trailer and trailer.get("key"):

        st.divider()

        st.subheader(
            "Trailer"
        )

        youtube_url = (
            "https://www.youtube.com/watch?v="
            + trailer.get("key")
        )

        st.video(
            youtube_url
        )


    # =====================================================
    # OTT AVAILABILITY
    # =====================================================

    st.divider()

    st.header(
        "Where to Watch in India"
    )

    st.caption(
        "Current India-region availability returned by TMDB."
    )


    try:

        provider_data = get_watch_providers(
            movie_id
        )

        results = provider_data.get(
            "results",
            {}
        )

        india = results.get(
            "IN",
            {}
        )


        streaming = india.get(
            "flatrate",
            []
        )

        rent = india.get(
            "rent",
            []
        )

        buy = india.get(
            "buy",
            []
        )


        # -------------------------------------------------
        # STREAMING
        # -------------------------------------------------

        if streaming:

            st.subheader(
                "Streaming"
            )

            show_provider_section(
                "Streaming",
                streaming,
                "Streaming"
            )


        # -------------------------------------------------
        # RENT
        # -------------------------------------------------

        if rent:

            st.subheader(
                "Rent"
            )

            show_provider_section(
                "Rent",
                rent,
                "Rent"
            )


        # -------------------------------------------------
        # BUY
        # -------------------------------------------------

        if buy:

            st.subheader(
                "Buy"
            )

            show_provider_section(
                "Buy",
                buy,
                "Buy"
            )


        # -------------------------------------------------
        # NOTHING FOUND
        # -------------------------------------------------

        if not streaming and not rent and not buy:

            st.info(
                "No OTT availability is currently listed "
                "for India."
            )


    except TMDBError:

        st.info(
            "OTT availability information is currently unavailable."
        )
