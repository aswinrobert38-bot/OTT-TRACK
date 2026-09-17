import html
import streamlit as st

from services.tmdb_service import (
    TMDBError,
    get_movie_details,
    get_watch_providers
)


def render_movie_details(movie_id):

    # -------------------------
    # Back Button
    # -------------------------

    if st.button("← Back", key="back_movie"):

        st.session_state.selected_movie_id = None
        st.query_params.clear()
        st.rerun()

    try:

        movie = get_movie_details(movie_id)

    except TMDBError as error:

        st.error(str(error))
        return

    # -------------------------
    # Movie Information
    # -------------------------

    title = movie.get("title") or "Untitled"

    overview = (
        movie.get("overview")
        or "No description available."
    )

    poster = movie.get("poster_url")

    backdrop = movie.get("backdrop_url")

    rating = movie.get("rating", 0)

    release_date = (
        movie.get("release_date")
        or "Not available"
    )

    original_language = (
        movie.get("original_language")
        or "Not available"
    )

    genres = movie.get("genres", [])

    genre_names = [
        genre.get("name")
        for genre in genres
        if genre.get("name")
    ]

    genre_text = ", ".join(genre_names)

    # -------------------------
    # Backdrop
    # -------------------------

    if backdrop:

        st.markdown(
            f"""
            <div class="movie-backdrop">
                <img src="{html.escape(backdrop, quote=True)}">
            </div>
            """,
            unsafe_allow_html=True
        )

    # -------------------------
    # Title
    # -------------------------

    st.markdown(
        f"""
        <div class="details-title">
            {html.escape(title)}
        </div>
        """,
        unsafe_allow_html=True
    )

    # -------------------------
    # Basic Information
    # -------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        try:
            rating_value = str(round(float(rating), 1))
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
            "Language",
            original_language.upper()
        )

    with col4:

        runtime = movie.get("runtime")

        if runtime:
            runtime_text = str(runtime) + " min"
        else:
            runtime_text = "N/A"

        st.metric(
            "Runtime",
            runtime_text
        )

    st.divider()

    # -------------------------
    # Main Content
    # -------------------------

    left, right = st.columns([1, 2])

    with left:

        if poster:

            st.markdown(
                f"""
                <img
                    src="{html.escape(poster, quote=True)}"
                    class="details-poster"
                >
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                """
                <div class="poster-fallback">
                    NO POSTER
                </div>
                """,
                unsafe_allow_html=True
            )

    with right:

        st.subheader("About the Movie")

        st.write(overview)

        if genre_text:

            st.markdown(
                "**Genre:** " +
                html.escape(genre_text)
            )

        tagline = movie.get("tagline")

        if tagline:

            st.markdown(
                "**Tagline:** " +
                html.escape(tagline)
            )

    # -------------------------
    # Cast & Crew
    # -------------------------

    st.divider()

    credits = movie.get("credits", {})

    cast = credits.get("cast", [])

    crew = credits.get("crew", [])

    directors = [
        person.get("name")
        for person in crew
        if person.get("job") == "Director"
        and person.get("name")
    ]

    st.subheader("Cast & Crew")

    if directors:

        st.markdown(
            "**Director:** " +
            ", ".join(directors)
        )

    if cast:

        cast_names = [
            person.get("name")
            for person in cast[:10]
            if person.get("name")
        ]

        st.markdown(
            "**Cast:** " +
            ", ".join(cast_names)
        )

    # -------------------------
    # Trailer
    # -------------------------

    videos = movie.get("videos", {})

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

        st.subheader("Trailer")

        youtube_url = (
            "https://www.youtube.com/watch?v=" +
            trailer.get("key")
        )

        st.video(youtube_url)

    # -------------------------
    # OTT Availability
    # -------------------------

    st.divider()

    st.subheader("Where to Watch in India")

    try:

        provider_data = get_watch_providers(movie_id)

        results = provider_data.get(
            "results",
            {}
        )

        india = results.get(
            "IN",
            {}
        )

        flatrate = india.get(
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

        # -------------------------
        # Stream
        # -------------------------

        if flatrate:

            st.markdown(
                '<div class="ott-heading">STREAM</div>',
                unsafe_allow_html=True
            )

            for provider in flatrate:

                provider_name = provider.get(
                    "provider_name",
                    "Unknown"
                )

                logo_path = provider.get(
                    "logo_path"
                )

                if logo_path:

                    logo_url = (
                        "https://image.tmdb.org/t/p/w92" +
                        logo_path
                    )

                    st.markdown(
                        f"""
                        <div class="ott-card">

                            <img
                                src="{html.escape(
                                    logo_url,
                                    quote=True
                                )}"
                                class="ott-logo"
                            >

                            <div class="ott-info">

                                <div class="ott-name">
                                    {html.escape(
                                        provider_name
                                    )}
                                </div>

                                <div class="ott-type">
                                    Streaming
                                </div>

                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                else:

                    st.markdown(
                        f"""
                        <div class="ott-card">

                            <div class="ott-info">

                                <div class="ott-name">
                                    {html.escape(
                                        provider_name
                                    )}
                                </div>

                                <div class="ott-type">
                                    Streaming
                                </div>

                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )

        # -------------------------
        # Rent
        # -------------------------

        if rent:

            st.markdown(
                '<div class="ott-heading">RENT</div>',
                unsafe_allow_html=True
            )

            for provider in rent:

                provider_name = provider.get(
                    "provider_name",
                    "Unknown"
                )

                logo_path = provider.get(
                    "logo_path"
                )

                if logo_path:

                    logo_url = (
                        "https://image.tmdb.org/t/p/w92" +
                        logo_path
                    )

                    st.markdown(
                        f"""
                        <div class="ott-card">

                            <img
                                src="{html.escape(
                                    logo_url,
                                    quote=True
                                )}"
                                class="ott-logo"
                            >

                            <div class="ott-info">

                                <div class="ott-name">
                                    {html.escape(
                                        provider_name
                                    )}
                                </div>

                                <div class="ott-type">
                                    Rent
                                </div>

                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )

        # -------------------------
        # Buy
        # -------------------------

        if buy:

            st.markdown(
                '<div class="ott-heading">BUY</div>',
                unsafe_allow_html=True
            )

            for provider in buy:

                provider_name = provider.get(
                    "provider_name",
                    "Unknown"
                )

                logo_path = provider.get(
                    "logo_path"
                )

                if logo_path:

                    logo_url = (
                        "https://image.tmdb.org/t/p/w92" +
                        logo_path
                    )

                    st.markdown(
                        f"""
                        <div class="ott-card">

                            <img
                                src="{html.escape(
                                    logo_url,
                                    quote=True
                                )}"
                                class="ott-logo"
                            >

                            <div class="ott-info">

                                <div class="ott-name">
                                    {html.escape(
                                        provider_name
                                    )}
                                </div>

                                <div class="ott-type">
                                    Buy
                                </div>

                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )

        if not flatrate and not rent and not buy:

            st.info(
                "No OTT availability information is currently available for India."
            )

    except TMDBError:

        st.info(
            "OTT availability information is currently unavailable."
        )
