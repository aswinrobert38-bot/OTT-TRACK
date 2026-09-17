import streamlit as st

from services.tmdb_service import (
    TMDBError,
    get_movie_details,
    get_watch_providers
)


IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
BACKDROP_BASE_URL = "https://image.tmdb.org/t/p/w1280"


def get_movie_languages(movie):
    languages = movie.get("spoken_languages", [])

    names = []

    for language in languages:
        name = language.get("english_name") or language.get("name")

        if name and name not in names:
            names.append(name)

    return names


def get_directors(movie):
    credits = movie.get("credits", {})
    crew = credits.get("crew", [])

    directors = []

    for person in crew:
        if person.get("job") == "Director":
            name = person.get("name")

            if name and name not in directors:
                directors.append(name)

    return directors


def get_cast(movie):
    credits = movie.get("credits", {})
    cast = credits.get("cast", [])

    names = []

    for person in cast[:10]:
        name = person.get("name")

        if name:
            names.append(name)

    return names


def get_provider_type(provider_type):
    provider_types = {
        "flatrate": "Streaming",
        "free": "Free",
        "ads": "Free with Ads",
        "rent": "Rent",
        "buy": "Buy"
    }

    return provider_types.get(
        provider_type,
        provider_type.title()
    )


def get_india_providers(provider_data):
    """
    Get ONLY India (IN) watch providers.
    """

    results = provider_data.get("results", {})

    india = results.get("IN", {})

    providers = []

    provider_categories = [
        ("flatrate", "Streaming"),
        ("free", "Free"),
        ("ads", "Free with Ads"),
        ("rent", "Rent"),
        ("buy", "Buy")
    ]

    for category, category_name in provider_categories:

        provider_list = india.get(category, [])

        for provider in provider_list:

            provider_id = provider.get("provider_id")
            provider_name = provider.get(
                "provider_name",
                "Unknown"
            )

            logo_path = provider.get("logo_path")

            logo_url = None

            if logo_path:
                logo_url = (
                    "https://image.tmdb.org/t/p/w92"
                    + logo_path
                )

            providers.append(
                {
                    "id": provider_id,
                    "name": provider_name,
                    "logo": logo_url,
                    "type": category_name
                }
            )

    return providers


def render_provider(provider):
    """
    Display one India OTT provider
    using native Streamlit components.
    """

    col1, col2, col3 = st.columns(
        [0.8, 2.5, 1.2]
    )

    with col1:

        if provider["logo"]:

            st.image(
                provider["logo"],
                width=55
            )

        else:

            st.write("🎬")

    with col2:

        st.markdown(
            "**" + provider["name"] + "**"
        )

    with col3:

        st.caption(
            provider["type"]
        )


def render_movie_details(movie_id):

    # --------------------------------
    # BACK BUTTON
    # --------------------------------

    if st.button(
        "← Back",
        key="back_movie"
    ):

        st.session_state.open_movie_id = None
        st.rerun()


    # --------------------------------
    # LOAD MOVIE
    # --------------------------------

    try:

        movie = get_movie_details(
            movie_id
        )

    except TMDBError as error:

        st.error(str(error))

        return


    # --------------------------------
    # MOVIE DATA
    # --------------------------------

    title = movie.get(
        "title",
        "Untitled"
    )

    overview = movie.get(
        "overview",
        "No description available."
    )

    poster = movie.get(
        "poster_url"
    )

    backdrop = movie.get(
        "backdrop_url"
    )

    rating = movie.get(
        "rating",
        0
    )

    release_date = movie.get(
        "release_date"
    ) or "Not available"

    original_language = movie.get(
        "original_language"
    ) or "Not available"

    runtime = movie.get(
        "runtime"
    )

    genres = movie.get(
        "genres",
        []
    )

    genre_names = []

    for genre in genres:

        name = genre.get("name")

        if name:
            genre_names.append(name)

    genre_text = ", ".join(
        genre_names
    )

    movie_languages = get_movie_languages(
        movie
    )

    directors = get_directors(
        movie
    )

    cast_names = get_cast(
        movie
    )


    # --------------------------------
    # BACKDROP
    # --------------------------------

    if backdrop:

        st.image(
            backdrop,
            use_container_width=True
        )


    # --------------------------------
    # TITLE
    # --------------------------------

    st.title(title)


    # --------------------------------
    # BASIC INFORMATION
    # --------------------------------

    col1, col2, col3, col4 = st.columns(4)


    with col1:

        try:

            rating_value = str(
                round(
                    float(rating),
                    1
                )
            )

        except Exception:

            rating_value = "N/A"

        st.metric(
            "Rating",
            "★ " + rating_value
        )


    with col2:

        st.metric(
            "Release",
            release_date
        )


    with col3:

        st.metric(
            "Original Language",
            original_language.upper()
        )


    with col4:

        if runtime:

            runtime_text = (
                str(runtime)
                + " min"
            )

        else:

            runtime_text = "N/A"

        st.metric(
            "Runtime",
            runtime_text
        )


    # --------------------------------
    # MAIN CONTENT
    # --------------------------------

    st.divider()

    left, right = st.columns(
        [1, 2]
    )


    # --------------------------------
    # POSTER
    # --------------------------------

    with left:

        if poster:

            st.image(
                poster,
                use_container_width=True
            )

        else:

            st.info(
                "Poster not available."
            )


    # --------------------------------
    # ABOUT
    # --------------------------------

    with right:

        st.subheader(
            "About the Movie"
        )

        st.write(
            overview
        )


        if genre_text:

            st.markdown(
                "**Genre:** "
                + genre_text
            )


        tagline = movie.get(
            "tagline"
        )

        if tagline:

            st.markdown(
                "**Tagline:** "
                + tagline
            )


        if movie_languages:

            st.markdown(
                "**Languages:** "
                + ", ".join(
                    movie_languages
                )
            )


    # --------------------------------
    # CAST & CREW
    # --------------------------------

    st.divider()

    st.subheader(
        "Cast & Crew"
    )


    if directors:

        st.markdown(
            "**Director:** "
            + ", ".join(directors)
        )


    if cast_names:

        st.markdown(
            "**Cast:** "
            + ", ".join(cast_names)
        )


    # --------------------------------
    # TRAILER
    # --------------------------------

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


    # --------------------------------
    # INDIA OTT AVAILABILITY
    # --------------------------------

    st.divider()

    st.subheader(
        "Where to Watch in India"
    )


    try:

        provider_data = get_watch_providers(
            movie_id
        )

        india_providers = get_india_providers(
            provider_data
        )


        # --------------------------------
        # NO PROVIDERS
        # --------------------------------

        if not india_providers:

            st.info(
                "No OTT availability found in India."
            )


        else:

            # Remove duplicate provider/category
            # combinations while preserving order.

            unique_providers = []

            seen = set()


            for provider in india_providers:

                key = (
                    provider["id"],
                    provider["type"]
                )

                if key not in seen:

                    seen.add(key)

                    unique_providers.append(
                        provider
                    )


            # --------------------------------
            # STREAMING
            # --------------------------------

            streaming = [
                provider
                for provider in unique_providers
                if provider["type"] == "Streaming"
            ]


            if streaming:

                st.markdown(
                    "### Streaming"
                )

                for provider in streaming:

                    render_provider(
                        provider
                    )

                    st.divider()


            # --------------------------------
            # FREE
            # --------------------------------

            free = [
                provider
                for provider in unique_providers
                if provider["type"] == "Free"
            ]


            if free:

                st.markdown(
                    "### Free"
                )

                for provider in free:

                    render_provider(
                        provider
                    )

                    st.divider()


            # --------------------------------
            # FREE WITH ADS
            # --------------------------------

            ads = [
                provider
                for provider in unique_providers
                if provider["type"] == "Free with Ads"
            ]


            if ads:

                st.markdown(
                    "### Free with Ads"
                )

                for provider in ads:

                    render_provider(
                        provider
                    )

                    st.divider()


            # --------------------------------
            # RENT
            # --------------------------------

            rent = [
                provider
                for provider in unique_providers
                if provider["type"] == "Rent"
            ]


            if rent:

                st.markdown(
                    "### Rent"
                )

                for provider in rent:

                    render_provider(
                        provider
                    )

                    st.divider()


            # --------------------------------
            # BUY
            # --------------------------------

            buy = [
                provider
                for provider in unique_providers
                if provider["type"] == "Buy"
            ]


            if buy:

                st.markdown(
                    "### Buy"
                )

                for provider in buy:

                    render_provider(
                        provider
                    )

                    st.divider()


    except TMDBError as error:

        st.error(
            "Unable to load India OTT availability: "
            + str(error)
        )


    # --------------------------------
    # LANGUAGE NOTE
    # --------------------------------

    if movie_languages:

        st.caption(
            "Movie languages: "
            + ", ".join(movie_languages)
        )


    # --------------------------------
    # ATTRIBUTION
    # --------------------------------

    st.caption(
        "OTT availability data powered by JustWatch through TMDB."
    )

    st.caption(
        "This product uses the TMDB API but is not endorsed or certified by TMDB."
    )
