import html
from urllib.parse import quote_plus

import streamlit as st

from services.tmdb_service import (
    TMDBError,
    get_movie_details,
    get_tv_details,
    get_watch_providers,
    get_tv_watch_providers,
)


# =========================================================
# HELPERS
# =========================================================

def get_languages(item):

    languages = item.get(
        "spoken_languages",
        []
    )

    names = []

    for language in languages:

        name = (
            language.get("english_name")
            or language.get("name")
        )

        if name and name not in names:
            names.append(name)

    if not names and item.get("original_language"):

        names.append(
            str(
                item.get("original_language")
            ).upper()
        )

    return names


def get_cast(item):

    cast = item.get(
        "credits",
        {}
    ).get(
        "cast",
        []
    )

    return [
        person.get("name")
        for person in cast[:10]
        if person.get("name")
    ]


def get_directors(item):

    crew = item.get(
        "credits",
        {}
    ).get(
        "crew",
        []
    )

    return list(
        dict.fromkeys(
            person.get("name")
            for person in crew
            if person.get("job")
            in (
                "Director",
                "Creator"
            )
            and person.get("name")
        )
    )


# =========================================================
# OTT TYPE
# =========================================================

def get_provider_type(category):

    return {

        "flatrate":
            "Streaming",

        "free":
            "Free",

        "ads":
            "Free with Ads",

        "rent":
            "Rent",

        "buy":
            "Buy"

    }.get(
        category,
        str(category).title()
    )


# =========================================================
# GET INDIA PROVIDERS
# =========================================================

def get_india_providers(provider_data):

    india = provider_data.get(
        "results",
        {}
    ).get(
        "IN",
        {}
    )

    providers = []

    categories = [
        "flatrate",
        "free",
        "ads",
        "rent",
        "buy"
    ]

    for category in categories:

        for provider in india.get(
            category,
            []
        ):

            logo = provider.get(
                "logo_path"
            )

            providers.append(
                {
                    "id":
                        provider.get(
                            "provider_id"
                        ),

                    "name":
                        provider.get(
                            "provider_name",
                            "Unknown"
                        ),

                    "logo":
                        (
                            "https://image.tmdb.org/t/p/w92"
                            + logo
                            if logo
                            else None
                        ),

                    "type":
                        get_provider_type(
                            category
                        ),

                    "tmdb_link":
                        india.get(
                            "link"
                        )
                }
            )

    return providers


# =========================================================
# PROVIDER TITLE SEARCH
# =========================================================

def provider_search_url(
    provider_name,
    title
):

    query = quote_plus(
        title.strip()
    )

    name = provider_name.lower()

    # -----------------------------------------------------
    # NETFLIX
    # -----------------------------------------------------

    if "netflix" in name:

        return (
            "https://www.netflix.com/search?q="
            + query
        )

    # -----------------------------------------------------
    # PRIME VIDEO
    # -----------------------------------------------------

    if (
        "prime video" in name
        or "amazon prime" in name
        or "amazon" in name
    ):

        return (
            "https://www.primevideo.com/search/ref=atv_nb_sr?phrase="
            + query
        )

    # -----------------------------------------------------
    # JIOHOTSTAR / HOTSTAR
    # -----------------------------------------------------

    if (
        "jiohotstar" in name
        or "jio hotstar" in name
        or "hotstar" in name
    ):

        return (
            "https://www.hotstar.com/in/search?q="
            + query
        )

    # -----------------------------------------------------
    # SONY LIV
    # -----------------------------------------------------

    if "sony liv" in name:

        return (
            "https://www.sonyliv.com/search/"
            + query
        )

    # -----------------------------------------------------
    # ZEE5
    # -----------------------------------------------------

    if "zee5" in name:

        return (
            "https://www.zee5.com/search?q="
            + query
        )

    # -----------------------------------------------------
    # YOUTUBE
    # -----------------------------------------------------

    if "youtube" in name:

        return (
            "https://www.youtube.com/results?search_query="
            + query
        )

    # -----------------------------------------------------
    # APPLE TV
    # -----------------------------------------------------

    if "apple tv" in name:

        return (
            "https://tv.apple.com/in/search?term="
            + query
        )

    # -----------------------------------------------------
    # AHA
    # -----------------------------------------------------

    if name == "aha" or "aha " in name:

        return (
            "https://www.aha.video/search/"
            + query
        )

    # -----------------------------------------------------
    # MX PLAYER
    # -----------------------------------------------------

    if "mx player" in name:

        return (
            "https://www.mxplayer.in/search/"
            + query
        )

    # -----------------------------------------------------
    # LIONSGATE PLAY
    # -----------------------------------------------------

    if "lionsgate" in name:

        return (
            "https://www.lionsgateplay.com/search?q="
            + query
        )

    # -----------------------------------------------------
    # DISCOVERY+
    # -----------------------------------------------------

    if "discovery" in name:

        return (
            "https://www.discoveryplus.in/search?q="
            + query
        )

    # -----------------------------------------------------
    # CRUNCHYROLL
    # -----------------------------------------------------

    if "crunchyroll" in name:

        return (
            "https://www.crunchyroll.com/search?q="
            + query
        )

    # -----------------------------------------------------
    # SUN NXT
    # -----------------------------------------------------

    if "sun nxt" in name:

        return (
            "https://www.sunnxt.com/search/"
            + query
        )

    # -----------------------------------------------------
    # MANORAMA MAX
    # -----------------------------------------------------

    if "manorama" in name:

        return (
            "https://www.manoramamax.com/search/"
            + query
        )

    # -----------------------------------------------------
    # DEFAULT
    # -----------------------------------------------------

    return None


# =========================================================
# CLICKABLE OTT CARD
# =========================================================

def render_provider(
    provider,
    title
):

    name = provider.get(
        "name",
        "OTT Platform"
    )

    logo = provider.get(
        "logo"
    )

    provider_type = provider.get(
        "type",
        "Streaming"
    )

    # -----------------------------------------------------
    # GET TITLE SEARCH URL
    # -----------------------------------------------------

    url = provider_search_url(
        name,
        title
    )

    # -----------------------------------------------------
    # FALLBACK
    # -----------------------------------------------------

    if not url:

        url = provider.get(
            "tmdb_link"
        )

    if not url:

        return

    # -----------------------------------------------------
    # LOGO
    # -----------------------------------------------------

    if logo:

        logo_html = f"""
        <img
            src="{html.escape(logo)}"
            class="ott-logo"
        >
        """

    else:

        logo_html = """
        <div class="ott-placeholder">
            ▶
        </div>
        """

    # -----------------------------------------------------
    # CLICKABLE CARD
    # -----------------------------------------------------

    card = f"""
    <a
        href="{html.escape(url)}"
        target="_blank"
        rel="noopener noreferrer"
        class="ott-card"
    >

        <div class="ott-logo-container">

            {logo_html}

        </div>

        <div class="ott-details">

            <div class="ott-name">
                {html.escape(name)}
            </div>

            <div class="ott-type">
                {html.escape(provider_type)}
            </div>

        </div>

        <div class="ott-open">
            ↗
        </div>

    </a>
    """

    # IMPORTANT
    # st.html makes the entire card clickable.
    st.html(card)


# =========================================================
# OTT SECTION
# =========================================================

def render_watch_section(
    item,
    content_type
):

    # =====================================================
    # CSS
    # =====================================================

    st.html(
        """
        <style>

        .ott-section-title {

            font-size: 30px;

            font-weight: 800;

            margin-top: 10px;

            margin-bottom: 5px;

        }


        .ott-section-subtitle {

            font-size: 14px;

            opacity: 0.60;

            margin-bottom: 25px;

        }


        .ott-category {

            font-size: 18px;

            font-weight: 750;

            margin-top: 20px;

            margin-bottom: 14px;

        }


        .ott-card {

            display: flex;

            align-items: center;

            gap: 14px;

            width: 100%;

            min-height: 82px;

            padding: 12px 14px;

            margin-bottom: 12px;

            box-sizing: border-box;

            border-radius: 18px;

            text-decoration: none !important;

            color: inherit !important;

            background:

                linear-gradient(
                    145deg,
                    rgba(255,255,255,0.10),
                    rgba(255,255,255,0.025)
                );

            border:

                1px solid
                rgba(255,255,255,0.10);

            transition:

                transform 0.20s ease,

                border-color 0.20s ease,

                background 0.20s ease,

                box-shadow 0.20s ease;

        }


        .ott-card:hover {

            transform:
                translateY(-4px);

            border-color:
                rgba(255,255,255,0.32);

            background:

                linear-gradient(
                    145deg,
                    rgba(255,255,255,0.16),
                    rgba(255,255,255,0.045)
                );

            box-shadow:

                0 12px 30px
                rgba(0,0,0,0.22);

        }


        .ott-logo-container {

            width: 56px;

            height: 56px;

            min-width: 56px;

            border-radius: 15px;

            display: flex;

            align-items: center;

            justify-content: center;

            overflow: hidden;

            background:
                rgba(255,255,255,0.08);

        }


        .ott-logo {

            width: 48px;

            height: 48px;

            object-fit: cover;

            border-radius: 12px;

            display: block;

        }


        .ott-placeholder {

            font-size: 22px;

        }


        .ott-details {

            flex: 1;

            min-width: 0;

        }


        .ott-name {

            font-size: 15px;

            font-weight: 750;

            white-space: nowrap;

            overflow: hidden;

            text-overflow: ellipsis;

        }


        .ott-type {

            font-size: 12px;

            opacity: 0.55;

            margin-top: 4px;

        }


        .ott-open {

            font-size: 23px;

            opacity: 0.60;

            transition:
                transform 0.20s ease;

        }


        .ott-card:hover .ott-open {

            transform:
                translate(3px,-3px);

            opacity: 1;

        }

        </style>
        """
    )

    # =====================================================
    # HEADER
    # =====================================================

    st.html(
        """
        <div class="ott-section-title">
            Where to Watch in India
        </div>

        <div class="ott-section-subtitle">
            Click an OTT platform to find this title
        </div>
        """
    )

    # =====================================================
    # GET OTT DATA
    # =====================================================

    try:

        if content_type == "tv":

            provider_data = get_tv_watch_providers(
                item["id"]
            )

        else:

            provider_data = get_watch_providers(
                item["id"]
            )

    except TMDBError as error:

        st.error(
            "Unable to load OTT availability: "
            + str(error)
        )

        return

    # =====================================================
    # PROVIDERS
    # =====================================================

    providers = get_india_providers(
        provider_data
    )

    if not providers:

        st.info(
            "No OTT availability found in India."
        )

        return

    # =====================================================
    # REMOVE DUPLICATES
    # =====================================================

    unique = []

    seen = set()

    for provider in providers:

        key = (
            provider.get("id"),
            provider.get("type")
        )

        if key not in seen:

            seen.add(key)

            unique.append(
                provider
            )

    # =====================================================
    # TITLE
    # =====================================================

    title = (
        item.get("title")
        or item.get("name")
        or ""
    )

    # =====================================================
    # CATEGORY ORDER
    # =====================================================

    categories = [
        "Streaming",
        "Free",
        "Free with Ads",
        "Rent",
        "Buy"
    ]

    # =====================================================
    # DISPLAY
    # =====================================================

    for category in categories:

        group = [
            provider
            for provider in unique
            if provider.get("type") == category
        ]

        if not group:
            continue

        st.html(
            f"""
            <div class="ott-category">
                {html.escape(category)}
            </div>
            """
        )

        # Two cards per row
        for i in range(
            0,
            len(group),
            2
        ):

            row = group[
                i:i + 2
            ]

            columns = st.columns(
                len(row),
                gap="medium"
            )

            for column, provider in zip(
                columns,
                row
            ):

                with column:

                    render_provider(
                        provider,
                        title
                    )


# =========================================================
# MAIN DETAILS PAGE
# =========================================================

def render_movie_details(
    content_id,
    content_type="movie"
):

    # =====================================================
    # BACK
    # =====================================================

    if st.button(
        "← Back",
        key="back_content"
    ):

        st.session_state.open_content = None

        st.session_state.open_movie_id = None

        st.rerun()

    # =====================================================
    # LOAD DETAILS
    # =====================================================

    try:

        if content_type == "tv":

            item = get_tv_details(
                content_id
            )

        else:

            item = get_movie_details(
                content_id
            )

    except TMDBError as error:

        st.error(
            str(error)
        )

        return

    # =====================================================
    # DATA
    # =====================================================

    title = (
        item.get("title")
        or item.get("name")
        or "Untitled"
    )

    overview = (
        item.get("overview")
        or "No description available."
    )

    poster = item.get(
        "poster_url"
    )

    backdrop = item.get(
        "backdrop_url"
    )

    rating = item.get(
        "rating",
        0
    )

    genres = [
        genre.get("name")
        for genre in item.get(
            "genres",
            []
        )
        if genre.get("name")
    ]

    languages = get_languages(
        item
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
    # DETAILS
    # =====================================================

    left, right = st.columns(
        [1, 2.2],
        gap="large"
    )

    with left:

        if poster:

            st.image(
                poster,
                use_container_width=True
            )

    with right:

        st.markdown(
            '<div class="details-title">'
            + html.escape(title)
            + '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="details-description">'
            + html.escape(overview)
            + '</div>',
            unsafe_allow_html=True
        )

        st.write("")

        st.markdown(
            "**★ Rating:** "
            + str(
                round(
                    float(
                        rating or 0
                    ),
                    1
                )
            )
        )

        st.markdown(
            "**Genre:** "
            + (
                ", ".join(genres)
                if genres
                else "Not available"
            )
        )

        st.markdown(
            "**Languages:** "
            + (
                ", ".join(languages)
                if languages
                else "Not available"
            )
        )

        # -------------------------------------------------
        # MOVIE
        # -------------------------------------------------

        if content_type == "movie":

            st.markdown(
                "**Release date:** "
                + str(
                    item.get(
                        "release_date"
                    )
                    or "Not available"
                )
            )

            if item.get("runtime"):

                st.markdown(
                    "**Runtime:** "
                    + str(
                        item.get(
                            "runtime"
                        )
                    )
                    + " min"
                )

        # -------------------------------------------------
        # WEB SERIES
        # -------------------------------------------------

        else:

            st.markdown(
                "**First air date:** "
                + str(
                    item.get(
                        "first_air_date"
                    )
                    or "Not available"
                )
            )

            st.markdown(
                "**Status:** "
                + str(
                    item.get(
                        "status"
                    )
                    or "Not available"
                )
            )

            st.markdown(
                "**Seasons:** "
                + str(
                    item.get(
                        "number_of_seasons",
                        "N/A"
                    )
                )
            )

            st.markdown(
                "**Episodes:** "
                + str(
                    item.get(
                        "number_of_episodes",
                        "N/A"
                    )
                )
            )

    # =====================================================
    # CAST
    # =====================================================

    st.divider()

    st.subheader(
        "Cast & Crew"
    )

    people = get_directors(
        item
    )

    if people:

        if content_type == "movie":

            st.markdown(
                "**Director:** "
                + ", ".join(people)
            )

        else:

            st.markdown(
                "**Creator:** "
                + ", ".join(people)
            )

    cast = get_cast(
        item
    )

    if cast:

        st.markdown(
            "**Cast:** "
            + ", ".join(cast)
        )

    # =====================================================
    # SEASONS
    # =====================================================

    if content_type == "tv":

        seasons = item.get(
            "seasons",
            []
        )

        if seasons:

            st.divider()

            st.subheader(
                "Seasons"
            )

            for season in seasons:

                number = season.get(
                    "season_number"
                )

                if number == 0:
                    continue

                name = (
                    season.get("name")
                    or "Season "
                    + str(number)
                )

                episodes = season.get(
                    "episode_count",
                    0
                )

                air = season.get(
                    "air_date"
                ) or "N/A"

                st.markdown(
                    f"**{html.escape(name)}**"
                    f" • {episodes} episodes"
                    f" • {air}"
                )

    # =====================================================
    # TRAILER
    # =====================================================

    trailer = next(
        (
            video
            for video in item.get(
                "videos",
                {}
            ).get(
                "results",
                []
            )
            if video.get("site") == "YouTube"
            and video.get("type") == "Trailer"
        ),
        None
    )

    if trailer and trailer.get("key"):

        st.divider()

        st.subheader(
            "Trailer"
        )

        st.video(
            "https://www.youtube.com/watch?v="
            + trailer["key"]
        )

    # =====================================================
    # OTT
    # =====================================================

    render_watch_section(
        item,
        content_type
    )

    # =====================================================
    # FOOTER
    # =====================================================

    st.caption(
        "OTT availability data powered by JustWatch through TMDB."
    )

    st.caption(
        "This product uses the TMDB API but is not endorsed or certified by TMDB."
    )
