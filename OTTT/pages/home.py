import html
import streamlit as st

from services.tmdb_service import (
    TMDBError,
    get_now_playing,
    get_popular,
    get_trending,
    get_upcoming,
    get_popular_tv,
    get_trending_tv,
    get_airing_today_tv,
    search_movies,
    search_multi,
    search_tv,
)


def get_results(data):
    if isinstance(data, dict):
        return data.get("results", [])
    return data if isinstance(data, list) else []


def get_title(item):
    return item.get("title") or item.get("name") or "Untitled"


def get_poster(item):
    return item.get("poster_url") or (
        "https://image.tmdb.org/t/p/w500" + item["poster_path"]
        if item.get("poster_path") else None
    )


def get_year(item):
    date = item.get("release_date") or item.get("first_air_date") or ""
    return date[:4] if date else "N/A"


def get_rating(item):
    rating = item.get("rating", item.get("vote_average"))
    try:
        return f"{float(rating):.1f}" if rating is not None else "NR"
    except (TypeError, ValueError):
        return "NR"


def get_language(item):
    return str(item.get("original_language") or item.get("language") or "N/A").upper()


def set_content(item):
    content_id = item.get("id")
    if not content_id:
        return
    content_type = item.get("content_type") or (
        "tv" if item.get("first_air_date") is not None and not item.get("release_date") else "movie"
    )
    st.session_state.open_content = {"id": int(content_id), "type": content_type}
    st.session_state.pop("selected_movie_id", None)
    st.session_state.pop("open_movie_id", None)


def content_card(item, key_suffix=""):
    content_id = item.get("id")
    content_type = item.get("content_type", "movie")
    title = get_title(item)
    poster = get_poster(item)
    year = get_year(item)
    rating = get_rating(item)
    language = get_language(item)
    label = "Series" if content_type == "tv" else "Movie"

    with st.container():
        if poster:
            st.markdown(
                f'<div class="rr-card"><div class="rr-poster-wrap"><img src="{html.escape(poster, quote=True)}" alt="{html.escape(str(title), quote=True)}"></div>'
                f'<div class="rr-card-info"><div class="rr-card-title">{html.escape(str(title))}</div>'
                f'<div class="rr-card-meta"><span class="rr-rating">★</span> {rating} &nbsp;•&nbsp; {year} &nbsp;•&nbsp; {language} &nbsp;•&nbsp; {label}</div></div></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="rr-card"><div class="rr-poster-wrap" style="display:grid;place-items:center;color:#697283">NO POSTER</div>'
                f'<div class="rr-card-info"><div class="rr-card-title">{html.escape(str(title))}</div>'
                f'<div class="rr-card-meta">{label} • {year} • {language}</div></div></div>',
                unsafe_allow_html=True,
            )

        st.markdown('<div class="rr-view-button">', unsafe_allow_html=True)
        if st.button(
            "View Series" if content_type == "tv" else "View Movie",
            key=f"view_{content_type}_{content_id}_{key_suffix}",
            use_container_width=True,
        ):
            set_content(item)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


def section(title, description, items, limit=6):
    st.markdown(
        f'<div class="rr-section-head"><div><div class="rr-section-title">{html.escape(title)}</div><div class="rr-section-subtitle">{html.escape(description)}</div></div></div>',
        unsafe_allow_html=True,
    )
    if not items:
        st.markdown('<div class="rr-empty">No titles available right now.</div>', unsafe_allow_html=True)
        return
    columns = st.columns(min(limit, 6), gap="small")
    for index, item in enumerate(items[:limit]):
        with columns[index % len(columns)]:
            content_card(item, f"{title}_{index}")


def search_area():
    st.markdown('<div class="rr-search-shell">', unsafe_allow_html=True)
    st.markdown('<div class="rr-section-title" style="font-size:18px">Search the ReelRoute catalogue</div>', unsafe_allow_html=True)
    st.caption("Find movies and web series, then open the exact selected title inside ReelRoute.")

    content_type = st.radio(
        "Content type", ["All", "Movies", "Web Series"], horizontal=True,
        key="home_content_type", label_visibility="collapsed"
    )

    with st.form("movie_search_form", clear_on_submit=False):
        col1, col2 = st.columns([5, 1], gap="small")
        with col1:
            query = st.text_input(
                "Title", placeholder="Search a movie or web series…",
                label_visibility="collapsed", key="movie_search_query"
            )
        with col2:
            search_clicked = st.form_submit_button("Search", use_container_width=True)

    if search_clicked:
        if not query.strip():
            st.warning("Please enter a title.")
        else:
            try:
                if content_type == "Movies":
                    data = search_movies(query.strip())
                elif content_type == "Web Series":
                    data = search_tv(query.strip())
                else:
                    data = search_multi(query.strip())
                st.session_state.search_query = query.strip()
                st.session_state.search_results = get_results(data)
            except TMDBError as error:
                st.error(f"Search unavailable: {error}")

    saved_query = st.session_state.get("search_query", "")
    saved_results = st.session_state.get("search_results", [])
    if saved_query:
        st.markdown(
            f'<div class="rr-section-head"><div><div class="rr-section-title">Results for “{html.escape(saved_query)}”</div><div class="rr-section-subtitle">{len(saved_results)} result(s) • Movies and series</div></div></div>',
            unsafe_allow_html=True,
        )
        if saved_results:
            columns = st.columns(6, gap="small")
            for index, item in enumerate(saved_results[:24]):
                with columns[index % 6]:
                    content_card(item, f"search_{index}")
        else:
            st.markdown('<div class="rr-empty">No matching movies or web series found.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_home():
    st.markdown(
        """
        <section class="rr-hero">
            <div class="rr-hero-content">
                <div class="rr-eyebrow">Your cinematic route</div>
                <h1>Every Movie.<br>Every Series.<br>One Place.</h1>
                <p>Discover what to watch, explore complete TMDB details, and find where titles are available to stream, rent, or buy in India.</p>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    search_area()

    try:
        section("Trending Movies", "Popular titles people are discovering right now.", get_results(get_trending()), 6)
    except TMDBError:
        st.warning("Trending movies could not be loaded.")

    try:
        section("Recently Released", "Movies currently listed in theatrical releases.", get_results(get_now_playing()), 6)
    except TMDBError:
        st.warning("Recently released movies could not be loaded.")

    try:
        section("Popular Movies", "Popular movie titles from TMDB.", get_results(get_popular()), 6)
    except TMDBError:
        st.warning("Popular movies could not be loaded.")

    try:
        section("Trending Web Series", "Series people are discovering right now.", get_results(get_trending_tv()), 6)
    except TMDBError:
        st.warning("Trending series could not be loaded.")

    try:
        section("Popular Web Series", "Popular TV and streaming series from TMDB.", get_results(get_popular_tv()), 6)
    except TMDBError:
        st.warning("Popular series could not be loaded.")

    try:
        section("Airing Today", "Series currently airing today.", get_results(get_airing_today_tv()), 6)
    except TMDBError:
        st.warning("Airing series could not be loaded.")

    try:
        section("Coming Soon", "Upcoming movies listed by TMDB.", get_results(get_upcoming()), 6)
    except TMDBError:
        st.warning("Upcoming movies could not be loaded.")

    st.markdown(
        '<div class="rr-panel"><div class="rr-panel-title">OTT availability in India</div><div class="rr-panel-copy">Open any movie or series to see the platforms currently listed by TMDB for India.</div><span class="rr-type-pill">STREAM • RENT • BUY</span></div>',
        unsafe_allow_html=True,
    )
