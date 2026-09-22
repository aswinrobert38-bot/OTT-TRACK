import os
import requests
import streamlit as st


TMDB_BASE_URL = "https://api.themoviedb.org/3"

IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
BACKDROP_BASE_URL = "https://image.tmdb.org/t/p/w1280"


class TMDBError(Exception):
    pass


def get_token():

    token = None

    try:
        token = st.secrets.get("TMDB_TOKEN")
    except Exception:
        pass

    if not token:
        token = os.getenv("TMDB_TOKEN")

    if not token:
        raise TMDBError(
            "TMDB_TOKEN is missing. Add TMDB_TOKEN to .env or Streamlit Cloud Secrets."
        )

    return str(token).strip()


def get_headers():

    return {
        "Authorization": "Bearer " + get_token(),
        "Content-Type": "application/json;charset=utf-8"
    }


def _request(endpoint, params=None):

    url = TMDB_BASE_URL + endpoint

    try:
        response = requests.get(
            url,
            headers=get_headers(),
            params=params,
            timeout=20
        )

    except requests.RequestException as error:

        raise TMDBError(
            "Unable to connect to TMDB: " + str(error)
        )

    if response.status_code != 200:

        try:
            message = response.json().get(
                "status_message",
                "TMDB request failed"
            )
        except Exception:
            message = "TMDB request failed"

        raise TMDBError(str(message))

    return response.json()


# =========================================================
# MOVIE NORMALIZATION
# =========================================================

def normalize_movie(movie):

    movie["poster_url"] = None
    movie["backdrop_url"] = None

    if movie.get("poster_path"):
        movie["poster_url"] = (
            IMAGE_BASE_URL +
            movie["poster_path"]
        )

    if movie.get("backdrop_path"):
        movie["backdrop_url"] = (
            BACKDROP_BASE_URL +
            movie["backdrop_path"]
        )

    movie["rating"] = movie.get(
        "vote_average",
        0
    )

    movie["content_type"] = "movie"

    return movie


# =========================================================
# TV / WEB SERIES NORMALIZATION
# =========================================================

def normalize_tv(show):

    show["poster_url"] = None
    show["backdrop_url"] = None

    if show.get("poster_path"):
        show["poster_url"] = (
            IMAGE_BASE_URL +
            show["poster_path"]
        )

    if show.get("backdrop_path"):
        show["backdrop_url"] = (
            BACKDROP_BASE_URL +
            show["backdrop_path"]
        )

    show["rating"] = show.get(
        "vote_average",
        0
    )

    show["content_type"] = "tv"

    return show


# =========================================================
# MOVIE SEARCH
# =========================================================

def search_movies(
    query,
    page=1,
    year=None,
    language=None
):

    params = {
        "query": query.strip(),
        "page": page,
        "include_adult": False,
        "region": "IN"
    }

    if year:
        params["year"] = year

    if language:
        params["with_original_language"] = language

    data = _request(
        "/search/movie",
        params
    )

    data["results"] = [
        normalize_movie(movie)
        for movie in data.get("results", [])
    ]

    return data


# =========================================================
# TV SEARCH
# =========================================================

def search_tv(
    query,
    page=1,
    language=None
):

    params = {
        "query": query.strip(),
        "page": page,
        "include_adult": False,
        "region": "IN"
    }

    if language:
        params["with_original_language"] = language

    data = _request(
        "/search/tv",
        params
    )

    data["results"] = [
        normalize_tv(show)
        for show in data.get("results", [])
    ]

    return data


# =========================================================
# MOVIES + TV TOGETHER
# =========================================================

def search_multi(
    query,
    page=1
):

    data = _request(
        "/search/multi",
        {
            "query": query.strip(),
            "page": page,
            "include_adult": False,
            "region": "IN"
        }
    )

    results = []

    for item in data.get("results", []):

        media_type = item.get("media_type")

        if media_type == "movie":

            item["content_type"] = "movie"

            results.append(
                normalize_movie(item)
            )

        elif media_type == "tv":

            item["content_type"] = "tv"

            results.append(
                normalize_tv(item)
            )

    data["results"] = results

    return data


# =========================================================
# HOME MOVIE DATA
# =========================================================

def get_now_playing(page=1):

    data = _request(
        "/movie/now_playing",
        {
            "region": "IN",
            "page": page
        }
    )

    data["results"] = [
        normalize_movie(movie)
        for movie in data.get("results", [])
    ]

    return data


def get_popular(page=1):

    data = _request(
        "/movie/popular",
        {
            "region": "IN",
            "page": page
        }
    )

    data["results"] = [
        normalize_movie(movie)
        for movie in data.get("results", [])
    ]

    return data


def get_trending():

    data = _request(
        "/trending/movie/week"
    )

    data["results"] = [
        normalize_movie(movie)
        for movie in data.get("results", [])
    ]

    return data


def get_upcoming(page=1):

    data = _request(
        "/movie/upcoming",
        {
            "region": "IN",
            "page": page
        }
    )

    data["results"] = [
        normalize_movie(movie)
        for movie in data.get("results", [])
    ]

    return data


# =========================================================
# MOVIE DETAILS
# =========================================================

def get_movie_details(movie_id):

    data = _request(
        "/movie/" + str(movie_id),
        {
            "append_to_response":
                "credits,videos,external_ids"
        }
    )

    return normalize_movie(data)


# =========================================================
# MOVIE OTT PROVIDERS
# =========================================================

def get_watch_providers(movie_id):

    return _request(
        "/movie/" +
        str(movie_id) +
        "/watch/providers"
    )


# =========================================================
# TV / WEB SERIES DETAILS
# =========================================================

def get_tv_details(tv_id):

    data = _request(
        "/tv/" + str(tv_id),
        {
            "append_to_response":
                "credits,videos,external_ids"
        }
    )

    return normalize_tv(data)


# =========================================================
# TV / WEB SERIES OTT PROVIDERS
# =========================================================

def get_tv_watch_providers(tv_id):

    return _request(
        "/tv/" +
        str(tv_id) +
        "/watch/providers"
    )


# =========================================================
# OTT WATCH DATA
# =========================================================

def build_watch_data(content_id, content_type="movie"):

    if content_type == "tv":

        provider_data = get_tv_watch_providers(
            content_id
        )

    else:

        provider_data = get_watch_providers(
            content_id
        )

    india = provider_data.get(
        "results",
        {}
    ).get(
        "IN",
        {}
    )

    return {
        "link": india.get("link"),
        "flatrate": india.get("flatrate", []),
        "free": india.get("free", []),
        "ads": india.get("ads", []),
        "rent": india.get("rent", []),
        "buy": india.get("buy", [])
    }
