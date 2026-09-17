import html
import streamlit as st


def safe_text(value, fallback="Not available"):
    if value is None or value == "":
        return fallback
    return html.escape(str(value))


def rating_text(rating, votes=0):
    if not rating:
        return "NR"
    if votes:
        return f"★ {float(rating):.1f} · {int(votes):,} votes"
    return f"★ {float(rating):.1f}"


def movie_card(movie, key_suffix=""):
    poster = movie.get("poster") or movie.get("poster_url", "")
    movie_id = movie.get("id")

    if poster:
        st.image(poster, use_container_width=True)
    else:
        st.markdown(
            '<div class="poster-fallback"><span>NO<br>POSTER</span></div>',
            unsafe_allow_html=True
        )

    title = safe_text(movie.get("title", "Untitled"))
    year = safe_text(movie.get("year", "TBD"))
    language = safe_text(movie.get("language") or movie.get("original_language", "Unknown"))
    rating = rating_text(movie.get("rating"), movie.get("vote_count", 0))

    st.markdown(
        f'<div class="movie-title">{title}</div><div class="movie-meta">{year} · {language} · {rating}</div>',
        unsafe_allow_html=True,
    )

    if movie_id is not None:
        if st.button(
            "View movie details",
            key=f"view_{movie_id}_{key_suffix}",
            use_container_width=True,
        ):
            st.session_state.open_movie_id = movie_id
            st.rerun()
