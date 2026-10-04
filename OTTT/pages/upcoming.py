import html
import streamlit as st
from services.tmdb_service import TMDBError, get_upcoming
from pages.home import content_card


def render_upcoming():
    st.markdown('<div class="rr-section-title">Coming Soon</div><div class="rr-section-subtitle">Upcoming movies listed by TMDB.</div>', unsafe_allow_html=True)
    try:
        movies = get_upcoming().get("results", [])
    except TMDBError as error:
        st.error(str(error))
        return
    if not movies:
        st.markdown('<div class="rr-empty">No upcoming movies found.</div>', unsafe_allow_html=True)
        return
    columns = st.columns(6, gap="small")
    for index, movie in enumerate(movies[:24]):
        with columns[index % 6]:
            content_card(movie, f"upcoming_{index}")
