import html
import streamlit as st

from services.tmdb_service import (
    TMDBError,
    get_movie_details,
    get_watch_providers,
)


# =========================================================
# HELPERS
# =========================================================

def safe_text(value, default="N/A"):
    if value is None:
        return default

    text = str(value).strip()

    return text if text else default


def get_title(movie):
    return safe_text(
        movie.get("title")
        or movie.get("name"),
        "Untitled"
    )


def get_year(movie):
    release_date = (
        movie.get("release_date")
        or movie.get("first_air_date")
        or ""
    )

    if release_date:
        return str(release_date)[:4]

    return "N/A"


def get_rating(movie):
    rating = (
        movie.get("rating")
        if movie.get("rating") is not None
        else movie.get("vote_average")
    )

    if rating is None:
        return "N/A"

    try:
        return str(round(float(rating), 1))
    except Exception:
        return "N/A"


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


def get_backdrop(movie):
    backdrop = movie.get("backdrop_url")

    if backdrop:
        return backdrop

    backdrop_path = movie.get("backdrop_path")

    if backdrop_path:
        return (
            "https://image.tmdb.org/t/p/w1280"
            + backdrop_path
        )

    return None


def get_genres(movie):
    genres = movie.get("genres", [])

    if not isinstance(genres, list):
        return []

    result = []

    for genre in genres:
        if isinstance(genre, dict):
            name = genre.get("name")

            if name and name not in result:
                result.append(name)

    return result


def get_languages(movie):
    languages = movie.get("spoken_languages")

    if isinstance(languages, list):

        result = []

        for language in languages:

            if not isinstance(language, dict):
                continue

            name = (
                language.get("english_name")
                or language.get("name")
                or language.get("iso_639_1")
            )

            if name and name not in result:
                result.append(str(name))

        if result:
            return result

    original_language = movie.get(
        "original_language"
    )

    if original_language:
        return [str(original_language).upper()]

    return []


def get_director(movie):
    credits = movie.get("credits", {})

    if not isinstance(credits, dict):
        return "N/A"

    crew = credits.get("crew", [])

    if not isinstance(crew, list):
        return "N/A"

    directors = []

    for person in crew:

        if not isinstance(person, dict):
            continue

        if person.get("job") == "Director":

            name = person.get("name")

            if name and name not in directors:
                directors.append(name)

    if directors:
        return ", ".join(directors)

    return "N/A"


def get_cast(movie, limit=8):
    credits = movie.get("credits", {})

    if not isinstance(credits, dict):
        return []

    cast = credits.get("cast", [])

    if not isinstance(cast, list):
        return []

    result = []

    for person in cast:

        if not isinstance(person, dict):
            continue

        name = person.get("name")

        if name and name not in result:
            result.append(name)

        if len(result) >= limit:
            break

    return result


# =========================================================
# PROVIDER HELPERS
# =========================================================

def get_provider_logo(logo_path):
    if not logo_path:
        return None

    if str(logo_path).startswith("http"):
        return logo_path

    return (
        "https://image.tmdb.org/t/p/w92"
        + str(logo_path)
    )


def get_provider_type_name(provider_type):
    names = {
        "flatrate": "Streaming",
        "free": "Free",
        "ads": "Free with Ads",
        "rent": "Rent",
        "buy": "Buy",
    }

    return names.get(
        provider_type,
        provider_type.replace("_", " ").title()
    )


def collect_providers(provider_data):
    """
    Convert TMDB's country-based provider response into
    provider-based information.

    Example:

    Netflix
        countries: India, United States, United Kingdom
        types: Streaming, Rent
    """

    if not isinstance(provider_data, dict):
        return {}

    results = provider_data.get(
        "results",
        {}
    )

    if not isinstance(results, dict):
        return {}

    providers = {}

    for country_code, country_data in results.items():

        if not isinstance(country_data, dict):
            continue

        provider_groups = [
            ("flatrate", country_data.get("flatrate", [])),
            ("free", country_data.get("free", [])),
            ("ads", country_data.get("ads", [])),
            ("rent", country_data.get("rent", [])),
            ("buy", country_data.get("buy", [])),
        ]

        for provider_type, provider_list in provider_groups:

            if not isinstance(provider_list, list):
                continue

            for provider in provider_list:

                if not isinstance(provider, dict):
                    continue

                provider_id = provider.get(
                    "provider_id"
                )

                provider_name = provider.get(
                    "provider_name"
                )

                if not provider_id or not provider_name:
                    continue

                key = str(provider_id)

                if key not in providers:

                    providers[key] = {
                        "name": provider_name,
                        "logo_path": provider.get(
                            "logo_path"
                        ),
                        "countries": [],
                        "types": [],
                    }

                if country_code not in providers[key]["countries"]:

                    providers[key]["countries"].append(
                        country_code
                    )

                type_name = get_provider_type_name(
                    provider_type
                )

                if type_name not in providers[key]["types"]:

                    providers[key]["types"].append(
                        type_name
                    )

    return providers


# =========================================================
# PROVIDER CARD
# =========================================================

def render_provider_card(provider):

    name = safe_text(
        provider.get("name"),
        "Unknown Platform"
    )

    logo = get_provider_logo(
        provider.get("logo_path")
    )

    provider_types = provider.get(
        "types",
        []
    )

    countries = provider.get(
        "countries",
        []
    )

    st.markdown(
        '<div class="rr-provider-card">',
        unsafe_allow_html=True
    )

    # -----------------------------------------------------
    # LOGO
    # -----------------------------------------------------

    if logo:

        st.image(
            logo,
            width=58
        )

    # -----------------------------------------------------
    # NAME
    # -----------------------------------------------------

    st.markdown(
        f"### {html.escape(name)}"
    )

    # -----------------------------------------------------
    # AVAILABILITY TYPE
    # -----------------------------------------------------

    if provider_types:

        type_text = "  •  ".join(
            provider_types
        )

        st.caption(
            type_text
        )

    # -----------------------------------------------------
    # GLOBAL AVAILABILITY
    # -----------------------------------------------------

    if countries:

        st.markdown(
            "**Available regions**"
        )

        # Display country codes rather than pretending
        # that every country has the same offer.
        display_countries = countries[:30]

        st.caption(
            " • ".join(display_countries)
        )

        if len(countries) > 30:

            st.caption(
                f"+ {len(countries) - 30} more regions"
            )

    # -----------------------------------------------------
    # LANGUAGE NOTICE
    # -----------------------------------------------------

    st.markdown(
        "**Languages**"
    )

    st.caption(
        "Provider-specific audio/subtitle languages "
        "are not supplied by TMDB's watch-provider response."
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# =========================================================
# MAIN
# =========================================================

def render_movie_details(movie_id):

    # =====================================================
    # BACK
    # =====================================================

    if st.button(
        "← Back to movies",
        key="movie_details_back"
    ):

        st.session_state.selected_movie_id = None

        st.query_params.clear()

        st.rerun()


    # =====================================================
    # LOAD MOVIE
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


    if not movie:

        st.error(
            "Movie details could not be found."
        )

        return


    # =====================================================
    # BASIC INFORMATION
    # =====================================================

    title = get_title(movie)

    year = get_year(movie)

    rating = get_rating(movie)

    poster = get_poster(movie)

    backdrop = get_backdrop(movie)

    genres = get_genres(movie)

    languages = get_languages(movie)

    director = get_director(movie)

    cast = get_cast(movie)

    overview = safe_text(
        movie.get("overview"),
        "No description available."
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
    # TITLE AREA
    # =====================================================

    st.title(title)

    meta_parts = [
        year,
        f"★ {rating}",
    ]

    if genres:

        meta_parts.append(
            " • ".join(genres)
        )

    st.caption(
        "  •  ".join(meta_parts)
    )


    # =====================================================
    # MAIN INFORMATION
    # =====================================================

    poster_col, info_col = st.columns(
        [1, 2],
        gap="large"
    )


    # =====================================================
    # POSTER
    # =====================================================

    with poster_col:

        if poster:

            st.image(
                poster,
                use_container_width=True
            )

        else:

            st.info(
                "Poster unavailable"
            )


    # =====================================================
    # INFORMATION
    # =====================================================

    with info_col:

        st.subheader(
            "About the Movie"
        )

        st.write(
            overview
        )

        st.markdown(
            f"**Director:** {director}"
        )

        # -------------------------------------------------
        # MOVIE LANGUAGES
        # -------------------------------------------------

        st.markdown(
            "### Languages"
        )

        if languages:

            st.write(
                " • ".join(languages)
            )

        else:

            st.caption(
                "Language information unavailable."
            )

        # -------------------------------------------------
        # CAST
        # -------------------------------------------------

        st.markdown(
            "### Cast"
        )

        if cast:

            st.write(
                " • ".join(cast)
            )

        else:

            st.caption(
                "Cast information unavailable."
            )


    # =====================================================
    # WHERE TO WATCH
    # =====================================================

    st.divider()

    st.markdown(
        "## Where to Watch"
    )

    st.caption(
        "Streaming, rental and purchase availability "
        "across the regions returned by the provider data."
    )


    # =====================================================
    # GET PROVIDERS
    # =====================================================

    try:

        provider_data = get_watch_providers(
            movie_id
        )

        providers = collect_providers(
            provider_data
        )

    except TMDBError as error:

        st.error(
            str(error)
        )

        providers = {}


    # =====================================================
    # PROVIDERS
    # =====================================================

    if not providers:

        st.info(
            "No OTT availability information is currently available."
        )

    else:

        provider_items = list(
            providers.values()
        )

        provider_columns = st.columns(
            3,
            gap="large"
        )

        for index, provider in enumerate(
            provider_items
        ):

            with provider_columns[
                index % 3
            ]:

                render_provider_card(
                    provider
                )


    # =====================================================
    # SOURCE / ATTRIBUTION
    # =====================================================

    st.divider()

    st.caption(
        "Availability information is provided through "
        "TMDB's watch-provider data powered by JustWatch."
    )

    st.caption(
        "This product uses the TMDB API but is not endorsed "
        "or certified by TMDB."
    )
