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

    return movie


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


def get_movie_details(movie_id):

    data = _request(
        "/movie/" + str(movie_id),
        {
            "append_to_response": "credits,videos"
        }
    )

    return normalize_movie(data)


def get_watch_providers(movie_id):

    return _request(
        "/movie/" +
        str(movie_id) +
        "/watch/providers"
    )
