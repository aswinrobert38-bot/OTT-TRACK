import html
import streamlit as st


def safe_text(value, fallback="Not available"):
    if value is None or value == "":
        return fallback
    return html.escape(str(value))


def rating_text(rating, votes=0):
    if rating in (None, ""):
        return "NR"
    try:
        base = f"★ {float(rating):.1f}"
        return f"{base} · {int(votes):,} votes" if votes else base
    except (TypeError, ValueError):
        return "NR"


def movie_card(movie, key_suffix=""):
    """Compatibility helper using the same single navigation state as Home."""
    poster = movie.get("poster") or movie.get("poster_url")
    movie_id = movie.get("id")
    content_type = movie.get("content_type", "movie")
    title = safe_text(movie.get("title") or movie.get("name") or "Untitled")
    year = safe_text(movie.get("year") or movie.get("release_date", "")[:4] or "TBD")
    language = safe_text(movie.get("language") or movie.get("original_language") or "Unknown")
    rating = rating_text(movie.get("rating"), movie.get("vote_count", 0))

    if poster:
        st.image(poster, use_container_width=True)
    else:
        st.markdown('<div class="rr-empty">NO POSTER</div>', unsafe_allow_html=True)

    st.markdown(
        f'<div class="rr-card-title">{title}</div><div class="rr-card-meta">{year} · {language} · {rating}</div>',
        unsafe_allow_html=True,
    )

    if movie_id is not None and st.button("View Details", key=f"compat_{content_type}_{movie_id}_{key_suffix}", use_container_width=True):
        st.session_state.open_content = {"id": int(movie_id), "type": content_type}
        st.session_state.pop("selected_movie_id", None)
        st.session_state.pop("open_movie_id", None)
        st.rerun()
