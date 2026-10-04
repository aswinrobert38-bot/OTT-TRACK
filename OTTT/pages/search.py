import html
import streamlit as st

from services.tmdb_service import TMDBError, search_movies, search_tv, search_multi
from pages.home import content_card, get_results


def render_search():
    st.markdown(
        '''
        <div class="rr-hero" style="min-height:260px">
            <div class="rr-hero-content">
                <div class="rr-eyebrow">Discover</div>
                <h1 style="font-size:clamp(34px,5vw,58px)">Find your next watch.</h1>
                <p>Search movies and web series, then open the exact result inside ReelRoute.</p>
            </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

    content_type = st.radio(
        "Content type", ["All", "Movies", "Web Series"],
        horizontal=True, key="search_page_content_type",
    )
    query = st.text_input(
        "Title", placeholder="Search a movie or web series…",
        key="search_page_query", label_visibility="collapsed",
    )

    if not query.strip():
        st.markdown(
            '<div class="rr-empty"><b>Search the catalogue</b><br>Try a movie title, actor name, or web series.</div>',
            unsafe_allow_html=True,
        )
        return

    try:
        if content_type == "Movies":
            data = search_movies(query.strip())
        elif content_type == "Web Series":
            data = search_tv(query.strip())
        else:
            data = search_multi(query.strip())
        results = get_results(data)
    except TMDBError as error:
        st.error(str(error))
        return

    st.markdown(
        f'<div class="rr-section-head"><div><div class="rr-section-title">Results for “{html.escape(query.strip())}”</div><div class="rr-section-subtitle">{len(results)} result(s)</div></div></div>',
        unsafe_allow_html=True,
    )

    if not results:
        st.markdown('<div class="rr-empty">No matching movies or web series were found.</div>', unsafe_allow_html=True)
        return

    columns = st.columns(6, gap="small")
    for index, item in enumerate(results[:24]):
        with columns[index % 6]:
            content_card(item, f"standalone_search_{index}")
