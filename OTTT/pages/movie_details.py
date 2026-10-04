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


def get_languages(item):
    names = []
    for language in item.get("spoken_languages", []):
        name = language.get("english_name") or language.get("name")
        if name and name not in names:
            names.append(name)
    if not names and item.get("original_language"):
        names.append(str(item["original_language"]).upper())
    return names


def get_cast(item):
    return [
        person.get("name")
        for person in item.get("credits", {}).get("cast", [])[:10]
        if person.get("name")
    ]


def get_directors(item):
    return list(dict.fromkeys(
        person.get("name")
        for person in item.get("credits", {}).get("crew", [])
        if person.get("job") in ("Director", "Creator") and person.get("name")
    ))


def get_provider_type(category):
    return {
        "flatrate": "Streaming",
        "free": "Free",
        "ads": "Free with Ads",
        "rent": "Rent",
        "buy": "Buy",
    }.get(category, str(category).title())


def get_india_providers(provider_data):
    india = provider_data.get("results", {}).get("IN", {})
    providers = []
    for category in ("flatrate", "free", "ads", "rent", "buy"):
        for provider in india.get(category, []):
            logo = provider.get("logo_path")
            providers.append({
                "id": provider.get("provider_id"),
                "name": provider.get("provider_name", "Unknown"),
                "logo": f"https://image.tmdb.org/t/p/w92{logo}" if logo else None,
                "type": get_provider_type(category),
                "tmdb_link": india.get("link"),
            })
    return providers


# Provider search URLs are deliberately explicit. We do not scrape Bing/Google
# and we never invent a title-specific deep link.
PROVIDER_CONFIG = {
    "netflix": "https://www.netflix.com/search?q={query}",
    "prime video": "https://www.primevideo.com/search/ref=atv_nb_sr?phrase={query}",
    "amazon": "https://www.primevideo.com/search/ref=atv_nb_sr?phrase={query}",
    "jiohotstar": "https://www.hotstar.com/in/search?q={query}",
    "sony liv": "https://www.sonyliv.com/search/{query}",
    "zee5": "https://www.zee5.com/search?q={query}",
    "youtube": "https://www.youtube.com/results?search_query={query}",
    "apple tv": "https://tv.apple.com/in/search?term={query}",
    "aha": "https://www.aha.video/search/{query}",
    "mx player": "https://www.mxplayer.in/search/{query}",
    "lionsgate play": "https://www.lionsgateplay.com/search?q={query}",
    "discovery+": "https://www.discoveryplus.in/search?q={query}",
    "crunchyroll": "https://www.crunchyroll.com/search?q={query}",
    "sun nxt": "https://www.sunnxt.com/search/{query}",
    "manorama": "https://www.manoramamax.com/search/{query}",
}


def get_provider_search_url(provider_name, title):
    name = provider_name.strip().lower()
    key = None
    if "netflix" in name:
        key = "netflix"
    elif "prime video" in name or "amazon prime" in name or name == "amazon":
        key = "prime video"
    elif "jiohotstar" in name or "jio hotstar" in name or "hotstar" in name:
        key = "jiohotstar"
    elif "sony liv" in name:
        key = "sony liv"
    elif "zee5" in name:
        key = "zee5"
    elif "youtube" in name:
        key = "youtube"
    elif "apple tv" in name:
        key = "apple tv"
    elif name == "aha" or name.startswith("aha "):
        key = "aha"
    elif "mx player" in name:
        key = "mx player"
    elif "lionsgate" in name:
        key = "lionsgate play"
    elif "discovery" in name:
        key = "discovery+"
    elif "crunchyroll" in name:
        key = "crunchyroll"
    elif "sun nxt" in name:
        key = "sun nxt"
    elif "manorama" in name:
        key = "manorama"
    if not key:
        return None
    return PROVIDER_CONFIG[key].format(query=quote_plus(title.strip()))


def get_final_ott_url(provider, title):
    """Return a reliable provider search URL, otherwise TMDB/JustWatch fallback."""
    url = get_provider_search_url(provider.get("name", ""), title)
    return url or provider.get("tmdb_link")


def render_watch_section(item, content_type):
    st.markdown(
        '<div class="rr-panel"><div class="rr-panel-title">Where to Watch in India</div><div class="rr-panel-copy">Availability comes from TMDB/JustWatch provider data. Provider links open in a new browser tab.</div>',
        unsafe_allow_html=True,
    )

    try:
        provider_data = (
            get_tv_watch_providers(item["id"])
            if content_type == "tv"
            else get_watch_providers(item["id"])
        )
    except TMDBError as error:
        st.error(f"Unable to load OTT availability: {error}")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    providers = get_india_providers(provider_data)
    if not providers:
        st.markdown('<div class="rr-empty">No India availability is currently listed for this title.</div></div>', unsafe_allow_html=True)
        return

    unique = []
    seen = set()
    for provider in providers:
        key = (provider.get("id"), provider.get("type"))
        if key not in seen:
            seen.add(key)
            unique.append(provider)

    groups = [
        ("Streaming", [p for p in unique if p["type"] == "Streaming"]),
        ("Free", [p for p in unique if p["type"] == "Free"]),
        ("Free with Ads", [p for p in unique if p["type"] == "Free with Ads"]),
        ("Rent", [p for p in unique if p["type"] == "Rent"]),
        ("Buy", [p for p in unique if p["type"] == "Buy"]),
    ]

    for category, group in groups:
        if not group:
            continue
        st.markdown(f'<div style="color:#AEB6C4;font-size:12px;font-weight:850;text-transform:uppercase;letter-spacing:.8px;margin:18px 0 9px">{html.escape(category)}</div>', unsafe_allow_html=True)
        columns = st.columns(min(3, len(group)), gap="small")
        for index, provider in enumerate(group):
            with columns[index % len(columns)]:
                url = get_final_ott_url(provider, item.get("title") or item.get("name") or "")
                if not url:
                    continue
                logo = provider.get("logo")
                logo_html = (
                    f'<img class="rr-ott-logo" src="{html.escape(logo, quote=True)}" alt="">'
                    if logo else '<div class="rr-ott-logo" style="display:grid;place-items:center">▶</div>'
                )
                card = (
                    f'<a class="rr-ott-card" href="{html.escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">'
                    f'{logo_html}<div><div class="rr-ott-name">{html.escape(provider["name"])}</div>'
                    f'<div class="rr-ott-type">{html.escape(provider["type"])} • Open in new tab</div></div>'
                    f'<div class="rr-ott-arrow">↗</div></a>'
                )
                st.markdown(card, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def render_movie_details(content_id, content_type="movie"):
    # The selected ID and type are passed directly from the single navigation
    # object. Never infer type from title/poster data here.
    try:
        item = get_tv_details(content_id) if content_type == "tv" else get_movie_details(content_id)
    except TMDBError as error:
        st.error(str(error))
        if st.button("← Back to ReelRoute"):
            st.session_state.open_content = None
            st.rerun()
        return

    title = item.get("title") or item.get("name") or "Untitled"
    overview = item.get("overview") or "No description available."
    poster = item.get("poster_url")
    backdrop = item.get("backdrop_url")
    rating = item.get("rating", 0)
    genres = [g.get("name") for g in item.get("genres", []) if g.get("name")]
    languages = get_languages(item)
    content_label = "Web Series" if content_type == "tv" else "Movie"

    if st.button("← Back to ReelRoute", key="details_back"):
        st.session_state.open_content = None
        st.rerun()

    backdrop_html = (
        f'<img class="rr-details-backdrop" src="{html.escape(backdrop, quote=True)}" alt="">'
        if backdrop else ""
    )
    poster_html = (
        f'<img class="rr-details-poster" src="{html.escape(poster, quote=True)}" alt="{html.escape(title, quote=True)}">'
        if poster else '<div class="rr-details-poster" style="height:360px;display:grid;place-items:center;background:#11151C;color:#697283">NO POSTER</div>'
    )

    try:
        rating_value = f"{float(rating or 0):.1f}"
    except (TypeError, ValueError):
        rating_value = "NR"

    if content_type == "tv":
        date_label, date_value = "First Air", item.get("first_air_date") or "Not available"
        extra_label, extra_value = "Seasons", item.get("number_of_seasons", "N/A")
        extra2_label, extra2_value = "Episodes", item.get("number_of_episodes", "N/A")
    else:
        date_label, date_value = "Release", item.get("release_date") or "Not available"
        extra_label, extra_value = "Runtime", f'{item.get("runtime")} min' if item.get("runtime") else "Not available"
        extra2_label, extra2_value = "Type", "Movie"

    chips = ''.join(f'<span class="rr-chip">{html.escape(g)}</span>' for g in genres)
    st.markdown(
        f'''
        <section class="rr-details-hero">
            {backdrop_html}
            <div class="rr-details-shade"></div>
            <div class="rr-details-content">
                <div>{poster_html}</div>
                <div>
                    <span class="rr-type-pill">{html.escape(content_label)}</span>
                    <div class="rr-details-title">{html.escape(title)}</div>
                    <div class="rr-details-overview">{html.escape(overview)}</div>
                    <div class="rr-chip-row">{chips}</div>
                    <div class="rr-detail-grid">
                        <div class="rr-stat"><div class="rr-stat-label">TMDB Rating</div><div class="rr-stat-value">★ {rating_value}</div></div>
                        <div class="rr-stat"><div class="rr-stat-label">{html.escape(date_label)}</div><div class="rr-stat-value">{html.escape(str(date_value))}</div></div>
                        <div class="rr-stat"><div class="rr-stat-label">{html.escape(extra_label)}</div><div class="rr-stat-value">{html.escape(str(extra_value))}</div></div>
                        <div class="rr-stat"><div class="rr-stat-label">{html.escape(extra2_label)}</div><div class="rr-stat-value">{html.escape(str(extra2_value))}</div></div>
                    </div>
                </div>
            </div>
        </section>
        ''',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="rr-panel"><div class="rr-panel-title">Overview</div><div class="rr-panel-copy">{html.escape(overview)}</div>'
        f'<div class="rr-chip-row"><span class="rr-chip">Languages: {html.escape(", ".join(languages) if languages else "Not available")}</span>'
        f'<span class="rr-chip">TMDB ID: {html.escape(str(content_id))}</span></div></div>',
        unsafe_allow_html=True,
    )

    people = get_directors(item)
    cast = get_cast(item)
    if people or cast:
        st.markdown('<div class="rr-panel"><div class="rr-panel-title">Cast & Crew</div>', unsafe_allow_html=True)
        if people:
            role = "Creator" if content_type == "tv" else "Director"
            st.markdown(f'<div class="rr-panel-copy"><b style="color:#F5F7FA">{role}:</b> {html.escape(", ".join(people))}</div>', unsafe_allow_html=True)
        if cast:
            st.markdown(f'<div class="rr-panel-copy"><b style="color:#F5F7FA">Cast:</b> {html.escape(", ".join(cast))}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if content_type == "tv":
        seasons = [s for s in item.get("seasons", []) if s.get("season_number") != 0]
        if seasons:
            rows = ''.join(
                f'<div class="rr-stat" style="margin-bottom:8px"><div class="rr-stat-value">{html.escape(str(s.get("name") or "Season "+str(s.get("season_number"))))}</div>'
                f'<div class="rr-stat-label">{s.get("episode_count", 0)} episodes • {html.escape(str(s.get("air_date") or "N/A"))}</div></div>'
                for s in seasons
            )
            st.markdown(f'<div class="rr-panel"><div class="rr-panel-title">Seasons</div>{rows}</div>', unsafe_allow_html=True)

    trailer = next(
        (v for v in item.get("videos", {}).get("results", []) if v.get("site") == "YouTube" and v.get("type") == "Trailer" and v.get("key")),
        None,
    )
    if trailer:
        st.markdown('<div class="rr-panel"><div class="rr-panel-title">Trailer</div><div class="rr-panel-copy">Official trailer</div>', unsafe_allow_html=True)
        st.video(f'https://www.youtube.com/watch?v={trailer["key"]}')
        st.markdown('</div>', unsafe_allow_html=True)

    render_watch_section(item, content_type)

    st.caption("OTT availability data is supplied through TMDB/JustWatch provider data. ReelRoute does not guarantee availability or platform ownership.")
    st.caption("This product uses the TMDB API but is not endorsed or certified by TMDB.")
