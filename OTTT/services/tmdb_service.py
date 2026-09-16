import os
from typing import Any, Dict, List, Optional

import requests
import streamlit as st

BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE = "https://image.tmdb.org/t/p"


class TMDBError(Exception):
    pass


def get_token() -> str:
    token = os.getenv("TMDB_API_KEY", "").strip()
    if not token or token.lower().startswith("your_"):
        return ""
    return token


def _headers() -> Dict[str, str]:
    token = get_token()
    if not token:
        raise TMDBError("TMDB_API_KEY is missing")
    return {"Authorization": f"Bearer {token}", "accept": "application/json"}


@st.cache_data(ttl=900, show_spinner=False)
def tmdb_get(path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    try:
        response = requests.get(
            f"{BASE_URL}{path}",
            headers=_headers(),
            params=params or {},
            timeout=15,
        )
    except requests.RequestException as exc:
        raise TMDBError(f"Network error while contacting TMDB: {exc}") from exc

    if response.status_code == 401:
        raise TMDBError("TMDB token is invalid or expired.")
    if response.status_code == 429:
        raise TMDBError("TMDB rate limit reached. Please wait and try again.")
    if not response.ok:
        try:
            message = response.json().get("status_message", response.text)
        except Exception:
            message = response.text
        raise TMDBError(f"TMDB request failed: {message}")

    return response.json()


def image_url(path: Optional[str], size: str = "w500") -> str:
    if not path:
        return ""
    return f"{IMAGE_BASE}/{size}{path}"


def poster_url(path: Optional[str]) -> str:
    return image_url(path, "w500")


def backdrop_url(path: Optional[str]) -> str:
    return image_url(path, "w1280")


def search_movies(query: str, page: int = 1, year: Optional[int] = None, language: Optional[str] = None) -> List[Dict[str, Any]]:
    params: Dict[str, Any] = {
        "query": query,
        "page": page,
        "include_adult": "false",
        "language": "en-IN",
        "region": "IN",
    }
    if year:
        params["year"] = year
    if language:
        params["with_original_language"] = language

    data = tmdb_get("/search/movie", params)
    return data.get("results", [])


def get_movie(movie_id: int) -> Dict[str, Any]:
    return tmdb_get(
        f"/movie/{movie_id}",
        {
            "language": "en-IN",
            "append_to_response": "credits,release_dates,videos,watch/providers",
        },
    )


def get_watch_providers(movie_id: int) -> Dict[str, Any]:
    data = tmdb_get(f"/movie/{movie_id}/watch/providers")
    return data.get("results", {}).get("IN", {})


def get_now_playing(page: int = 1) -> List[Dict[str, Any]]:
    return tmdb_get("/movie/now_playing", {"language": "en-IN", "region": "IN", "page": page}).get("results", [])


def get_upcoming(page: int = 1) -> List[Dict[str, Any]]:
    return tmdb_get("/movie/upcoming", {"language": "en-IN", "region": "IN", "page": page}).get("results", [])


def get_popular(page: int = 1) -> List[Dict[str, Any]]:
    return tmdb_get("/movie/popular", {"language": "en-IN", "region": "IN", "page": page}).get("results", [])


def get_trending() -> List[Dict[str, Any]]:
    return tmdb_get("/trending/movie/week", {"language": "en-IN"}).get("results", [])


def _provider_name(provider: Dict[str, Any]) -> str:
    return provider.get("provider_name", "Unknown platform")


def _provider_logo(provider: Dict[str, Any]) -> str:
    return image_url(provider.get("logo_path"), "w92")


def build_watch_data(movie_id: int) -> List[Dict[str, Any]]:
    data = get_watch_providers(movie_id)
    rows: List[Dict[str, Any]] = []

    # TMDB's watch-provider endpoint is powered by JustWatch. It reports
    # current availability categories, not an OTT release-date history.
    for bucket, label in [
        ("flatrate", "Streaming"),
        ("free", "Free"),
        ("ads", "Streaming with Ads"),
        ("rent", "Rent"),
        ("buy", "Buy"),
    ]:
        for provider in data.get(bucket, []) or []:
            rows.append(
                {
                    "platform": _provider_name(provider),
                    "logo": _provider_logo(provider),
                    "type": label,
                    "date": "TBD",
                    "status": "Date Not Announced",
                    "source": "TMDB / JustWatch availability",
                    "source_url": data.get("link", "https://www.themoviedb.org/"),
                    "source_strength": "Availability data",
                }
            )

    # Avoid duplicate platform + type entries.
    unique = {}
    for row in rows:
        unique[(row["platform"], row["type"])] = row
    return list(unique.values())


def normalize_movie(item: Dict[str, Any]) -> Dict[str, Any]:
    release_date = item.get("release_date") or "TBD"
    release_year = release_date[:4] if release_date and release_date != "TBD" else "TBD"
    return {
        "id": item.get("id"),
        "title": item.get("title") or item.get("original_title") or "Untitled",
        "original_title": item.get("original_title") or item.get("title") or "Untitled",
        "year": release_year,
        "release_date": release_date,
        "language_code": item.get("original_language", "unknown"),
        "language": (item.get("original_language") or "unknown").upper(),
        "rating": item.get("vote_average") or 0,
        "vote_count": item.get("vote_count") or 0,
        "poster": poster_url(item.get("poster_path")),
        "backdrop": backdrop_url(item.get("backdrop_path")),
        "overview": item.get("overview") or "No overview is available from TMDB.",
    }


def normalize_details(item: Dict[str, Any]) -> Dict[str, Any]:
    normalized = normalize_movie(item)
    credits = item.get("credits", {}) or {}
    crew = credits.get("crew", []) or []
    cast = credits.get("cast", []) or []
    directors = [p.get("name") for p in crew if p.get("job") == "Director" and p.get("name")]

    release_dates = []
    for country in (item.get("release_dates", {}) or {}).get("results", []) or []:
        if country.get("iso_3166_1") == "IN":
            release_dates = country.get("release_dates", []) or []
            break
    theatrical = item.get("release_date") or "TBD"
    if release_dates:
        dated = [r.get("release_date", "") for r in release_dates if r.get("release_date")]
        if dated:
            theatrical = min(dated)[:10]

    normalized.update(
        {
            "genres": [g.get("name") for g in item.get("genres", []) if g.get("name")],
            "runtime": item.get("runtime"),
            "status": item.get("status"),
            "tagline": item.get("tagline") or "",
            "director": ", ".join(dict.fromkeys(directors)) or "Not listed",
            "cast": [p.get("name") for p in cast[:12] if p.get("name")],
            "languages": [x.get("english_name") or x.get("name") for x in item.get("spoken_languages", []) if x.get("english_name") or x.get("name")],
            "theatrical": theatrical,
            "homepage": item.get("homepage") or "",
            "imdb_id": item.get("imdb_id") or "",
            "watch": build_watch_data(item.get("id")),
        }
    )
    return normalized
