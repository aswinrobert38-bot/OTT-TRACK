import html
import re
from urllib.parse import quote_plus, unquote

import requests
import streamlit as st

from services.tmdb_service import (
    TMDBError,
    get_movie_details,
    get_tv_details,
    get_watch_providers,
    get_tv_watch_providers,
)


# =========================================================
# GENERAL HELPERS
# =========================================================

def get_languages(item):
    languages = item.get("spoken_languages", [])
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
            str(item.get("original_language")).upper()
        )

    return names


def get_cast(item):
    cast = (
        item.get("credits", {})
        .get("cast", [])
    )

    return [
        person.get("name")
        for person in cast[:10]
        if person.get("name")
    ]


def get_directors(item):
    crew = (
        item.get("credits", {})
        .get("crew", [])
    )

    return list(
        dict.fromkeys(
            person.get("name")
            for person in crew
            if person.get("job") in (
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
        "flatrate": "Streaming",
        "free": "Free",
        "ads": "Free with Ads",
        "rent": "Rent",
        "buy": "Buy",
    }.get(
        category,
        str(category).title()
    )


# =========================================================
# INDIA PROVIDERS
# =========================================================

def get_india_providers(provider_data):

    india = (
        provider_data.get("results", {})
        .get("IN", {})
    )

    providers = []

    categories = [
        "flatrate",
        "free",
        "ads",
        "rent",
        "buy",
    ]

    for category in categories:

        for provider in india.get(category, []):

            logo = provider.get("logo_path")

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
                    ),
                }
            )

    return providers


# =========================================================
# PROVIDER CONFIGURATION
# =========================================================

PROVIDER_CONFIG = {

    "netflix": {
        "domain": "netflix.com",
        "search": "https://www.netflix.com/search?q={query}",
        "patterns": [
            r"https?://(?:www\.)?netflix\.com/title/\d+",
        ],
    },

    "prime video": {
        "domain": "primevideo.com",
        "search": (
            "https://www.primevideo.com/search/"
            "ref=atv_nb_sr?phrase={query}"
        ),
        "patterns": [
            r"https?://(?:www\.)?primevideo\.com/detail/[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]+",
        ],
    },

    "amazon": {
        "domain": "primevideo.com",
        "search": (
            "https://www.primevideo.com/search/"
            "ref=atv_nb_sr?phrase={query}"
        ),
        "patterns": [
            r"https?://(?:www\.)?primevideo\.com/detail/[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]+",
        ],
    },

    "jiohotstar": {
        "domain": "hotstar.com",
        "search": (
            "https://www.hotstar.com/in/search?q={query}"
        ),
        "patterns": [
            r"https?://(?:www\.)?hotstar\.com/in/[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]+",
        ],
    },

   "jiohotstar": {
    "domain": "hotstar.com",
    "search": (
        "https://www.hotstar.com/in/search?q={query}"
    ),
    "patterns": [],
},
    "sony liv": {
        "domain": "sonyliv.com",
        "search": (
            "https://www.sonyliv.com/search/{query}"
        ),
        "patterns": [
            r"https?://(?:www\.)?sonyliv\.com/[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]+",
        ],
    },

    "zee5": {
        "domain": "zee5.com",
        "search": (
            "https://www.zee5.com/search?q={query}"
        ),
        "patterns": [
            r"https?://(?:www\.)?zee5\.com/[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]+",
        ],
    },

    "youtube": {
        "domain": "youtube.com",
        "search": (
            "https://www.youtube.com/results?"
            "search_query={query}"
        ),
        "patterns": [
            r"https?://(?:www\.)?youtube\.com/watch\?v=[A-Za-z0-9_-]+",
        ],
    },

    "apple tv": {
        "domain": "tv.apple.com",
        "search": (
            "https://tv.apple.com/in/search?term={query}"
        ),
        "patterns": [
            r"https?://tv\.apple\.com/in/[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]+",
        ],
    },

    "aha": {
        "domain": "aha.video",
        "search": (
            "https://www.aha.video/search/{query}"
        ),
        "patterns": [
            r"https?://(?:www\.)?aha\.video/[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]+",
        ],
    },

    "mx player": {
        "domain": "mxplayer.in",
        "search": (
            "https://www.mxplayer.in/search/{query}"
        ),
        "patterns": [
            r"https?://(?:www\.)?mxplayer\.in/[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]+",
        ],
    },

    "lionsgate play": {
        "domain": "lionsgateplay.com",
        "search": (
            "https://www.lionsgateplay.com/search?q={query}"
        ),
        "patterns": [
            r"https?://(?:www\.)?lionsgateplay\.com/[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]+",
        ],
    },

    "discovery+": {
        "domain": "discoveryplus.in",
        "search": (
            "https://www.discoveryplus.in/search?q={query}"
        ),
        "patterns": [
            r"https?://(?:www\.)?discoveryplus\.in/[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]+",
        ],
    },

    "crunchyroll": {
        "domain": "crunchyroll.com",
        "search": (
            "https://www.crunchyroll.com/search?q={query}"
        ),
        "patterns": [
            r"https?://(?:www\.)?crunchyroll\.com/[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]+",
        ],
    },

    "sun nxt": {
        "domain": "sunnxt.com",
        "search": (
            "https://www.sunnxt.com/search/{query}"
        ),
        "patterns": [
            r"https?://(?:www\.)?sunnxt\.com/[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]+",
        ],
    },

    "manorama": {
        "domain": "manoramamax.com",
        "search": (
            "https://www.manoramamax.com/search/{query}"
        ),
        "patterns": [
            r"https?://(?:www\.)?manoramamax\.com/[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]+",
        ],
    },
}


# =========================================================
# NORMALIZE PROVIDER NAME
# =========================================================

def get_provider_config(provider_name):

    name = (
        provider_name
        .strip()
        .lower()
    )

    if "netflix" in name:
        return PROVIDER_CONFIG["netflix"]

    if (
        "prime video" in name
        or "amazon prime" in name
        or name == "amazon"
    ):
        return PROVIDER_CONFIG["prime video"]

    if (
        "jiohotstar" in name
        or "jio hotstar" in name
    ):
        return PROVIDER_CONFIG["jiohotstar"]

    if "hotstar" in name:
        return PROVIDER_CONFIG["hotstar"]

    if "sony liv" in name:
        return PROVIDER_CONFIG["sony liv"]

    if "zee5" in name:
        return PROVIDER_CONFIG["zee5"]

    if "youtube" in name:
        return PROVIDER_CONFIG["youtube"]

    if "apple tv" in name:
        return PROVIDER_CONFIG["apple tv"]

    if name == "aha" or name.startswith("aha "):
        return PROVIDER_CONFIG["aha"]

    if "mx player" in name:
        return PROVIDER_CONFIG["mx player"]

    if "lionsgate" in name:
        return PROVIDER_CONFIG["lionsgate play"]

    if "discovery" in name:
        return PROVIDER_CONFIG["discovery+"]

    if "crunchyroll" in name:
        return PROVIDER_CONFIG["crunchyroll"]

    if "sun nxt" in name:
        return PROVIDER_CONFIG["sun nxt"]

    if "manorama" in name:
        return PROVIDER_CONFIG["manorama"]

    return None


# =========================================================
# FALLBACK PROVIDER SEARCH URL
# =========================================================

def provider_search_url(provider_name, title):

    config = get_provider_config(
        provider_name
    )

    query = quote_plus(
        title.strip()
    )

    if config:
        return config["search"].format(
            query=query
        )

    return None


# =========================================================
# EXTRACT URL FROM SEARCH RESULT
# =========================================================

def clean_result_url(url):

    if not url:
        return None

    url = html.unescape(url)

    url = url.replace(
        "&amp;",
        "&"
    )

    # Remove Bing redirect wrappers
    if "u=" in url and (
        "bing.com/ck/a" in url
        or "bing.com/aclick" in url
    ):
        match = re.search(
            r"[?&]u=([^&]+)",
            url
        )

        if match:
            try:
                url = unquote(
                    match.group(1)
                )
            except Exception:
                pass

    return url


# =========================================================
# VERIFY URL BELONGS TO PROVIDER
# =========================================================

def is_provider_url(url, domain):

    if not url:
        return False

    value = url.lower()

    return (
        domain.lower() in value
        and not any(
            blocked in value
            for blocked in [
                "/search",
                "search?",
                "/browse",
                "/collections",
            ]
        )
    )


# =========================================================
# EXACT OTT LINK RESOLVER
# =========================================================

@st.cache_data(
    ttl=60 * 60 * 12,
    show_spinner=False
)
def resolve_exact_ott_url(
    provider_name,
    title
):

    config = get_provider_config(
        provider_name
    )

    if not config:
        return None

    domain = config["domain"]

    # Search query specifically restricted
    # to the OTT provider's domain.
    search_query = (
        f'site:{domain} "{title}"'
    )

    bing_url = (
        "https://www.bing.com/search?q="
        + quote_plus(search_query)
    )

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/153.0 Safari/537.36"
        )
    }

    try:

        response = requests.get(
            bing_url,
            headers=headers,
            timeout=8
        )

        if response.status_code != 200:
            return None

        page = response.text

    except Exception:
        return None

    # -----------------------------------------------------
    # First try provider-specific URL patterns
    # -----------------------------------------------------

    for pattern in config["patterns"]:

        matches = re.findall(
            pattern,
            page,
            flags=re.IGNORECASE
        )

        for match in matches:

            url = clean_result_url(
                match
            )

            if is_provider_url(
                url,
                domain
            ):

                return url

    # -----------------------------------------------------
    # Generic href extraction
    # -----------------------------------------------------

    hrefs = re.findall(
        r'href=["\']([^"\']+)["\']',
        page,
        flags=re.IGNORECASE
    )

    for href in hrefs:

        url = clean_result_url(
            href
        )

        if not is_provider_url(
            url,
            domain
        ):
            continue

        # Ignore generic provider pages
        lowered = url.lower()

        if lowered.endswith(
            (
                ".com",
                ".in",
                ".com/",
                ".in/",
            )
        ):
            continue

        return url

    return None


# =========================================================
# RESOLVE FINAL OTT URL
# =========================================================

def get_final_ott_url(provider, title):

    provider_name = provider.get(
        "name",
        ""
    ).strip().lower()

    # =====================================================
    # JIOHOTSTAR
    # =====================================================
    #
    # Do NOT use the external search-engine resolver here.
    # Hotstar URLs can change and stale title URLs can cause
    # BFF_102 / "Something went wrong".
    #
    if (
        "jiohotstar" in provider_name
        or "jio hotstar" in provider_name
        or "hotstar" in provider_name
    ):

        query = quote_plus(
            title.strip()
        )

        return (
            "https://www.hotstar.com/in/search?q="
            + query
        )

    # =====================================================
    # OTHER PROVIDERS
    # =====================================================

    exact_url = resolve_exact_ott_url(
        provider_name,
        title
    )

    if exact_url:
        return exact_url

    # =====================================================
    # PROVIDER SEARCH FALLBACK
    # =====================================================

    search_url = provider_search_url(
        provider_name,
        title
    )

    if search_url:
        return search_url

    # =====================================================
    # TMDB / JUSTWATCH FALLBACK
    # =====================================================

    return provider.get(
        "tmdb_link"
    )


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
    # RESOLVE EXACT LINK
    # -----------------------------------------------------

    with st.spinner(
        f"Finding {name} title..."
    ):

        url = get_final_ott_url(
            provider,
            title
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
        href="{html.escape(url, quote=True)}"
        target="_blank"
        rel="noopener noreferrer"
        class="ott-card"
        title="Open {html.escape(title)} on {html.escape(name)}"
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
            transform: translateY(-4px);

            border-color:
                rgba(32,215,215,0.65);

            background:
                linear-gradient(
                    145deg,
                    rgba(32,215,215,0.14),
                    rgba(255,255,255,0.045)
                );

            box-shadow:
                0 12px 30px
                rgba(0,0,0,0.30);
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
            Click an OTT platform to open this title
        </div>
        """
    )

    # =====================================================
    # GET OTT DATA
    # =====================================================

    try:

        if content_type == "tv":

            provider_data = (
                get_tv_watch_providers(
                    item["id"]
                )
            )

        else:

            provider_data = (
                get_watch_providers(
                    item["id"]
                )
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
        "Buy",
    ]

    # =====================================================
    # DISPLAY
    # =====================================================

    for category in categories:

        group = [
            provider
            for provider in unique
            if provider.get("type")
            == category
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

        st.error(str(error))
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

        try:
            rating_value = round(
                float(rating or 0),
                1
            )
        except Exception:
            rating_value = 0

        st.markdown(
            "**★ Rating:** "
            + str(rating_value)
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
                    f"**{html.escape(name)}** "
                    f"• {episodes} episodes "
                    f"• {html.escape(str(air))}"
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
            if video.get("site")
            == "YouTube"
            and video.get("type")
            == "Trailer"
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
        "This product uses the TMDB API but is not endorsed "
        "or certified by TMDB."
    )
