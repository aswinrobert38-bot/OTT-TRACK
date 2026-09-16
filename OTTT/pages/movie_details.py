import streamlit as st
from services.tmdb_service import TMDBError, get_movie, normalize_details
from utils.helpers import safe_text


def _status_badge(status):
    if status == "Date Not Announced":
        return '<span class="badge badge-yellow">DATE TBD</span>'
    if status == "Confirmed":
        return '<span class="badge badge-green">CONFIRMED</span>'
    return '<span class="badge badge-gray">NOT CONFIRMED</span>'


def render_movie_details(movie_id):
    if st.button("← Back", key="back_movie"):
        st.session_state.selected_movie_id = None
        st.rerun()

    try:
        movie = normalize_details(get_movie(int(movie_id)))
    except (TMDBError, ValueError) as exc:
        st.error(str(exc))
        return

    if movie.get("backdrop"):
        st.image(movie["backdrop"], use_container_width=True)

    left, right = st.columns([1, 2.25], gap="large")
    with left:
        if movie.get("poster"):
            st.image(movie["poster"], use_container_width=True)
        else:
            st.markdown('<div class="poster-fallback large"><span>NO<br>POSTER</span></div>', unsafe_allow_html=True)

    with right:
        st.markdown(f'<div class="hero-kicker">{safe_text(movie.get("year"))} · {safe_text(movie.get("language"))}</div>', unsafe_allow_html=True)
        st.markdown(f'<h1 class="detail-title">{safe_text(movie.get("title"))}</h1>', unsafe_allow_html=True)
        if movie.get("tagline"):
            st.markdown(f'<p class="tagline-detail">{safe_text(movie["tagline"])}</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="detail-rating">★ {float(movie.get("rating") or 0):.1f} <span>TMDB · {int(movie.get("vote_count") or 0):,} votes</span></div>', unsafe_allow_html=True)
        st.write(movie.get("overview", ""))

        a, b, c, d = st.columns(4)
        cards = [
            (a, "Director", movie.get("director")),
            (b, "Genres", ", ".join(movie.get("genres", [])) or "Not listed"),
            (c, "Theatrical", movie.get("theatrical", "TBD")),
            (d, "Runtime", f'{movie.get("runtime")} min' if movie.get("runtime") else "Not listed"),
        ]
        for col, label, value in cards:
            with col:
                st.markdown(f'<div class="info-card"><div class="info-label">{label}</div><div class="info-value">{safe_text(value)}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-heading detail-section"><h2>Where to watch in India</h2><span>Current availability from TMDB / JustWatch · OTT release date is not inferred</span></div>', unsafe_allow_html=True)

    watch = movie.get("watch", [])
    if not watch:
        st.markdown('<div class="empty-state"><h3>No current India provider listed</h3><p>TMDB does not currently list an India streaming, rent, or purchase provider for this title.</p></div>', unsafe_allow_html=True)
    else:
        for row in watch:
            st.markdown('<div class="ott-row">', unsafe_allow_html=True)
            p1, p2, p3, p4 = st.columns([2.4, 1.2, 1.2, 1.4], vertical_alignment="center")
            with p1:
                if row.get("logo"):
                    st.image(row["logo"], width=48)
                st.markdown(f'<div class="ott-name">{safe_text(row["platform"])}</div><div class="ott-type">{safe_text(row["type"])}</div>', unsafe_allow_html=True)
            with p2:
                st.markdown('<div class="mini-label">OTT date</div><div class="mini-value">TBD</div>', unsafe_allow_html=True)
            with p3:
                st.markdown(f'<div class="mini-label">Status</div>{_status_badge(row["status"]) }', unsafe_allow_html=True)
            with p4:
                if row.get("source_url"):
                    st.link_button("View source", row["source_url"], use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-heading detail-section"><h2>Movie information</h2><span>Metadata supplied by TMDB</span></div>', unsafe_allow_html=True)
    x, y = st.columns(2)
    with x:
        langs = ", ".join(movie.get("languages", [])) or "Not listed"
        cast = ", ".join(movie.get("cast", [])) or "Not listed"
        st.markdown(f'<div class="info-card"><div class="info-label">TMDB-listed languages</div><div class="info-value">{safe_text(langs)}</div></div>', unsafe_allow_html=True)
    with y:
        st.markdown(f'<div class="info-card"><div class="info-label">Cast</div><div class="info-value">{safe_text(cast)}</div></div>', unsafe_allow_html=True)

    st.caption("Data and images: TMDB. OTT availability: TMDB / JustWatch. This product is not endorsed or certified by TMDB.")
