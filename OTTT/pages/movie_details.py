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
    languages = item.get("spoken_languages", [])
    names = []

    for language in languages:
        name = language.get("english_name") or language.get("name")

        if name and name not in names:
            names.append(name)

    if not names and item.get("original_language"):
        names.append(
            str(item.get("original_language")).upper()
        )

    return names


def get_cast(item):
    cast = item.get("credits", {}).get("cast", [])

    return [
        person.get("name")
        for person in cast[:10]
        if person.get("name")
    ]


def get_directors(item):
    crew = item.get("credits", {}).get("crew", [])

    return list(
        dict.fromkeys(
            person.get("name")
            for person in crew
            if person.get("job") in ("Director", "Creator")
            and person.get("name")
        )
    )


# =========================================================
# OTT HELPERS
# =========================================================

def get_provider_type(value):

    return {
        "flatrate": "Streaming",
        "free": "Free",
        "ads": "Free with Ads",
        "rent": "Rent",
        "buy": "Buy",
    }.get(
        value,
        str(value).title()
    )


def get_india_providers(provider_data):

    india = provider_data.get(
        "results",
        {}
    ).get(
        "IN",
        {}
    )

    providers = []

    for category in (
        "flatrate",
        "free",
        "ads",
        "rent",
        "buy"
    ):

        for provider in india.get(
            category,
            []
        ):

            logo = provider.get(
                "logo_path"
            )

            providers.append(
                {
                    "id": provider.get(
                        "provider_id"
                    ),

                    "name": provider.get(
                        "provider_name",
                        "Unknown"
                    ),

                    "logo": (
                        "https://image.tmdb.org/t/p/w92"
                        + logo
                        if logo
                        else None
                    ),

                    "type": get_provider_type(
                        category
                    ),

                    "tmdb_link": india.get(
                        "link"
                    )
                }
            )

    return providers


# =========================================================
# OTT SEARCH / REDIRECTION
# =========================================================

def provider_search_url(name, title):

    query = quote_plus(
        title
    )

    provider = name.lower()

    # Netflix
    if "netflix" in provider:

        return (
            "https://www.netflix.com/search?q="
            + query
        )

    # Prime Video / Amazon
    if (
        "amazon" in provider
        or "prime video" in provider
        or "amazon prime" in provider
    ):

        return (
            "https://www.primevideo.com/search/ref=atv_nb_sr?phrase="
            + query
        )

    # YouTube
    if "youtube" in provider:

        return (
            "https://www.youtube.com/results?search_query="
            + query
        )

    # Apple TV
    if "apple tv" in provider:

        return (
            "https://tv.apple.com/in/search?term="
            + query
        )

    # JioHotstar
    if (
        "hotstar" in provider
        or "jiohotstar" in provider
        or "jio hotstar" in provider
    ):

        return (
            "https://www.hotstar.com/in/search?q="
            + query
        )

    # Sony LIV
    if "sony liv" in provider:

        return (
            "https://www.sonyliv.com/search/"
            + query
        )

    # ZEE5
    if "zee5" in provider:

        return (
            "https://www.zee5.com/search?q="
            + query
        )

    # Aha
    if "aha" in provider:

        return (
            "https://www.aha.video/search/"
            + query
        )

    # MX Player
    if "mx player" in provider:

        return (
            "https://www.mxplayer.in/search/"
            + query
        )

    # Lionsgate Play
    if "lionsgate" in provider:

        return (
            "https://www.lionsgateplay.com/search?q="
            + query
        )

    # Discovery+
    if "discovery" in provider:

        return (
            "https://www.discoveryplus.in/search?q="
            + query
        )

    # Crunchyroll
    if "crunchyroll" in provider:

        return (
            "https://www.crunchyroll.com/search?q="
            + query
        )

    # Sun NXT
    if "sun nxt" in provider:

        return (
            "https://www.sunnxt.com/search/"
            + query
        )

    # ManoramaMAX
    if "manorama" in provider:

        return (
            "https://www.manoramamax.com/search/"
            + query
        )

    return None


# =========================================================
# OTT CARD
# =========================================================

def render_provider(provider, title):

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

    url = provider_search_url(
        name,
        title
    )

    # Fallback to TMDB/JustWatch
    if not url:
        url = provider.get(
            "tmdb_link"
        )

    if not url:
        return

    # Logo
    if logo:

        logo_html = f"""
        <img
            src="{html.escape(logo)}"
            class="ott-logo"
        >
        """

    else:

        logo_html = """
        <div class="ott-logo-placeholder">
            ▶
        </div>
        """

    # Complete card
    card_html = f"""
    <a
        href="{html.escape(url)}"
        target="_blank"
        rel="noopener noreferrer"
        class="ott-card"
    >

        <div class="ott-icon-area">
            {logo_html}
        </div>

        <div class="ott-info">

            <div class="ott-name">
                {html.escape(name)}
            </div>

            <div class="ott-type">
                {html.escape(provider_type)}
            </div>

        </div>

        <div class="ott-arrow">
            ↗
        </div>

    </a>
    """

    # IMPORTANT:
    # Use st.html(), NOT st.markdown()
    st.html(card_html)


# =========================================================
# OTT SECTION
# =========================================================

def render_watch_section(item, content_type):

    # -----------------------------------------------------
    # OTT CSS
    # -----------------------------------------------------

    st.html(
        """
        <style>

        .ott-section-title {
            font-size: 30px;
            font-weight: 800;
            margin-top: 10px;
            margin-bottom: 4px;
        }

        .ott-section-subtitle {
            font-size: 14px;
            opacity: 0.65;
            margin-bottom: 22px;
        }

        .ott-category {
            font-size: 18px;
            font-weight: 700;
            margin-top: 18px;
            margin-bottom: 12px;
        }

        .ott-card {
            display: flex;
            align-items: center;

            gap: 12px;

            min-height: 82px;

            width: 100%;

            padding: 12px 14px;

            margin-bottom: 12px;

            border-radius: 18px;

            box-sizing: border-box;

            text-decoration: none !important;

            color: inherit !important;

            background:
                linear-gradient(
                    145deg,
                    rgba(255,255,255,0.09),
                    rgba(255,255,255,0.025)
                );

            border:
                1px solid
                rgba(255,255,255,0.10);

            transition:
                transform 0.2s ease,
                border-color 0.2s ease,
                background 0.2s ease;

        }

        .ott-card:hover {

            transform:
                translateY(-4px);

            border-color:
                rgba(255,255,255,0.30);

            background:
                linear-gradient(
                    145deg,
                    rgba(255,255,255,0.15),
                    rgba(255,255,255,0.05)
                );

        }

        .ott-icon-area {

            width: 54px;

            height: 54px;

            min-width: 54px;

            border-radius: 14px;

            display: flex;

            align-items: center;

            justify-content: center;

            background:
                rgba(255,255,255,0.08);

            overflow: hidden;

        }

        .ott-logo {

            width: 46px;

            height: 46px;

            object-fit: cover;

            border-radius: 11px;

            display: block;

        }

        .ott-logo-placeholder {

            font-size: 23px;

        }

        .ott-info {

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

            margin-top: 3px;

        }

        .ott-arrow {

            font-size: 22px;

            opacity: 0.55;

            padding-left: 5px;

        }

        </style>
        """
    )

    # -----------------------------------------------------
    # TITLE
    # -----------------------------------------------------

    st.divider()

    st.html(
        """
        <div class="ott-section-title">
            Where to Watch in India
        </div>

        <div class="ott-section-subtitle">
            Available streaming platforms for this title
        </div>
        """
    )

    # -----------------------------------------------------
    # GET PROVIDERS
    # -----------------------------------------------------

    try:

        if content_type == "tv":

            data = get_tv_watch_providers(
                item["id"]
            )

        else:

            data = get_watch_providers(
                item["id"]
            )

        providers = get_india_providers(
            data
        )

        if not providers:

            st.info(
                "No OTT availability found in India."
            )

            return

        # -------------------------------------------------
        # REMOVE DUPLICATES
        # -------------------------------------------------

        unique = []

        seen = set()

        for provider in providers:

            key = (
                provider["id"],
                provider["type"]
            )

            if key not in seen:

                seen.add(key)

                unique.append(
                    provider
                )

        title = (
            item.get("title")
            or item.get("name")
            or ""
        )

        # -------------------------------------------------
        # CATEGORIES
        # -------------------------------------------------

        categories = (
            "Streaming",
            "Free",
            "Free with Ads",
            "Rent",
            "Buy"
        )

        for category in categories:

            group = [
                provider
                for provider in unique
                if provider["type"] == category
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

            # ---------------------------------------------
            # 2 CARDS PER ROW
            # ---------------------------------------------

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

    except TMDBError as error:

        st.error(
            "Unable to load India OTT availability: "
            + str(error)
        )


# =========================================================
# MAIN DETAILS PAGE
# =========================================================

def render_movie_details(
    content_id,
    content_type="movie"
):

    # -----------------------------------------------------
    # BACK
    # -----------------------------------------------------

    if st.button(
        "← Back",
        key="back_content"
    ):

        st.session_state.open_content = None

        st.session_state.open_movie_id = None

        st.rerun()

    # -----------------------------------------------------
    # GET CONTENT
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # BASIC INFORMATION
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # BACKDROP
    # -----------------------------------------------------

    if backdrop:

        st.image(
            backdrop,
            use_container_width=True
        )

    # -----------------------------------------------------
    # MAIN DETAILS
    # -----------------------------------------------------

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
    # CAST & CREW
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
    # WEB SERIES SEASONS
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

                # Skip specials
                if number == 0:
                    continue

                name = (
                    season.get("name")
                    or (
                        "Season "
                        + str(number)
                    )
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
