import streamlit as st

from services.tmdb_service import (
    TMDBError,
    get_movie_details,
    get_watch_providers
)


def render_movie_details(movie_id):

    if st.button("← Back"):

        st.session_state.selected_movie_id = None
        st.rerun()

    try:

        movie = get_movie_details(movie_id)

    except TMDBError as error:

        st.error(str(error))
        return

    title = movie.get("title") or "Untitled"

    overview = movie.get("overview") or "No description available."

    poster = movie.get("poster_url")

    backdrop = movie.get("backdrop_url")

    rating = movie.get("rating", 0)

    release_date = movie.get("release_date") or "Not available"

    original_language = (
        movie.get("original_language") or
        "Not available"
    )

    genres = movie.get("genres", [])

    genre_names = [
        genre.get("name")
        for genre in genres
    ]

    genre_text = ", ".join(genre_names)

    # Backdrop
    if backdrop:

        st.image(
            backdrop,
            use_container_width=True
        )

    # Title
    st.title(title)

    # Basic information
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Rating",
            str(round(float(rating), 1))
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
        st.metric(
            "Runtime",
            str(movie.get("runtime", "N/A")) +
            " min"
        )

    st.divider()

    # Main content
    left, right = st.columns([1, 2])

    with left:

        if poster:

            st.image(
                poster,
                use_container_width=True
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

            st.write(
                "**Genre:** " +
                genre_text
            )

        tagline = movie.get("tagline")

        if tagline:

            st.write(
                "**Tagline:** " +
                tagline
            )

    st.divider()

    # Cast and Director
    credits = movie.get("credits", {})

    cast = credits.get("cast", [])

    crew = credits.get("crew", [])

    directors = [
        person.get("name")
        for person in crew
        if person.get("job") == "Director"
    ]

    st.subheader("Cast & Crew")

    if directors:

        st.write(
            "**Director:** " +
            ", ".join(directors)
        )

    if cast:

        cast_names = [
            person.get("name")
            for person in cast[:10]
        ]

        st.write(
            "**Cast:** " +
            ", ".join(cast_names)
        )

    # Trailer
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

    if trailer:

        st.divider()

        st.subheader("Trailer")

        youtube_url = (
            "https://www.youtube.com/watch?v=" +
            trailer.get("key")
        )

        st.video(youtube_url)

    # OTT providers
    st.divider()

    st.subheader("Where to Watch")

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

        if flatrate:

            st.write("### Stream")

            for provider in flatrate:

                st.write(
                    "• " +
                    provider.get(
                        "provider_name",
                        "Unknown"
                    )
                )

        if rent:

            st.write("### Rent")

            for provider in rent:

                st.write(
                    "• " +
                    provider.get(
                        "provider_name",
                        "Unknown"
                    )
                )

        if buy:

            st.write("### Buy")

            for provider in buy:

                st.write(
                    "• " +
                    provider.get(
                        "provider_name",
                        "Unknown"
                    )
                )

        if not flatrate and not rent and not buy:

            st.info(
                "No OTT availability information is currently available for India."
            )

    except TMDBError:

        st.info(
            "OTT availability information is currently unavailable."
        )
